# UIScriptManager.py
import json
import imp, re
import sys, os
import inspect

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

# Custom Key
Qt.Key_Enter = 16777220

from functools import partial

from . import StyleSheetScriptManager
imp.reload(StyleSheetScriptManager)
UIStyle = StyleSheetScriptManager

from ...G_CPSystem.UtilPathManager import *
PathManager = PathManager()

# Local Variables
USER_NAME = os.environ["USERNAME"]
USER_HOME = PathManager.ConvertAbsPath(os.path.expanduser("~"))
USER_CODINGPANDA_SCRIPT_ENV_DIRECTORY = PathManager.ConvertAbsPath(USER_HOME + "/.codingPanda_script_env")

SCRIPT_ROOT_DIRECTORY = PathManager.ConvertAbsPath(USER_CODINGPANDA_SCRIPT_ENV_DIRECTORY + "/ScriptManager")
SCRIPT_ENV_FILE = PathManager.ConvertAbsPath(SCRIPT_ROOT_DIRECTORY + "/ScriptManager.env")

SCRIPT_LOCAL_PRESET_DIRECTORY = PathManager.ConvertAbsPath(SCRIPT_ROOT_DIRECTORY + "/preset")
SCRIPT_LOCAL_PRESET_DEFAULT_FILE = PathManager.ConvertAbsPath(SCRIPT_LOCAL_PRESET_DIRECTORY + "/default.json")

SCRIPT_SERVER = PathManager.ConvertAbsPath("/mofac/team/rig_cfx/__system__/script_bin/ScriptManager")
SCRIPT_SERVER_AUTHORITY = PathManager.ConvertAbsPath(SCRIPT_SERVER + "/authority.json")
SCRIPT_SERVER_PRESET_DIRECTORY = PathManager.ConvertAbsPath(SCRIPT_SERVER + "/preset")
SCRIPT_SERVER_PRESET_DEFAULT_FILE = PathManager.ConvertAbsPath(SCRIPT_SERVER_PRESET_DIRECTORY + "/default.json")

class mainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        
        super(mainWindow, self).__init__(parent)
        
        # self.attributes
        self.mousePosX = QCursor.pos().x()
        self.mousePosY = QCursor.pos().y()
        self.currentHierarchy = dict()
        self.authority = self.GetAuthority()
        self.childrenUI = list()
        self.executerQPBs = list()
        self.widgetInfo = dict()        

        # self.attributes in dynamic
        self.deleteWidgetFullNames = list()
        
        # UI
        self.setWindowTitle("ScriptManager")
        
        self.centralQW = QWidget()        
        self.setCentralWidget(self.centralQW)
        
        self.titleQLB = QLabel("Script Manager")
        self.titleQLB.setAlignment(Qt.AlignCenter)
        self.titleQHBL = QHBoxLayout()
        self.titleQHBL.addWidget(self.titleQLB)

        self.authorityQLB = QLabel("")
        self.UpdateAuthorityQLB()
        self.authorityQHBL = QHBoxLayout()
        self.authorityQHBL.setAlignment(Qt.AlignCenter)
        self.authorityQHBL.addWidget(self.authorityQLB)

        self.rootTabQTW  = QTabWidget()
        self.rootTabQVBL = QVBoxLayout()
        self.rootTabQVBL.addWidget(self.rootTabQTW)
        self.rootTabQTB = self.rootTabQTW.tabBar()

        self.localTabQTW = QTabWidget()
        self.localTabQTW.setTabsClosable(True)
        self.localTabQVBL = QVBoxLayout(self.localTabQTW)
        self.localTabQVBL.setAlignment(Qt.AlignTop)
        self.rootTabQTW.addTab(self.localTabQTW, "Local")

        self.localTabQTB = self.localTabQTW.tabBar()
        self.localTabQTB.setMovable(True)
        self.localTabQTB.setUsesScrollButtons(True)
        self.localTabNewQPB = QPushButton("+")
        self.localTabQTW.setCornerWidget(self.localTabNewQPB, Qt.TopRightCorner)

        self.serverTabQTW = QTabWidget()
        self.serverTabQVBL = QVBoxLayout(self.serverTabQTW)
        self.serverTabQVBL.setAlignment(Qt.AlignTop)
        self.rootTabQTW.addTab(self.serverTabQTW, "Server")
        self.serverTabQTB = self.serverTabQTW.tabBar()
        self.serverTabQTB.setUsesScrollButtons(True)

        self.localTabMainQW = QWidget()
        self.localTabMainQVBL = QVBoxLayout(self.localTabMainQW)
        self.localTabMainQVBL.setAlignment(Qt.AlignTop)        
        self.localTabQTW.addTab(self.localTabMainQW, "Main")
        
        self.exitQPB = QPushButton("Exit")
        self.defaultBtnQHBL = QHBoxLayout()
        self.defaultBtnQHBL.addWidget(self.exitQPB)
        
        self.mainLayout = QVBoxLayout(self.centralQW)
        self.mainLayout.addLayout(self.titleQHBL)
        self.mainLayout.addLayout(self.authorityQHBL)
        self.mainLayout.addLayout(self.rootTabQVBL)
        self.mainLayout.addLayout(self.defaultBtnQHBL)

        # LOCATOR:: Debug
        self.debugQPB = QPushButton("Debug")
        self.debugQHBL = QHBoxLayout()
        self.debugQHBL.addWidget(self.debugQPB)
        # self.mainLayout.addLayout(self.debugQHBL)
        
        # MenuBar
        self.importQA = QAction("Import Script", self)
        self.saveQA = QAction("Save", self)
        self.loadQA = QAction("Load", self)
        self.updateQA = QAction("Update", self)
        self.publishQA = QAction("Publish", self)
        
        mainMenuBar = self.menuBar()
        mainMenuFile = mainMenuBar.addMenu("File")
        mainMenuFile.addAction(self.importQA)
        mainMenuFile.addSeparator().setText("Local")
        mainMenuFile.addAction(self.saveQA)
        mainMenuFile.addAction(self.loadQA)
        mainMenuFile.addSeparator().setText("Server")
        mainMenuFile.addAction(self.updateQA)
        mainMenuFile.addAction(self.publishQA)

        # Set StyleSheet
        self.titleQLB.setStyleSheet(UIStyle.mainWindow.titleQLB)
        
        self.resize(512,768)
        self.move(self.mousePosX, self.mousePosY)

        self.__connect__()
        self.__triggered__()

        # post - initSetting
        self.LoadPresetDefault()

        # self.AddWidgetQuery(pWidget, widgetText="", rootTabText="", childrenTabText="", executeButtonText="")
        self.AddWidgetInfo(self.serverTabQTW, rootTabText="Server")
        self.AddWidgetInfo(self.localTabQTW, rootTabText="Local")
        self.AddWidgetInfo(self.localTabMainQW, rootTabText="Local", childrenTabText="Main")

        # post - Attributes         
        self.currentRootTabWidget = None
        self.currentRootTabText     = None
        self.currentActivatedTabWidget = None
        self.currentActivatedTabText     = None
        self.GetCurrentTabActivated()
        
    def __connect__(self):
        self.localTabQTW.currentChanged.connect(self.__connect__tabCurrentChanged)
        self.localTabQTW.tabCloseRequested.connect(self.__connect__tabRemoved)
        self.localTabQTB.tabMoved.connect(self.__connect__localTabMoved)
        self.localTabNewQPB.clicked.connect(partial(self.__connect__addNewTab, self.localTabQTW))

        self.serverTabQTW.currentChanged.connect(self.__connect__tabCurrentChanged)

        self.exitQPB.clicked.connect(self.__connect__exit)

        self.debugQPB.clicked.connect(self.__connect__debug)

    def __connect__localTabMoved(self):
        self.UpdateWidgetInfo()

    def __connect__tabRemoved(self, index):

        fullName = self.GetTabFullName(self.currentRootTabText, self.currentRootTabWidget.tabText(index))

        self.localTabQTW.removeTab(index)

        self.RemoveWidgetInfo(fullName)

    def __connect__tabInserted(self):
        self.GetIndexOfCreateTab()

    def __connect__tabCurrentChanged(self):
        self.UpdateCurrentTabActivated()

    def __connect__addNewTab(self, pTabWidget):
        self.CreateNewTab(pTabWidget)

    def __connect__exit(self):
        self.close()
        del(self)
        
    def __connect__debug(self):
        saveLog = self.CreateSaveLog()
        for fullName in saveLog:
            print(fullName, saveLog[fullName])

    def __connect__rejected(self):
        del(self)

    def __triggered__(self):
        self.importQA.triggered.connect(self.__triggered__importQA)
        self.saveQA.triggered.connect(self.__triggered__saveLocalPresetQA)
        self.loadQA.triggered.connect(self.__triggered__loadLocalPresetQA)
        self.updateQA.triggered.connect(self.__triggered__updateServerQA)
        self.publishQA.triggered.connect(self.__triggered__saveServerQA)

    def __triggered__saveLocalPresetQA(self):

        self.UpdateCurrentTabActivated()
        self.SavePresetToLocal()

    def __triggered__loadLocalPresetQA(self):

        initDirectory = USER_HOME
        if os.path.exists(SCRIPT_LOCAL_PRESET_DIRECTORY):
            initDirectory = SCRIPT_LOCAL_PRESET_DIRECTORY

        presetJsonFilePath = QFileDialog.getOpenFileName(parent=None, caption="Load Preset Json File",
                                                                                                    dir=initDirectory, filter="Json (*.json)")[0]

        if not presetJsonFilePath:
            return False

        self.LoadPreset(presetJsonFilePath)

        return True

    def __triggered__saveServerQA(self):

        self.UpdateCurrentTabActivated()
        self.SavePresetToServer()

    def __triggered__updateServerQA(self):

        self.LoadPresetServerDefault()
        
    def __triggered__importQA(self):

        if self.DenyAccessToServer():
            return False

        _ImportScriptQDG = ImportScriptQDG(self)
        _ImportScriptQDG.show()

    def __update__mainWindowTabQTW(self):
        pass

    def keyPressEvent(self, keyEvent):
        if keyEvent.key() == Qt.Key_Escape:
            self.exitQPB.click()

    def UpdateAuthorityQLB(self):

        if self.authority == "GLOBAL":
            self.authorityQLB.setText("Authority : Script Author")            
        elif self.authority and self.authority != "GLOBAL":
            self.authorityQLB.setText("Authority : {} Team Manager".format(self.authority))
        else:
            self.authorityQLB.setText("Authority : User")

        return True

    def UpdateCurrentTabActivated(self):
        self.currentRootTabWidget = self.rootTabQTW.currentWidget()
        self.currentRootTabText = self.rootTabQTW.tabText(self.rootTabQTW.currentIndex())

        self.currentActivatedTabWidget = self.currentRootTabWidget.currentWidget()
        self.currentActivatedTabText = self.currentRootTabWidget.tabText(self.currentRootTabWidget.currentIndex())

        return True

    def RemoveWidgetInfo(self, fullName):
        
        removes = list()
        for fn in self.widgetInfo:
            if fn.startswith(fullName):
                removes.append(fn)

        for remove in removes:
            del(self.widgetInfo[remove]["pointer"])
            self.widgetInfo.pop(remove)

        return True

    def UpdateIndexOfCreateTab(self):
        self.localTabCreateIndex = self.localTabQTW.indexOf(self.localTabNewQW)
        self.serverTabCreateIndex = self.serverTabQTW.indexOf(self.serverTabNewQW)

    def GetTabFullName(self, rootTabText="", childrenTabText=""):
        if childrenTabText:
            return "{}:{}".format(rootTabText, childrenTabText)
        else:
            return "{}".format(rootTabText)

    def GetIndexOfCreateTab(self):
        self.UpdateIndexOfCreateTab()
        return dict(local=self.localTabCreateIndex, server=self.serverTabCreateIndex)

    def GetCurrentTabActivated(self):
        self.UpdateCurrentTabActivated()

        return (self.currentRootTabWidget, self.currentRootTabText,
                      self.currentActivatedTabWidget, self.currentActivatedTabText)

    def GetLocalTabChildren(self):
        return self.GetCurrentChildrenTab(self.localTabQTW)

    def GetServerTabChildren(self):
        return self.GetCurrnetChildrenTab(self.serverTabQTW)

    def GetCurrentChildrenTab(self, pParentQTW):
        tabs = list()
        for idx in range(pParentQTW.count()):
            tabs.append(pParentQTW.tabText(idx))

        return tabs

    def CreateNewExecuteButton(self, rootTabText, childrenTabPointer, childrenTabText,
                                                        label, iconPath, scriptFilePath):

        self.UpdateCurrentTabActivated()

        cmds = self.GetExecuteCommands(scriptFilePath)

        executeButton = QPushButton(label)
        if iconPath:
            executeButton.setIcon(QIcon(iconPath))
        executeButton.clicked.connect(partial(self.GetCallBackFunction, cmds))

        childrenTabPointer.layout().addWidget(executeButton)

        _widgetInfo = self.AddWidgetInfo(executeButton, executeButtonText=label, 
                                                                    rootTabText=rootTabText, childrenTabText=childrenTabText)

        self.widgetInfo[_widgetInfo[0]]["iconPath"] = iconPath
        self.widgetInfo[_widgetInfo[0]]["scriptFilePath"] = scriptFilePath

        return executeButton

    def AddWidgetInfo(self, pWidget, rootTabText="", childrenTabText="", executeButtonText=""):

        _fullName = self.CreateFullName(rootTabText, childrenTabText, executeButtonText)
        _pointer = pWidget

        if not self.widgetInfo.get(_fullName, False):
            self.widgetInfo[_fullName] = dict()

        self.widgetInfo[_fullName]["pointer"] = _pointer

        return (_fullName, _pointer)

    def CreateNewTab(self, pTabWidget):
        createNewTabQDG = CreateNewTabQDG(pTabWidget, self)
        createNewTabQDG.show()

    def CreateFullName(self, rootTabText="", childrenTabText="", executeButtonText=""):
        _fullName = ""
        if rootTabText:
            _fullName = "{}".format(rootTabText)
        if childrenTabText:
            _fullName = _fullName + ":{}".format(childrenTabText)
        if executeButtonText:
            _fullName = _fullName + ":{}".format(executeButtonText)

        return _fullName

    def GetExecuteCommands(self, scriptFilePath):

        scriptDirs = PathManager.GetListFromAbsPath(scriptFilePath)

        scriptFile = scriptDirs[-1]
        scriptFileExt = os.path.splitext(scriptFile)[1].replace(".", "")
        scriptFileName = os.path.splitext(scriptFile)[0]

        scriptParentDir = scriptDirs[-2]
        scriptAncestorDirs = scriptDirs[:-2]

        scriptAncestorPath = ""
        for scriptAncestorDir in scriptAncestorDirs:
            scriptAncestorPath = os.path.join(scriptAncestorPath, scriptAncestorDir)

        scriptAncestorPath = PathManager.ConvertAbsPath(scriptAncestorPath)
        if scriptAncestorPath not in sys.path:
            sys.path.append(scriptAncestorPath)

        cmds = ""
        cmds += "import imp;"
        cmds += "from {spd} import {sfn};".format(spd=scriptParentDir, sfn=scriptFileName)
        cmds += "imp.reload({sfn});".format(sfn=scriptFileName)

        return cmds

    def GetCallBackFunction(self, cmds):

        exec(cmds)

        return True

    def GetAuthority(self):

        with open(SCRIPT_SERVER_AUTHORITY) as authority:
            aboutAuthority = json.load(authority)

        authority = None

        for team in aboutAuthority:
            if USER_NAME in aboutAuthority[team]:
                authority = team
                break

        return authority

    def ImportScript(self, label, iconPath, scriptFilePath):

        self.UpdateCurrentTabActivated()

        self.CreateNewExecuteButton(self.currentRootTabText, self.currentActivatedTabWidget,
                                                            self.currentActivatedTabText, label, iconPath, scriptFilePath)

        return False

    def SavePreset(self, jsonFilePath, jsonObject):

        savePresetJsonDirectoryPath = PathManager.ConvertAbsPath(PathManager.GetListFromAbsPath(jsonFilePath)[:-1])        
        PathManager.CreateDirectoryTree(savePresetJsonDirectoryPath)        

        with open(jsonFilePath, 'w') as presetJsonFile:
            json.dump(jsonObject, presetJsonFile, indent=2)

        return True

    def SavePresetToServer(self):

        self.UpdateCurrentTabActivated()
        
        if self.DenyAccessToServer():
            return False

        saveLog = None
        with open(SCRIPT_SERVER_PRESET_DEFAULT_FILE) as default:
            saveLog = json.load(default)

        _saveLog = self.CreateSaveLog()
        prefix = "Server:{team}".format(team=self.authority)
        for fullName in _saveLog:
            if fullName.startswith(prefix):
                saveLog[fullName] = _saveLog[fullName]

        self.SavePreset(SCRIPT_SERVER_PRESET_DEFAULT_FILE, saveLog)

        return True

    def SavePresetToLocal(self):

        self.UpdateCurrentTabActivated()

        saveLog = dict()

        _saveLog = self.CreateSaveLog()
        for fullName in _saveLog:

            if fullName.startswith("Local"):
                saveLog[fullName] = _saveLog[fullName]

        savePresetQDG = SavePresetQDG(self, saveLog)
        savePresetQDG.show()

        return True

    def CreateSaveLog(self):

        self.UpdateCurrentTabActivated()

        saveLog = dict()
        for fullName in self.widgetInfo:

            saveLog[fullName] = dict()

            for attr in self.widgetInfo[fullName]:

                if attr == "pointer" or attr == "query":
                    continue

                saveLog[fullName][attr] = self.widgetInfo[fullName][attr]

        return saveLog

    def LoadPresetLocalDefault(self):

        if not os.path.exists(SCRIPT_LOCAL_PRESET_DEFAULT_FILE):
            return False

        self.LoadPreset(SCRIPT_LOCAL_PRESET_DEFAULT_FILE)

        self.rootTabQTW.setCurrentWidget(self.localTabQTW)
        self.localTabQTW.setCurrentIndex(0)

        return True

    def LoadPresetServerDefault(self):

        if not os.path.exists(SCRIPT_SERVER_PRESET_DEFAULT_FILE):
            return False

        self.LoadPreset(SCRIPT_SERVER_PRESET_DEFAULT_FILE)

        self.rootTabQTW.setCurrentWidget(self.serverTabQTW)
        self.serverTabQTW.setCurrentIndex(0)

        return True

    def LoadPresetDefault(self):

        self.LoadPresetLocalDefault()
        self.LoadPresetServerDefault()

        self.rootTabQTW.setCurrentWidget(self.localTabQTW)
        self.localTabQTW.setCurrentIndex(0)        

    def LoadPreset(self, jsonFilePath):
        
        # Load Preset.json
        with open(jsonFilePath) as jsonFile:
            saveLog = json.load(jsonFile)

        if not saveLog:
            return False

        widgetInfo = self.widgetInfo
        depthList = [[],[],[]]
        for fullName in saveLog:
            hierarchy = fullName.split(":")
            depth         = len(hierarchy) - 1
            depthList[depth].append(fullName)

        for fullName in depthList[0]:
            widgetInfo[fullName] = saveLog[fullName]
            if fullName == "Local":
                widgetInfo[fullName]["pointer"] = self.localTabQTW
            elif fullName == "Server":
                widgetInfo[fullName]["pointer"] = self.serverTabQTW

            # Temp
            widgetInfo[fullName]["pointer"].clear()

        for fullName in depthList[1]:
            hierarchy = fullName.split(":")
            widgetInfo[fullName] = saveLog[fullName]
            widgetInfo[fullName]["pointer"] = self.CreateChildrenTab(hierarchy[1], widgetInfo[hierarchy[0]]["pointer"])

        for fullName in depthList[2]:
            hierarchy = fullName.split(":")
            childrenTabFullName = self.CreateFullName(hierarchy[0],hierarchy[1])
            widgetInfo[fullName] = saveLog[fullName]
            widgetInfo[fullName]["pointer"] = self.CreateNewExecuteButton(hierarchy[0],
                                                                                                                                widgetInfo[childrenTabFullName]["pointer"],
                                                                                                                                hierarchy[1], hierarchy[2],
                                                                                                                                widgetInfo[fullName]["iconPath"],
                                                                                                                                widgetInfo[fullName]["scriptFilePath"])

        self.widgetInfo = widgetInfo

        return True

    def CreateChildrenTab(self, name, pRootTabWidget):

        childrenTabQW = QWidget()
        childrenTabQVBL = QVBoxLayout(childrenTabQW)
        childrenTabQVBL.setAlignment(Qt.AlignTop)

        pRootTabWidget.addTab(childrenTabQW, name)
        pRootTabWidget.setCurrentWidget(childrenTabQW)

        return childrenTabQW

    def DenyAccessToServer(self):

        self.UpdateCurrentTabActivated()

        if self.currentRootTabText == "Server":
            if self.authority == "GLOBAL":
                return False
            if self.authority != self.currentActivatedTabText or not self.authority:
                authorityWarning = AuthorityWarningQDG(self)
                authorityWarning.show()
                return True        

        return False

