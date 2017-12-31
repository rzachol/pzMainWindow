
import os
import platform
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
# import helpform
# import newimagedlg
import qrc_resources
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

        # Build "File" menu
        fileNewAction = self.createAction("&New", self.fileNew,
                                          QKeySequence.New, "filenew",
                                          "Create an image file")
        fileOpenAction = self.createAction("&Open", self.fileOpen, QKeySequence.Open,
                                           "fileopen", "Open file")
        fileSaveAction = self.createAction("&Save", self.fileSave, QKeySequence.Save,
                                           "filesave", "Save file")
        fileSaveAsAction = self.createAction("Save &As", self.fileSaveAs, QKeySequence.SaveAs,
                                             "filesaveas", "Save file as ...")
        filePrintAction = self.createAction("&Print", self.filePrint,
                                            QKeySequence.Print, "fileprint", "Print file")
        fileQuitAction = self.createAction("&Quit", self.close, "Ctrl+Q",
                                            "filequit", "Close the application")
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenuActions = (fileNewAction, fileOpenAction, fileSaveAction, None,
                                fileSaveAsAction, filePrintAction, fileQuitAction)
        self.addActions(self.fileMenu, self.fileMenuActions)
        self.connect(self.fileMenu, SIGNAL("aboutToShow()"), self.updateFileMenu)

        # Build "Edit" menu
        editZoomAction = self.createAction("&Zoom...", self.editZoom, "Alt+Z",
                                           "editzoom", "Zoom the image")
        editInvertAction = self.createAction("&Invert", self.editInvert,
                                             "Ctrl+I", "editinvert",
                                             "Invert the image's colors",
                                             True, "toggled(bool)")
        editSwapRedAndBlueAction = self.createAction("&Swap red and blue", self.editSwapRedAndBlue,
                                             "Ctrl+B", "editswap",
                                             "Swap red and blue colors",
                                             True, "toggled(bool)")

        mirrorGroup = QActionGroup(self)
        editUnMirrorAction = self.createAction("&Unmirror", self.editUnMirror,
                                               "Ctrl+U", "editunmirror",
                                               "Unmirror the image", True,
                                               "toggled(bool)")
        editMirrorVertAction = self.createAction("&Mirror Vertically",
                                                 self.editMirrorVert,
                                                 "Ctrl+V",
                                                 "editmirrorvert",
                                                 "Mirror the image vertically",
                                                 True, "toggled(bool)")
        editMirrorHorizAction = self.createAction("&Mirror Horizontally",
                                                  self.editMirrorHoriz,
                                                  "Ctrl+M",
                                                  "editmirrorhoriz",
                                                  "Mirror the image horizontally",
                                                  True, "toggled(bool)")
        mirrorGroup.addAction(editUnMirrorAction)
        mirrorGroup.addAction(editMirrorVertAction)
        mirrorGroup.addAction(editMirrorHorizAction)
        editUnMirrorAction.setChecked(True)

        editMenu = self.menuBar().addMenu("&Edit")
        self.addActions(editMenu, (editInvertAction, editSwapRedAndBlueAction, editZoomAction))
        mirrorMenu = editMenu.addMenu(QIcon(":/editmirror.png"), "&Mirror")
        self.addActions(mirrorMenu, (editUnMirrorAction, editMirrorHorizAction, editMirrorVertAction))

        # Add "Help" menu
        helpAboutAction = self.createAction("&About", self.helpAbout)
        helpHelpAction = self.createAction("&Help", self.helpHelp, QKeySequence.HelpContents)
        helpMenu = self.menuBar().addMenu("&Help")
        self.addActions(helpMenu, (helpAboutAction, helpHelpAction))

        # Add "File" toolbar
        fileToolbar = self.addToolBar("File")
        fileToolbar.setObjectName("FileToolBar")
        self.addActions(fileToolbar, (fileNewAction, fileOpenAction, fileSaveAction, fileSaveAsAction))

        # Add "Edit" toolbar
        editToolBar = self.addToolBar("Edit")
        editToolBar.setObjectName("EditToolBar")
        self.addActions(editToolBar, (editInvertAction, editSwapRedAndBlueAction, editUnMirrorAction,
                                      editMirrorVertAction, editMirrorHorizAction))
        self.zoomSpinBox = QSpinBox()
        self.zoomSpinBox.setRange(1, 400)
        self.zoomSpinBox.setSuffix(" %")
        self.zoomSpinBox.setValue(100)
        self.zoomSpinBox.setToolTip("Zoom the image")
        self.zoomSpinBox.setStatusTip(self.zoomSpinBox.toolTip())
        self.zoomSpinBox.setFocusPolicy(Qt.NoFocus)
        self.connect(self.zoomSpinBox, SIGNAL("valueChanged(int)"), self.showImage)
        editToolBar.addWidget(self.zoomSpinBox)

        # Add context menu to the imageLabel widget
        separator = QAction(self)       # QLabel object doesn't change "None" action into separator
        separator.setSeparator(True)
        self.addActions(self.imageLabel, (editInvertAction, editSwapRedAndBlueAction, separator,
                                          editUnMirrorAction, editMirrorVertAction, editMirrorHorizAction))

        # initial state when new image loaded:
        self.resetableActions = ((editInvertAction, False), (editSwapRedAndBlueAction, False),
                                 (editUnMirrorAction, True))

        settings = QSettings()
        self.recentFiles = settings.value("RecentFiles") or []
        self.restoreGeometry(settings.value("MainWindow/Geometry", QByteArray()))
        self.restoreState(settings.value("MainWindow/State", QByteArray()))
        self.setWindowTitle("Image Changer")
        self.updateFileMenu()
        QTimer.singleShot(0, self.loadInitialFile)
    # end of __init__(self) declaration

    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def fileNew(self):
        pass

    def fileOpen(self):
        pass

    def fileSave(self):
        pass

    def fileSaveAs(self):
        pass

    def filePrint(self):
        pass

    def fileQuit(self):
        pass

    def editZoom(self):
        pass

    def editInvert(self):
        pass

    def editSwapRedAndBlue(self):
        pass

    def editUnMirror(self):
        pass

    def editMirrorVert(self):
        pass

    def editMirrorHoriz(self):
        pass

    def helpAbout(self):
        pass

    def helpHelp(self):
        pass

    def updateFileMenu(self):
        pass

    def showImage(self):
        pass

    def loadInitialFile(self):
        pass


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("Qtrac Ltd.")
    app.setOrganizationDomain("qtrac.com")
    app.setApplicationName("Image Changer")
    app.setWindowIcon(QIcon(":/icon.png"))
    form = MainWindow()
    form.show()
    app.exec_()

main()