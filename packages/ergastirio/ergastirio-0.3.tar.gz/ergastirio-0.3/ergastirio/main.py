import os
import PyQt5
dirname = os.path.dirname(PyQt5.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
import PyQt5.QtWidgets as Qt# QApplication, QWidget, QMainWindow, QPushButton, QHBoxLayout
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import logging
import sys
import argparse
import json
import importlib
import numpy as np
import datetime

import ergastirio.experiment_initializer

class EnhancedList(list):
    '''
    This class is used to generate an "event-based" list object. Everytime the content of the list changes, it also stores a copy of the list 
    in a certain property of all the objects specified in the list linked_objects. 
    Each element of linked_objects is a two-element list in the form [class_instance,class_property]. This behavior is useful when the linked objects
    are, e.g., plots and tables, and the targeted property is defined via a @setter, in order to automatically update parts of the gui

    Examples:

        class test():
            def __init__( self ):
                self.__value = "old value"

            @property
            def value( self ):
                return self.__value

            @value.setter
            def value( self, value ):
                self.__value = value
                print("Targeted list changed to " + str(value))

        a = EnhancedList([1,2,3])
        t=test()
        a.add_syncronized_objects([t,test.value])
        a.append(4)

    Targeted list changed to [1, 2, 3, 4]

    '''
    linked_objects = []

    # def __init__(self,  *args):
    #     super().__init__(self, *args)

    def add_syncronized_objects(self,list_objects):
        self.linked_objects.append(list_objects)

    def sync(self):
        for obj in self.linked_objects:
            obj[1].fset(obj[0], self.copy())

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.sync()
    def __delitem__(self, value):
        super().__delitem__(value)
        self.sync()
    def __add__(self, value):
        super().__add__(value)
        self.sync()
    def __iadd__(self, value):
        super().__iadd__(value)
        self.sync()
    def append(self, value):
        super().append(value)
        self.sync()
    def remove(self, value):
        super().remove(value)
        self.sync()
    def insert(self, *args):
        super().insert(*args)
        self.sync()
    def pop(self, *args):
        super().pop(*args)
        self.sync()
    def clear(self):
        super().clear()
        self.sync()


class experiment():
    _config_file = ''
    _verbose = True #Keep track of whether this instance of the interface should produce logs or not
    _name_logger = ''
    data_headers =[]    #List of strings, will contain the label of each 'column" of acquired data, based on the instruments connected, in the format "dev#i_dataname#j"
                        # where #i runs from 0 to the number of instruments minus 1, and dataname#j is the name of the jth data created by the i-th instrument.
                        # the data created by each instrument are specified by the keys of the output dictionary defined in the interface of each instrument
    continous_acquisition = False #Boolean variable that keeps track of wheter we are performing a continuous acquisition
    _refresh_time = 0.2

    def __init__(self, app, mainwindow, parent, config_file, name_logger=__package__):
        # app           = The pyqt5 QApplication() object
        # mainwindow    = Main Window of the application
        # parent        = a QWidget (or QMainWindow) object that will be the parent for the gui of this device. Normally, this is set to the mdi object of the mainwindow object
        #                 This QWdiget must have 4 attributes defined as QWdiget() objects and called: 
        #                 parent.tabledata_container, parent.logging_container, parent.plots_container and parent.instruments_container
        #                 These 4 widgets will be used to host the GUI of the experiment
        # config_file   = a valid .json file containing all settings of this experiment
        # name_logger   = The name of the logger used for this particular experiment. If none is specified, the name of the package (i.e. ergastirio) is used as logger name

        self.mainwindow = mainwindow
        self.app = app
        self.parent = parent
        self.name_logger = name_logger #Setting this property will also create the logger,set defaulat output style, and store the logger object in self.logger (see @name_logger.setter)
        ergastirio.experiment_initializer.create_gui_logging(self,self.parent.containers['logging']['container']) 
                                                                    #By calling this function here (instead than later inside set_up_experiment_gui() ) we make sure that any log message is shown in the GUI
                                                                    #Need to implement this more elegantly
        self.mainwindow.experiment = self
        self.config_file = config_file #Setting the config file name will also automatically open the file and load the settings (see @config_file.setter)
        return

    @property
    def verbose(self):
        return self.verbose
    @verbose.setter
    def verbose(self,verbose):
        #When the verbose property of this interface is changed, we also update accordingly the level of the logger object
        if verbose: loglevel = logging.INFO
        else: loglevel = logging.CRITICAL
        self.logger.setLevel(level=loglevel)

    @property
    def name_logger(self):
        return self._name_logger
    @name_logger.setter
    def name_logger(self,name):
        #Create logger, and set default output style.
        self._name_logger = name
        self.logger = logging.getLogger(self._name_logger)
        self.verbose = self._verbose #This will automatically set the logger verbosity too
        if not self.logger.handlers:
            formatter = logging.Formatter(f"[{self.name_logger}]: %(message)s")
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
        self.logger.propagate = False

    @property
    def refresh_time(self):
        return self._refresh_time
    @refresh_time.setter
    def refresh_time(self,r):
        try: 
            r = float(r)
            if self._refresh_time == r: #in this case the number in the refresh time edit box is the same as the refresh time currently stored
                return True
        except ValueError:
            self.logger.error(f"The refresh time must be a valid number.")
            return self._refresh_time
        if r < 0.001:
            self.logger.error(f"The refresh time must be positive and >= 1ms.")
            return self._refresh_time
        self.logger.info(f"The refresh time is now {r} s.")
        self._refresh_time = r
        return self.refresh_time

    @property
    def config_file(self):
        return self._config_file
    @config_file.setter
    def config_file(self,config_file):
        self.logger.info(f"Setting the config file to {config_file}... [Note: this will reset the experiment]")
        self._config_file = config_file
        self.load_config()
        return 

    def load_config(self):
        '''
        Import experiment settings from the .json file stored in self.config_file, and then starts setting up the experiment 
        by calling the function ergastirio.experiment_initializer.setup(self).
        '''
        self.logger.info(f"Loading the content of {self.config_file}")
        try:
            with open(self.config_file) as jsonfile:
                self.config = json.load(jsonfile)
        except Exception as e:
            self.logger.error(f"An error occurred while loading the file. Fix the error and restart this application\n: {e}")
            return
        if not ergastirio.experiment_initializer.setup(self):
            return

    def read_current_data_from_all_instruments(self):
        '''
        It looks into all the instruments interfaces (defined via the key 'interface' in each dictionary of the list exp.instruments) 
        and it extracts data from each instrument. From each instrument, the data to exctract is contained in the dictionary exp.instruments[i]['interface'].output
        '''
        current_data = []
        self.logger.info(f"Reading data from all instruments...")
        for instrument in self.instruments:
            for data in instrument['interface'].output.values():
                current_data.append(data)  
        
        return current_data

    def store_current_data_from_all_instruments(self):
        '''
        '''
        current_data = self.read_current_data_from_all_instruments() #Read the current data from all instruments
        acq_numb = len(self.data) + 1 #We look at the number of rows of self.data
        now = datetime.datetime.now()
        time_string=now.strftime("%Y-%m-%d %H:%M:%S.%f")
        timestamp = datetime.datetime.timestamp(now)
        self.logger.info(f"[{time_string}] Acquisition #{acq_numb} {current_data}")
        current_data.insert(0, time_string)
        current_data.insert(0, timestamp )
        #self.data = np.append(self.data,[current_data] ,axis=0)
        self.data.append(current_data)
        self.data_std.append([0]*(len(current_data)-1))

    def update(self):
        if self.continous_acquisition:
            self.store_current_data_from_all_instruments()
            QtCore.QTimer.singleShot(int(self.refresh_time*1e3), self.update)

    def delete_current_data(self):
        self.logger.info(f"All store data was deleted.")
        self.data.clear()
        self.data_std.clear()

    def delete_row_from_data(self,row):
        try:
            self.data.pop(row)
            self.data_std.pop(row)
            if row == -1:
                row = 'Last'
            self.logger.info(f"{row} row has been removed from data.")
        except:
            pass

    def save_stored_data(self,filename):
        '''
        Saves the values of all currently stored data on file. 
        The data are saved in a tabular form and delimited by a comma.
        '''
        d =','
        header = ''
        for h in self.data_headers:
            header = header + h + d 
        for h in self.data_headers: #We skip the first element of headers which corresponds to acquisition time
            header = header + (h+'_std') +  d

        A = np.concatenate((np.array(self.data), np.array(self.data_std)),axis=1)
        print(A)
        np.savetxt(filename, A, delimiter=d, header=header, comments="")#,fmt=d.join(['%s'] + ['%e']*(A.shape[1]-1)))
        self.logger.info(f"Saved all stored data (number of rows = {A.shape[0]} in the file {filename}")
        return

    def close_experiment(self):
        for instrument in self.instruments:
            try:
                instrument['interface'].close()
            except:
                pass

class MainWindow(Qt.QMainWindow):
    '''
    The main window contains several menus and a QMdiArea object, 
    The QMdiArea object in turn contains subwindows where instruments, plots, data table and logs will be created
    Object creation:
        window = MainWindow()
    The QMdiArea object is saved as attribute:
        window.mdi 
    The mdi object is also the parent object which needs to be passed as parameter when creating an instance of the experiment object
    For example:
        Experiment = experiment(app,window,window.mdi,config_file)
    The mdi object contains a dictionary, window.mdi.containers whose elements represent the different subwindows.
    Specifically, window.mdi.containers = {'logging':{...},'tabledata':{...},'instruments':{...},'plots':{...} }
    The object
        window.mdi.containers[name]['container']
    is the widget that will act as container for the different part of the gui. 
    Each of this widget is a child (via setWidget() method) of a corresponding QScrollArea object, 
        window.mdi.containers[name]['scrollarea']
    In turns, the scrollarea objects are children (via setWidget() method) of corresponding QMdiSubWindow objects
        window.mdi.containers[name]['subwindow']
    '''
    def __init__(self):
        super().__init__()
        self.setWindowTitle(__package__)
        self.mdi = Qt.QMdiArea()
        self.setCentralWidget(self.mdi)

        #This dictionary will be used to create the subwindows of the mdi, and also to populate the "View" menu
        mdi_panels ={ 'logging':{'title':'Logging'},
                      'tabledata':{'title':'Acquired Data'},
                      'instruments':{'title':'Instruments'},
                      'plots':{'title':'Plots'}
                      }

        bar = self.menuBar()
        file = bar.addMenu("File")
        file.addAction("New Experiment")
        view = bar.addMenu("View")
        view.addAction("Tile Windows")
        view.addSeparator()
        for mdi_panel in mdi_panels.values():
            view.addAction(mdi_panel['title'])
        view.triggered[Qt.QAction].connect(self.action_view)
        
        #Create the different subdiwndows, based on the element of the dictionary mdi_panels
        for key,mdi_panel in mdi_panels.items():
            mdi_panels[key]['subwindow'] = Qt.QMdiSubWindow()
            mdi_panels[key]['subwindow'].setWindowFlags(QtCore.Qt.CustomizeWindowHint)
            mdi_panels[key]['subwindow'].setWindowTitle(mdi_panels[key]['title'])
            mdi_panels[key]['scrollarea'] = Qt.QScrollArea(self)
            #mdi_panels[key]['scrollarea'].verticalScrollBar().rangeChanged.connect(lambda : self.adjust_position_scroll_area(mdi_panels[key]['scrollarea']))
            #mdi_panels[key]['scrollarea'].verticalScrollBar().rangeChanged.connect(lambda: mdi_panels[key]['scrollarea'].verticalScrollBar().setValue(mdi_panels[key]['scrollarea'].verticalScrollBar().maximum()))
            mdi_panels[key]['container'] = Qt.QWidget(self)
            mdi_panels[key]['subwindow'].setWidget(mdi_panels[key]['scrollarea'])
            mdi_panels[key]['scrollarea'].setWidget(mdi_panels[key]['container'])
            mdi_panels[key]['scrollarea'].setWidgetResizable(True)
            self.mdi.addSubWindow(mdi_panels[key]['subwindow'])
            mdi_panel['container'].show()
        self.mdi.containers = mdi_panels

        #lambda: scroll_bar.setValue(scroll_bar.maximum())
        self.mdi.tileSubWindows()
        #self.mdi.setActivationOrder(Qt.QMdiArea.CreationOrder)

    #def adjust_position_scroll_area(self,scrollarea):
    #    print('test')
    #    scrollarea.verticalScrollBar().setValue(scrollarea.verticalScrollBar().maximum())

    def action_view(self, p):
        if p.text() == "Tile Windows":
            self.mdi.tileSubWindows()
            return
        for mdi_panel in self.mdi.containers.values():
            if p.text() == mdi_panel['title']:
                mdi_panel['subwindow'].setHidden(not mdi_panel['subwindow'].isHidden())

    def closeEvent(self, event):
        if self.experiment:
            self.experiment.close_experiment()


def main():

    parser = argparse.ArgumentParser(description = "",epilog = "")
    parser.add_argument('-e', 
                        help=f"Path of .json file contaning the configuration of this experiment",
                        action="store", dest="config", type=str, default=None)
    parser.add_argument("-s", "--decrease_verbose", help="Decrease verbosity.", action="store_true")
    args = parser.parse_args()
    
    app = Qt.QApplication(sys.argv)
    window = MainWindow()
    
    #app.aboutToQuit.connect(Interface.closeEvent) 

    if args.config:
        config_file = os.path.abspath(args.config)
    else:
        folder_default_file = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(folder_default_file,'config_default.json')

    Experiment = experiment(app,window,window.mdi,config_file)

    window.show()
    app.exec()# Start the event loop.

if __name__ == '__main__':
    main()