class ImportScriptQDG(QDialog):

    def __init__(self, parent=None):

        super(ImportScriptQDG, self).__init__(parent)

        # Attributes
        self.label = ""
        self.iconPath = ""
        self.scriptPath = ""

        # UI
        self.setWindowTitle("Create New ExecuterQPB")

        self.labelQLB = QLabel("Label")
        self.labelQLB.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.labelQLB.setMinimumWidth(64)
        self.labelQLB.setMaximumWidth(64)
        self.labelQLE = QLineEdit()
        self.labelQPB = QPushButton("Check")
        self.labelQHBL = QHBoxLayout()
        self.labelQHBL.setAlignment(Qt.AlignLeft)
        self.labelQHBL.addWidget(self.labelQLB)
        self.labelQHBL.addWidget(self.labelQLE)
        self.labelQHBL.addWidget(self.labelQPB)

        self.scriptQLB = QLabel("Sciprt")
        self.scriptQLB.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.scriptQLB.setMinimumWidth(64)
        self.scriptQLB.setMaximumWidth(64)
        self.scriptQLE = QLineEdit()
        self.scriptQPB = QPushButton("Find")
        self.scriptQHBL = QHBoxLayout()
        self.scriptQHBL.setAlignment(Qt.AlignLeft)
        self.scriptQHBL.addWidget(self.scriptQLB)
        self.scriptQHBL.addWidget(self.scriptQLE)
        self.scriptQHBL.addWidget(self.scriptQPB)

        self.iconQLB = QLabel("Icon")
        self.iconQLB.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.iconQLB.setMinimumWidth(64)
        self.iconQLB.setMaximumWidth(64)
        self.iconQLE = QLineEdit()
        self.iconQPB = QPushButton("Find")
        self.iconQHBL = QHBoxLayout()
        self.iconQHBL.setAlignment(Qt.AlignLeft)
        self.iconQHBL.addWidget(self.iconQLB)
        self.iconQHBL.addWidget(self.iconQLE)
        self.iconQHBL.addWidget(self.iconQPB)

        self.notifyQLB = QLabel("Enter Information of Button")
        self.notifyQLB.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.notifyQHBL = QHBoxLayout()
        self.notifyQHBL.setAlignment(Qt.AlignCenter)
        self.notifyQHBL.addWidget(self.notifyQLB)
        self.enterQPB = QPushButton("Enter")
        self.cancelQPB = QPushButton("cancel")
        self.buttonsQHBL = QHBoxLayout()
        self.buttonsQHBL.addWidget(self.enterQPB)
        self.buttonsQHBL.addWidget(self.cancelQPB)
        self.bottomQHBL = QHBoxLayout()
        self.bottomQHBL.addLayout(self.notifyQHBL)
        self.bottomQHBL.addLayout(self.buttonsQHBL)

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setAlignment(Qt.AlignTop)
        self.mainLayout.addLayout(self.labelQHBL)
        self.mainLayout.addLayout(self.scriptQHBL)
        self.mainLayout.addLayout(self.iconQHBL)
        self.mainLayout.addLayout(self.bottomQHBL)

        self.__connect__(parent)

        self.resize(512, self.sizeHint().height())

    def __connect__(self, parent=None):

        self.rejected.connect(self.__connect__rejected)

        self.scriptQPB.clicked.connect(self.__connect__scriptQPB)
        self.iconQPB.clicked.connect(self.__connect__iconQPB)
        self.enterQPB.clicked.connect(partial(self.__connect__enterQPB, parent))
        self.cancelQPB.clicked.connect(self.__connect__cancelQPB)

    def __connect__scriptQPB(self):

        scriptPath = QFileDialog.getOpenFileName(caption="Import Script", filter="Script (*.py *mel)")[0]

        self.scriptQLE.setText(scriptPath)

    def __connect__iconQPB(self):

        iconPath = QFileDialog.getOpenFileName(caption="Import Image", filter="Image File(*.jpeg *.png *tga)")[0]

        self.iconQLE.setText(iconPath)

    def __connect__enterQPB(self, parent):

        label = self.labelQLE.text()
        iconPath = self.iconQLE.text()
        scriptFilePath = self.scriptQLE.text()

        if not label:
            self.notifyQLB.setText("Please Enter Text ofLabel to Parameter")
        elif not scriptFilePath:
            self.notifyQLB.setText("Please Enter Path of ScriptFilePath to Parameter")
        else:
            parent.ImportScript(label, iconPath, scriptFilePath)
            self.close()

    def __connect__cancelQPB(self):
        self.close()
        del(self)

    def __connect__rejected(self):
        del(self)

    def keyPressEvent(self, keyEvent):
        if keyEvent.key() == Qt.Key_Escape:
            self.cancelQPB.click()
        elif keyEvent.key() == Qt.Key_Enter:
            self.enterQPB.click()

