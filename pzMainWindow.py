
import os
import platform
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
# import helpform
# import newimagedlg
# import qrc_resources
__version__ = "1.0.0"

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.image = QImage()
        self.dirty = False
        self.filename = None
        self.mirroredvertically = False
        self.mirroredhorizontally = False

        self.imageLabel = QLabel()
        self.imageLabel.setMinimumSize = (200, 200)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.setCentralWidget(self.imageLabel)

        logDockWidget = QDockWidget("Log", self)
        logDockWidget.setObjectName("LogDockWidget")
        logDockWidget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.listWidget = QListWidget()
        logDockWidget.setWidget(self.listWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, logDockWidget)

        self.printer = None

        self.sizeLabel = QLabel()
        self.sizeLabel.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.addPermanentWidget(self.sizeLabel)
        status.showMessage("Ready", 5000)

        fileNewAction = QAction(QIcon("icons/filenew.png"), "&New", self)
        fileNewAction.setShortcut(QKeySequence.New)
        helpText = "Create new image"
        fileNewAction.setToolTip(helpText)
        fileNewAction.setStatusTip(helpText)
        self.connect(fileNewAction, SIGNAL("triggered()"), self.fileNew)
        fileMenu.addAction(fileNewAction)
        fileToolbar.addAction(fileNewAction)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setOrganizationName("Qtrac Ltd.")
    app.setOrganizationDomain("qtrac.com")
    app.setApplicationName("Image Changer")
    # app.setWindowIcon(QIcon(":/icon.png"))
    form = MainWindow()
    form.show()
    app.exec_()
