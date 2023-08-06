from PyQt5 import QtGui, QtCore, QtWidgets
from ..GeneratedUiElements.flashdialog import Ui_FlasherDialog


class FlasherDialog(QtWidgets.QDialog, Ui_FlasherDialog):

    def __init__(self, parent=None):
        Ui_FlasherDialog.__init__(self)
        QtWidgets.QDialog.__init__(self, parent=parent)
        self.setupUi(self)
        self.logoLabel.setColor(0, 38, 92)
        self.logoLabel.setSvgResource('logo_white')
