import os
import PyQt5.QtWidgets as Qt# QApplication, QWidget, QMainWindow, QPushButton, QHBoxLayout
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import logging
import ergastirio.utils

graphics_dir = os.path.join(os.path.dirname(__file__), 'graphics')

'''
The panels defined in this module are meant to be ONLY gui for other classes, i.e. their event are directly connected to methods of other objects
do not have their own logger, and they do not produce any logging event. Rather, they connect to methods 
of the experiment object
'''

class acquisition_control():

    def __init__(self, app, mainwindow, parent, experiment):
        # app           = The pyqt5 QApplication() object
        # mainwindow    = Main Window of the application
        # parent        = a QWidget (or QMainWindow) object that will be the parent of this gui
        # experiment    = an experiment() object, whose acquisition will be controlled by this panel

        self.mainwindow = mainwindow
        self.app = app
        self.parent = parent
        self.experiment  = experiment 

    def create_gui(self): 

        #self.widgets_enabled_when_connected = []     #The widgets in this list will only be enabled when the interface has succesfully connected to a device
        #self.widgets_enabled_when_disconnected = []  #The widgets in this list will only be enabled when the interface is not connected to a device
        
        hbox1 = Qt.QHBoxLayout()

        self.button_StartPauseContinuousAcquisition = Qt.QPushButton("")
        self.button_StartPauseContinuousAcquisition.setIcon(QtGui.QIcon(os.path.join(graphics_dir,'play.png')))
        self.button_StartPauseContinuousAcquisition.setToolTip('Start or pause continuous data acquisition.') 
        self.button_StartPauseContinuousAcquisition.clicked.connect(self.click_button_StartPauseContinuousAcquisition)
        self.label_Trigger = Qt.QLabel("Trigger: ")
        self.radio_TriggerGlobal = Qt.QRadioButton()
        self.radio_TriggerGlobal.setText("Global")
        self.radio_TriggerGlobal.setStyleSheet("QRadioButton { font: bold;}");
        self.radio_TriggerGlobal.setChecked(True)
        self.radio_TriggerGlobal.value= "global"
        self.radio_TriggerGlobal.toggled.connect(self.click_radio_global_instrument)
        self.radio_TriggerGlobal.setToolTip('In this modality, data from all instruments is acquired at periodic inteverals of time, set by the \'refresh time\'. \nNote: user must check that each instrument is running and refreshing its own data.') 
        self.label_RefreshTime = Qt.QLabel("refresh time (s) = ")
        self.edit_RefreshTime = Qt.QLineEdit()
        self.edit_RefreshTime.setText(str(self.experiment.refresh_time))
        self.edit_RefreshTime.returnPressed.connect(self.press_enter_refresh_time)
        self.edit_RefreshTime.setAlignment(QtCore.Qt.AlignRight)
        
        self.radio_TriggerInstrument = Qt.QRadioButton("By Instrument")
        self.radio_TriggerInstrument.setStyleSheet("QRadioButton { font: bold;}");
        self.radio_TriggerInstrument.value= "by_instrument"
        self.radio_TriggerInstrument.toggled.connect(self.click_radio_global_instrument)
        self.label_TriggerInstrument = Qt.QLabel(" master = ")
        self.combo_TriggerInstruments = Qt.QComboBox()
        self.combo_TriggerInstruments.resize(self.combo_TriggerInstruments.sizeHint())

        #self.button_StartPauseReading.clicked.connect(self.click_button_StartPauseReading)
        #self.button_StopReading = Qt.QPushButton("")
        #self.button_StopReading.setIcon(QtGui.QIcon(os.path.join(graphics_dir,'stop.png')))
        #self.button_StopReading.setToolTip('Stop the reading from the powermeter. All previous data points are discarded.') 
        #


        
        #self.combo_Devices = Qt.QComboBox()
        ##self.combo_Devices.resize(self.combo_Devices.sizeHint())
        #self.button_RefreshDeviceList = Qt.QPushButton("")
        #self.button_RefreshDeviceList.setIcon(QtGui.QIcon(os.path.join(graphics_dir,'refresh.png')))
        #self.button_RefreshDeviceList.clicked.connect(self.click_button_refresh_list_devices)
        hbox1.addWidget(self.button_StartPauseContinuousAcquisition)
        hbox1.addWidget(self.label_Trigger)
        hbox1.addWidget(self.radio_TriggerGlobal)
        hbox1.addWidget(self.label_RefreshTime)
        hbox1.addWidget(self.edit_RefreshTime)
        hbox1.addWidget(self.radio_TriggerInstrument)
        hbox1.addWidget(self.label_TriggerInstrument)
        hbox1.addWidget(self.combo_TriggerInstruments)
        #hbox1.addWidget(self.combo_Devices,stretch=1)
        #hbox1.addWidget(self.button_RefreshDeviceList)
        hbox1.addStretch(1)

        #hbox2 = Qt.QHBoxLayout()
        #self.button_ConnectDevice = Qt.QPushButton("Connect")
        #self.button_ConnectDevice.clicked.connect(self.click_button_connect_disconnect)
        #self.button_SetZeroPowermeter = Qt.QPushButton("Set Zero")
        #self.button_SetZeroPowermeter.clicked.connect(self.click_button_set_zero_powermeter)
        #self.label_Wavelength = Qt.QLabel("Wavelength: ")
        #self.edit_Wavelength = Qt.QLineEdit()
        #self.edit_Wavelength.returnPressed.connect(self.press_enter_wavelength)
        #self.edit_Wavelength.setAlignment(QtCore.Qt.AlignRight)
        ##self.edit_Wavelength.setMaximumWidth(50)
        #self.label_WavelengthUnits = Qt.QLabel("nm")
        #self.label_PowerRange = Qt.QLabel("Power range: ")
        #self.button_DecreasePowerRange = Qt.QPushButton("<")
        #self.button_DecreasePowerRange.setToolTip('Decrease the powermeter power range.')
        #self.button_DecreasePowerRange.setMaximumWidth(15)
        #self.button_DecreasePowerRange.clicked.connect(lambda x:self.click_button_change_power_range(-1))
        #self.edit_PowerRange = Qt.QLineEdit()
        #self.edit_PowerRange.setToolTip('Maximum power measurable in the current power range (unless \'Auto\' is checked).')
        ##self.edit_PowerRange.setMaximumWidth(60)
        #self.edit_PowerRange.setReadOnly(True)
        #self.button_IncreasePowerRange = Qt.QPushButton(">")
        #self.button_IncreasePowerRange.setToolTip('Increase the powermeter power range.')
        #self.button_IncreasePowerRange.setMaximumWidth(15)
        #self.button_IncreasePowerRange.clicked.connect(lambda x:self.click_button_change_power_range(+1))
        #self.box_PowerRangeAuto = Qt.QCheckBox("Auto")
        #self.box_PowerRangeAuto.stateChanged.connect(self.click_box_PowerRangeAuto)
        #self.box_PowerRangeAuto.setToolTip('Set the power range of the powermeter to Automatic.')
        #hbox2.addWidget(self.button_ConnectDevice)
        #hbox2.addWidget(self.button_SetZeroPowermeter)
        #hbox2.addWidget(self.label_Wavelength)
        #hbox2.addWidget(self.edit_Wavelength)
        #hbox2.addWidget(self.label_WavelengthUnits)
        #hbox2.addWidget(self.label_PowerRange)
        #hbox2.addWidget(self.button_DecreasePowerRange)
        #hbox2.addWidget(self.edit_PowerRange)
        #hbox2.addWidget(self.button_IncreasePowerRange)
        #hbox2.addWidget(self.box_PowerRangeAuto)
        ##hbox2.addStretch(1)

        #hbox3 = Qt.QHBoxLayout()
        #self.button_StartPauseReading = Qt.QPushButton("")
        #self.button_StartPauseReading.setIcon(QtGui.QIcon(os.path.join(graphics_dir,'play.png')))
        #self.button_StartPauseReading.setToolTip('Start or pause the reading from the powermeter. The previous data points are not discarded when pausing.') 
        #self.button_StartPauseReading.clicked.connect(self.click_button_StartPauseReading)
        #self.button_StopReading = Qt.QPushButton("")
        #self.button_StopReading.setIcon(QtGui.QIcon(os.path.join(graphics_dir,'stop.png')))
        #self.button_StopReading.setToolTip('Stop the reading from the powermeter. All previous data points are discarded.') 
        #self.button_StopReading.clicked.connect(self.click_button_StopReading)

        #self.label_RefreshTime = Qt.QLabel("Refresh time (s): ")
        #self.label_RefreshTime.setToolTip('Specifies how often the power is read from the powermeter (Minimum value = 0.001 s).') 
        #self.edit_RefreshTime  = Qt.QLineEdit()
        #self.edit_RefreshTime.setText(f"{self.refresh_time:.3f}")
        #self.edit_RefreshTime.setToolTip('Specifies how often the power is read from the powermeter (Minimum value = 0.001 s).') 
        #self.edit_RefreshTime.returnPressed.connect(self.press_enter_refresh_time)
        #self.edit_RefreshTime.setAlignment(QtCore.Qt.AlignRight)
        ##self.edit_RefreshTime.setMaximumWidth(50)

        #font = QtGui.QFont("Times", 12,QtGui.QFont.Bold)
        #self.label_Power = Qt.QLabel("Power: ")
        #self.label_Power.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignCenter)
        #self.label_Power.setFont(font)
        #self.edit_Power = Qt.QLineEdit()
        #self.edit_Power.setFont(font)
        #self.edit_Power.setText(self.current_power_string)
        ##self.edit_Power.setMaximumWidth(150)
        ##self.edit_Power.resize(self.edit_Power.sizeHint());
        #self.edit_Power.setAlignment(QtCore.Qt.AlignRight)
        #self.edit_Power.setReadOnly(True)
        #if plot:
        #    self.button_ShowHidePlot = Qt.QPushButton("Show/Hide Plot")
        #    #self.button_StopReading.setIcon(QtGui.QIcon(os.path.join(graphics_dir,'stop.png')))
        #    self.button_ShowHidePlot.setToolTip('Show/Hide Plot.') 
        #    self.button_ShowHidePlot.clicked.connect(self.click_button_ShowHidePlot)

        #hbox3.addWidget(self.button_StartPauseReading)
        #hbox3.addWidget(self.button_StopReading)
        #hbox3.addWidget(self.label_RefreshTime)
        #hbox3.addWidget(self.edit_RefreshTime)
        #hbox3.addWidget(self.label_Power)
        #hbox3.addWidget(self.edit_Power)
        #if plot:
        #    hbox3.addWidget(self.button_ShowHidePlot)
        ##hbox3.addStretch(1)
                
        vbox = Qt.QVBoxLayout()
        vbox.addLayout(hbox1)  
        #vbox.addLayout(hbox2)  
        #vbox.addLayout(hbox3)  
        vbox.addStretch(1)

        self.parent.setLayout(vbox) #This line makes sure that all widgest defined so far are assigned to the widget defines in self.parent
        
        #self.parent.layout().setSizeConstraint(Qt.QLayout.SetFixedSize)
        self.parent.resize(self.parent.minimumSize())

        #Initialize part of the GUI by mimicking events
        self.click_radio_global_instrument()

        #The widgets in this list will be enabled when we are NOT continuosly acquiring
        self.widgets_enabled_when_not_continous_acquisition = [ self.button_StartPauseContinuousAcquisition,
                                                            self.radio_TriggerGlobal,
                                                            self.edit_RefreshTime,
                                                            self.radio_TriggerInstrument,
                                                            self.combo_TriggerInstruments ]

        #The widgets in this list will be enabled when we are continuosly acquiring
        self.widgets_enabled_when_continous_acquisition = [ self.button_StartPauseContinuousAcquisition ]

        #The widgets in this list will be disabled when we are continuosly acquiring
        self.widgets_disabled_when_continous_acquisition = [self.radio_TriggerGlobal,
                                                            self.edit_RefreshTime,
                                                            self.radio_TriggerInstrument,
                                                            self.combo_TriggerInstruments
                                                            ]
        self.populate_combo_TriggerInstruments()
        #self.click_button_refresh_list_devices()    #By calling this method, as soon as the gui is created we also look for devices
        #self.set_disconnected_state()               #When GUI is created, all widgets are set to the "Disconnected" state

        return self

    ### GUI Events Functions

    def click_button_StartPauseContinuousAcquisition(self): 
        if(self.experiment.continous_acquisition == False):
            self.start_continous_acquisition()
        elif (self.experiment.continous_acquisition == True):
            self.pause_continous_acquisition()
        return

    def press_enter_refresh_time(self):
        refresh_time = self.edit_RefreshTime.text()
        self.experiment.refresh_time = refresh_time #When doing this assignment, the self.experiment.refresh_time setter will take care of checking if refresh_time is valid, and eventually update the value
        self.edit_RefreshTime.setText(f"{self.experiment.refresh_time:.3f}") #In case refresh_time is not valid, this instruction will restore the displayed value to 
                                                                             #its previous (valid) value
        return True

    def click_radio_global_instrument(self):
        if self.radio_TriggerGlobal.isChecked():
            ergastirio.utils.enable_widget([self.edit_RefreshTime])
            ergastirio.utils.disable_widget([self.combo_TriggerInstruments])
        if self.radio_TriggerInstrument.isChecked():
            ergastirio.utils.disable_widget([self.edit_RefreshTime])
            ergastirio.utils.enable_widget([self.combo_TriggerInstruments])

    ### END GUI Events Functions

    def populate_combo_TriggerInstruments(self):
        list_instruments = [instrument['fullname'] for instrument in self.experiment.instruments]
        self.combo_TriggerInstruments.clear()
        self.combo_TriggerInstruments.addItems(list_instruments)  

    def start_continous_acquisition(self):

        self.press_enter_refresh_time()
        self.experiment.continous_acquisition = True
        self.experiment.update()
        self.set_continous_acquisition_state() # Change some widgets

        return

    def pause_continous_acquisition(self):
        #Sets self.ContinuousRead to 0 (this will force the function Update() to stop calling itself)
        #self.continuous_read = False
        #self.logger.info(f"Paused reading from device {self.connected_device_name}.")
        self.experiment.continous_acquisition = False
        self.set_pause_continous_acquisition_state() # Change some widgets
        return

    def set_pause_continous_acquisition_state(self):
        #Changes the GUI based on the state
        self.button_StartPauseContinuousAcquisition.setIcon(QtGui.QIcon(os.path.join(graphics_dir,'play.png')))
        ergastirio.utils.enable_widget(self.widgets_enabled_when_not_continous_acquisition)
        self.click_radio_global_instrument() #mimick a click on radio button to reset the enabled/disabled state of the corresponding widgets

    def set_continous_acquisition_state(self):
        #Changes the GUI based on the state
        self.button_StartPauseContinuousAcquisition.setIcon(QtGui.QIcon(os.path.join(graphics_dir,'pause.png')))
        ergastirio.utils.enable_widget(self.widgets_enabled_when_continous_acquisition)
        ergastirio.utils.disable_widget(self.widgets_disabled_when_continous_acquisition)


