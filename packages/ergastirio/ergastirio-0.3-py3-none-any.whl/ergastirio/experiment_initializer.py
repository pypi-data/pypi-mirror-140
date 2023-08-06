'''
This module contains several function which are used to initialize a certain experiment. 
Before using the functions in this module, an experiment() object needs to be created (typically by the main.pyw file), and a config file needs to be assigned to 
the experiment. After the experiment have been assigned a config file, the function set_up_experiment(exp) is called, where exp is the experiment() object.
'''

import PyQt5.QtWidgets as Qt# QApplication, QWidget, QMainWindow, QPushButton, QHBoxLayout
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import logging
import numpy as np
import importlib
import ergastirio.plots
import ergastirio.panels
import ergastirio.widgets

style1 = """{
            font: bold;
            border: 1px solid black;
            border-radius: 6px;
            margin-top: 6px;
        }
"""

style2 = """::title {
            subcontrol-origin: margin;
            left: 7px;
            padding: -8px 5px 0px 5px;
        }
        """

def setup(exp):
    if not ergastirio.experiment_initializer.set_up_experiment(exp):
        return False
    if not ergastirio.experiment_initializer.set_up_experiment_gui(exp):
        return False
    ergastirio.experiment_initializer.link_data_to_gui(exp)
    return True
  
def set_up_experiment(exp):
    '''
    This function initializes a certain experiment (passed as an input argument) based on the settings stored in the dictionary exp.config.
    It subsequently calls several functions to load instruments, initialize storage arrays, validate user configs
    '''
        
    if not load_instruments(exp):       #Load all instruments based on the strings specified in the list exp.config['Instruments']
        return False

    if not generate_data_headers(exp):  #Based on the loaded instruments, and on the data created by each instrument, it populates the list of strings exp.data_headers
        return False

    initialize_storage_variable(exp)    #Create Storage variables
    initialize_temporary_variable(exp)
       
    if not validate_plots_settings(exp): #check if the plots settings specified in the .json file are valid (i.e. any quantity defined in 'x' and 'y' is a valid device data
        return False
    return True


def set_up_experiment_gui(exp):
    '''
    This function initializes the GUI of an experiment (passed as an input argument). It must be called after calling the function set_up_experiment()
    '''
    create_gui_table_data(exp,exp.parent.containers['tabledata']['container'])
    create_gui_plots(exp,exp.parent.containers['plots']['scrollarea'])
    if not create_gui_instruments(exp,exp.parent.containers['instruments']['container']): #Create GUIs for all loaded instruments 
        return False
    exp.parent.tileSubWindows()
    return True

def link_data_to_gui(exp):
    exp.data.add_syncronized_objects([  exp.tabledata,  ergastirio.widgets.Table.data])
    for plot in exp.plots:
        exp.data.add_syncronized_objects([  plot['plotobject'],  ergastirio.widgets.PlotObject.data])
        

def create_gui_logging(exp,container):
    '''
    Create GUIs for logger
    container
        QWidget which will contain the GUIs
    '''
    exp.logger.info(f"Creating GUI for logger...")
    box = Qt.QVBoxLayout()
    exp.logging_text_area = ergastirio.widgets.LoggerTextArea()
    exp.logging_text_area.add_logger(logger=logging.getLogger(exp.name_logger))
        
    box.addWidget(exp.logging_text_area)
    container.setLayout(box)

    return True

def load_instruments(exp):
    exp.logger.info(f"Loading all instruments specified in {exp.config_file}...")
    exp.instruments = []
    i=0
    for instrument in exp.config['Instruments']:
        IsValidPackage = importlib.util.find_spec(instrument) is not None
        if not(IsValidPackage):
            exp.logger.error(f"{instrument} is not a valid python package. Fix the error and restart this application")
            return False
        device_module =  importlib.import_module(instrument+'.main')
        if not(hasattr(device_module,'interface')):
            exp.logger.error(f"{instrument} is a valid package, but it does not contain an 'interface' class.")
            return False
        exp.instruments.append({'name':f"dev{i}",
                                    'fullname':f"dev{i}_{instrument}",
                                    'type':instrument,
                                    'interface_class':device_module.interface}
                                )
        exp.logger.info(f"Instrument loaded: {exp.instruments[i]['name']} -> {exp.instruments[i]['type']}")
        i = i+1
    return True

