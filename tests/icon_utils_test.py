import os
from PyQt6.QtGui import QPixmap
from src.pyqttoast import ToastIcon
from src.pyqttoast.icon_utils import IconUtils


ROOT_PATH = os.path.abspath(os.curdir)


def test_get_icon_from_enum(qtbot):
    """Test converting an enum icon to a QPixmap"""

    information_image = QPixmap(ROOT_PATH + '/src/pyqttoast/icons/information.png').toImage()
    success_image = QPixmap(ROOT_PATH + '/src/pyqttoast/icons/success.png').toImage()
    warning_image = QPixmap(ROOT_PATH + '/src/pyqttoast/icons/warning.png').toImage()
    error_image = QPixmap(ROOT_PATH + '/src/pyqttoast/icons/error.png').toImage()
    close_image = QPixmap(ROOT_PATH + '/src/pyqttoast/icons/close.png').toImage()

    assert IconUtils.get_icon_from_enum(ToastIcon.INFORMATION).toImage() == information_image
    assert IconUtils.get_icon_from_enum(ToastIcon.SUCCESS).toImage() == success_image
    assert IconUtils.get_icon_from_enum(ToastIcon.WARNING).toImage() == warning_image
    assert IconUtils.get_icon_from_enum(ToastIcon.ERROR).toImage() == error_image
    assert IconUtils.get_icon_from_enum(ToastIcon.CLOSE).toImage() == close_image
