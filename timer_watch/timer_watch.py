# Import Krita
from krita import *
from PyQt5 import QtWidgets, QtCore, QtGui, uic
import os.path
import time
import datetime

# Set Window Title Name
DOCKER_NAME = 'Timer Watch'

# Docker Class
class TimerWatchDocker(DockWidget):
    """
    Control amount of work time spent or see the current time
    """
    def __init__(self):
        super(TimerWatchDocker, self).__init__()

        # Window Title
        self.setWindowTitle(DOCKER_NAME)
        # Widget
        self.window = QTabWidget()
        self.layout = uic.loadUi(os.path.dirname(os.path.realpath(__file__)) + '/timer_watch.ui', self.window)
        self.setWidget(self.window)

        # Timer
        self.timer_hm = QtCore.QTimer(self)
        self.timer_hm.timeout.connect(self.HM_Display)
        self.timer_hm.start(1000)

        self.timer_sw = QtCore.QTimer(self)
        self.timer_sw.timeout.connect(self.SW_Display)
        self.timer_sw.start(1000)

        # Inictialize Variables
        self.counter = 0
        self.switch = 0 # 0=Pause, 1=Play
        self.isreset = True

        # Start up Connection
        self.Connect()

    # Connect Funtions to Buttons
    def Connect(self):
        # Clean First Start
        self.SW_Reset()

        # Stopwatch buttons
        self.layout.pushButton_startpause.clicked.connect( self.SW_StartPause )
        self.layout.pushButton_reset.clicked.connect( self.SW_Reset )

    # Functions
    def HM_Display(self):
        self.currentTime = QtCore.QTime.currentTime()
        self.layout.lcdNumber_1.setDigitCount(5) # 5=hh:mm 8=hh:mm:ss
        self.strCurrentTime = self.currentTime.toString('hh:mm') # 'hh:mm' 'hh:mm:ss'
        self.layout.lcdNumber_1.display(self.strCurrentTime)

    def SW_Display(self):
        self.counter += 1
        self.SW_Tick(self.counter)

    def SW_Tick(self, counter):
        self.layout.lcdNumber_2.setDigitCount(8)
        self.strProgressTime = time.strftime('%H:%M:%S', time.gmtime(self.counter))
        # self.layout.lcdNumber_2.display(self.strProgressTime)
        if not self.isreset:
            self.layout.lcdNumber_2.display(self.strProgressTime)
            self.layout.progressBar_1.setValue(self.counter)
            self.layout.progressBar_2.setValue(self.counter)
        else:
            self.layout.lcdNumber_2.display('00:00:00')

    def SW_Time(self):
        # Convert Input Time
        hh = self.layout.timeEdit.time().hour()
        mm = self.layout.timeEdit.time().minute()
        ss = self.layout.timeEdit.time().second()
        conv = datetime.timedelta(hours=hh, minutes=mm)
        tsec = conv.total_seconds() + ss
        msec = tsec * 1000
        return tsec

    def SW_StartPause(self):
        # Select Operation
        if   self.switch == 0 : self.SW_Start() # 0=Pause change to Start
        elif self.switch == 1 : self.SW_Pause() # 1=Start change to Pause
        else : self.SW_Reset()

    def SW_Start(self):
        # Start Ready
        self.maximum = self.SW_Time()
        self.layout.progressBar_1.setMaximum(self.maximum)
        self.layout.progressBar_2.setMaximum(self.maximum)
        # Commands
        self.timer_sw.start()
        # UI
        self.switch = 1
        self.isreset = False
        if self.maximum == 0 : # if User time == Zero
            self.layout.pushButton_startpause.setText("Pause:Zero")
            self.layout.timeEdit.setEnabled(False)
            self.layout.progressBar_1.setEnabled(False)
            self.layout.progressBar_2.setEnabled(False)
        else : # if User time is NOT Zero
            self.layout.pushButton_startpause.setText("Pause")
            self.layout.timeEdit.setEnabled(False)
            self.layout.progressBar_1.setEnabled(True)
            self.layout.progressBar_2.setEnabled(True)

    def SW_Pause(self):
        # Commands
        self.timer_sw.stop()
        # UI
        self.switch = 0
        self.isreset = False
        self.layout.pushButton_startpause.setText("Start")
        self.layout.timeEdit.setEnabled(False)
        self.layout.progressBar_1.setEnabled(True)
        self.layout.progressBar_2.setEnabled(True)

    def SW_Reset(self):
        # Variables
        self.counter = 0
        # Commands
        self.timer_sw.stop()
        self.SW_Tick(self.counter)
        # UI
        self.switch = 0
        self.isreset = True
        self.layout.pushButton_startpause.setText("Start")
        self.layout.timeEdit.setEnabled(True)
        self.layout.progressBar_1.setEnabled(True)
        self.layout.progressBar_2.setEnabled(True)
        self.layout.progressBar_1.setValue(0)
        self.layout.progressBar_2.setValue(0)

    # def Status(self, message):
    #     message = str(message)
    #     self.layout.label.setText(message)

    # Change the Canvas
    def canvasChanged(self, canvas):
        pass