def generate_data_headers(exp):
    exp.logger.info(f"Preparing the data headers...")
    exp.data_headers =[]
    exp.data_headers.append('timestamp')
    exp.data_headers.append('time')
    for instrument in exp.instruments:
        for key in instrument['interface_class'].output.keys():
            exp.data_headers.append(instrument['name']+'.'+key)
    exp.logger.info(f"The following data will be acquired: {exp.data_headers}")
    return True

def initialize_storage_variable(exp):
    ''' Initialize all arrays for data storage. '''      
    exp.data = ergastirio.EnhancedList([]) #np.empty([0,len(exp.data_headers)]) 
    exp.data_std = [] # = np.empty([0,len(exp.data_headers)-2])  #Note: each column of exp.data_std contains the error of each data in the same column of exp.data
                                                                    #if that data was acquired via an average (otherwise the error is set to zero)
   
    return True
    
def initialize_temporary_variable(exp):
    ''' These variables will only be used as temporary arrays for averaging purposes. The number of columns in the storage matrices is given by the length of exp.data_headers. '''
    exp.numb_acq_to_average = 0 # This will contain the number of acquisitions to be averaged, chosen by the user
    exp.data_being_averaged = False #It's a flag which keeps track of whether data is being currently averaged
    exp.data_temp = np.empty([0,len(exp.data_headers)-2]) #The number of columns of expdata_temp is 2 less than the number of columns of exp.data
                                                                #because the first 2 columns of exp.data are for time and acquisition number
    return True

def validate_plots_settings(exp):
    '''
    This function looks at the content of exp.config['Plots'] and check that all settings specified by the user are valid
    '''
    exp.logger.info(f"Validating all plot settings...")
    exp.plots = []
    valid_data = exp.data_headers.copy()
    valid_data.append("acq#") #Need to implement this better
    for plotindex, plot in enumerate(exp.config['Plots']):
        if isinstance(plot,dict) and ('x' in plot.keys()) and ('y' in plot.keys()):
            if not plot['x'] in valid_data:
                exp.logger.error(f"Plot #{plotindex}: {plot['x']} is not a valid device data")
                return False
            if isinstance(plot['y'],str):
                plot['y'] = [plot['y']]
            for y_data in plot['y']:
                if not y_data in valid_data:
                    exp.logger.error(f"Plot #{plotindex}: {y_data} is not a valid device data")
                    return False            
        else:
            exp.logger.error(f"Each plot must be defined in the .json file as a dictionary containing an 'x' and a 'y' key.")
            return False
        exp.plots.append({'name':f"plot{plotindex}",
                            'x':plot['x'],
                            'y':plot['y']})
        exp.logger.info(f"Plot #{plotindex}, x = {plot['x']}, y = {plot['y']}")
    return True

