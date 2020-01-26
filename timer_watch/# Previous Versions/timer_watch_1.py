# Import Krita
from krita import *
from PyQt5 import QtWidgets, QtCore, QtGui, uic
import os.path

# Set Window Title Name
DOCKER_NAME = 'Timer Watch'

# Docker Class
class Timer_Watch_Docker(DockWidget):
    """
    Control amount of work time spent or see the hours
    """
    def __init__(self):
        super(Timer_Watch_Docker, self).__init__()

        # Window Title
        self.setWindowTitle(DOCKER_NAME)
        # Widget
        self.window = QTabWidget()
        self.layout = uic.loadUi(os.path.dirname(os.path.realpath(__file__)) + '/timer_watch.ui', self.window)
        self.setWidget(self.window)
        self.Connect()

    # Connect Funtions to Buttons
    def Connect(self):
        # Clock
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.Time_LCD)
        self.timer.start(1000)
    # Functions
    def Time_LCD(self):
        self.currentTime = QtCore.QTime.currentTime()
        self.strCurrentTime = self.currentTime.toString('hh:mm')
        self.layout.lcdNumber_time.display(self.strCurrentTime)

    # Change the Canvas
    def canvasChanged(self, canvas):
        pass

# viewLCDClock is a module that is imported
