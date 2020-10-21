import cv2
import numpy as np
from skimage.measure import profile_line
from glob import glob
import os
import json


def list_file_tree(path, file_type="tif"):
    image_list = list()
    dir_list = os.listdir(path)
    if os.path.isdir(path):
        image_list += glob(os.path.join(path, "*" + file_type))
    for dir_name in dir_list:
        sub_path = os.path.join(path, dir_name)
        if os.path.isdir(sub_path):
            image_list += list_file_tree(sub_path, file_type)
    return image_list


# 创建回调函数
def OnMouse(event, x, y, flags, param):
    if mode == 0 and event == cv2.EVENT_LBUTTONDOWN:
        point_dict["start"] = (x, y)
        cv2.circle(img, (x, y), 1, 255, 1)
        print("起始点", point_dict["start"], "按键盘的'enter'确认")
    if mode == 1 and event == cv2.EVENT_LBUTTONDOWN:
        point_dict["end"] = (x, y)
        cv2.circle(img, (x, y), 1, 255, 1)
        print("结束点", point_dict["end"], "按键盘的'enter'确认")


def instenty_line(img, p1, p2):
    data = profile_line(img, (p1[1], p1[0]), (p2[1], p2[0]), order=3)
    data = [int(x) for x in data]
    return data


def merge_json():
    json_path = "4x/json_test_4x"
    ori_path = "4x/SRGAN_ORI_4x_new_test_project"
    vanilla_path = "4x/SRGAN_vanilla_4x_new_test_project"
    json_save_path = "4x/json_new"
    files = list_file_tree(json_path, "json")
    for file in files:
        filename = os.path.split(file)[1]
        img_ori = cv2.imread(os.path.join(ori_path, filename[:-5] + ".png"), cv2.IMREAD_GRAYSCALE)
        img_vanilla = cv2.imread(os.path.join(vanilla_path, filename[:-5] + ".png"), cv2.IMREAD_GRAYSCALE)
        data = json.load(open(file))
        for i in range(len(data)):
            point_dict = data[i][2]
            data[i][1]["ori"] = instenty_line(img_ori, point_dict["start"], point_dict["end"])
            data[i][1]["vanilla"] = instenty_line(img_vanilla, point_dict["start"], point_dict["end"])
        json.dump(data, open(os.path.join(json_save_path, filename), "w"))


# def json2csv():
#     json_path = "3x/test/json_test_3x_new"
#     save_path = "3x/test/csv_test_3x_new"
#     os.makedirs(save_path, exist_ok=True)
#     files = list_file_tree(json_path, "json")
#     xyz_split = [0, 150, 300]
#     result = {}
#     for file in files:
#         data = json.load(open(file))
#         for line in data:
#             filename = line[0]
#             for key, ll in line[1].items():
#                 if key not in result.keys():
#                     result[key] = []


if __name__ == '__main__':
    # merge_json()
    low_path = "4x/4X_project"
    high_path = "4x/20X_project"
    sr_path = "4x/SRGAN_L1-4x-new_test_project"
    mse_path = "4x/SRGAN_MSE-4x-new_test_project"
    json_save_path = "4x/json_test_4x"
    files = list_file_tree(sr_path, "png")
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', OnMouse)
    for file in files:
        points_list = []
        mode = 0
        point_dict = {"start": (0, 0),
                      "end": (0, 0)}
        filename = os.path.split(file)[1]
        img_low = cv2.imread(os.path.join(low_path, filename), cv2.IMREAD_GRAYSCALE)
        img_high = cv2.imread(os.path.join(high_path, filename), cv2.IMREAD_GRAYSCALE)
        img_sr = cv2.imread(os.path.join(sr_path, filename), cv2.IMREAD_GRAYSCALE)
        img_mse = cv2.imread(os.path.join(mse_path, filename), cv2.IMREAD_GRAYSCALE)
        img = img_mse.copy()
        while True:
            cv2.imshow('image', img)
            k = cv2.waitKey(0)
            print(k)
            if k == ord('\r'):
                mode += 1
                mode = mode % 2
                img = img_mse.copy()
                cv2.line(img, point_dict["start"], point_dict["end"], color=255, thickness=1)
            elif k == ord(' '):
                data_dict = {"low": instenty_line(img_low, point_dict["start"], point_dict["end"]),
                             "high": instenty_line(img_high, point_dict["start"], point_dict["end"]),
                             "sr": instenty_line(img_sr, point_dict["start"], point_dict["end"]),
                             "mse": instenty_line(img_mse, point_dict["start"], point_dict["end"])}
                points_list.append([filename, data_dict.copy(), point_dict.copy()])
                print(data_dict, point_dict)
            elif k == ord('\x1b'):
                if len(points_list) > 0:
                    json.dump(points_list, open(os.path.join(json_save_path, filename[:-4] + ".json"), "w"))
                    print(points_list)
                break
            elif k == ord('r'):
                points_list = []
                mode = 0
                point_dict = {"start": (0, 0),
                              "end": (0, 0)}
                img = img_mse.copy()
    cv2.destroyAllWindows()
