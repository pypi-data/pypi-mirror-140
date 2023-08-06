'''
tensorrt_use.py
tensorrt模型初始化与调用使用程序


'''
import os
import random
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit
import numpy as np
import time
import cv2
from PIL import Image

TRT_LOGGER = trt.Logger()

def letterbox_image(image, size):
    '''
        图像按比例resize
        Args:
            image: 输入待resize图像
            size: resize到的size大小

        Returns:

    '''

    '''resize image with unchanged aspect ratio using padding'''
    iw, ih = image.size
    h, w = size
    scale = min(w/iw, h/ih)
    nw = int(iw*scale)
    nh = int(ih*scale)

    image = image.resize((w,h), Image.BICUBIC)
    # image = image.resize((nw,nh), Image.BICUBIC)
    # new_image = Image.new('RGB', size, (128,128,128))
    # new_image.paste(image, ((w-nw)//2, (h-nh)//2))
    return image

def preprocess_input(x):
    x /= 127.5
    x -= 1.
    return x

def cvtColor(image):
    '''
        图像转为伪灰度图
        Args:
            image:

        Returns:

    '''
    image = image.convert('L')
    if len(np.shape(image)) == 3 and np.shape(image)[-2] == 3:
        return image
    else:
        image = image.convert('RGB')
        return image

def get_img_np_nchw(image):

    '''
    Image格式图像转tensorrt输入图像
    Args:
        image: Image格式图像

    Returns: tensorrt输入图像

    '''
    image = cvtColor(image)
    # ---------------------------------------------------#
    #   对图片进行不失真的resize
    # ---------------------------------------------------#
    image_data = letterbox_image(image, [224, 224])
    # ---------------------------------------------------------#
    #   归一化+添加上batch_size维度+转置
    # ---------------------------------------------------------#
    image_data = np.transpose(np.expand_dims(preprocess_input(np.array(image_data, np.float32)), 0), (0, 3, 1, 2))
    return image_data

class HostDeviceMem(object):
    def __init__(self, host_mem, device_mem):
        super(HostDeviceMem, self).__init__()
        self.host = host_mem
        self.device = device_mem

    def __str__(self):
        return "Host:\n" + str(self.host) + "\nDevice:\n" + str(self.device)

    def __repr__(self):
        return self.__str__()

def allocate_buffers(engine):
    inputs = []
    outputs = []
    bindings = []
    stream = cuda.Stream()  # pycuda 操作缓冲区
    for binding in engine:
        size = trt.volume(engine.get_binding_shape(binding)) * engine.max_batch_size
        dtype = trt.nptype(engine.get_binding_dtype(binding))

        host_mem = cuda.pagelocked_empty(size, dtype)
        device_mem = cuda.mem_alloc(host_mem.nbytes)  # 分配内存
        bindings.append(int(device_mem))

        if engine.binding_is_input(binding):
            inputs.append(HostDeviceMem(host_mem, device_mem))
        else:
            outputs.append(HostDeviceMem(host_mem, device_mem))
    return inputs, outputs, bindings, stream

def get_engine(engine_file_path=""):
    print("Reading engine from file {}".format(engine_file_path))
    with open(engine_file_path, "rb") as f, trt.Runtime(TRT_LOGGER) as runtime:
        return runtime.deserialize_cuda_engine(f.read())

def do_inference(context, bindings, inputs, outputs, stream, batch_size=1):
    [cuda.memcpy_htod_async(inp.device, inp.host, stream) for inp in inputs]  # 将输入放入device
    context.execute_async(batch_size=batch_size, bindings=bindings, stream_handle=stream.handle)  # 执行模型推理
    [cuda.memcpy_dtoh_async(out.host, out.device, stream) for out in outputs]  # 将预测结果从缓冲区取出
    stream.synchronize()  # 线程同步
    return [out.host for out in outputs]

def postprocess_the_outputs(h_outputs, shape_of_output):
    h_outputs = h_outputs.reshape(*shape_of_output)
    return h_outputs

def init():
    '''
    预留模型初始化函数
    Returns:

    '''
    trt_engine_path = './app/ai/screening/model_data/resnet50.trt'
    engine = get_engine(trt_engine_path)
    context = engine.create_execution_context()
    print(111111111)
    return engine,context

# 为了解决多进程使用模型问题
import pycuda.driver as cuda
cuda.init()
device = cuda.Device(0)
ctx = device.make_context()

