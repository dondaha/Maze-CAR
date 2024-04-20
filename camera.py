import cv2
import json
import numpy as np
import cv2.aruco as aruco
from pathlib import Path
from map import Maze
import threading

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]




def rasterize_image(image, num_rows, num_cols, threshold_low, threshold_high):
    # 获取图像大小
    rows, cols = image.shape[:2]
    
    # 计算栅格的大小
    grid_height = rows // num_rows
    grid_width = cols // num_cols
    
    # 创建一个空白的二维数组，用于存储栅格化后的结果
    rasterized_image = np.zeros((num_rows, num_cols), dtype=np.uint8)
    
    # 遍历每个栅格
    for i in range(num_rows):
        for j in range(num_cols):
            # 计算栅格的范围
            y_min = i * grid_height
            y_max = (i + 1) * grid_height
            x_min = j * grid_width
            x_max = (j + 1) * grid_width
            
            # 获取当前栅格的区域
            grid_region = image[y_min:y_max, x_min:x_max]
            
            # 统计当前栅格内的黑色像素点数目
            black_pixel_count = np.sum(grid_region == 0)
            # print("栅格(", i, ",", j, ")中的黑色像素点数目:", black_pixel_count)
            
            # 根据黑色像素点数目确定标记值
            if black_pixel_count < threshold_high:
                rasterized_image[i, j] = 0 # 有车和空白块都是0
            else:
                rasterized_image[i, j] = 1
    
    return rasterized_image


def calc_pose(corners):
    x, y = corners.mean(axis=0)
    head = (corners[0] + corners[1]) / 2
    rear = (corners[2] + corners[3]) / 2
    theta = np.arctan2(head[1] - rear[1], head[0] - rear[0])
    sz = np.linalg.norm(head - rear)
    return x, y, theta, sz

class Camera:
    def __init__(self, cam:int = 1, imagesize:tuple = (900, 600)) -> None:
        # 各个窗口显示情况
        self.show_frame = True # 赛道图像
        self.show_raw = False # 畸变校正之后的图像
        self.exit_flag = False
        self.lock = threading.Lock()
        # 确定栅格大小
        self.num_rows = 6  # 纵向栅格数
        self.num_cols = 9  # 横向栅格数
        self.maze = Maze(9, 6)  # 创建迷宫对象
        # 从param.json加载畸变校正参数
        with open(ROOT / 'param.json', 'r') as file:
            self.param = json.load(file)
        for key in self.param.keys():
            self.param[key] = np.array(self.param[key])
        # 计算摄像头参数
        self.imagesize = imagesize
        p = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(self.param['k'], self.param['d'], (1920, 1080), None)
        self.map_x, self.map_y = cv2.fisheye.initUndistortRectifyMap(self.param['k'], self.param['d'], None, p, (1920, 1080), cv2.CV_32F)

        self.cap = cv2.VideoCapture(cam)  # 打开摄像头
        # 设置摄像头每帧图像的宽、高
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        self.matrix = cv2.getPerspectiveTransform(
            np.array([[534, 239], [172, 893], [1844, 899], [1489, 222]], dtype=np.float32),   # 透视变换前的四个点，左上\左下\右下\右上
            np.array([[0, 0], [0, imagesize[1]], [imagesize[0], imagesize[1]], [imagesize[0], 0]], dtype=np.float32)
        )

        ARUCO_PARAMETERS = aruco.DetectorParameters()  # ArUco参数
        ARUCO_DICT = aruco.getPredefinedDictionary(aruco.DICT_4X4_250)  # ArUco字典
        self.detector = aruco.ArucoDetector(ARUCO_DICT, ARUCO_PARAMETERS)  # ArUco检测器

        self.mouse_x, self.mouse_y = 0, 0
    def get_maze(self) -> Maze:
        return self.maze
    def update(self) -> None:
        while True:
            with self.lock:
                if self.exit_flag:
                    break
                ret, raw = self.cap.read()
            if not ret:
                break
            raw = cv2.remap(raw, self.map_x, self.map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT) # 畸变校正
            frame = cv2.warpPerspective(raw, self.matrix, self.imagesize) # 透视变换
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # 转灰度图
            blurred = cv2.GaussianBlur(gray, (5, 5), 0) # 高斯模糊
            binary_image = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 12) # 自适应二值化
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))  # 定义一个3x3的矩形腐蚀核
            eroded_image = cv2.erode(binary_image, kernel, iterations=2) # 腐蚀图像
            cv2.imshow('Eroded Image', eroded_image) # 显示腐蚀后的图像
            # 定义两个阈值
            threshold_low = 2400
            threshold_high = 9000
            # 进行连通域提取
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(eroded_image, connectivity=8, ltype=cv2.CV_32S)
            # 找到面积最大的连通域的索引        
            max_area_index = np.argmax(stats[1:, cv2.CC_STAT_AREA]) + 1  # 从1开始索引，因为0是背景
            result = np.zeros_like(labels, dtype=np.uint8) # 创建一个与原始图像大小相同的空白图像，并将其填充为黑色
            result[labels == max_area_index] = 255 # 将面积最大的连通域在空白图像上填充为白色
            # 显示结果
            cv2.imshow('Separated Connected Components', result)
            rasterized_result = rasterize_image(result, self.num_rows, self.num_cols,threshold_low,threshold_high)
            # 显示栅格化后的结果
            print("Rasterized Result:")
            # print(rasterized_result)
            # 迷宫更新
            self.maze.set_point_from_np_array(rasterized_result)
            # print(self.maze)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):  # 按下q键退出
                break
        # 释放摄像头并关闭窗口
        self.cap.release()
        cv2.destroyAllWindows()
            

    def start(self) -> None:
        with self.lock:
            if self.exit_flag:
                return
            self.exit_flag = False
        # start the update thread
        t = threading.Thread(target=self.update)
        t.start()
    def stop(self) -> None:
        with self.lock:
            self.exit_flag = True
        print("Safely exited")


if __name__ == "__main__":
    camera = Camera()
    camera.start()