'''
predict.py有几个注意点
1、无法进行批量预测，如果想要批量预测，可以利用os.listdir()遍历文件夹，利用Image.open打开图片文件进行预测。
2、如果想要将预测结果保存成txt，可以利用open打开txt文件，使用write方法写入txt，可以参考一下txt_annotation.py文件。
'''
import os
import shutil
import time
import sys
import numpy as np
from PIL import Image
sys.path.append("./app/ai/screening")

# print(sys.path)
# from classification import Classification
# import seaborn as sns
# import matplotlib.pyplot as plt
from skimage import measure
import cv2
import multiprocessing as mp
from pathlib import Path
import json
# import tensorrt_use

queue_final_res = mp.Queue(maxsize=100)
queue_in = mp.Queue(maxsize=1000)

def sliding_window(image, stepSize, windowSize):
    # slide a window across the image
    for y in range(0, image.shape[0], stepSize):
        for x in range(0, image.shape[1], stepSize):
            # yield the current window
            yield (x, y, image[y:y + windowSize[1], x:x + windowSize[0]])

def mergeBox(boxes):
    new_box = []
    record = []
    for i in range(len(boxes)):
        box_now = boxes[i]
        y1 = box_now[0]
        x1 = box_now[1]
        y2 = box_now[2]
        x2 = box_now[3]
        if i in record:
            temp = [y1, x1, y2, x2]
            new_box.append(temp)
            continue
        j = 0
        while (j < len(boxes)):
            flag = False
            if (j != i and j not in record):
                box_temp = boxes[j]
                y11 = box_temp[0]
                x11 = box_temp[1]
                y21 = box_temp[2]
                x21 = box_temp[3]
                if (max(abs(y21 - y1),abs(y2-y11)) <= (y2 - y1 + y21 - y11)) and (max(abs(x2-x11),abs(x21 - x1)) <= (x2 - x1 + x21 - x11)):
                    y1 = min(y1, y11)
                    x2 = max(x2, x21)
                    x1 = min(x1, x11)
                    y2 = max(y2, y21)
                    record.append(j)
                    flag = True
            j = j + 1
            if flag == True:
                j = 0
        temp = [y1, x1, y2, x2]
        new_box.append(temp)
        boxes[i] = temp
    new_box = [new_box[i] for i in range(0, len(new_box), 1) if i not in record]
    return new_box


##
##image:二值图像
##threshold_point:符合面积条件大小的阈值
def remove_small_points(image, threshold_point,resized):
    img = image  # 输入的二值图像
    img_label, num = measure.label(img, connectivity=2, return_num=True)  # 输出二值图像中所有的连通域
    props = measure.regionprops(img_label)  # 输出连通域的属性，包括面积等
    uuu_list = []
    for i in props:

        if i.area > threshold_point:
            uuu = i.bbox
            # if 0 in uuu:
            #     continue
            if np.average(image[uuu[0]:uuu[2],uuu[1]:uuu[3]])<1:
                continue
            else:
                uuu_list.append(uuu)
            # cv2.rectangle(resized,(uuu[1],uuu[0]),(uuu[3],uuu[2]),(0,255,0,), 5)
    flag = []
    for i in range(len(uuu_list)):
        uuu_now = uuu_list[i]
        y1 = uuu_now[0]
        x1 = uuu_now[1]
        y2 = uuu_now[2]
        x2 = uuu_now[3]
        for j in range(len(uuu_list)):
            if j == i:
                continue
            uuu_temp = uuu_list[j]
            y11 = uuu_temp[0]
            x11 = uuu_temp[1]
            y21 = uuu_temp[2]
            x21 = uuu_temp[3]
            xxx = ((x1 >= x11) and (x2 <= x21) and (y1 >= y11) and (y2 <= y21))
            if xxx:
                flag.append(i)
                continue

    uuu_list_np = np.array(uuu_list)
    uuu_list_np = np.delete(uuu_list_np,flag,axis=0)
    uuu_list_use = uuu_list_np.tolist()
    uuu_list_use_merge = mergeBox(uuu_list_use)
    return uuu_list_use_merge