# 现模型初始化
current_model_path = "./app/ai/screening/model_data/notexture_2_16_vgg16_fp16.trt"
# engine = get_engine('./app/ai/screening/model_data/notexture_1_26_vgg16_fp32.trt')
engine = get_engine(current_model_path)
# engine = get_engine('./app/ai/screening/model_data/notexture_1_24_vgg16.trt')
# engine1 = get_engine('./app/ai/screening/model_data/resnet50.trt')
context = engine.create_execution_context()
# context1 = engine.create_execution_context()
inputs, outputs, bindings, stream = allocate_buffers(engine)
# inputs1, outputs1, bindings1, stream1 = allocate_buffers(engine1)

class Classification(object):
    _defaults = {
        #--------------------------------------------------------------------------#
        #   使用自己训练好的模型进行预测一定要修改model_path和classes_path！
        #   model_path指向logs文件夹下的权值文件，classes_path指向model_data下的txt
        #   如果出现shape不匹配，同时要注意训练时的model_path和classes_path参数的修改
        #--------------------------------------------------------------------------#
        "model_path"    : './app/ai/screening/model_data/resnet50.trt',
        "classes_path"  : './app/ai/screening/model_data/cls_classes.txt',
        #--------------------------------------------------------------------#
        #   输入的图片大小
        #--------------------------------------------------------------------#
        "input_shape"   : [224, 224],
        #--------------------------------------------------------------------#
        #   所用模型种类：
        #   mobilenet、resnet50、vgg16是常用的分类网络
        #   cspdarknet53用于示例如何使用mini_imagenet训练自己的预训练权重
        #--------------------------------------------------------------------#
        "backbone"      : 'resnet50',
        #-------------------------------#
        #   是否使用Cuda
        #   没有GPU可以设置成False
        #-------------------------------#
        "cuda"          : True
    }

    @classmethod
    def get_defaults(cls, n):
        if n in cls._defaults:
            return cls._defaults[n]
        else:
            return "Unrecognized attribute name '" + n + "'"

    #---------------------------------------------------#
    #   初始化classification
    #---------------------------------------------------#
    def __init__(self, **kwargs):
        self.__dict__.update(self._defaults)
        for name, value in kwargs.items():
            setattr(self, name, value)

        #---------------------------------------------------#
        #   获得种类
        #---------------------------------------------------#
        # self.class_names, self.num_classes = get_classes(self.classes_path)
        # self.generate()

    #---------------------------------------------------#
    #   获得所有的分类
    #---------------------------------------------------#
    def generate(self):
        #---------------------------------------------------#
        #   载入模型与权值
        #---------------------------------------------------#
        self.engine = get_engine(self.model_path)
        self.context = self.engine.create_execution_context()

    def landmark_detection(self,image):
        # self.engine = get_engine(self.model_path)
        # context = self.engine.create_execution_context()
        ctx.push()

        # image = cv2.imread(image_path)
        # image = Image.fromarray(image)
        img_np_nchw = get_img_np_nchw(image)
        img_np_nchw = img_np_nchw.astype(dtype=np.float32)

        inputs[0].host = img_np_nchw.reshape(-1)
        # i = random.randint(0,10)
        # t1 = time.time()
        trt_outputs = do_inference(context, bindings=bindings, inputs=inputs, outputs=outputs, stream=stream)
        # if i%2==0:
        #     print("调用模型1--------------------------------------------------------------")
        #     trt_outputs = do_inference(context, bindings=bindings, inputs=inputs, outputs=outputs, stream=stream)
        # else:
        #     print("调用模型222222--------------------------------------------------------------")
        #     trt_outputs = do_inference(context1, bindings=bindings1, inputs=inputs1, outputs=outputs1, stream=stream1)
        class_names = ["defect", "nodefect"]
        class_name = class_names[np.argmax(trt_outputs)]
        ctx.pop()
        # t2 = time.time()
        # print('used time: ', t2 - t1)
        # print("trt_outputs")
        # print(class_name)
        # shape_of_output = (1, 212)
        # landmarks = postprocess_the_outputs(trt_outputs[1], shape_of_output)
        # landmarks = landmarks.reshape(landmarks.shape[0], -1, 2)
        #
        # height, width = image.shape[:2]
        # pred_landmark = landmarks[0] * [height, width]
        #
        # for (x, y) in pred_landmark.astype(np.int32):
        #     cv2.circle(image, (x, y), 1, (0, 255, 255), -1)
        #
        # cv2.imshow('landmarks', image)
        # cv2.waitKey(0)

        return class_name

    def getModelName(self):
        return os.path.basename(current_model_path)