class CreateNewTabQDG(QDialog):

    def __init__(self, pTabWidget, parent=None):

        super(CreateNewTabQDG, self).__init__(parent)

        # Attributes
        self.mousePosX = QCursor.pos().x()
        self.mousePosY = QCursor.pos().y()
        self.centerFromCursorX = self.mousePosX - (self.sizeHint().width() / 2)
        self.centerFromCursorY = self.mousePosY - (self.sizeHint().height() / 2)

        # UI
        self.notifyMsgQLB   = QLabel("Enter New Tab's Name")
        self.notifyMsgQHBL = QHBoxLayout()
        self.notifyMsgQHBL.addWidget(self.notifyMsgQLB)

        self.nameQLB   = QLabel("Name")
        self.nameQLE   = QLineEdit()
        self.nameQHBL = QHBoxLayout()
        self.nameQHBL.addWidget(self.nameQLB)
        self.nameQHBL.addWidget(self.nameQLE)

        self.enterQPB      = QPushButton("Enter")
        self.cancelQPB    = QPushButton("Cancel")
        self.bottomQHBL  = QHBoxLayout()
        self.bottomQHBL.addWidget(self.enterQPB)
        self.bottomQHBL.addWidget(self.cancelQPB)

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addLayout(self.notifyMsgQHBL)
        self.mainLayout.addLayout(self.nameQHBL)
        self.mainLayout.addLayout(self.bottomQHBL)

        # Default Settings
        self.resize(256, 64)
        if parent:
            self.move(parent.pos().x() + (parent.size().width() / 2.0) - (self.size().width() / 2.0),
                              parent.pos().y() + (parent.size().height() / 2.0) - (self.size().height() / 2.0))

        # function
        self.__connect__(pTabWidget, parent)

    def __connect__(self, pTabWidget, parent):
        self.enterQPB.clicked.connect(partial(self.__connect__enterQPB, pTabWidget, parent))
        self.cancelQPB.clicked.connect(self.__connect__cancelQPB)

    def __connect__enterQPB(self, pTabWidget, parent):

        if self.CreateNewTab(pTabWidget, parent):
            self.close()
            del(self)

    def __connect__cancelQPB(self):
        self.close()
        del(self)

    def keyPressEvent(self, keyEvent):

        if keyEvent.key() == Qt.Key_Escape:
            self.close()
        elif keyEvent.key() == Qt.Key_Enter:
            if self.nameQLE.text():
                self.enterQPB.click()
            else:
                self.close()

    def CreateNewTab(self, pTabWidget, parent):

        newTabName = self.nameQLE.text()

        if newTabName in parent.GetCurrentChildrenTab(pTabWidget):
            self.notifyMsgQLB.setText("The Tab have same name is already existing")
            return False
        else:
            newTabQW = QWidget()
            newTabQVBL = QVBoxLayout(newTabQW)
            newTabQVBL.setAlignment(Qt.AlignTop)

            pTabWidget.addTab(newTabQW, newTabName)
            pTabWidget.setCurrentWidget(newTabQW)

            parent.UpdateCurrentTabActivated()
            parent.AddWidgetInfo(parent.currentActivatedTabWidget,
                                                    rootTabText=parent.currentRootTabText,
                                                    childrenTabText=parent.currentActivatedTabText)

            return True            