def slideWindow(queue_in,queue_slide1,queue_slide2,queue_slide3,queue_slide4):
    while True:
        if queue_in.qsize()>0:
            start_slide = time.time()
            try:
                input = queue_in.get()
                print("has image in")
            except:
                print('Open Error! Try again!')
                continue

            else:
                if input is None:
                    print("has none image")
                    continue
                (winW, winH) = (224, 224)
                # (winW, winH) = (448, 448)
                resized = cv2.resize(input, (int(0.5*input.shape[1]), int(0.5*input.shape[0])),interpolation=cv2.INTER_AREA)
                # resized = cv2.resize(input, (int(input.shape[1]), int(input.shape[0])),interpolation=cv2.INTER_AREA)
                # resized = input
                slide_image = []
                cnt = 0
                for (x, y, window) in sliding_window(resized, stepSize=224, windowSize=(winW, winH)):
                    cnt = cnt + 1
                    image_map_temp = {}
                    # if the window does not meet our desired window size, ignore it
                    if window.shape[0] != winH or window.shape[1] != winW:
                        continue

                    # THIS IS WHERE YOU WOULD PROCESS YOUR WINDOW, SUCH AS APPLYING A
                    # MACHINE LEARNING CLASSIFIER TO CLASSIFY THE CONTENTS OF THE
                    # WINDOW

                    # since we do not have a classifier, we'll just draw the window
                    img_use_temp = resized[y:y + winH, x:x + winW]
                    image_map_temp["id"] = cnt
                    image_map_temp["image"] = img_use_temp
                    image_map_temp["x"] = x
                    image_map_temp["y"] = y
                    image_map_temp["winH"] = winH
                    image_map_temp["winW"] = winW
                    image_map_temp["imgTotal"] = resized
                    # image_map_temp["name"] = img
                    slide_image.append(image_map_temp)
                queue_slide1.put(slide_image[:int(0.25 * len(slide_image))])
                queue_slide2.put(slide_image[int(0.25 * len(slide_image)):int(0.5 * len(slide_image))])
                queue_slide3.put(slide_image[int(0.5 * len(slide_image)):int(0.75 * len(slide_image))])
                queue_slide4.put(slide_image[int(0.75 * len(slide_image)):])
                end_slide = time.time()
                print("slide cost "+str(end_slide-start_slide))


def onlineMatch1(queue1,queue1_res,classfication):

    while True:
        if queue1.qsize()>0:
            list_temp = queue1.get()
            list_res = []
            for map_temp in list_temp:
                img_use_temp = Image.fromarray(map_temp["image"])
                class_name = classfication.landmark_detection(img_use_temp)
                # class_name = tensorrt_use.landmark_detection(img_use_temp,classfication,context)
                map_temp["class"] = class_name
                list_res.append(map_temp)
            queue1_res.put(list_res)

def onlineMatch2(queue2,queue2_res,classfication):

    while True:
        if queue2.qsize() > 0:
            list_temp = queue2.get()
            list_res = []
            for map_temp in list_temp:
                img_use_temp = Image.fromarray(map_temp["image"])
                # start_inference_time = time.time()
                class_name = classfication.landmark_detection(img_use_temp)
                # end_inference_time = time.time()
                # print("inference cost "+str(end_inference_time-start_inference_time))
                # class_name = tensorrt_use.landmark_detection(img_use_temp,classfication,context)
                map_temp["class"] = class_name
                list_res.append(map_temp)
            queue2_res.put(list_res)


def onlineMatch3(queue3,queue3_res,classfication):

    while True:
        if queue3.qsize() > 0:
            list_temp = queue3.get()
            list_res = []
            for map_temp in list_temp:
                img_use_temp = Image.fromarray(map_temp["image"])
                class_name = classfication.landmark_detection(img_use_temp)
                # class_name = tensorrt_use.landmark_detection(img_use_temp,classfication,context)
                map_temp["class"] = class_name
                list_res.append(map_temp)
            queue3_res.put(list_res)


def onlineMatch4(queue4,queue4_res,classfication):

    while True:
        if queue4.qsize() > 0:
            list_temp = queue4.get()
            list_res = []
            for map_temp in list_temp:
                img_use_temp = Image.fromarray(map_temp["image"])
                # stat_infer = time.time()
                class_name = classfication.landmark_detection(img_use_temp)
                # end_infer = time.time()
                # print("-------------------"+str(end_infer-stat_infer))
                # class_name = tensorrt_use.landmark_detection(img_use_temp,classfication,context)
                map_temp["class"] = class_name
                list_res.append(map_temp)
            queue4_res.put(list_res)

# def getInputImage(queue_in):
#     new_save_dir = "./save_origin"
#     first_flag = True
#
#     if not os.path.exists(new_save_dir):
#         os.mkdir(new_save_dir)
#         print("dir make")
#     else:
#         print("already make")
#     while True:
#         # print("input inuse")
#         scan_image_path_list = scanUtils.readDir("/sdc/workspace/micode")
#         # print(scan_image_path_list)
#         while(queue_in.qsize()>=0 and queue_in.qsize()<50 and len(scan_image_path_list)>0):
#             # print("queue_in size is: "+str(queue_in.qsize()))
#
#             for i in scan_image_path_list:
#                 new_path = os.path.join(new_save_dir,os.path.basename(i))
#                 my_file = Path(new_path)
#
#                 if not my_file.exists():
#                     shutil.copy(i,new_save_dir)
#                     # os.remove(i)
#                     queue_in.put(i)
#                     first_flag = False
#                     print(str(i)+" in the queue")
#                 # else:
#                 #     print("already used")
#
#
#
#                 if queue_in.qsize()>=50:
#                     time.sleep(3)
#                     break
#             if queue_in.qsize() == 0 and first_flag == False:
#                 break



