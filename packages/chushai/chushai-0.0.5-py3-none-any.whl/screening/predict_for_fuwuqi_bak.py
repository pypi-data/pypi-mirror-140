'''
predict.py有几个注意点
1、无法进行批量预测，如果想要批量预测，可以利用os.listdir()遍历文件夹，利用Image.open打开图片文件进行预测。
2、如果想要将预测结果保存成txt，可以利用open打开txt文件，使用write方法写入txt，可以参考一下txt_annotation.py文件。
'''
import os
import time

import numpy as np
from PIL import Image
import cv2
# from classification import Classification
from tensorrt_use import Classification
# import seaborn as sns
# import matplotlib.pyplot as plt



classfication = Classification()

# sns.set()
def sliding_window(image, stepSize, windowSize):
    # slide a window across the image
    for y in range(0, image.shape[0], stepSize):
        for x in range(0, image.shape[1], stepSize):
            # yield the current window
            yield (x, y, image[y:y + windowSize[1], x:x + windowSize[0]])





from skimage import measure
import cv2

# def processContours(cnts):
#     '''
#     处理轮廓
#     :param cnts: 未处理的轮廓
#     :return: 处理后的轮廓
#     '''
#     # 找出面积最大的40个轮廓
#     # area_index = np.argsort([cv2.contourArea(c) for c in cnts])
#     cnts = np.array(cnts)
#     # loop over the contours
#     count = 1
#     flag = []
#     for i in range(len(cnts)):
#         flag.append(True)
#
#     for i in range(len(cnts)):
#         x1, y1, w1, h1 = cnts[i][1],cnts[i][0],cnts[i][3]-cnts[i][1],cnts[i][2]-cnts[i][0]
#         for j in range(len(cnts)):
#             if not flag[j]:
#                 continue
#             x2, y2, w2, h2 = cnts[j][1],cnts[j][0],cnts[j][3]-cnts[j][1],cnts[j][2]-cnts[j][0]
#             if x1 < x2 and y1 < y2 and x1 + w1 > x2 + w2 and y1 + h1 > y2 + h2:
#                 flag[j] = False
#
#     for i in range(len(flag)):
#         if flag[i]:
#             index = i
#             break
#
#     cnts = np.delete(cnts, index,axis=0)
#     flag = []
#     for i in range(len(cnts)):
#         flag.append(True)
#     for i in range(len(cnts)):
#         x1, y1, w1, h1 = cnts[i][1],cnts[i][0],cnts[i][3]-cnts[i][1],cnts[i][2]-cnts[i][0]
#         for j in range(len(cnts)):
#             if not flag[j]:
#                 continue
#             x2, y2, w2, h2 = cnts[j][1],cnts[j][0],cnts[j][3]-cnts[j][1],cnts[j][2]-cnts[j][0]
#             if x1 < x2 and y1 < y2 and x1 + w1 > x2 + w2 and y1 + h1 > y2 + h2:
#                 flag[j] = False
#     tmp = []
#     for i in range(len(flag)):
#         if not flag[i]:
#             tmp.append(int(i))
#
#     cnts = np.delete(cnts, tmp,axis=0)
#     return cnts
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
    # res = np.array(new_box)
    return new_box


