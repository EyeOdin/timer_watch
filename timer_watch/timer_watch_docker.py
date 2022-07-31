# Timer Watch is a Krita plugin and it is a Time Management Tool.
# Copyright (C) 2020  Ricardo Jeremias.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


#\\ Import Krita ###############################################################
# Python Modules
import os.path
import time
import datetime
import xml
# Krita Module
from krita import *
# PyQt5 Modules
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

#//
#\\ Global Variables ###########################################################
DOCKER_NAME = 'Timer Watch'
message = "Time is Over"
# time constants
horas = 24
minutos = 60
segundos = 60

#//

# Docker Class
class TimerWatch_Docker(DockWidget):
    """
    Time management
    """

    #\\ Initialize #############################################################
    def __init__(self):
        super(TimerWatch_Docker, self).__init__()

        # Construct
        self.Variables()
        self.User_Interface()
        self.Connections()
        self.Modules()
        self.Style()
        self.Timer()
        self.Settings()

    def Variables(self):
        # UI
        self.mode_index = 0
        # Clock
        self.clock_time = QTime.currentTime()
        # Stopwatch
        self.sw_state = False
        self.sw_counter = QTime(0,0)
        self.sw_alarm = False
        self.sw_limit = 0
    def User_Interface(self):
        # Window
        self.setWindowTitle(DOCKER_NAME)

        # Operating System
        self.OS = str(QSysInfo.kernelType()) # WINDOWS=winnt & LINUX=linux
        if self.OS == 'winnt': # Unlocks icons in Krita for Menu Mode
            QApplication.setAttribute(Qt.AA_DontShowIconsInMenus, False)

        # Path Name
        self.directory_plugin = str(os.path.dirname(os.path.realpath(__file__)))

        # Widget Docker
        self.window = QWidget()
        self.layout = uic.loadUi(self.directory_plugin + "/timer_watch_docker.ui", self.window)
        self.setWidget(self.window)

        # Dialog Copyright
        self.copyright = Dialog_CR(self)
        self.copyright.accept()
    def Connections(self):
        self.layout.start_pause.toggled.connect(self.SW_StartPause)
        self.layout.reset.clicked.connect(self.SW_Reset)
        self.layout.alarm.clicked.connect(self.SW_Alarm)
        self.layout.time_edit.timeChanged.connect(self.SW_TimeEdit)
        self.layout.settings.clicked.connect(self.Menu_Copyright)
    def Modules(self):
        # Multimedia
        self.player = QMediaPlayer()
        # UI
        self.mode_index = Menu_Mode(self.layout.lcd_number)
        self.mode_index.SIGNAL_MODE.connect(self.Mode_Index)
    def Style(self):
        # Icons
        self.layout.start_pause.setIcon(Krita.instance().icon('media-playback-start'))
        # self.layout.start_pause.setIcon(Krita.instance().icon('media-playback-stop'))
        self.layout.reset.setIcon(Krita.instance().icon('fileLayer'))
        self.layout.alarm.setIcon(Krita.instance().icon('warning'))
        self.layout.settings.setIcon(Krita.instance().icon('settings-button'))

        # StyleSheets
        self.layout.lcd_number.setStyleSheet("#lcd_number{background-color: rgba(0, 0, 0, 50);}")
        self.layout.progress_bar.setStyleSheet("#progress_bar{background-color: rgba(0, 0, 0, 50);}")
    def Timer(self):
        self.timer_pulse = QTimer(self)
        self.timer_pulse.timeout.connect(self.Pulse)
    def Settings(self):
        # Menu Mode
        mode_index = Krita.instance().readSetting("Timer Watch", "mode_index", "")
        if mode_index == "":
            Krita.instance().writeSetting("Timer Watch", "mode_index", str(0) )
            self.Mode_Index(0)
        else:
            self.Mode_Index(int(mode_index))
        # Time Limit
        ms = Krita.instance().readSetting("Timer Watch", "sw_limit", "")
        if ms == "":
            Krita.instance().writeSetting("Timer Watch", "sw_limit", str(0) )
        else:
            tempo = QTime(0,0,0).addSecs(float(ms))
            self.layout.time_edit.setTime(tempo)
        self.SW_TimeEdit()

    #//
    #\\ Menu Signals ###########################################################
    def Mode_Index(self, index):
        # Clock
        if index == 0:
            a = 0
            self.layout.lcd_number.setDigitCount(5)  # 5=hh:mm 8=hh:mm:ss
        # Stopwatch
        elif index == 1:
            a = 20
            self.layout.lcd_number.setDigitCount(8)
        # Layout Adjust
        self.layout.horizontal_buttons.setMaximumHeight(a)

        # update cycle
        if self.mode_index != index: # After a search with null results this ensure other modes update
            self.mode_index = index
            self.Number_Display()
            self.SW_ProgressBar()
        # Save
        Krita.instance().writeSetting("Timer Watch", "mode_index", str( self.mode_index ))
    def Menu_Copyright(self):
        self.copyright.show()

    #//
    #\\ Time ###################################################################
    def Pulse(self):
        # Timers
        self.clock_time = QTime.currentTime()
        self.SW_Pulse()
        # Display
        self.Number_Display()
        self.SW_ProgressBar()
    def Number_Display(self):
        if self.mode_index == 0:
            self.layout.lcd_number.display(str(self.clock_time.toString('hh:mm')))
        if self.mode_index == 1:
            self.layout.lcd_number.display(str(self.sw_counter.toString('hh:mm:ss')))

    #//
    #\\ Stopwatch ##############################################################
    def SW_Pulse(self):
        if self.sw_state == True:
            # Read
            h = self.sw_counter.hour()
            m = self.sw_counter.minute()
            s = self.sw_counter.second() + 1
            ms = self.sw_counter.msec()
            # loop restriction
            if s >= segundos:
                s = 0
                m += 1
            if m >= minutos:
                m = 0
                h += 1
            if h >= horas:
                h = 0
            # QTime
            self.sw_counter.setHMS(h,m,s,ms)

    def SW_ProgressBar(self):
        # UI
        maxi = self.layout
        counter = self.hms_to_time(self.sw_counter.hour(), self.sw_counter.minute(), self.sw_counter.second())
        self.layout.progress_bar.setValue(counter)
        # Alarm
        if (self.sw_alarm == True and counter == self.sw_limit and counter != 0 and self.sw_limit != 0):
            self.Alarm_Warnning()
    def SW_StartPause(self, boolean):
        # Variable
        self.sw_state = boolean
        # UI
        if boolean == True:
            self.layout.start_pause.setIcon(Krita.instance().icon('media-playback-stop'))
            self.layout.start_pause.setText("STOP")
        else:
            self.layout.start_pause.setIcon(Krita.instance().icon('media-playback-start'))
            self.layout.start_pause.setText("START")
        self.Widget_Enable(False)
        self.Number_Display()
    def SW_Reset(self):
        # Variables
        self.sw_state = False
        self.sw_counter.setHMS(0,0,0,0)
        # UI
        self.layout.start_pause.setIcon(Krita.instance().icon('media-playback-start'))
        self.layout.start_pause.setText("START")
        self.layout.start_pause.setChecked(False)
        self.Widget_Enable(True)
        self.Number_Display()
    def SW_Alarm(self, boolean):
        self.sw_alarm = boolean
    def SW_TimeEdit(self):
        # Variable
        qtime = self.layout.time_edit.time()
        self.sw_limit = self.hms_to_time(qtime.hour(), qtime.minute(), qtime.second())
        self.layout.progress_bar.setMaximum(self.sw_limit)
        # Save
        Krita.instance().writeSetting("Timer Watch", "sw_limit", str( self.sw_limit ))

    def Widget_Enable(self, boolean):
        self.layout.alarm.setEnabled(boolean)
        self.layout.time_edit.setEnabled(boolean)
        self.layout.settings.setEnabled(boolean)
    def hms_to_time(self, h, m, s):
        # hours
        hm = h * minutos
        hs = hm * segundos
        # minutes
        ms = m * segundos
        # Total
        time = hs + ms + s
        return time

    def Alarm_Warnning(self):
        # Play Sound
        path = self.directory_plugin + "/ALARM/pop.mp3"
        url = QUrl.fromLocalFile(path)
        content = QMediaContent(url)
        self.player.setMedia(content)
        self.player.play()
        # Show Written Message
        QMessageBox.information(QWidget(), i18n("Warnning"), i18n(message))

    #//
    #\\ Widget Events ##########################################################
    def showEvent(self, event):
        self.timer_pulse.start(1000)
    def enterEvent(self, event):
        pass
    def leaveEvent(self, event):
        self.layout.time_edit.clearFocus()
    def resizeEvent(self, event):
        pass
    def closeEvent(self, event):
        self.timer_pulse.stop()

    #//
    #\\ Change Canvas ##########################################################
    def canvasChanged(self, canvas):
        pass

    #//
    #\\ Notes ##################################################################
    """
    # Label Message
    self.layout.label.setText("message")

    # Pop Up Message
    QMessageBox.information(QWidget(), i18n("Warnning"), i18n("message"))

    # Log Viewer Message
    QtCore.qDebug("value = " + str(value))
    QtCore.qDebug("message")
    QtCore.qWarning("message")
    QtCore.qCritical("message")
    """
    #//


