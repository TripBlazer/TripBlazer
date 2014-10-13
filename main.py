import sys,os

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from view import MainWindow


def main():
    app = QApplication(sys.argv)
    
    mainwindow = MainWindow()
    mainwindow.layout()
    

    sys.exit(app.exec_())
    


if __name__=="__main__":
    main()