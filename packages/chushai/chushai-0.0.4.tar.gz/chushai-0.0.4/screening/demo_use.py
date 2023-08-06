import chushai_tensorrt
import cv2
import os
import time

if __name__ == '__main__':
    # 初始化初筛进程
    classfication,queue_in,queue_final_res = chushai_tensorrt.initChushai()
    print("初始化完毕")

    '''
    假设需要做点别的事情
    '''
    # time.sleep(5)

    metadata = {}
    path_root = "/sdc/workspace/test/cloth1-1"
    img_path_list = []
    for path in os.listdir(path_root):
        path_use = os.path.join(path_root,path)
        print("path_use "+str(path_use))
        start_time = time.time()
        img_temp = cv2.imread(path_use)
        # img_temp = cv2.resize(img_temp, (int(0.5 * img_temp.shape[1]), int(0.5 * img_temp.shape[0])),
        #                      interpolation=cv2.INTER_AREA)
        # 调用初筛进程
        res = chushai_tensorrt.imageScreening(img_temp,queue_in,queue_final_res,metadata)
        if res["has_blemish"] == True:
            res_list = res["res"]
            for ress in res_list:
                loc = ress["loc"]
                x_min = loc["xmin"]
                x_max = loc["xmax"]
                y_min = loc["ymin"]
                y_max = loc["ymax"]
                cv2.rectangle(img_temp, (x_min, y_min), (x_max, y_max), (0, 255, 0,), 5)
        path_save = os.path.join("/sdc/workspace/img_res",path)
        if not os.path.exists("/sdc/workspace/img_res"):
            os.mkdir("/sdc/workspace/img_res")
        cv2.imwrite(path_save,img_temp)
        print(res)
        end_time = time.time()
        # 测试初筛过程返回时间
        print("cost time "+str(end_time-start_time))