class SavePresetQDG(QDialog):

    def __init__(self, parent=None, jsonObject=dict()):

        super(SavePresetQDG, self).__init__(parent)

        self.titleQLB = QLabel("Save Current Setting as New Preset")
        self.titleQLB.setStyleSheet(UIStyle.SavePresetQDG.titleQLB)
        self.titleQHBL = QHBoxLayout()
        self.titleQHBL.setAlignment(Qt.AlignCenter)
        self.titleQHBL.addWidget(self.titleQLB)

        self.presetFilePathQLB = QLabel("File")
        self.presetFilePathQLB.setMaximumWidth(64)
        self.presetFilePathQLE = QLineEdit()
        self.presetFilePathQLE.setText(SCRIPT_LOCAL_PRESET_DIRECTORY)
        self.presetFilePathQPB = QPushButton("Select")
        self.presetFilePathQPB.setMaximumWidth(64)
        self.presetFilePathQHBL = QHBoxLayout()
        self.presetFilePathQHBL.setAlignment(Qt.AlignLeft)
        self.presetFilePathQHBL.addWidget(self.presetFilePathQLB)
        self.presetFilePathQHBL.addWidget(self.presetFilePathQLE)
        self.presetFilePathQHBL.addWidget(self.presetFilePathQPB)

        self.saveQPB = QPushButton("Save")
        self.cancelQPB = QPushButton("Cancel")
        self.bottomQHBL = QHBoxLayout()
        self.bottomQHBL.addWidget(self.saveQPB)
        self.bottomQHBL.addWidget(self.cancelQPB)

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addLayout(self.titleQHBL)
        self.mainLayout.addLayout(self.presetFilePathQHBL)
        self.mainLayout.addLayout(self.bottomQHBL)

        # post - initialSetting
        self.resize(640, 128)

        self.__connect__(parent, jsonObject)

    def __connect__(self, parent, jsonObject):
        self.rejected.connect(self.__connect__rejected)
        self.presetFilePathQPB.clicked.connect(self.__connect__presetFilePathQPB)
        self.saveQPB.clicked.connect(partial(self.__connect__saveQPB, jsonObject))
        self.cancelQPB.clicked.connect(self.__connect__cancelQPB)

    def __connect__rejected(self):
        del(self)

    def __connect__presetFilePathQPB(self):

        initDirectory = USER_HOME
        if os.path.exists(SCRIPT_LOCAL_PRESET_DIRECTORY):
            initDirectory = SCRIPT_LOCAL_PRESET_DIRECTORY

        presetJsonFilePath = QFileDialog.getSaveFileName(parent=None, caption="Save Preset Json File",
                                                                                                                    dir=initDirectory, filter="Json (*.json)")[0]

        self.presetFilePathQLE.setText(presetFilePath)

    def __connect__saveQPB(self, jsonObject):

        jsonFilePath = self.RefineJsonFilePath(self.presetFilePathQLE.text())
        if os.path.exists(jsonFilePath):
            overwriteWarning = OverwritingWarningQDG(partial(self.Save, jsonFilePath, jsonObject), self)
            overwriteWarning.show()
        else:
            self.Save(jsonFilePath, jsonObject)
            self.close()
            del(self)

    def __connect__cancelQPB(self):
        self.close()
        del(self)

    def keyPressEvent(self, keyEvent):
        if keyEvent.key() == Qt.Key_Escape:
            self.cancelQPB.click()
        elif keyEvent.key() == Qt.Key_Enter:
            self.saveQPB.click()

    def Save(self, jsonFilePath, jsonObject):

        jsonFileDirectory = PathManager.ConvertAbsPath(PathManager.GetListFromAbsPath(jsonFilePath)[:-1])
        PathManager.CreateDirectoryTree(jsonFileDirectory) # Create Directory if it is not existing

        with open(jsonFilePath, "w") as jsonFile:
            json.dump(jsonObject, jsonFile, indent=2)

        return True

    def RefineJsonFilePath(self, jsonFilePath):

        if jsonFilePath:
            if not os.path.splitext(jsonFilePath)[1]:
                jsonFilePath = jsonFilePath + ".json"
            elif os.path.splitext(jsonFilePath)[1] != ".json":
                jsonFilePath = jsonFilePath.replace(os.path.splitext(jsonFilePath)[1], ".json")

        jsonFilePath = PathManager.ConvertAbsPath(jsonFilePath)

        return jsonFilePath

