from PySide6 import QtWidgets, QtCore, QtGui
# from PySide6.QtWidgets import QMainWindow
import cv2, os, time
from threading import Thread

class MWindow(QtWidgets,QMainWindow):
    def __init__(self):
        super().__init__()
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
        mainLayout.addLayout(bottomLayout)
        btnLayout = QtWidgets.QVBoxLayout()
        self.videoBtn = QtWidgets.QPushButton('🎞视频文件')
        self.camBtn = QtWidgets.QPushButton('📷摄像头')
        self.stopBtn = QtWidgets.QPushButton('🛑停止')

        btnLayout.addWidget(self.videoBtn)
        btnLayout.addWidget(self.camBtn)
        btnLayout.addWidget(self.stopBtn)

        bottomLayout.addLayout(btnLayout)

        self.camBtn.clicked.connect(self.startCamera)


        self.timer_camera = QtCore.QTimer()
        # 定时到了，回调 self.show_camera
        self.timer_camera.timeout.connect(self.show_camera)

        

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
        
        frame = cv2.resize(frame, (520, 400))
        # 视频色彩转换回RGB， OpenCV images as BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGR)
        qImage = QtGui.QImage(frame.data, frame.shape[1], frame.shape[0],
                              QtGui.QImage.Format_RGB888)
        
        # 往显示视频的Label里 显示QImage
        self.label_ori_video.setPixmap(QtGui.QPixmap.fromImage(qImage))

        # 如果当前没有处理任务
        if not self.frameToAnalyze:
            self.frameToANALYZE.APPEND(frame)




app = QtWidgets.QApplication()
window = MWindow()
window.show()
app.exec()