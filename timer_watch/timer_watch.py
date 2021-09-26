# Pigment.O is a Krita plugin and it is a Color Picker and Color Mixer.
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


# Import Krita
from krita import *
from PyQt5 import QtWidgets, QtCore, QtGui, uic
import os.path
import time
import datetime
import xml

# Set Window Title Name
DOCKER_NAME = 'Timer Watch'
# Alarm QMessageBox
message = "Time is Over"

# Docker Class
class TimerWatchDocker(DockWidget):
    """Control amount of work time spent working"""

    def __init__(self):
        super(TimerWatchDocker, self).__init__()

        # Window Title
        self.setWindowTitle(DOCKER_NAME)
        # Widget
        self.window = QWidget()
        self.layout = uic.loadUi(os.path.dirname(os.path.realpath(__file__)) + '/timer_watch.ui', self.window)
        self.setWidget(self.window)

        # Timer
        self.timer_hm = QtCore.QTimer(self)
        self.timer_hm.timeout.connect(self.HM_Display)
        self.timer_hm.timeout.connect(self.Info_Display)
        self.timer_hm.start(1000)

        self.timer_sw = QtCore.QTimer(self)
        self.timer_sw.timeout.connect(self.SW_Display)
        self.timer_sw.start(1000)

        # Inictialize Variables
        self.counter = 0
        self.switch = 0  # 0=Pause, 1=Play
        self.isreset = True

        # Start up Connections
        self.Connect()

    # Connect Funtions to Buttons
    def Connect(self):
        # Clean First Start
        self.SW_Reset()

        # Stopwatch buttons
        self.layout.pushButton_startpause.clicked.connect(self.SW_StartPause)
        self.layout.pushButton_reset.clicked.connect(self.SW_Reset)

        # Combobox Connection
        self.layout.menu_timer.currentTextChanged.connect(self.Menu_Timer)

        # Default Start UP Tab Display
        self.Menu_Timer()

    # Functions
    def Menu_Timer(self):
        self.menu_timer = self.layout.menu_timer.currentText()
        if self.menu_timer == "Clock":
            self.layout.tab_clock.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)
            self.layout.tab_stopwatch.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            self.layout.tab_info.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        if self.menu_timer == "Stopwatch":
            self.layout.tab_clock.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            self.layout.tab_stopwatch.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)
            self.layout.tab_info.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        if self.menu_timer == "Information":
            self.layout.tab_clock.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            self.layout.tab_stopwatch.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            self.layout.tab_info.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)

    def HM_Display(self):
        self.currentTime = QtCore.QTime.currentTime()
        self.layout.lcdNumber_1.setDigitCount(5)  # 5=hh:mm 8=hh:mm:ss
        self.strCurrentTime = self.currentTime.toString('hh:mm')  # 'hh:mm' 'hh:mm:ss'
        self.layout.lcdNumber_1.display(self.strCurrentTime)

    def SW_Display(self):
        self.counter += 1
        self.SW_Tick(self.counter)

    def SW_Tick(self, counter):
        self.layout.lcdNumber_2.setDigitCount(8)
        self.strProgressTime = time.strftime('%H:%M:%S', time.gmtime(self.counter))
        if not self.isreset:
            self.layout.lcdNumber_2.display(self.strProgressTime)
            self.layout.progressBar_1.setValue(self.counter)
            self.layout.progressBar_2.setValue(self.counter)
            if (self.layout.pushButton_alarm.isChecked() == True and self.counter >= self.maximum and self.maximum != 0):
                self.SW_Alarm()
        else:
            self.layout.lcdNumber_2.display('00:00:00')

    def SW_Time(self):
        # Convert Input Time
        hh = self.layout.timeEdit.time().hour()
        mm = self.layout.timeEdit.time().minute()
        ss = self.layout.timeEdit.time().second()
        conv = datetime.timedelta(hours=hh, minutes=mm)
        tsec = conv.total_seconds() + ss
        return tsec

    def SW_StartPause(self):
        # Select Operation
        if self.switch == 0:
            self.SW_Start()  # 0=Pause change to Start
        elif self.switch == 1:
            self.SW_Pause()  # 1=Start change to Pause
        else:
            self.SW_Reset()

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
        if self.maximum == 0:  # if User time == Zero
            self.layout.pushButton_startpause.setText("Pause:Zero")
            self.layout.timeEdit.setEnabled(False)
            self.layout.progressBar_1.setEnabled(False)
            self.layout.progressBar_2.setEnabled(False)
        else:  # if User time is NOT Zero
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

    def SW_Alarm(self):
        QMessageBox.information(QWidget(), i18n("Warnning"), i18n(message))
        self.SW_Pause()
        self.SW_Reset()

    def Info_Display(self):
        # Active Document
        ki = Krita.instance()
        ad = ki.activeDocument()
        if ad is None:  # No Document is Active
            self.layout.label_00_title.setText("Title")
            self.layout.label_05_initial_creator.setText("Initial Creator")
            self.layout.label_11_12_first_last_name.setText("Creator Name")
            self.layout.label_10_nick_name.setText("Nickname")
            self.layout.label_17_contact_type.setText("Contact Type")
            self.layout.label_09_creation_date.setText("Creation Date")
            self.layout.label_09_date_delta.setText("Date Delta")
            self.layout.label_07_editing_time.setText("Editing Time")
            self.layout.label_07_active_time.setText("Active Time")
            self.layout.label_06_editing_cycles.setText("Editing Cycles")
        else:  # Requesto to active Document
            self.Info_Document()

    def Info_Document(self):
        # Active Document
        ki = Krita.instance()
        ad = ki.activeDocument()
        text = ad.documentInfo()
        ET = xml.etree.ElementTree
        root = ET.fromstring(text)

        # Call XML items with Error Check
        try:    title              = root[0][0].text  # title
        except: title              = "Title"
        # try:    description        = root[0][1].text  # description
        # except: description        = "Description"
        # try:    subject            = root[0][2].text  # subject
        # except: subject            = "Subject"
        # try:    abstract           = root[0][3].text  # abstract
        # except: abstract           = "Abstract"
        # try:    keyword            = root[0][4].text  # keyword
        # except: keyword            = "Keyword"
        try:    initial_creator    = root[0][5].text  # initial-creator
        except: initial_creator    = "Initial Creator"
        try:    editing_cycles     = root[0][6].text  # editing-cycles
        except: editing_cycles     = "Editing Cycles"
        try:    editing_time       = root[0][7].text  # editing-time
        except: editing_time       = "Editing Time"
        try:    date               = root[0][8].text  # date
        except: date               = "Date"
        try:    creation_date      = root[0][9].text  # creation-date
        except: creation_date      = "Creation Date"
        # try:    language           = root[0][10].text  # language
        # except: language           = "Language"
        # try:    license            = root[0][11].text  # license
        # except: license            = "License"
        try:    nick_name          = root[1][0].text  # full-name
        except: nick_name          = "Nickname"
        try:    creator_first_name = root[1][1].text  # creator-first-name
        except: creator_first_name = "Fname"
        try:    creator_last_name  = root[1][2].text  # creator-last-name
        except: creator_last_name  = "Lname"
        # try:    initial            = root[1][3].text  # initial
        # except: initial            = "Initial"
        # try:    author_title       = root[1][4].text  # author-title
        # except: author_title       = "Author Title"
        # try:    position           = root[1][5].text  # position
        # except: position           = "Position"
        # try:    company            = root[1][6].text  # company
        # except: company            = "Company"
        try:    contact_type       = root[1][7].text  # contact type
        except: contact_type       = "Contact Type"

        # Date Edits
        creator_first_last_name = str(creator_first_name)+" "+str(creator_last_name)

        cd2 = list(creation_date)
        cd2[10] = ' '
        cd3 = "".join(cd2)

        date1 = list(creation_date)
        year1 = int("".join(date1[0:4]))
        month1 = int("".join(date1[5:7]))
        day1 = int("".join(date1[8:10]))
        hour1 = int("".join(date1[11:13]))
        minute1 = int("".join(date1[14:16]))
        second1 = int("".join(date1[17:19]))

        date2 = list(date)
        year2 = int("".join(date2[0:4]))
        month2 = int("".join(date2[5:7]))
        day2 = int("".join(date2[8:10]))
        hour2 = int("".join(date2[11:13]))
        minute2 = int("".join(date2[14:16]))
        second2 = int("".join(date2[17:19]))

        date_start = datetime.datetime(year1, month1, day1, hour1, minute1, second1)
        date_now = datetime.datetime(year2, month2, day2, hour2, minute2, second2)
        delta = (date_now - date_start).days

        yearHH = int(delta) // 365
        yearTT = int(delta) - (yearHH * 365)
        monthHH = yearTT // 30
        monthTT = yearTT - (monthHH * 30)
        dayHH = monthTT

        date_delta = str(yearHH)+"y "+str(monthHH)+"m "+str(dayHH)+"d since creation"

        if editing_time == "Editing Time" or editing_time is None:
            editing_time = "Unaware"
            active_time = "Unaware"
        else:
            yearNN = int(editing_time) // 31557600  #year
            yearRR = int(editing_time) - (yearNN * 31557600)
            monthNN = yearRR // 2629800  # month
            monthRR = yearRR - (monthNN * 2629800)
            dayNN = monthRR // 86400  # day
            dayRR = monthRR - (dayNN * 86400)
            hourNN = dayRR // 3600
            hourRR = dayRR - (hourNN * 3600)
            minuteNN = hourRR // 60
            minuteRR = hourRR - (minuteNN * 60)
            secondNN = minuteRR
            active_time = str(yearNN)+"y "+str(monthNN)+"m "+str(dayNN)+"d . "+str(hourNN)+"h "+str(minuteNN)+"m "+str(secondNN)+"s of active work"

        # Deplay XML items on the tab
        self.layout.label_00_title.setText(title)
        self.layout.label_05_initial_creator.setText(initial_creator)
        self.layout.label_11_12_first_last_name.setText(creator_first_last_name)
        self.layout.label_10_nick_name.setText(nick_name)
        self.layout.label_17_contact_type.setText(contact_type)
        self.layout.label_09_creation_date.setText(cd3)
        self.layout.label_09_date_delta.setText(date_delta)
        self.layout.label_07_editing_time.setText(editing_time)
        self.layout.label_07_active_time.setText(active_time)
        self.layout.label_06_editing_cycles.setText(editing_cycles)

    # Change the Canvas
    def canvasChanged(self, canvas):
        pass
