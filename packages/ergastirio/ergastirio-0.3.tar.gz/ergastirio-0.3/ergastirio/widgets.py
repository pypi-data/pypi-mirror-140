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
        self.resizeColumnsToContents()

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
        self.resizeRowsToContents()
        self.scrollToBottom()


class PlotObject:
    _data_headers =[]
    _data = []
    _colors = 'bgrcmyw'
    _styles = [pg.mkPen(c, width=2, style=QtCore.Qt.SolidLine) for c in _colors]
    _symbol = 'o'
    _style_labels = {"color": "#fff", "font-size": "20px"}
    def __init__(self, app, mainwindow, parent, data_headers, plot_config):
        '''
        app           = The pyqt5 QApplication() object
        mainwindow    = Main Window of the application
        parent        = a QWidget (or QMainWindow) object that will be the parent for this plot
        data_headers
        plot_config   = a dictionary specifying the settings of this plot. The dictionary must contain at least two keys, 'x' and 'y'. 
                        The value of 'x' must be a single string. The value of 'y' can be either a string or a list of strings.
        '''
        self.mainwindow = mainwindow
        self.app = app
        self.parent = parent
        self.data_headers = data_headers #Note: here we assume that data_headers do not already contain the "acq#" field. It will be added dynamically by counting the number of rows
        self.plot_config = plot_config

        self.Max = 0 #Keep track of the maximum of minimum values plotted in this plot (among all possible curves). It is used for resizing purposes
        self.Min = 0

        #self.PlotErrorBars_var = tk.IntVar(value=1) #This TK variable keeps track of wheter the user wants to plot the errorbars or not

        self.graphWidget = self.create_plot()
        self.controlWidget = self.create_controlPanel()

        vbox = Qt.QVBoxLayout()
        vbox.addWidget(self.graphWidget) 
        vbox.addWidget(self.controlWidget) 
        vbox.setSpacing(0)
        #vbox.addStretch(1)
        self.parent.setLayout(vbox)

        self.set_quantities_to_plot() #This will initialize axis and legend of the plot based on the current value of self.plot_config
        self.refresh_plot()
    
    @property
    def data_headers(self):
        return self._data_headers
    @data_headers.setter
    def data_headers(self,h):
        self._data_headers = h
        self._data_headers_full = h.copy()
        self._data_headers_full.insert(0,"acq#")
        self._data_headers_full_radiobuttons_x_axis =[] # these two lists will store the radiobuttons and checkbox used to decide which quantity is plotted 
        self._data_headers_full_checkboxs_y_axis =[]    # on x and y axis. Each element of self._data_headers_full is associated to one radiobutton and one checkbox

    @property
    def data(self):
        return self._data
    @data.setter
    def data(self,d):
        self._data = d
        self.refresh_plot()

    ### GUI

    def create_plot(self):
        graphWidget = pg.PlotWidget()
        graphWidget.showGrid(x=True, y=True)
        #graphWidget.setMenuEnabled(False)
        return graphWidget

    def create_controlPanel(self):
        w = Qt.QWidget()
        hbox = Qt.QHBoxLayout()
        w.button_home = Qt.QPushButton("")
        w.button_home.setIcon(QtGui.QIcon(os.path.join(graphics_dir,'home.png')))
        w.button_home.setFixedSize( 40, 40)

        w.toolButton_X = Qt.QToolButton()
        w.toolButton_X.setText('X')
        w.toolButton_X.show()
        w.toolButton_X.setFixedSize( 40, 40)
        w.toolButton_Y = Qt.QToolButton()
        w.toolButton_Y.setText('Y')
        w.toolButton_Y.show()
        w.toolButton_Y.setFixedSize( 40, 40)
        self.create_menu_XY(w.toolButton_X,w.toolButton_Y)

        hbox.addWidget(w.button_home)
        hbox.addWidget(w.toolButton_X)
        hbox.addWidget(w.toolButton_Y)

        hbox.addStretch(1)
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)
        w.setLayout(hbox)
        return w

    def create_menu_XY(self,toolButton_X,toolButton_Y):
        #code inspired by an answer to https://stackoverflow.com/questions/34731826/keep-menu-open-after-clicking-on-the-button-it-is-launched-with
        toolMenuX = Qt.QMenu()
        toolMenuY = Qt.QMenu()
        self._data_headers_full_radiobuttons_x_axis = []
        self._data_headers_full_checkboxs_y_axis = []
        #self.radio_x = []
        for data_name in self._data_headers_full:
            radiobutton = Qt.QRadioButton(data_name,toolMenuX)
            radiobutton.value = data_name
            if data_name == self.plot_config['x']:
                radiobutton.setChecked(True)
            radiobutton.toggled.connect(lambda x,object=radiobutton: self.update_plotted_data('x',object))
            checkableAction = Qt.QWidgetAction(toolMenuX)
            checkableAction.setDefaultWidget(radiobutton)
            toolMenuX.addAction(checkableAction)
            self._data_headers_full_radiobuttons_x_axis.append(radiobutton)

            checkbox = Qt.QCheckBox(data_name,toolMenuY)
            checkbox.value = data_name
            if data_name in self.plot_config['y']:
                checkbox.setChecked(True)
            checkbox.stateChanged.connect(lambda: self.update_plotted_data('y'))
            checkableAction = Qt.QWidgetAction(toolMenuY)
            checkableAction.setDefaultWidget(checkbox)
            toolMenuY.addAction(checkableAction)
            self._data_headers_full_checkboxs_y_axis.append(checkbox)

            #radiobutton.setText(data_name)
            #if data_name == self.plot_config['x']:
            #    radiobutton.setChecked(True)
            #radiobutton.value= data_name
            #radiobutton.toggled.connect(self.click_radio_global_instrument)
            #vbox1.addWidget(radiobutton)
            #self.radio_x.append(radiobutton)

        toolButton_X.toolMenu = toolButton_X
        toolButton_Y.toolMenu = toolButton_Y
        toolButton_X.setMenu(toolMenuX)
        toolButton_Y.setMenu(toolMenuY)
        toolButton_X.setPopupMode(Qt.QToolButton.InstantPopup)
        toolButton_X.setStyleSheet('QToolButton::menu-indicator { image: none; }')
        toolButton_Y.setPopupMode(Qt.QToolButton.InstantPopup)
        toolButton_Y.setStyleSheet('QToolButton::menu-indicator { image: none; }')

    ### END GUI

    ### GUI Events Functions

    def update_plotted_data(self, axis, object = None):
        '''
        Based on the current values of the radiobuttons and checkbox in the toolbutton menu, it updates 
        the content of self.plot_config['x'] and self.plot_config['y']
        '''
        if axis == 'x':
            if object.isChecked() == True:
                self.plot_config['x'] = object.value #(need to implement this better)
        if axis == 'y':
            self.plot_config['y'] = []
            for checkbox in self._data_headers_full_checkboxs_y_axis:
                if checkbox.isChecked() == True:
                    self.plot_config['y'].append(checkbox.value)
        self.set_quantities_to_plot()
        self.refresh_plot()

    ### END GUI Events Functions

    def set_quantities_to_plot(self):
        '''
        Based on the content of self.plot_config, it updates the values of self.x_index and self.y_index .
        self.x_index corresponds to the column index of the self._data matrix which will be used as x-quantity
        self.y_index is a list of indices, corresponding to the columns of the self._data matrix which will be used as y-quantities
        '''
        self.x_name = self.plot_config['x'] 
        self.x_index = self._data_headers_full.index(self.x_name) - 1 #in the self._data_headers_full list, we have added the "acq#" element at the beginning
                                                                      #thus, we substract 1 to the index to match this index with the column index in self._data
        self.y_index =[]
        self.y_names = self.plot_config['y']
        for y_name in self.plot_config['y']:
            self.y_index.append(self._data_headers_full.index(y_name) - 1) #in the self._data_headers_full list, we have added the "acq#" element at the beginning
        return

    def refresh_plot(self):
        self.graphWidget.clear()
        self.graphWidget.addLegend()

        if self.x_index == -1:
            x = list(range(1,len(self._data)+1)) #if self.x_index=-1, then the data to use on x axis is the acquisition number. We build the x-data explicitly.
        else:
            x = [row[self.x_index] for row in self._data] #otherwise,  the data to use on x axis is one of the columns of self._data. We extract it.

        for i,y_index in enumerate(self.y_index):
            if y_index == -1:
                y = list(range(1,len(self._data)+1)) #if self.x_index=-1, then this specific y-data is the acquisition number. We build the ydata explicitly.
            else:
                y = [row[y_index] for row in self._data] #otherwise, this specific y-data is one of the columns of self._data. We extract it.

            self.graphWidget.setLabel('bottom', self.x_name ,**self._style_labels)
            #self.dataplot.setData(x,y)
            index_style = (y_index+1) % len(self._styles)
            try:
                self.graphWidget.plot(x,y,  name=self.y_names[i],    pen=self._styles[index_style],    symbol=self._symbol,    symbolBrush=self._colors[index_style])
            except Exception as e:
                print(f"An error occurred while trying to plot\n: {e}")
                return
            
 