def processRes(queue1_res,queue2_res,queue3_res,queue4_res,queue_final_res):
    while True:
        if queue1_res.qsize()>0 and queue2_res.qsize()>0 and queue3_res.qsize()>0 and queue4_res.qsize()>0:
            start_process = time.time()
            list_temp1 = queue1_res.get()
            list_temp2 = queue2_res.get()
            list_temp3 = queue3_res.get()
            list_temp4 = queue4_res.get()
            # img = list_temp1[0]["name"]
            print("img out queue")
            resized = list_temp1[0]["imgTotal"]
            # resized = cv2.resize(resized, (int(0.5 * resized.shape[1]), int(0.5 * resized.shape[0])),
            #                      interpolation=cv2.INTER_AREA)
            uniform_data = np.zeros((int(resized.shape[0]), int(resized.shape[1])))
            for map_temp in list_temp1:
                if map_temp["class"] == "defect":
                    y = map_temp["y"]
                    winH = map_temp["winH"]
                    x = map_temp["x"]
                    winW = map_temp["winW"]
                    uniform_data[y:y + winH, x:x + winW] = uniform_data[y:y + winH, x:x + winW] + 1
            for map_temp in list_temp2:
                if map_temp["class"] == "defect":
                    y = map_temp["y"]
                    winH = map_temp["winH"]
                    x = map_temp["x"]
                    winW = map_temp["winW"]
                    uniform_data[y:y + winH, x:x + winW] = uniform_data[y:y + winH, x:x + winW] + 1
            for map_temp in list_temp3:
                if map_temp["class"] == "defect":
                    y = map_temp["y"]
                    winH = map_temp["winH"]
                    x = map_temp["x"]
                    winW = map_temp["winW"]
                    uniform_data[y:y + winH, x:x + winW] = uniform_data[y:y + winH, x:x + winW] + 1
            for map_temp in list_temp4:
                if map_temp["class"] == "defect":
                    y = map_temp["y"]
                    winH = map_temp["winH"]
                    x = map_temp["x"]
                    winW = map_temp["winW"]
                    uniform_data[y:y + winH, x:x + winW] = uniform_data[y:y + winH, x:x + winW] + 1
            try:
                merge_res = remove_small_points(uniform_data, 1,resized)
                final_res_to_return = {}
                # final_res_to_return["metadata"] = {}

                # imgname = os.path.basename(img)
                res = {}
                # res["imgname"] = imgname
                str_list_liujun = []
                # img_name_use = imgname.split(".")[0]
                res_loc_list = []
                for uuu in merge_res:
                    xxx = {}
                    loc_temp = {}
                    res_img = resized[uuu[0]:uuu[2], uuu[1]:uuu[3]]
                    # cv2.rectangle(resized, (uuu[1], uuu[0]), (uuu[3], uuu[2]), (0, 255, 0,), 5)
                    str_list_liujun.append([[uuu[1], uuu[0]],[uuu[3], uuu[2]]])
                    loc_temp["xmin"] = uuu[1]*2
                    loc_temp["ymin"] = uuu[0]*2
                    loc_temp["xmax"] = uuu[3]*2
                    loc_temp["ymax"] = uuu[2]*2
                    xxx["loc"] = loc_temp
                    res_loc_list.append(xxx)
                print(len(res_loc_list))
                if len(str_list_liujun) == 0:
                    final_res_to_return["has_blemish"] = False
                else:
                    final_res_to_return["has_blemish"] = True


                final_res_to_return["res"] = res_loc_list
                end_process = time.time()
                print("process res " + str(end_process - start_process))
                queue_final_res.put(final_res_to_return)


            except Exception as e:
                print(e)
                print("erro in process res")
                # print(imgname)
def mmm():
    while True:
        print(1)
        time.sleep(5)
