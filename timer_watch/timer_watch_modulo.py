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
# Krita Module
from krita import *
# PyQt5 Modules
from PyQt5 import QtWidgets, QtCore, QtGui, uic
#//


#\\ Settings ###################################################################
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

class Dialog_UI(QDialog):
    def __init__(self, parent):
        super(Dialog_UI, self).__init__(parent)
        self.dir_name = str(os.path.dirname(os.path.realpath(__file__)))
        uic.loadUi(self.dir_name + "/timer_watch_settings.ui", self)

#//