def create_gui_instruments(exp,container):
    '''
    Create GUIs for all loaded instruments, and for the acquisition control panel

    container
        QWidget which will contain the GUIs
    '''
    if exp.config['Alignment_Instruments_Window'] and exp.config['Alignment_Instruments_Window']=='H':
        box = Qt.QHBoxLayout()
    else: 
        box = Qt.QVBoxLayout()

    ## CREATE ACQUISITION CONTROL PANEL
    exp.logger.info(f"Creating GUI for acquisition control panel...")
    exp.control_panel = dict()
    exp.control_panel['frame'] = Qt.QGroupBox() 
    exp.control_panel['frame'].setObjectName('acquisition_panel')
    string = 'QGroupBox#acquisition_panel'
    exp.control_panel['frame'].setStyleSheet(string + style1 + '\nQGroupBox' + style2) #This line changes the style of ONLY this QWdiget
    exp.control_panel['frame'].setTitle(f"Acquisition Panel")
    exp.control_panel['fullname'] = 'AcqControlPanel'
    exp.control_panel['interface'] = ergastirio.panels.acquisition_control(   exp.app,
                                                                                    exp.mainwindow,
                                                                                    exp.control_panel['frame'],
                                                                                    exp,
                                                                                    #name_logger=exp.control_panel['fullname']
                                                                                    )
    #exp.logging_text_area.add_logger(logger=logging.getLogger(exp.control_panel['fullname'])) #Connect the logger of this panel to the text area for logging in the GUI
    exp.control_panel['interface'].create_gui()
    box.addWidget(exp.control_panel['frame'])
    ####

    exp.logger.info(f"Creating GUI for all loaded instruments...")
    
    for i,instrument in enumerate(exp.instruments):
        exp.instruments[i]['frame'] = Qt.QGroupBox() # Qt.QWidget()
        exp.instruments[i]['frame'].setObjectName(exp.instruments[i]['name']+'_frame')
        string = "QGroupBox#"+ exp.instruments[i]['frame'].objectName()
        exp.instruments[i]['frame'].setStyleSheet(string + style1 + string + style2) #This line changes the style of ONLY this QWdiget

        exp.instruments[i]['frame'].setTitle(f"{exp.instruments[i]['name']} ({exp.instruments[i]['type']})")
        exp.instruments[i]['interface'] = exp.instruments[i]['interface_class'](    exp.app,
                                                                                    exp.mainwindow,
                                                                                    exp.instruments[i]['frame'],
                                                                                    name_logger=exp.instruments[i]['fullname']) #It might make more sense to create the interface objects in the load_instruments function instead
        exp.logging_text_area.add_logger(logger=logging.getLogger(exp.instruments[i]['fullname'])) #Connect the logger of this instrument to the text area for logging in the GUI
        exp.instruments[i]['interface'].create_gui()
        box.addWidget(exp.instruments[i]['frame'] )
    box.addStretch(1)

    container.setLayout(box) #This line makes sure that all widgest defined so far are assigned to the widget defines in exp.parent
    exp.container_instruments = container
    return True

def create_gui_plots(exp,container):
    '''
    Create GUIs for all plots

    container
        QWidget which will contain the GUIs
    '''
    exp.logger.info(f"Creating GUI for all plots...")

    container.mdi = Qt.QMdiArea()
    container.setWidget(container.mdi)
    for plotindex, plot in enumerate(exp.plots):
        exp.plots[plotindex]['subwindow'] = Qt.QMdiSubWindow()
        exp.plots[plotindex]['subwindow'].setWindowFlags(QtCore.Qt.FramelessWindowHint)
        exp.plots[plotindex]['subwindow'].setWindowTitle(exp.plots[plotindex]['name'])
        exp.plots[plotindex]['scrollarea'] = Qt.QScrollArea()
        exp.plots[plotindex]['widget'] = Qt.QWidget()
        exp.plots[plotindex]['subwindow'].setWidget(exp.plots[plotindex]['scrollarea'])
        exp.plots[plotindex]['scrollarea'].setWidget(exp.plots[plotindex]['widget'])
        exp.plots[plotindex]['scrollarea'].setWidgetResizable(True)
        container.mdi.addSubWindow(exp.plots[plotindex]['subwindow'])
        exp.plots[plotindex]['plotobject'] = ergastirio.widgets.PlotObject(exp.app, 
                                                                           exp.mainwindow, 
                                                                           exp.plots[plotindex]['widget'],
                                                                           data_headers = exp.data_headers,
                                                                           plot_config=exp.plots[plotindex])
        exp.plots[plotindex]['widget'].show()
    container.mdi.tileSubWindows()
    exp.container_plots = container
    return True

def create_gui_table_data(exp,container):
    '''
    Create GUIs for the table showing the currently stored data

    container
        QWidget which will contain the GUIs
    '''  
    exp.logger.info(f"Creating GUI for table...")

    layout = Qt.QVBoxLayout()
    exp.data_management_panel_container = Qt.QGroupBox()
    exp.data_management_panel = ergastirio.panels.data_management(  exp.app,
                                                                    exp.mainwindow,
                                                                    exp.data_management_panel_container,
                                                                    exp)

    exp.data_management_panel.create_gui()
    exp.tabledata = ergastirio.widgets.Table()
    exp.tabledata.data_headers = exp.data_headers
    exp.tabledata.data = exp.data
    
    layout.addWidget(exp.data_management_panel_container)
    layout.addWidget(exp.tabledata,stretch=1)
    container.setLayout(layout)
    exp.container_tabledata = container
    return True