def initChushai():
    '''
    初筛初始化
    return
    classfication：分类器
    queue_in：输入队列
    queue_final_res：结果队列
    '''
    # classfication = Classification()
    import tensorrt_use
    classfication = tensorrt_use.Classification()
    time.sleep(10)
    mp.set_start_method(method='spawn',force=True)
    # mp.set_start_method(method='spawn')
    queue1 = mp.Queue(maxsize=100)
    queue2 = mp.Queue(maxsize=100)
    queue3 = mp.Queue(maxsize=100)
    queue4 = mp.Queue(maxsize=100)
    queue1_res = mp.Queue(maxsize=100)
    queue2_res = mp.Queue(maxsize=100)
    queue3_res = mp.Queue(maxsize=100)
    queue4_res = mp.Queue(maxsize=100)
    # queue_final_res = mp.Queue(maxsize=100)
    # queue_in = mp.Queue(maxsize=1000)
    # # queue_model_1 = mp.Queue(maxsize=2)
    # # queue_model_1.put(classfication)
    # # queue_model_1.put(context)
    # # queue_model_2 = mp.Queue(maxsize=2)
    # # queue_model_2.put(classfication)
    # # queue_model_2.put(context)
    # # queue_model_1 = mp.Queue(maxsize=2)
    # # queue_model_1.put(classfication)
    # # queue_model_1.put(context)
    # # queue_model_2 = mp.Queue(maxsize=2)
    # # queue_model_2.put(classfication)
    # # queue_model_2.put(context)
    # # queue_model_3 = mp.Queue(maxsize=2)
    # # queue_model_3.put(classfication)
    # # queue_model_3.put(context)
    # # queue_model_4 = mp.Queue(maxsize=2)
    # # queue_model_4.put(classfication)
    # # queue_model_4.put(context)

    # # queue_split_daijian = mp.Queue(maxsize=1000)

    processes = [
        mp.Process(target=slideWindow, args=(queue_in, queue1, queue2, queue3, queue4)),
        mp.Process(target=processRes, args=(queue1_res, queue2_res, queue3_res, queue4_res, queue_final_res)),
        mp.Process(target=onlineMatch1, args=(queue1, queue1_res,classfication)),
        mp.Process(target=onlineMatch2, args=(queue2, queue2_res,classfication)),
        mp.Process(target=onlineMatch3, args=(queue3, queue3_res,classfication)),
        mp.Process(target=onlineMatch4, args=(queue4, queue4_res,classfication))
    ]
    [process.start() for process in processes]
    time.sleep(10)
    # [process.join() for process in processes]
    return classfication,queue_in,queue_final_res

def imageScreening(img,metadata):
    '''
    初筛调用/返回结果
    输入：
    img：ndarray图片
    queue_in：输入队列
    queue_final_res：结果队列
    '''
    queue_in.put(img)
    while True:
        if queue_final_res.qsize()>0:
            print("has final res")
            final_return = queue_final_res.get()
            final_return["metadata"] = metadata
            # print(final_return)
            break
    return final_return


def simpleUse(img):
    input = img
    (winW, winH) = (224, 224)
    # (winW, winH) = (448, 448)
    resized = cv2.resize(input, (int(0.5 * input.shape[1]), int(0.5 * input.shape[0])), interpolation=cv2.INTER_AREA)
    # resized = input
    slide_image = []
    cnt = 0
    for (x, y, window) in sliding_window(resized, stepSize=168, windowSize=(winW, winH)):
        cnt = cnt + 1
        image_map_temp = {}
        # if the window does not meet our desired window size, ignore it
        if window.shape[0] != winH or window.shape[1] != winW:
            continue

        # THIS IS WHERE YOU WOULD PROCESS YOUR WINDOW, SUCH AS APPLYING A
        # MACHINE LEARNING CLASSIFIER TO CLASSIFY THE CONTENTS OF THE
        # WINDOW

        # since we do not have a classifier, we'll just draw the window
        img_use_temp = resized[y:y + winH, x:x + winW]
        image_map_temp["id"] = cnt
        image_map_temp["image"] = img_use_temp
        image_map_temp["x"] = x
        image_map_temp["y"] = y
        image_map_temp["winH"] = winH
        image_map_temp["winW"] = winW
        image_map_temp["imgTotal"] = resized

        img_use_temp = Image.fromarray(img_use_temp)
        class_name = classfication.landmark_detection(img_use_temp)



'''
if __name__ == '__main__':
    classfication,queue_in,queue_final_res = init()
    print("初始化完毕")
    path_root = "/sdc/workspace/micode"
    img_path_list = []
    for path in os.listdir(path_root):
        path_use = os.path.join(path_root,path)
        print("path_use "+str(path_use))
        img_path_list.append(path_use)
        start_time = time.time()

        res = main(path_use,queue_in,queue_final_res)
        print(res)
        end_time = time.time()
        print("cost time "+str(end_time-start_time))
        # print(len(img_path_list))
'''