class data_management():
    def __init__(self, app, mainwindow, parent, experiment):
        # app           = The pyqt5 QApplication() object
        # mainwindow    = Main Window of the application
        # parent        = a QWidget (or QMainWindow) object that will be the parent of this gui
        # experiment    = an experiment() object, whose acquisition will be controlled by this panel

        self.mainwindow = mainwindow
        self.app = app
        self.parent = parent
        self.experiment  = experiment 

    def create_gui(self): 
        hbox1 = Qt.QHBoxLayout()

        self.button_SaveData = Qt.QPushButton("Save data")
        self.button_SaveData.setToolTip('Save all currently stored data in a .csv file.') 
        self.button_SaveData.clicked.connect(self.click_button_SaveData)
        
        self.button_DeleteAllData = Qt.QPushButton("Delete all data")
        self.button_DeleteAllData.setToolTip('Delete all currently stored data.') 
        self.button_DeleteAllData.clicked.connect(self.click_button_DeleteAllData)

        self.button_DeleteLastRowData = Qt.QPushButton("Delete last row")
        self.button_DeleteLastRowData.setToolTip('Delete last row of stored data.') 
        self.button_DeleteLastRowData.clicked.connect(self.click_button_DeleteLastRowData)

        hbox1.addWidget(self.button_SaveData)
        hbox1.addWidget(self.button_DeleteAllData)
        hbox1.addWidget(self.button_DeleteLastRowData)
        hbox1.addStretch(1)

        vbox = Qt.QVBoxLayout()
        vbox.addLayout(hbox1)  
        vbox.addStretch(1)

        self.parent.setLayout(vbox) #This line makes sure that all widgest defined so far are assigned to the widget defines in self.parent
        self.parent.resize(self.parent.minimumSize())

        return self

    ### GUI Events Functions

    def click_button_SaveData(self): 
        filename, _ = Qt.QFileDialog.getSaveFileName(self.mainwindow, 
                        "Save File", "", "Csv Files (*.csv);;Text Files (*.txt)")
        if filename:
            self.experiment.save_stored_data(filename)
        return

    def click_button_DeleteAllData(self):
        answer = Qt.QMessageBox.question(self.parent,'', "Are you sure?", Qt.QMessageBox.Yes | Qt.QMessageBox.No, Qt.QMessageBox.No)
        if answer == Qt.QMessageBox.Yes:
            self.experiment.delete_current_data()
        return

    def click_button_DeleteLastRowData(self):
        self.experiment.delete_row_from_data(-1)
        return