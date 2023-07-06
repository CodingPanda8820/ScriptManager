# UIScriptManagerSS.py
import imp

from ...G_CPSystem import UtilPathManager
imp.reload(UtilPathManager)
PathManager = UtilPathManager.PathManager

__PATH__FILE__ = PathManager.GetListFromAbsPath(__file__)
__PATH__SERVER__ = PathManager.ConvertAbsPath(__PATH__FILE__[:-3])

# ID
_IDI_001_ = PathManager.ConvertAbsPath(__PATH__SERVER__ + "/__SOURCE__/images/File_0000.png").replace("\\", "/")

class mainWindow:

    titleQLB = """
    QLabel{
        font: bold 42px;
        color: white;
    }
    """

class importQD:

    scriptQPB = """
    QPushButton{
        background-image: url('%s') 0 0 2 2;
    }
    QPushButton:hover{
        background-color: gray;
    }
    QPushButton:pressed{
        background-color: darkGray;
    }
    """ % (_IDI_001_)

    iconQPB = """
    QPushButton{
        border-image: url('%s') 0 0 0 0;    
    }
    """ % (_IDI_001_)

class SavePresetQDG:

    titleQLB = """
    QLabel{
        font: bold 24px;
        color: white;
    }
    """