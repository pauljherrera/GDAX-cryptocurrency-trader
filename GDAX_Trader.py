# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 11:02:18 2017

@author: forex
"""

import sys
import pandas as pd
import datetime as dt

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QFrame, 
                             QSplitter, QStyleFactory, QApplication, QLabel, 
                             QPushButton, QCheckBox, QFileDialog, QLineEdit,
                             QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QTextCursor

from data_feeder import HistoricalDataFeeder, RealTimeFeeder
from strategy import DeviationStrategy
from trader import PaperTrader    


class GDAXGUI(QWidget):
    
    def __init__(self):
        super().__init__()
        self.product = 'BTC-USD'
        self.dataFeeder = RealTimeFeeder
        self.trader = PaperTrader()
        self.data = None
        self.period = 0
        self.EntryStd = 0
        self.ExitStd = 0
        
        self.initUI()
        
        
    def initUI(self):
        # Fonts
        font01 = QFont('Times New Roman')
        font01.setPointSize(15)
        
        # Set window background color
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

        # Main window layout
        hbox = QHBoxLayout(self)

        left = QFrame(self)
        left.setFrameShape(QFrame.StyledPanel)
 
        topright = QFrame(self)
        topright.setFrameShape(QFrame.StyledPanel)

        bottomright = QFrame(self)
        bottomright.setFrameShape(QFrame.StyledPanel)

        splitter1 = QSplitter(Qt.Vertical)
        splitter1.addWidget(topright)
        splitter1.addWidget(bottomright)

        splitter2 = QSplitter(Qt.Horizontal)
        splitter2.addWidget(left)
        splitter2.addWidget(splitter1)
        splitter2.setSizes([400, 600])

        hbox.addWidget(splitter2)
        self.setLayout(hbox)
        
        ## Product box
        productTitleHBox = HBox01(widget=Label01('Product'))
        BTCButton = Button01('BTC-USD', self)
        BTCButton.toggle()
        ETHButton = Button01('ETH-USD', self)
        LTCButton = Button01('LTC-USD', self)
                
        productButtonsHBox = QHBoxLayout()
        productButtonsHBox.addWidget(BTCButton)
        productButtonsHBox.addStretch(1)
        productButtonsHBox.addWidget(ETHButton)
        productButtonsHBox.addStretch(1)
        productButtonsHBox.addWidget(LTCButton)

        productVBox = QVBoxLayout()
        productVBox.addStretch(1)
        productVBox.addLayout(productTitleHBox)
        productVBox.addLayout(productButtonsHBox)
        productVBox.addStretch(1)
     
        ## Data box
        dataFileButton = QPushButton('Choose data file')
        dataFileButton.setStyleSheet("margin-bottom: 30px; padding: 5px 20px")
        self.fileLabel = QLabel('File: ')
        self.fileLabel.setStyleSheet("margin-bottom: 30px; padding: 5px 5px")
        
        dataTitleHBox = HBox01(widget=Label01('Data'))
        RealCB = CheckBox01(RealTimeFeeder, 'Real time data')
        HistoricCB = CheckBox01(HistoricalDataFeeder, 'Historical data')
        RealCB.toggle()
        RealCB.subscribe(HistoricCB)
        HistoricCB.subscribe(RealCB)
        
        dataFileHBox = QHBoxLayout()
        dataFileHBox.addWidget(dataFileButton)
        dataFileHBox.addWidget(self.fileLabel)
        
        dataVBox = QVBoxLayout()
        dataVBox.addLayout(dataTitleHBox)
        dataVBox.addWidget(RealCB)
        dataVBox.addWidget(HistoricCB)
        dataVBox.addLayout(dataFileHBox)

        ## Strategy box
        startButton = QPushButton('START')
        startButton.setFont(font01)
        startButton.setStyleSheet("""
            margin-top: 30px; padding: 5px 20px; background-color: white;
            border: 3px solid blue;
        """)
        
        strategyLabel = Label01('Strategy')
        startHBox = HBox01(widget=startButton)

        strategyVBox = QVBoxLayout()
        strategyVBox.addLayout(HBox01(widget=strategyLabel))
        strategyVBox.addLayout(HBox02(label='Periods'))
        strategyVBox.addLayout(HBox02(label='Entry Standard Deviations'))
        strategyVBox.addLayout(HBox02(label='Exit Standard Deviations'))
        strategyVBox.addLayout(startHBox)

        # Left layout.
        leftVBox = QVBoxLayout(left)
        leftVBox.addLayout(productVBox)
        leftVBox.addLayout(dataVBox)
        leftVBox.addLayout(strategyVBox)
        leftVBox.addStretch(1)
        
                
        # Inconming data
        incomingLabel = Label01('Incoming data')
        self.incomingTextEdit = QTextEdit()
        self.incomingTextEdit.setReadOnly(True)
        self.incomingTextEdit.ensureCursorVisible()
        
        topRightVBox = QVBoxLayout(topright)
        topRightVBox.addLayout(HBox01(widget=incomingLabel))
        topRightVBox.addWidget(self.incomingTextEdit)
        
        # Trading signals
        incomingLabel = Label01('Trading signals')
        self.signalsTextEdit = QTextEdit()
        self.signalsTextEdit.setReadOnly(True)
        self.signalsTextEdit.ensureCursorVisible()
        
        topRightVBox = QVBoxLayout(bottomright)
        topRightVBox.addLayout(HBox01(widget=incomingLabel))
        topRightVBox.addWidget(self.signalsTextEdit)
        
        # Product events.
        BTCButton.clicked.connect(self.productClicked)            
        ETHButton.clicked.connect(self.productClicked)
        LTCButton.clicked.connect(self.productClicked)
        
        # Data events.
        RealCB.clicked.connect(self.dataBoxChecked)
        HistoricCB.clicked.connect(self.dataBoxChecked)
        dataFileButton.clicked.connect(self.fileButtonClicked)
        
        # Strategy events.
        ql01 = HBox02.QLineEditInstances['Periods']
        ql02 = HBox02.QLineEditInstances['Entry Standard Deviations']
        ql03 = HBox02.QLineEditInstances['Exit Standard Deviations']
        
        ql01.textChanged[str].connect(self.periodChange)
        ql02.textChanged[str].connect(self.entryStdChange)
        ql03.textChanged[str].connect(self.exitStdChange)
        
        # Start event.
        startButton.clicked.connect(self.start)
        
        # Window Size
        self.setGeometry(30, 30, 800, 600)
        self.setWindowTitle('GDAX Trader')
        self.show()
        
    def start(self):
        """
        Main function. Starts the backtester.
        """
                
        strategy = DeviationStrategy(self.period, self.entryStd, self.exitStd)
        try:
            feeder = self.dataFeeder(strategy, product=self.product)
            self.incomingTextEdit.insertPlainText("Openning communication with GDAX.\n")
        except TypeError:
            feeder = self.dataFeeder(strategy)
        strategy.subscribe(self.trader)
        
        dataReceiver = DataFeederReceiver(self)
        signalsReceiver = PaperTraderReceiver(self)
        feeder.subscribe(dataReceiver)
        self.trader.subscribe(signalsReceiver)
        
        try:
            feeder.start()
            self.incomingTextEdit.insertPlainText("Communication channel open. Waiting for new data.\n")
        except AttributeError:
            feeder.feed(self.data)
        

        
        
    def productClicked(self):
        sender = self.sender()
        # Toggle other buttons.
        for b in sender.__class__.instances:
            if b.isChecked() and (b != sender):
                b.toggle()
        
        # Set product.
        self.product = sender.text()
            
    def dataBoxChecked(self):
        sender = self.sender()
        # Toggling other check boxes.
        sender.publish()
        # Assigning DataFeeder to backtester.
        self.dataFeeder = sender.inObject
        print(self.dataFeeder)
        
    def fileButtonClicked(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', 'data_files/')
        fname = fname[0]
        if fname:
            self.data = pd.read_csv(fname, index_col=0)
            self.fileLabel.setText("File: {}".format(fname.split('/')[-1]))
    
    def periodChange(self, text):
        try:
            self.period = int(text)
        except ValueError:
            pass
        
    def entryStdChange(self, text):
        try:
            self.entryStd = float(text)
        except ValueError:
            pass
        
    def exitStdChange(self, text):
        try:
            self.exitStd = float(text)
        except ValueError:
            pass

# Widgets classes.

        
class Label01(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        font = QFont('Georgia')
        font.setPointSize(18)
        self.setFont(font)
        
class Button01(QPushButton):
    instances = []
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCheckable(True)
        font = QFont('Georgia')
        font.setPointSize(14)
        self.setFont(font)
        self.setStyleSheet("""
            QPushButton { 
                background-color: white;
                border: 3px solid blue;
                padding: 5px 20px;
                margin-bottom: 30px;
            }
            QPushButton:checked { 
                background-color: blue;
                color: white;
            }
        """)
        self.__class__.instances.append(self)

class HBox01(QHBoxLayout):
    def __init__(self, widget=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addStretch(1)
        self.addWidget(widget)
        self.addStretch(1)
        
class HBox02(QHBoxLayout):
    QLineEditInstances = {}
    
    def __init__(self, label='', *args, **kwargs):
        super().__init__(*args, **kwargs)
        font = QFont('Times New Roman')
        font.setPointSize(15)
        lab = QLabel(label)
        lab.setFont(font)
        self.addWidget(lab)
        ql = QLineEdit()
        self.addWidget(ql)
        self.__class__.QLineEditInstances.update({label: ql})
        
class CheckBox01(QCheckBox):
    def __init__(self, inObject, *args, **kwargs):
        super().__init__(*args, **kwargs)
        font = QFont('Times New Roman')
        font.setPointSize(15)
        self.setFont(font)
        self.inObject = inObject
        self.subscribers = []
    
    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)
    
    def publish(self):
        for s in self.subscribers:
            if s.isChecked():
                s.toggle()
        
# Helping classes:
class Receiver():
    def __init__(self, gui):
        self.gui = gui
    
    def receive(self, msg):
        raise NotImplementedError

class DataFeederReceiver(Receiver):
    def receive(self, msg):
        _time = dt.datetime.strptime(msg[0], "%Y-%m-%dT%H:%M:%S.%fZ")\
                           .replace(microsecond=0)
        self.gui.incomingTextEdit.moveCursor(QTextCursor.End)
        self.gui.incomingTextEdit.insertPlainText("{}   {}   {}\n"\
            .format(_time, round(float(msg[1]), 2), msg[2]))
#        print(msg)

class PaperTraderReceiver(Receiver):
    def receive(self, msg):
        self.gui.signalsTextEdit.moveCursor(QTextCursor.End)
        self.gui.signalsTextEdit.insertPlainText("{0}   {2}   {1}\n".format(*msg))
#        print(msg)
        
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    gui = GDAXGUI()
    sys.exit(app.exec_())