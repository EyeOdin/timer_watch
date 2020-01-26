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

        # Timer
        self.timer = QtCore.QTimer(self)
        # HH:MM
        self.timer.timeout.connect(self.Time_Display)
        self.timer.start(1000)
        # Stopwatch
        self.timer.timeout.connect(self.SW_Display)
        self.timer.setInterval(1)
        self.mscounter = 0
        self.isreset = True

        # Start up Connection
        self.Connect()

    # Connect Funtions to Buttons
    def Connect(self):
        # Stopwatch buttons
        self.layout.pushButton_start.clicked.connect( self.SW_Start )
        self.layout.pushButton_pause.clicked.connect( self.SW_Pause )
        self.layout.pushButton_reset.clicked.connect( self.SW_Reset )

    # Functions
    def Time_Display(self):
        self.currentTime = QtCore.QTime.currentTime()
        self.strCurrentTime = self.currentTime.toString('hh:mm')
        self.layout.lcdNumber_1.display(self.strCurrentTime)

    def SW_Display(self):
        self.mscounter += 1
        self.SW_Show()
        self.SW_Progress(self.mscounter)
    def SW_Show(self):
        text = str(datetime.timedelta(milliseconds=self.mscounter))[:-3]
        self.layout.lcdNumber_2.setDigitCount(12)
        if not self.isreset:
            self.layout.lcdNumber_2.display(text)
        else:
            self.layout.lcdNumber_2.display('0:00:00.000')
    def SW_Start(self):
        cond = self.SW_Time()
        self.layout.progressBar_1.setMaximum(cond)
        self.layout.progressBar_2.setMaximum(cond)
        if cond == 0: # progressBar needs a limit
            self.layout.pushButton_start.setText("00:00 Error")
            self.layout.progressBar_1.setDisabled(True)
            self.layout.progressBar_2.setDisabled(True)
        else:
            pass
        self.timer.start()
        self.isreset = False
        self.layout.pushButton_start.setDisabled(True)
        self.layout.pushButton_pause.setDisabled(False)
        self.layout.pushButton_reset.setDisabled(True)
        self.layout.timeEdit.setDisabled(True)
    def SW_Pause(self):
        self.timer.stop()
        self.isreset = False
        self.layout.pushButton_start.setDisabled(False)
        self.layout.pushButton_pause.setDisabled(True)
        self.layout.pushButton_reset.setDisabled(False)
        self.layout.timeEdit.setDisabled(True)
    def SW_Reset(self):
        self.timer.stop()
        self.mscounter = 0
        self.reset = 0
        self.isreset = True
        self.SW_Show()
        self.layout.pushButton_start.setDisabled(False)
        self.layout.pushButton_pause.setDisabled(True)
        self.layout.pushButton_reset.setDisabled(True)
        self.layout.timeEdit.setDisabled(False)
        self.layout.pushButton_start.setText("Start")
        self.layout.progressBar_1.setDisabled(False)
        self.layout.progressBar_2.setDisabled(False)
        self.layout.progressBar_1.setValue(0)
        self.layout.progressBar_2.setValue(0)
    def SW_Time(self): # Convert Input Time
        hh = self.layout.timeEdit.time().hour()
        mm = self.layout.timeEdit.time().minute()
        total = datetime.timedelta(hours=hh, minutes=mm)
        seconds = total.total_seconds()
        msec = seconds * 1000
        return msec
    def SW_Progress(self, mscounter):
        cond = self.SW_Time()
        if self.mscounter > cond:
            # self.SW_Pause()
            self.layout.progressBar_1.setValue(cond)
            self.layout.progressBar_2.setValue(cond)
            return
        self.layout.progressBar_1.setValue(self.mscounter)
        self.layout.progressBar_2.setValue(self.mscounter)

    # def Status(self, message):
    #     self.layout.label.setText(message)

    # Change the Canvas
    def canvasChanged(self, canvas):
        pass
