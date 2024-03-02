# Timer Watch is a Krita plugin and it is a Time Management Tool.
# Copyright ( C ) 2020  Ricardo Jeremias.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# ( at your option ) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


#region Import Krita

# Python Modules
import os.path
import time
import datetime
import xml
import webbrowser
# Krita Module
from krita import *
# PyQt5 Modules
from PyQt5 import QtWidgets, QtCore, QtGui, uic
from PyQt5.QtCore import QUrl

#endregion
#region Global Variables

# Plugin
DOCKER_NAME = 'Timer Watch'
timer_watch_version = "2024_03_02"
message = "Time is Over"

# time constants
horas = 24
minutos = 60
segundos = 60

# Photoshoot
photoshoot = False

#endregion


class TimerWatch_Docker( DockWidget ):

    #region Initialize

    def __init__( self ):
        super( TimerWatch_Docker, self ).__init__()

        # Construct
        self.User_Interface()
        self.Variables()
        self.Connections()
        self.Style()
        self.Timer()
        self.Settings()
        self.Plugin_Load()

    def User_Interface( self ):
        # Window
        self.setWindowTitle( DOCKER_NAME )

        # Operating System
        self.OS = str( QSysInfo.kernelType() ) # WINDOWS=winnt & LINUX=linux
        if self.OS == 'winnt': # Unlocks icons in Krita for Menu Mode
            QApplication.setAttribute( Qt.AA_DontShowIconsInMenus, False )

        # Path Name
        self.directory_plugin = str( os.path.dirname( os.path.realpath( __file__ ) ) )

        # Widget Docker
        self.layout = uic.loadUi( os.path.join( self.directory_plugin, "timer_watch_docker.ui" ), QWidget( self ) )
        self.setWidget( self.layout )

        # Settings
        self.dialog = uic.loadUi( os.path.join( self.directory_plugin, "timer_watch_settings.ui" ), QDialog( self ) )
        self.dialog.setWindowTitle( "Timer Watch : Settings" )
    def Variables( self ):
        # UI
        self.mode_index = 0
        # Clock
        self.clock_time = QTime.currentTime()
        # Stopwatch
        self.sw_state = False
        self.sw_counter = QTime( 0,0 )
        self.sw_alarm = False
        self.sw_limit = 0
        # Alarm
        self.alarm_message = message
    def Connections( self ):
        # Layout
        self.layout.start_pause.toggled.connect( self.SW_StartPause )
        self.layout.reset.clicked.connect( self.SW_Reset )
        self.layout.alarm.clicked.connect( self.SW_Alarm )
        self.layout.time_limit.timeChanged.connect( self.SW_TimeEdit )
        self.layout.settings.clicked.connect( self.Menu_Settings )

        # Dialog
        self.dialog.menu_alarm_message.textChanged.connect( self.Menu_Message )
        self.dialog.manual.clicked.connect( self.Menu_Manual )
        self.dialog.copyright.clicked.connect( self.Menu_Copyright )

        # Event Filter
        self.layout.mode.installEventFilter( self )
        self.layout.lcd_number.installEventFilter( self )
    def Style( self ):
        # Icons
        self.layout.start_pause.setIcon( Krita.instance().icon( 'media-playback-start' ) ) # media-playback-stop
        self.layout.reset.setIcon( Krita.instance().icon( 'fileLayer' ) )
        self.layout.alarm.setIcon( Krita.instance().icon( 'paintbrush' ) )
        self.layout.settings.setIcon( Krita.instance().icon( 'settings-button' ) )

        # ToolTips
        self.layout.start_pause.setToolTip( "Start" )
        self.layout.reset.setToolTip( "Reset" )
        self.layout.alarm.setToolTip( "Alarm" )
        self.layout.time_limit.setToolTip( "Time Limit" )
        self.layout.settings.setToolTip( "Settings" )

        # StyleSheets
        self.layout.lcd_number.setStyleSheet( "#lcd_number{background-color: rgba( 0, 0, 0, 50 );}" )
        self.layout.progress_bar.setStyleSheet( "#progress_bar{background-color: rgba( 0, 0, 0, 50 );}" )
        self.dialog.settings.setStyleSheet( "#settings{background-color: rgba( 0, 0, 0, 20 );}" )
    def Timer( self ):
        self.timer_pulse = QTimer( self )
        self.timer_pulse.timeout.connect( self.Pulse )
    def Settings( self ):
        self.mode_index = self.Set_Read( "INT", "mode_index", self.mode_index )
        self.sw_limit = self.Set_Read( "INT", "sw_limit", self.sw_limit )
        self.alarm_message = self.Set_Read( "STR", "alarm_message", self.alarm_message )
    def Plugin_Load( self ):
        try:
            self.Loader()
        except Exception as e:
            self.Message_Warnning( "ERROR", f"Load\n{ e }" )
            self.Variables()
            self.Loader()

    def Loader( self ):
        # Menu Mode
        self.Mode_Index( self.mode_index )

        # Time Limit
        tempo = QTime( 0,0,0 ).addSecs( self.sw_limit )
        self.layout.time_limit.setTime( tempo )
        self.SW_TimeEdit()

        # Alarm Message
        self.dialog.menu_alarm_message.setText( self.alarm_message )
    def Set_Read( self, mode, entry, default ):
        setting = Krita.instance().readSetting( "Timer Watch", entry, "" )
        if setting == "":
            read = default
        else:
            try:
                if mode == "EVAL":
                    read = eval( setting )
                elif mode == "STR":
                    read = str( setting )
                elif mode == "INT":
                    read = int( setting )
            except:
                read = default
        Krita.instance().writeSetting( "Timer Watch", entry, str( read ) )
        return read

    #endregion
    #region Menu Signals

    def Mode_Index( self, index ):
        # Clock
        if index == 0:
            self.layout.lcd_number.setDigitCount( 5 )  # 5=hh:mm 8=hh:mm:ss
        # Stopwatch
        elif index == 1:
            self.layout.lcd_number.setDigitCount( 8 )

        # update cycle
        if self.mode_index != index: # After a search with null results this ensure other modes update
            self.mode_index = index
            self.Number_Display()
            self.SW_ProgressBar()
        # Save
        Krita.instance().writeSetting( "Timer Watch", "mode_index", str( self.mode_index ) )

    def Menu_Message( self, string ):
        if string == "":
            self.alarm_message = message
        else:
            self.alarm_message = string
        # Save
        Krita.instance().writeSetting( "Timer Watch", "alarm_message", str( self.alarm_message ) )
    def Menu_Mode_Press( self, event ):
        # Menu
        cmenu = QMenu( self )
        # Actions
        cmenu_clock = cmenu.addAction( "Clock" )
        cmenu_stopwatch = cmenu.addAction( "Stopwatch" )

        # Execute
        geo = self.layout.mode.geometry()
        qpoint = geo.bottomLeft()
        position = self.layout.footer_widget.mapToGlobal( qpoint )
        action = cmenu.exec_( position )
        # Triggers
        if action == cmenu_clock:
            self.Mode_Index( 0 )
        elif action == cmenu_stopwatch:
            self.Mode_Index( 1 )
    def Menu_Mode_Wheel( self, event ):
        delta = event.angleDelta()
        if event.modifiers() == QtCore.Qt.NoModifier:
            delta_y = delta.y()
            value = 0
            if delta_y > 20:
                value = -1
            if delta_y < -20:
                value = 1
            if ( value == -1 or value == 1 ):
                new_index = self.Limit_Range( self.mode_index + value, 0, 1 )
                if self.mode_index != new_index:
                    self.Mode_Index( new_index )

    def Menu_Settings( self ):
        # Display
        self.dialog.show()
        # Resize Geometry
        qmw = Krita.instance().activeWindow().qwindow()
        px = qmw.x()
        py = qmw.y()
        pw = 500
        ph = 100
        w2 = qmw.width() * 0.5
        h2 = qmw.height() * 0.5
        self.dialog.setGeometry( int( px + w2 - pw * 0.5 ), int( py + h2 - ph * 0.5 ), int( pw ), int( ph ) )
    def Menu_Manual( self ):
        url = "https://github.com/EyeOdin/timer_watch/wiki"
        webbrowser.open_new( url )
    def Menu_Copyright( self ):
        url = "https://github.com/EyeOdin/timer_watch/blob/master/LICENSE"
        webbrowser.open_new( url )

    #endregion
    #region Management

    def Message_Log( self, operation, message ):
        string = f"Timer Watch | { operation } { message }"
        try:QtCore.qDebug( string )
        except:pass
    def Message_Warnning( self, operation, message ):
        string = f"Timer Watch | { operation } { message }"
        QMessageBox.information( QWidget(), i18n( "Warnning" ), i18n( string ) )
    def Message_Float( self, operation, message, icon ):
        ki = Krita.instance()
        string = f"Timer Watch | { operation } { message }"
        ki.activeWindow().activeView().showFloatingMessage( string, ki.icon( icon ), 5000, 0 )

    def Limit_Range( self, value, minimum, maximum ):
        if value <= minimum:
            value = minimum
        if value >= maximum:
            value = maximum
        return value

    def Resize_Print( self, event ):
        # Used doing a photoshoot
        width = self.width()
        height = self.height()
        QtCore.qDebug( "size = " + str( width ) + " x "  + str( height ) )

    #endregion
    #region Time

    def Pulse( self ):
        # Timers
        self.clock_time = QTime.currentTime()
        self.SW_Pulse()
        # Display
        self.Number_Display()
        self.SW_ProgressBar()
    def Number_Display( self ):
        if self.mode_index == 0:
            if photoshoot == True:self.layout.lcd_number.display( str( '00:00' ) ) # for preview photo
            else:self.layout.lcd_number.display( str( self.clock_time.toString( 'hh:mm' ) ) )
        if self.mode_index == 1:
            self.layout.lcd_number.display( str( self.sw_counter.toString( 'hh:mm:ss' ) ) )

    #endregion
    #region Stopwatch

    def SW_Pulse( self ):
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
            self.sw_counter.setHMS( h,m,s,ms )

    def SW_ProgressBar( self ):
        # UI
        maxi = self.layout
        counter = self.hms_to_time( self.sw_counter.hour(), self.sw_counter.minute(), self.sw_counter.second() )
        self.layout.progress_bar.setValue( counter )
        # Alarm
        if ( self.sw_alarm == True and counter == self.sw_limit and counter != 0 and self.sw_limit != 0 ):
            self.Message_Warnning( "MESSAGE", f"\n{ self.alarm_message }" )
    def SW_StartPause( self, boolean ):
        # Variable
        self.sw_state = boolean
        # UI
        if boolean == True:
            self.layout.start_pause.setIcon( Krita.instance().icon( 'media-playback-stop' ) )
            self.layout.start_pause.setToolTip( "Pause" )
        else:
            self.layout.start_pause.setIcon( Krita.instance().icon( 'media-playback-start' ) )
            self.layout.start_pause.setToolTip( "Start" )
        self.Widget_Enable( False )
        self.Number_Display()
    def SW_Reset( self ):
        # Variables
        self.sw_state = False
        self.sw_counter.setHMS( 0,0,0,0 )
        # UI
        self.layout.start_pause.setIcon( Krita.instance().icon( 'media-playback-start' ) )
        self.layout.start_pause.setToolTip( "Start" )
        self.layout.start_pause.setChecked( False )
        self.Widget_Enable( True )
        self.Number_Display()
    def SW_Alarm( self, boolean ):
        self.sw_alarm = boolean
        if boolean == True:
            self.layout.alarm.setIcon( Krita.instance().icon( 'warning' ) )
        else:
            self.layout.alarm.setIcon( Krita.instance().icon( 'paintbrush' ) )
    def SW_TimeEdit( self ):
        # Variable
        qtime = self.layout.time_limit.time()
        self.sw_limit = self.hms_to_time( qtime.hour(), qtime.minute(), qtime.second() )
        self.layout.progress_bar.setMaximum( self.sw_limit )
        # Save
        Krita.instance().writeSetting( "Timer Watch", "sw_limit", str( self.sw_limit ) )

    def Widget_Enable( self, boolean ):
        self.layout.alarm.setEnabled( boolean )
        self.layout.time_limit.setEnabled( boolean )
        self.layout.settings.setEnabled( boolean )
    def hms_to_time( self, h, m, s ):
        # hours
        hm = h * minutos
        hs = hm * segundos
        # minutes
        ms = m * segundos
        # Total
        time = hs + ms + s
        return time

    #endregion
    #region Widget Events

    def showEvent( self, event ):
        self.timer_pulse.start( 1000 )
    def enterEvent( self, event ):
        pass
    def leaveEvent( self, event ):
        self.layout.time_limit.clearFocus()
    def resizeEvent( self, event ):
        # self.Resize_Print( event )
        pass
    def closeEvent( self, event ):
        self.timer_pulse.stop()

    def eventFilter( self, source, event ):
        # Check~
        source_valid = source == self.layout.mode or source == self.layout.lcd_number
        # Mode
        if ( event.type() == QEvent.MouseButtonPress and source is self.layout.mode ):
            self.Menu_Mode_Press( event )
            return True
        if ( event.type() == QEvent.Wheel and source_valid == True ):
            self.Menu_Mode_Wheel( event )
            return True

        return super().eventFilter( source, event )

    def canvasChanged( self, canvas ):
        pass

    #endregion
    #region Notes

    """
    # Label Message
    self.layout.label.setText( "message" )

    # Pop Up Message
    QMessageBox.information( QWidget(), i18n( "Warnning" ), i18n( "message" ) )

    # Log Viewer Message
    QtCore.qDebug( "value = " + str( value ) )
    QtCore.qDebug( "message" )
    QtCore.qWarning( "message" )
    QtCore.qCritical( "message" )

    # PyQt5 Multimedia playback
    from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
    self.player = QMediaPlayer()
    # Play Sound
    if self.alarm_sound == True:
        path = self.directory_plugin + "/ALARM/pop.mp3"
        url = QUrl.fromLocalFile( path )
        content = QMediaContent( url )
        self.player.setMedia( content )
        self.player.play()
    """
    #endregion
