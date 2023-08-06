'''
chushai_tensorrt.py
与外部交互主程序
initChushai函数：基于tensorrt初筛初始化
imageScreening函数：初筛在线调用
'''
import os
import shutil
import time
import sys
import numpy as np
from PIL import Image
sys.path.append("./app/ai/screening")
from skimage import measure
import cv2
import multiprocessing as mp
from pathlib import Path
import json

def sliding_window(image, stepSize, windowSize):
    # slide a window across the image
    for y in range(0, image.shape[0], stepSize):
        for x in range(0, image.shape[1], stepSize):
            # yield the current window
            yield (x, y, image[y:y + windowSize[1], x:x + windowSize[0]])

def mergeBox(boxes):

    '''
    合并文本框
    Args:
        boxes: 待合并文本框集合

    Returns: 合并后文本框集合

    '''
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

def remove_small_points(image, threshold_point,resized):

    '''
    去除不满足要求的连通域和框，并合并最终结果框
    Args:
        image: 输入缺陷情况热值图
        threshold_point: 连通域阈值
        resized: 原图(暂未用到）

    Returns:

    '''

    img = image
    img_label, num = measure.label(img, connectivity=1, return_num=True)  # 输出二值图像中所有的连通域
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

    # 生成标志位删除大框包小框情况时的小框
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
    # 合并框
    uuu_list_use_merge = mergeBox(uuu_list_use)
    return uuu_list_use_merge

def slideWindow(queue_in,queue_slide1,queue_slide2,queue_slide3,queue_slide4):

    '''
        对输入队列中的大图进行resize后并滑窗
        滑窗后的结果小图存到各个队列

    Args:
        queue_in: 输入大图队列
        queue_slide1: 滑窗后小图存放队列1
        queue_slide2: 滑窗后小图存放队列2
        queue_slide3: 滑窗后小图存放队列3
        queue_slide4: 滑窗后小图存放队列1

    Returns:

    '''

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

                # 滑窗窗口大小
                (winW, winH) = (224, 224)
                # (winW, winH) = (448, 448)

                # 全局resize
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
                    if window.shape[0] != winH or window.shape[1] != winW:
                        if window.shape[1] != winW and window.shape[0] != winH:
                            if x < resized.shape[1]:
                                x = resized.shape[1] - winW
                            if y < resized.shape[0]:
                                y = resized.shape[0] - winH
                        elif window.shape[1] != winW:
                            if x < resized.shape[1]:
                                x = resized.shape[1] - winW
                        elif window.shape[0] != winH:
                            if y < resized.shape[0]:
                                y = resized.shape[0] - winH
                        else:
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

    '''
    在线推理-进程1
    Args:
        queue1: 输入图像信息队列
        queue1_res: 输出带结果信息的队列，加入class字段
        classfication:分类模型class

    Returns:

    '''

    while True:
        if queue1.qsize()>0:
            list_temp = queue1.get()
            list_res = []
            for map_temp in list_temp:
                img_use_temp = Image.fromarray(map_temp["image"])
                class_name = classfication.landmark_detection(img_use_temp)
                map_temp["class"] = class_name
                list_res.append(map_temp)
            queue1_res.put(list_res)

def onlineMatch2(queue2,queue2_res,classfication):

    '''
    同onlineMatch1
    Args:
        queue2:
        queue2_res:
        classfication:

    Returns:

    '''

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
                map_temp["class"] = class_name
                list_res.append(map_temp)
            queue2_res.put(list_res)

def onlineMatch3(queue3,queue3_res,classfication):

    '''
    同onlineMatch1
    Args:
        queue3:
        queue3_res:
        classfication:

    Returns:

    '''

    while True:
        if queue3.qsize() > 0:
            list_temp = queue3.get()
            list_res = []
            for map_temp in list_temp:
                img_use_temp = Image.fromarray(map_temp["image"])
                class_name = classfication.landmark_detection(img_use_temp)
                map_temp["class"] = class_name
                list_res.append(map_temp)
            queue3_res.put(list_res)

def onlineMatch4(queue4,queue4_res,classfication):

    '''
    同onlineMatch1
    Args:
        queue4:
        queue4_res:
        classfication:

    Returns:

    '''

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
                map_temp["class"] = class_name
                list_res.append(map_temp)
            queue4_res.put(list_res)

def processRes(queue1_res,queue2_res,queue3_res,queue4_res,queue_final_res):

    '''
    处理多进程返回结果汇总到原图瑕疵位置
    Args:
        queue1_res: 推理进程1返回结果
        queue2_res: 推理进程2返回结果
        queue3_res: 推理进程3返回结果
        queue4_res: 推理进程4返回结果
        queue_final_res: 最终返回结果队列

    Returns:

    '''

    while True:
        if queue1_res.qsize()>0 and queue2_res.qsize()>0 and queue3_res.qsize()>0 and queue4_res.qsize()>0:
            start_process = time.time()
            list_temp1 = queue1_res.get()
            list_temp2 = queue2_res.get()
            list_temp3 = queue3_res.get()
            list_temp4 = queue4_res.get()
            print("img out queue")
            resized = list_temp1[0]["imgTotal"]
            uniform_data = np.zeros((int(resized.shape[0]), int(resized.shape[1])))

            # 生成结果矩阵
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
                res = {}
                str_list_liujun = []
                res_loc_list = []
                for uuu in merge_res:
                    xxx = {}
                    loc_temp = {}
                    res_img = resized[uuu[0]:uuu[2], uuu[1]:uuu[3]]
                    str_list_liujun.append([[uuu[1], uuu[0]],[uuu[3], uuu[2]]])

                    # 之前resize缩小的现在再放大回来
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

def initChushai():
    '''
    初筛初始化
    return
    classfication：分类器
    queue_in：输入队列
    queue_final_res：结果队列
    '''
    import tensorrt_use
    classfication = tensorrt_use.Classification()
    time.sleep(10)
    mp.set_start_method(method='spawn')
    queue1 = mp.Queue(maxsize=100)
    queue2 = mp.Queue(maxsize=100)
    queue3 = mp.Queue(maxsize=100)
    queue4 = mp.Queue(maxsize=100)
    queue1_res = mp.Queue(maxsize=100)
    queue2_res = mp.Queue(maxsize=100)
    queue3_res = mp.Queue(maxsize=100)
    queue4_res = mp.Queue(maxsize=100)
    queue_final_res = mp.Queue(maxsize=100)
    queue_in = mp.Queue(maxsize=1000)
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

def imageScreening(img,queue_in,queue_final_res,metadata):
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
    '''
    暂未用到，预留测试使用
    Args:
        img:

    Returns:

    '''
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
