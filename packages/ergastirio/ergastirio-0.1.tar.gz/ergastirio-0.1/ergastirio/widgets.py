'''
This module contains several customized widgets used by Ergastirio'''


import PyQt5.QtWidgets as Qt
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import logging
import numpy as np
import importlib
import pyqtgraph as pg
import os

graphics_dir = os.path.join(os.path.dirname(__file__), 'graphics')

'''
The next two widgets (QTextEditLogger and LoggerTextArea) are used to create a textarea which also acts as handler for the logger objects created by the logging module
'''

class QTextEditLogger(logging.Handler):
#Code of this class was adapted from https://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt
    def __init__(self, parent,textwidget):
        super().__init__()
        self.textwidget = textwidget

    def emit(self, record):
        msg = self.format(record)
        self.textwidget.appendPlainText(msg)


class LoggerTextArea(Qt.QDialog, Qt.QPlainTextEdit):
#Code of this class was adapted from https://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt
    def __init__(self, parent=None):
        super().__init__(parent)

        self.widget = Qt.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

        layout = Qt.QVBoxLayout()
        # Add the new logging box widget to the layout
        layout.addWidget(self.widget)
        self.setLayout(layout)

    def add_logger(self,logger):
        logTextBox = QTextEditLogger(self,self.widget)
        if len(logger.handlers)>0:
            logTextBox.setFormatter(logger.handlers[0].formatter)
        logger.addHandler(logTextBox)


class Table(Qt.QTableWidget):
    _data = []
    _data_headers = []

    def __init__(self,  *args):
        Qt.QTableWidget.__init__(self, *args)
        #self.verticalHeader().setVisible(False)

    @property
    def data_headers(self):
        return self._data_headers
    @data_headers.setter
    def data_headers(self,h):
        self._data_headers = h
        horHeaders = self._data_headers 
        self.setColumnCount(len(self._data_headers))
        self.setHorizontalHeaderLabels(horHeaders)

    @property
    def data(self):
        return self._data
    @data.setter
    def data(self,d):
        self._data = d
        rows = len(self._data)
        self.setRowCount(rows)
        for m,row in enumerate(self._data):
            for n,item in enumerate(row):
                newitem = Qt.QTableWidgetItem(str(row[n]))
                self.setItem(m, n, newitem)  
        self.data_headers = self._data_headers #We need to call this after data is added
        self.resizeColumnsToContents()
        self.resizeRowsToContents()


class PlotObject:
    _data_headers =[]
    _data = []
    _colors = 'bgrcmyw'
    _styles = [pg.mkPen(c, width=2, style=QtCore.Qt.SolidLine) for c in _colors]
    _symbol = 'o'
    _style_labels = {"color": "#fff", "font-size": "20px"}
    def __init__(self, app, mainwindow, parent, plot_config):
        '''
        app           = The pyqt5 QApplication() object
        mainwindow    = Main Window of the application
        parent        = a QWidget (or QMainWindow) object that will be the parent for this plot
        plot_config   = a dictionary specifying the settings of this plot. The dictionary must contain at least two keys, 'x' and 'y'. 
                        The value of 'x' must be a single string. The value of 'y' can be either a string or a list of strings.
        '''

        self.mainwindow = mainwindow
        self.app = app
        self.parent = parent
        
        self.ConfigPopupOpen = 0 #This variable is 1 when the popup for plot configuration is open, and 0 otherwise
        self.plot_config = plot_config

        self.Max = 0 #Keep track of the maximum of minimum values plotted in this plot (among all possible curves). It is used for resizing purposes
        self.Min = 0

        #self.PlotErrorBars_var = tk.IntVar(value=1) #This TK variable keeps track of wheter the user wants to plot the errorbars or not

        #Create the figure

        self.graphWidget = pg.PlotWidget()
        self.graphWidget.showGrid(x=True, y=True)
        self.controlWidget = self.controlPanel()
        #self.graphWidget.setMenuEnabled(False)
        vbox = Qt.QVBoxLayout()
        vbox.addWidget(self.graphWidget) 
        vbox.addWidget(self.controlWidget) 
        vbox.setSpacing(0)
        #vbox.addStretch(1)

        self.parent.setLayout(vbox)
        #X = []
        #Y = []
        ## plot data: x, y values
        #self.dataplot = self.graphWidget.plot(X,Y)

    def controlPanel(self):
        w = Qt.QWidget()
        hbox = Qt.QHBoxLayout()
        self.button_settings = Qt.QPushButton("")
        self.button_settings.setIcon(QtGui.QIcon(os.path.join(graphics_dir,'settings.png')))
        #self.button_settings.clicked.connect(self.click_button_refresh_list_devices)
        self.button_home = Qt.QPushButton("")
        self.button_home.setIcon(QtGui.QIcon(os.path.join(graphics_dir,'home.png')))
        hbox.addWidget(self.button_settings)
        hbox.addWidget(self.button_home)
        hbox.addStretch(1)
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)
        w.setLayout(hbox)
        return w

    @property
    def data_headers(self):
        return self._data_headers
    @data_headers.setter
    def data_headers(self,h):
        self._data_headers = h

    @property
    def data(self):
        return self._data
    @data.setter
    def data(self,d):
        self._data = d
        self.refresh_plot()

    def refresh_plot(self):
        self.graphWidget.clear()
        x_name = self.plot_config['x']
        if x_name == "acq#":
            x_index = -1
            x = list(range(1,len(self._data)+1))
        else:
            x_index = self._data_headers.index(x_name)
            x = [row[x_index] for row in self._data]

        for y_name in self.plot_config['y']:
            y_index = self._data_headers.index(y_name)
            y = [row[y_index] for row in self._data]
            self.graphWidget.setLabel('bottom', x_name ,**self._style_labels)
            #self.dataplot.setData(x,y)
            index_style = y_index%len(self._styles)
            self.graphWidget.plot(x,y,  name=y_name,    pen=self._styles[index_style],    symbol=self._symbol,    symbolBrush=self._colors[index_style])
            self.graphWidget.addLegend()
 