class Menu_Mode(QWidget):
    SIGNAL_MODE = QtCore.pyqtSignal(int)

    def __init__(self, parent):
        super(Menu_Mode, self).__init__(parent)
        # Variables
        self.mode_index = 0
    def sizeHint(self):
        return QtCore.QSize(5000,5000)

    def Set_Mode(self, mode_index):
        self.mode_index = mode_index

    def mousePressEvent(self, event):
        # Requires Active
        self.origin_x = event.x()
        self.origin_y = event.y()
        # Events
        if (event.buttons() == QtCore.Qt.LeftButton and event.modifiers() == QtCore.Qt.NoModifier):
            if self.mode_index == 0:
                self.Emit_Signal(1)
            elif self.mode_index == 1:
                self.Emit_Signal(0)
    def contextMenuEvent(self, event):
        if event.modifiers() == QtCore.Qt.NoModifier:
            cmenu = QMenu(self)
            # Actions
            cmenu_clock = cmenu.addAction("Clock")
            cmenu_stopwatch = cmenu.addAction("Stopwatch")
            action = cmenu.exec_(self.mapToGlobal(event.pos()))
            # Triggers
            if action == cmenu_clock:
                self.Emit_Signal(0)
            if action == cmenu_stopwatch:
                self.Emit_Signal(1)
    def wheelEvent(self, event):
        delta = event.angleDelta()
        if event.modifiers() == QtCore.Qt.NoModifier:
            delta_y = delta.y()
            value = 0
            if delta_y > 20:
                self.Emit_Signal(0)
            if delta_y < -20:
                self.Emit_Signal(1)
    def Emit_Signal(self, value):
        self.mode_index = value
        self.SIGNAL_MODE.emit(value)


class Dialog_CR(QDialog):
    def __init__(self, parent):
        super(Dialog_CR, self).__init__(parent)
        self.dir_name = str(os.path.dirname(os.path.realpath(__file__)))
        uic.loadUi(self.dir_name + "/timer_watch_copyright.ui", self)