class AuthorityWarningQDG(QDialog):

    def __init__(self, parent=None):

        super(AuthorityWarningQDG, self).__init__(parent)

        self.warningQLB = QLabel("Require authority to save server preset")
        self.warningQHBL = QHBoxLayout()
        self.warningQHBL.setAlignment(Qt.AlignCenter)
        self.warningQHBL.addWidget(self.warningQLB)

        self.okQPB = QPushButton("OK")
        self.okQHBL = QHBoxLayout()
        self.okQHBL.setAlignment(Qt.AlignCenter)
        self.okQHBL.addWidget(self.okQPB)

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addLayout(self.warningQHBL)
        self.mainLayout.addLayout(self.okQHBL)

        self.__connect__()

    def __connect__(self):
        self.okQPB.clicked.connect(self.__connect__okQPB)

    def __connect__okQPB(self):
        self.close()
        del(self)

    def keyPressEvent(self, keyEvent):

        if keyEvent.key() == Qt.Key_Escape:
            self.okQPB.click()
        elif keyEvent.key() == Qt.Key_Enter:
            self.okQPB.click()

class OverwritingWarningQDG(QDialog):

    def __init__(self, funcPointer, parent=None):

        super(OverwritingWarningQDG, self).__init__(parent)

        self.warningQLB = QLabel("Do you overwrite file?")
        self.warningQHBL = QHBoxLayout()
        self.warningQHBL.addWidget(self.warningQLB)

        self.overwriteQPB = QPushButton("Overwrite")
        self.cancelQPB = QPushButton("Cancel")
        self.buttonQHBL = QHBoxLayout()
        self.buttonQHBL.addWidget(self.overwriteQPB)
        self.buttonQHBL.addWidget(self.cancelQPB)

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addLayout(self.warningQHBL)
        self.mainLayout.addLayout(self.buttonQHBL)

        self.__connect__(funcPointer, parent)

    def __connect__(self, funcPointer, parent):
        self.overwriteQPB.clicked.connect(partial(self.__connect__overwriteQPB, funcPointer, parent))
        self.cancelQPB.clicked.connect(self.__connect__cancelQPB)

    def __connect__overwriteQPB(self, funcPointer, parent):
        funcPointer()
        self.close()
        del(self)
        parent.close()
        del(parent)

    def __connect__cancelQPB(self):
        self.close()
        del(self)

    def keyPressEvent(self, keyEvent):

        if keyEvent.key() == Qt.Key_Escape:
            self.cancelQPB.click()
        elif keyEvent.key() == Qt.Key_Enter:
            self.overwriteQPB.click()