##
##image:二值图像
##threshold_point:符合面积条件大小的阈值
def remove_small_points(image, threshold_point):
    img = image  # 输入的二值图像
    img_label, num = measure.label(img, connectivity=2, return_num=True)  # 输出二值图像中所有的连通域
    props = measure.regionprops(img_label)  # 输出连通域的属性，包括面积等

    resMatrix = np.zeros(img_label.shape)
    uuu_list = []
    for i in props:

        if i.area > threshold_point:
            uuu = i.bbox
            if 0 in uuu:
                continue
            if np.average(image[uuu[0]:uuu[2],uuu[1]:uuu[3]])<1:
                continue
            else:
                uuu_list.append(uuu)
            # cv2.rectangle(resized,(uuu[1],uuu[0]),(uuu[3],uuu[2]),(0,255,0,), 5)
            # print(1)
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
    # resized1 = resized.copy()
    # for uuu in uuu_list_use:
    #     # print(uuu[1])
    #     # print(uuu[0])
    #     # print(uuu[3])
    #     # print(uuu[2])
    #     cv2.rectangle(resized,(uuu[1],uuu[0]),(uuu[3],uuu[2]),(0,255,0,), 5)
    # cv2.namedWindow("uni", cv2.WINDOW_NORMAL)
    # cv2.imshow("uni", resized)
    # cv2.waitKey(0)

    uuu_list_use_merge = mergeBox(uuu_list_use)



    for uuu in uuu_list_use_merge:
        # print(uuu[1])
        # print(uuu[0])
        # print(uuu[3])
        # print(uuu[2])
        cv2.rectangle(resized,(uuu[1],uuu[0]),(uuu[3],uuu[2]),(0,255,0,), 5)
        # cv2.namedWindow("resized",cv2.WINDOW_NORMAL)
        # cv2.imshow("resized",resized)
        # cv2.waitKey(0)
    # print(1)
    # cv2.namedWindow("uni22", cv2.WINDOW_NORMAL)
    # cv2.imshow("uni22", resized1)
    # cv2.waitKey(0)
    for i in range(1, len(props)):
        if props[i].area > threshold_point:
            tmp = (img_label == i + 1).astype(np.uint8)
            resMatrix += tmp  # 组合所有符合条件的连通域
    resMatrix *= 255
    return resMatrix




while True:

    img_list = []
    imgsss = os.listdir("/sdc/workspace/img1")
    total_count = len(imgsss)
    for imgname in imgsss:
        # imgname = "Image_20211118163455908.bmp"
        img = os.path.join("/sdc/workspace/img1", imgname)

        print(img)
        start = time.time()
        try:
            image = Image.open(img)
        except:
            print('Open Error! Try again!')
            continue

        else:

            # image = Image.fromarray(image)
            (winW, winH) = (224, 224)

            # resized2 = np.array(image)
            resized = cv2.imread(img)

            # cv2.imshow("resized",resized)
            # cv2.waitKey(0)
            uniform_data = np.zeros((resized.shape[0], resized.shape[1]))

            for (x, y, window) in sliding_window(resized, stepSize=112, windowSize=(winW, winH)):
                # if the window does not meet our desired window size, ignore it
                if window.shape[0] != winH or window.shape[1] != winW:
                    continue

                # THIS IS WHERE YOU WOULD PROCESS YOUR WINDOW, SUCH AS APPLYING A
                # MACHINE LEARNING CLASSIFIER TO CLASSIFY THE CONTENTS OF THE
                # WINDOW

                # since we do not have a classifier, we'll just draw the window
                clone = resized.copy()
                img_use_temp = resized[y:y + winH,x:x+winW]

                # cv2.rectangle(clone, (x, y), (x + winW, y + winH), (0, 255, 0), 2)
                # cv2.imshow("Window", img_use_temp)
                # cv2.waitKey(0)
                # img_use_temp = cds_retinex.cds_main(img_use_temp)
                img_use_temp = Image.fromarray(img_use_temp)

                class_name = classfication.landmark_detection(img_use_temp)
                if class_name == "defect":
                    uniform_data[y:y + winH, x:x + winW] = uniform_data[y:y + winH, x:x + winW] + 1
                # print(class_name)
            end = time.time()
            print("cost " + str(end - start))
            try:
                res = remove_small_points(uniform_data, 1)
                # cv2.Canny(uniform_data)

                # cv2.imwrite("./dataset1227/aaa"+str(imgname).replace("bmp","jpg"),resized)
                end = time.time()
                print("cost "+str(end-start))
                # ax = sns.heatmap(uniform_data)
                # print(imgname)
                # fig = plt.figure()
                # fig = ax.get_figure()
                # # fig.savefig("output.png")
                # # plt.show()
                # fig.savefig("./dataset1227/"+str(imgname).replace("bmp","jpg"))
            except Exception as e:
                print(e)
                print(imgname)
            # cv2.imshow("uniform_data",uniform_data)
            # cv2.waitKey(0)


    break


