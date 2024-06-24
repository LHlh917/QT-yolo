from PySide6 import QtWidgets, QtCore, QtGui
import cv2, os, time
from threading import Thread

# 不然每次YOLO处理都会输出调试信息
os.environ['YOLO_VERBOSE'] = 'False'
from ultralytics import YOLO 

class MWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        # 设置界面
        self.setupUI()
        self.camBtn.clicked.connect(self.startCamera)
        self.stopBtn.clicked.connect(self.stop)
        self.videoBtn.clicked.connect(self.button_video_open)

        self.timer_camera = QtCore.QTimer()
        # 定时到了，回调 self.show_camera
        self.timer_camera.timeout.connect(self.show_camera)

        self.model = YOLO(r'C:\Users\LH\Desktop\yolo部署\yolov8s.pt')

        # 要处理的视频帧图片队列， 目前就放1帧图片
        self.frameToAnalyze = []

        # 启动处理视频帧独立线程
        Thread(target=self.frameAnalyzeThreadFunc,daemon=True).start()

        
    def setupUI(self):
        self.resize(1200, 800)

        # 中心窗口
        centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(centralWidget)

        # 中心窗口里面的主部件
        mainLayout = QtWidgets.QVBoxLayout(centralWidget)

        #界面的上半部分
        topLayout = QtWidgets.QHBoxLayout()
        self.label_ori_video = QtWidgets.QLabel(self)
        self.label_treated = QtWidgets.QLabel(self)
        self.label_ori_video.setMinimumSize(520,400)
        self.label_treated.setMinimumSize(520,400)
        self.label_ori_video.setStyleSheet('border:1px solid #1d649c;')
        self.label_treated.setStyleSheet('border:1px solid #1d649c;')

        topLayout.addWidget(self.label_ori_video)
        topLayout.addWidget(self.label_treated)

        mainLayout.addLayout(topLayout)

        # 界面下半部分： 输出框 和 按钮
        groupBox = QtWidgets.QGroupBox(self)
        bottomLayout = QtWidgets.QHBoxLayout(groupBox)
        self.textLog = QtWidgets.QTextBrowser()
        bottomLayout.addWidget(self.textLog)
        mainLayout.addWidget(groupBox)
        # mainLayout.addLayout(bottomLayout)
        btnLayout = QtWidgets.QVBoxLayout()
        self.videoBtn = QtWidgets.QPushButton('🎞视频文件')
        self.camBtn = QtWidgets.QPushButton('📷摄像头')
        self.stopBtn = QtWidgets.QPushButton('🛑停止')

        btnLayout.addWidget(self.videoBtn)
        btnLayout.addWidget(self.camBtn)
        btnLayout.addWidget(self.stopBtn)

        bottomLayout.addLayout(btnLayout)

                


    def startCamera(self):
        self.cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            print("1号摄像头不能打开")
            exit()
        if self.timer_camera.isActive() == False:
            self.timer_camera.start(50)

    def show_camera(self):
        ret, frame = self.cap.read()   # 从视频流中读取
        if not ret:
            return
        
        frame = cv2.resize(frame, (600, 400))
        # 视频色彩转换回RGB， OpenCV images as BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        qImage = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0],
                              QtGui.QImage.Format_RGB888)
        
        # 往显示视频的Label里 显示QImage
        self.label_ori_video.setPixmap(QtGui.QPixmap.fromImage(qImage))
        # 如果当前没有处理任务
        if not self.frameToAnalyze:
            self.frameToAnalyze.append(frame)

        # # 如果当前没有处理任务
        # if not self.frameToAnalyze:
        #     self.frameToANALYZE.APPEND(frame)
    def frameAnalyzeThreadFunc(self):
        while True:
            if not self.frameToAnalyze:
                time.sleep(0.01)
                continue
            frame = self.frameToAnalyze.pop(0)
            results = self.model(frame)[0]

            img = results.plot(line_width=1)

            qImage = QtGui.QImage(img.data, img.shape[1], img.shape[0],
                                    QtGui.QImage.Format_RGB888)
            
            self.label_treated.setPixmap(QtGui.QPixmap.fromImage(qImage))           # 往显示label里显示QImage


    def stop(self):
        self.timer_camera.stop()        # 关闭定时器
        self.cap.release()      # 释放视频流
        self.label_ori_video.clear()        # 清空视频显示区域
        self.label_treated.clear()          # 清空视频显示区域

    def button_video_open(self):
        video_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Video File')
        if video_name:
            self.load(video_name)

    def load(self, video_path):
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            QtWidgets.QMessageBox.warning(self, u"警告", u"无法打开视频文件", buttons=QtWidgets.QMessageBox.Ok,defaultButton=QtWidgets.QMessageBox.Ok)
            return
        
        # 启动定时器以显示视频帧
        self.timer_camera.start(30)

        # 在视频分析期间禁用其他按钮
        self.videoBtn.setDisabled(True)
        self.camBtn.setDisabled(True)
        self.stopBtn.setDisabled(False)  # 启用停止按钮


app = QtWidgets.QApplication()
window = MWindow()
window.show()
app.exec()