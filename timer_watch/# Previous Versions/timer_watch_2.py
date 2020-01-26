# Import Krita
from krita import *
from PyQt5 import QtWidgets, QtCore, QtGui, uic
import os.path
import datetime

# Set Window Title Name
DOCKER_NAME = 'Timer Watch'

# Docker Class
class Timer_Watch_Docker(DockWidget):
    """
    Control amount of work time spent or see the current time
    """
    def __init__(self):
        super(Timer_Watch_Docker, self).__init__()

        # Window Title
        self.setWindowTitle(DOCKER_NAME)
        # Widget
        self.window = QTabWidget()
        self.layout = uic.loadUi(os.path.dirname(os.path.realpath(__file__)) + '/timer_watch.ui', self.window)
        self.setWidget(self.window)

        # LCD display numbers
        self.timer = QtCore.QTimer(self)
        # Timer
        self.timer.timeout.connect(self.Time_Display)
        self.timer.start(1000)
        # Stopwatch
        self.timer.timeout.connect(self.SW_Display)
        self.timer.setInterval(1)
        self.mscounter = 0
        self.isreset = True

        # Connect the Buttons
        self.Connect()

    # Connect Funtions to Buttons
    def Connect(self):
        # Stopwatch buttons
        self.layout.pushButton_start.clicked.connect(self.SW_Start)
        self.layout.pushButton_stop.clicked.connect(self.SW_Stop)
        self.layout.pushButton_pause.clicked.connect(self.SW_Pause)
        self.layout.pushButton_reset.clicked.connect(self.SW_Reset)
        self.SW_Show()

        # Progress Bar
        # self.progress.setValue(value)

    # Functions
    def Time_Display(self):
        self.currentTime = QtCore.QTime.currentTime()
        self.strCurrentTime = self.currentTime.toString('hh:mm')
        self.layout.lcdNumber_time.display(self.strCurrentTime)

    def SW_Show(self):
        text = str(datetime.timedelta(milliseconds=self.mscounter))[:-3]
        self.layout.lcdNumber_stopwatch.setDigitCount(11)
        if not self.isreset:  # if "isreset" is False
            self.layout.lcdNumber_stopwatch.display(text)
        else:
            self.layout.lcdNumber_stopwatch.display('0:00:00.000')
    def SW_Display(self):
        self.mscounter += 1
        self.SW_Show()
    def SW_Start(self):
        self.timer.start()
        self.isreset = False
        self.layout.pushButton_reset.setDisabled(True)
        self.layout.pushButton_start.setDisabled(True)
        self.layout.pushButton_stop.setDisabled(False)
        self.layout.pushButton_pause.setDisabled(False)
    def SW_Stop(self):
        self.timer.stop()
        self.mscounter = 0
        self.layout.pushButton_reset.setDisabled(False)
        self.layout.pushButton_start.setDisabled(False)
        self.layout.pushButton_stop.setDisabled(True)
        self.layout.pushButton_pause.setDisabled(True)
    def SW_Pause(self):
        self.timer.stop()
        self.layout.pushButton_reset.setDisabled(False)
        self.layout.pushButton_start.setDisabled(False)
        self.layout.pushButton_stop.setDisabled(True)
        self.layout.pushButton_pause.setDisabled(True)
    def SW_Reset(self):
        self.timer.stop()
        self.mscounter = 0
        self.isreset = True
        self.SW_Show()
        self.layout.pushButton_reset.setDisabled(True)
        self.layout.pushButton_start.setDisabled(False)
        self.layout.pushButton_stop.setDisabled(True)
        self.layout.pushButton_pause.setDisabled(True)

    # Change the Canvas
    def canvasChanged(self, canvas):
        pass

# viewLCDClock is a module that is imported
