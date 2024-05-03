from PyQt6.QtCore import QSize, QMargins
from PyQt6.QtGui import QColor, QFont
from src.pyqttoast import Toast, ToastPosition, ToastButtonAlignment


def test_initial_values(qtbot):
    """Test initial values after instantiating"""

    # Instantiate toast
    toast = Toast()
    qtbot.addWidget(toast)

    # Default fonts
    title_font = QFont()
    title_font.setFamily('Arial')
    title_font.setPointSize(9)
    title_font.setBold(True)

    text_font = QFont()
    text_font.setFamily('Arial')
    text_font.setPointSize(9)

    # Assert initial values
    assert toast.getMaximumOnScreen() == 3
    assert toast.getSpacing() == 10
    assert toast.getOffset() == (20, 45)
    assert toast.isAlwaysOnMainScreen() == False
    assert toast.getPosition() == ToastPosition.BOTTOM_RIGHT
    assert toast.getDuration() == 5000
    assert toast.isShowDurationBar() == True
    assert toast.getTitle() == ''
    assert toast.getText() == ''
    assert toast.isShowIcon() == False
    assert toast.getIconSize() == QSize(18, 18)
    assert toast.isShowCloseButton() == True
    assert toast.getCloseButtonIconSize() == QSize(10, 10)
    assert toast.getCloseButtonSize() == QSize(24, 24)
    assert toast.getCloseButtonAlignment() == ToastButtonAlignment.TOP
    assert toast.getFadeInDuration() == 250
    assert toast.getFadeOutDuration() == 250
    assert toast.isResetDurationOnHover() == True
    assert toast.isStayOnTop() == True
    assert toast.getBorderRadius() == 0
    assert toast.getBackgroundColor() == QColor('#E7F4F9')
    assert toast.getTitleColor() == QColor('#000000')
    assert toast.getTextColor() == QColor('#5C5C5C')
    assert toast.getIconColor() == QColor('#5C5C5C')
    assert toast.getIconSeparatorColor() == QColor('#D9D9D9')
    assert toast.getCloseButtonIconColor() == QColor('#000000')
    assert toast.getDurationBarColor() == QColor('#5C5C5C')
    assert toast.getTitleFont() == title_font
    assert toast.getTextFont() == text_font
    assert toast.getMargins() == QMargins(20, 18, 10, 18)
    assert toast.getIconMargins() == QMargins(0, 0, 15, 0)
    assert toast.getIconSectionMargins() == QMargins(0, 0, 15, 0)
    assert toast.getTextSectionMargins() == QMargins(0, 0, 15, 0)
    assert toast.getCloseButtonMargins() == QMargins(0, -8, 0, -8)
    assert toast.getTextSectionSpacing() == 8
