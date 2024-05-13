import os
import pytest
from unittest.mock import patch
from PyQt6.QtCore import QSize, QMargins, Qt, QRect
from PyQt6.QtGui import QColor, QFont, QGuiApplication, QPixmap
from src.pyqttoast import Toast, ToastPosition, ToastButtonAlignment, ToastPreset, ToastIcon

ROOT_PATH = os.path.abspath(os.curdir)
DROP_SHADOW_SIZE = 5


@pytest.fixture(autouse=True)
def before():
    """Reset everything before each test"""

    Toast.reset()


def test_initial_values(qtbot):
    """Test initial values after instantiating"""

    toast = Toast()
    qtbot.addWidget(toast)

    information_image = QPixmap(ROOT_PATH + '/src/pyqttoast/icons/information.png').toImage()
    close_image = QPixmap(ROOT_PATH + '/src/pyqttoast/icons/close.png').toImage()

    assert Toast.getMaximumOnScreen() == 3
    assert Toast.getSpacing() == 10
    assert Toast.getOffset() == (20, 45)
    assert Toast.isAlwaysOnMainScreen() == False
    assert Toast.getFixedScreen() is None
    assert Toast.getPosition() == ToastPosition.BOTTOM_RIGHT
    assert toast.getDuration() == 5000
    assert toast.isShowDurationBar() == True
    assert toast.getTitle() == ''
    assert toast.getText() == ''
    assert toast.getIcon().toImage() == information_image
    assert toast.isShowIcon() == False
    assert toast.getIconSize() == QSize(18, 18)
    assert toast.isShowIconSeparator() == True
    assert toast.getIconSeparatorWidth() == 2
    assert toast.getCloseButtonIcon().toImage() == close_image
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
    assert toast.getTitleFont() == QFont('Arial', 9, QFont.Weight.Bold)
    assert toast.getTextFont() == QFont('Arial', 9)
    assert toast.getMargins() == QMargins(20, 18, 10, 18)
    assert toast.getIconMargins() == QMargins(0, 0, 15, 0)
    assert toast.getIconSectionMargins() == QMargins(0, 0, 15, 0)
    assert toast.getTextSectionMargins() == QMargins(0, 0, 15, 0)
    assert toast.getCloseButtonMargins() == QMargins(0, -8, 0, -8)
    assert toast.getTextSectionSpacing() == 8


def test_setters_after_show(qtbot):
    """
    Test using setters after already having called the show method
    (Should not do anything since the toast cannot be modified after being shown)
    """
    information_image = QPixmap(ROOT_PATH + '/src/pyqttoast/icons/information.png').toImage()
    close_image = QPixmap(ROOT_PATH + '/src/pyqttoast/icons/close.png').toImage()

    toast = Toast()
    qtbot.addWidget(toast)
    toast.show()

    toast.setDuration(10000)
    toast.setShowDurationBar(False)
    toast.setTitle('title')
    toast.setText('text')
    toast.setIcon(ToastIcon.WARNING)
    toast.setShowIcon(True)
    toast.setIconSize(QSize(35, 35))
    toast.setShowIconSeparator(False)
    toast.setIconSeparatorWidth(5)
    toast.setCloseButtonIcon(ToastIcon.ERROR)
    toast.setShowCloseButton(False)
    toast.setCloseButtonIconSize(QSize(5, 5))
    toast.setCloseButtonSize(QSize(33, 33))
    toast.setCloseButtonAlignment(ToastButtonAlignment.BOTTOM)
    toast.setFadeInDuration(75)
    toast.setFadeOutDuration(50)
    toast.setResetDurationOnHover(False)
    toast.setStayOnTop(False)
    toast.setBorderRadius(5)
    toast.setBackgroundColor(QColor('#000000'))
    toast.setTitleColor(QColor('#000000'))
    toast.setTextColor(QColor('#000000'))
    toast.setIconColor(QColor('#000000'))
    toast.setIconSeparatorColor(QColor('#000000'))
    toast.setCloseButtonIconColor(QColor('#000000'))
    toast.setDurationBarColor(QColor('#000000'))
    toast.setTitleFont(QFont('Helvetica', 14, QFont.Weight.Bold))
    toast.setTextFont(QFont('Helvetica', 12))
    toast.setMargins(QMargins(1, 2, 3, 4))
    toast.setIconMargins(QMargins(1, 2, 3, 4))
    toast.setIconSectionMargins(QMargins(1, 2, 3, 4))
    toast.setTextSectionMargins(QMargins(1, 2, 3, 4))
    toast.setCloseButtonMargins(QMargins(1, 2, 3, 4))
    toast.setTextSectionSpacing(5)

    assert toast.getDuration() == 5000
    assert toast.isShowDurationBar() == True
    assert toast.getTitle() == ''
    assert toast.getText() == ''
    assert toast.getIcon().toImage() == information_image
    assert toast.isShowIcon() == False
    assert toast.getIconSize() == QSize(18, 18)
    assert toast.isShowIconSeparator() == True
    assert toast.getIconSeparatorWidth() == 2
    assert toast.getCloseButtonIcon().toImage() == close_image
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
    assert toast.getTitleFont() == QFont('Arial', 9, QFont.Weight.Bold)
    assert toast.getTextFont() == QFont('Arial', 9)
    assert toast.getMargins() == QMargins(20, 18, 10, 18)
    assert toast.getIconMargins() == QMargins(0, 0, 15, 0)
    assert toast.getIconSectionMargins() == QMargins(0, 0, 15, 0)
    assert toast.getTextSectionMargins() == QMargins(0, 0, 15, 0)
    assert toast.getCloseButtonMargins() == QMargins(0, -8, 0, -8)
    assert toast.getTextSectionSpacing() == 8

    toast.setCloseButtonWidth(44)
    toast.setCloseButtonHeight(48)
    toast.setMarginLeft(5)
    toast.setMarginTop(6)
    toast.setMarginRight(7)
    toast.setMarginBottom(8)
    toast.setIconMarginLeft(5)
    toast.setIconMarginTop(6)
    toast.setIconMarginRight(7)
    toast.setIconMarginBottom(8)
    toast.setIconSectionMarginLeft(5)
    toast.setIconSectionMarginTop(6)
    toast.setIconSectionMarginRight(7)
    toast.setIconSectionMarginBottom(8)
    toast.setTextSectionMarginLeft(5)
    toast.setTextSectionMarginTop(6)
    toast.setTextSectionMarginRight(7)
    toast.setTextSectionMarginBottom(8)
    toast.setCloseButtonMarginLeft(5)
    toast.setCloseButtonMarginTop(6)
    toast.setCloseButtonMarginRight(7)
    toast.setCloseButtonMarginBottom(8)
    toast.applyPreset(ToastPreset.ERROR)

    assert toast.getCloseButtonWidth() == 24
    assert toast.getCloseButtonHeight() == 24
    assert toast.getMargins() == QMargins(20, 18, 10, 18)
    assert toast.getIconMargins() == QMargins(0, 0, 15, 0)
    assert toast.getIconSectionMargins() == QMargins(0, 0, 15, 0)
    assert toast.getTextSectionMargins() == QMargins(0, 0, 15, 0)
    assert toast.getCloseButtonMargins() == QMargins(0, -8, 0, -8)
    assert toast.getIconColor() == QColor('#5C5C5C')
    assert toast.getDurationBarColor() == QColor('#5C5C5C')


def test_count_methods(qtbot):
    """Test the static count methods"""

    assert Toast.getCount() == 0
    assert Toast.getVisibleCount() == 0
    assert Toast.getQueuedCount() == 0

    for i in range(5):
        toast = Toast()
        toast.show()
        qtbot.addWidget(toast)

    assert Toast.getCount() == 5
    assert Toast.getVisibleCount() == 3
    assert Toast.getQueuedCount() == 2


def test_set_maximum_on_screen(qtbot):
    """Test setting the maximum number of toasts on screen"""

    Toast.setMaximumOnScreen(2)
    toast_1 = Toast()
    toast_2 = Toast()
    toast_3 = Toast()
    toast_4 = Toast()
    toast_5 = Toast()
    toast_1.show()
    toast_2.show()
    toast_3.show()
    toast_4.show()
    toast_5.show()
    qtbot.addWidget(toast_1)
    qtbot.addWidget(toast_2)
    qtbot.addWidget(toast_3)
    qtbot.addWidget(toast_4)
    qtbot.addWidget(toast_5)

    assert toast_1.isVisible() == True
    assert toast_2.isVisible() == True
    assert toast_3.isVisible() == False
    assert toast_4.isVisible() == False
    assert toast_5.isVisible() == False


def test_set_maximum_on_screen_while_toasts_are_shown(qtbot):
    """Test setting the maximum number of toasts
     on screen while toasts are being shown"""

    Toast.setMaximumOnScreen(2)
    toast_1 = Toast()
    toast_2 = Toast()
    toast_3 = Toast()
    toast_4 = Toast()
    toast_5 = Toast()
    toast_1.show()
    toast_2.show()
    toast_3.show()
    toast_4.show()
    toast_5.show()
    qtbot.addWidget(toast_1)
    qtbot.addWidget(toast_2)
    qtbot.addWidget(toast_3)
    qtbot.addWidget(toast_4)
    qtbot.addWidget(toast_5)

    assert toast_1.isVisible() == True
    assert toast_2.isVisible() == True
    assert toast_3.isVisible() == False
    assert toast_4.isVisible() == False
    assert toast_5.isVisible() == False

    Toast.setMaximumOnScreen(4)

    assert toast_1.isVisible() == True
    assert toast_2.isVisible() == True
    assert toast_3.isVisible() == True
    assert toast_4.isVisible() == True
    assert toast_5.isVisible() == False


def test_set_spacing(qtbot):
    """Test setting the spacing of the toasts"""

    Toast.setSpacing(50)
    toast_1 = Toast()
    toast_2 = Toast()
    toast_1.setFadeInDuration(0)
    toast_2.setFadeInDuration(0)
    toast_1.show()
    toast_2.show()
    qtbot.addWidget(toast_1)
    qtbot.addWidget(toast_2)

    spacing = (toast_1.pos().y() - toast_2.pos().y()
               - toast_2.height() + 2 * DROP_SHADOW_SIZE)
    assert spacing == 50


def test_set_offset(qtbot):
    """Test setting the offset of the toasts"""

    Toast.setOffset(110, 120)
    assert Toast.getOffset() == (110, 120)

    Toast.setOffsetX(130)
    Toast.setOffsetY(140)
    assert Toast.getOffsetX() == 130
    assert Toast.getOffsetY() == 140

    toast = Toast()
    toast.setFadeInDuration(0)
    toast.show()
    qtbot.addWidget(toast)

    primary_screen = QGuiApplication.primaryScreen()
    offset_x = (primary_screen.geometry().width() - toast.pos().x()
                - toast.width() + DROP_SHADOW_SIZE)
    offset_y = (primary_screen.geometry().height() - toast.pos().y()
                - toast.height() + DROP_SHADOW_SIZE)

    assert offset_x == 130
    assert offset_y == 140


def test_set_always_on_main_screen(qtbot):
    """Test setting the always on main screen option"""

    Toast.setAlwaysOnMainScreen(True)
    toast = Toast()
    toast.show()
    qtbot.addWidget(toast)
    toast.setFadeInDuration(0)

    assert QGuiApplication.primaryScreen().geometry().contains(toast.geometry())


@patch('PyQt6.QtGui.QScreen')
def test_set_fixed_screen(MockedQScreen, qtbot):
    """Test setting a fixed screen to show the notifications on"""

    fixed_screen = MockedQScreen()
    fixed_screen.geometry.return_value = QRect(-3840, 0, 1920, 1080)
    Toast.setFixedScreen(fixed_screen)

    toast = Toast()
    toast.setFadeInDuration(0)
    toast.show()
    qtbot.addWidget(toast)

    assert fixed_screen.geometry().contains(toast.geometry())


def test_set_position_bottom_left(qtbot):
    """Test setting the position of the toasts to BOTTOM_LEFT"""

    Toast.setPosition(ToastPosition.BOTTOM_LEFT)
    toast = Toast()
    toast.setFadeInDuration(0)
    toast.show()
    qtbot.addWidget(toast)

    primary_screen = QGuiApplication.primaryScreen()
    pos_x = (primary_screen.geometry().x()
             + Toast.getOffsetX() - DROP_SHADOW_SIZE)
    pos_y = (primary_screen.geometry().height()
             - Toast.getOffsetY() - toast.height() + DROP_SHADOW_SIZE)

    assert toast.pos().x() == pos_x
    assert toast.pos().y() == pos_y


def test_set_position_bottom_middle(qtbot):
    """Test setting the position of the toasts to BOTTOM_MIDDLE"""

    Toast.setPosition(ToastPosition.BOTTOM_MIDDLE)
    toast = Toast()
    toast.setFadeInDuration(0)
    toast.show()
    qtbot.addWidget(toast)

    primary_screen = QGuiApplication.primaryScreen()
    pos_x = int(primary_screen.geometry().x()
                + primary_screen.geometry().width() / 2 - toast.width() / 2)
    pos_y = (primary_screen.geometry().height()
             - Toast.getOffsetY() - toast.height() + DROP_SHADOW_SIZE)

    assert toast.pos().x() == pos_x
    assert toast.pos().y() == pos_y


def test_set_position_bottom_right(qtbot):
    """Test setting the position of the toasts to BOTTOM_RIGHT"""

    Toast.setPosition(ToastPosition.BOTTOM_RIGHT)
    toast = Toast()
    toast.setFadeInDuration(0)
    toast.show()
    qtbot.addWidget(toast)

    primary_screen = QGuiApplication.primaryScreen()
    pos_x = (primary_screen.geometry().width() - toast.width()
             - Toast.getOffsetX() + DROP_SHADOW_SIZE)
    pos_y = (primary_screen.geometry().height()
             - Toast.getOffsetY() - toast.height() + DROP_SHADOW_SIZE)

    assert toast.pos().x() == pos_x
    assert toast.pos().y() == pos_y


def test_set_position_top_left(qtbot):
    """Test setting the position of the toasts to TOP_LEFT"""

    Toast.setPosition(ToastPosition.TOP_LEFT)
    toast = Toast()
    toast.setFadeInDuration(0)
    toast.show()
    qtbot.addWidget(toast)

    primary_screen = QGuiApplication.primaryScreen()
    pos_x = (primary_screen.geometry().x()
             + Toast.getOffsetX() - DROP_SHADOW_SIZE)
    pos_y = (primary_screen.geometry().y()
             + Toast.getOffsetY() - DROP_SHADOW_SIZE)

    assert toast.pos().x() == pos_x
    assert toast.pos().y() == pos_y


def test_set_position_top_middle(qtbot):
    """Test setting the position of the toasts to TOP_MIDDLE"""

    Toast.setPosition(ToastPosition.TOP_MIDDLE)
    toast = Toast()
    toast.setFadeInDuration(0)
    toast.show()
    qtbot.addWidget(toast)

    primary_screen = QGuiApplication.primaryScreen()
    pos_x = int(primary_screen.geometry().x()
                + primary_screen.geometry().width() / 2 - toast.width() / 2)
    pos_y = (primary_screen.geometry().y()
             + Toast.getOffsetY() - DROP_SHADOW_SIZE)

    assert toast.pos().x() == pos_x
    assert toast.pos().y() == pos_y


def test_set_position_top_right(qtbot):
    """Test setting the position of the toasts to TOP_RIGHT"""

    Toast.setPosition(ToastPosition.TOP_RIGHT)
    toast = Toast()
    toast.setFadeInDuration(0)
    toast.show()
    qtbot.addWidget(toast)

    primary_screen = QGuiApplication.primaryScreen()
    pos_x = (primary_screen.geometry().width() - toast.width()
             - Toast.getOffsetX() + DROP_SHADOW_SIZE)
    pos_y = (primary_screen.geometry().y()
             + Toast.getOffsetY() - DROP_SHADOW_SIZE)

    assert toast.pos().x() == pos_x
    assert toast.pos().y() == pos_y


def test_set_position_center(qtbot):
    """Test setting the position of the toasts to CENTER"""

    Toast.setPosition(ToastPosition.CENTER)
    toast = Toast()
    toast.setFadeInDuration(0)
    toast.show()
    qtbot.addWidget(toast)

    primary_screen = QGuiApplication.primaryScreen()
    pos_x = int(primary_screen.geometry().x()
                + primary_screen.geometry().width() / 2 - toast.width() / 2)
    pos_y = int(primary_screen.geometry().height() / 2
                - toast.height() / 2)

    assert toast.pos().x() == pos_x
    assert toast.pos().y() == pos_y


def test_reset(qtbot):
    """Test resetting the Toast class"""

    Toast.setMaximumOnScreen(10)
    Toast.setSpacing(25)
    Toast.setOffset(100, 150)
    Toast.setAlwaysOnMainScreen(True)
    Toast.setFixedScreen(QGuiApplication.primaryScreen())
    Toast.setPosition(ToastPosition.CENTER)

    toast = Toast()
    qtbot.addWidget(toast)
    toast.show()
    Toast.reset()

    assert Toast.getMaximumOnScreen() == 3
    assert Toast.getSpacing() == 10
    assert Toast.getOffset() == (20, 45)
    assert Toast.isAlwaysOnMainScreen() == False
    assert Toast.getFixedScreen() is None
    assert Toast.getPosition() == ToastPosition.BOTTOM_RIGHT
    assert Toast.getCount() == 0
    assert Toast.getQueuedCount() == 0
    assert Toast.getVisibleCount() == 0
    assert toast.isVisible() == False


def test_set_duration(qtbot):
    """Test setting the duration of a toast"""

    toast = Toast()
    toast.setDuration(2000)
    qtbot.addWidget(toast)

    assert toast.getDuration() == 2000


def test_set_show_duration_bar(qtbot):
    """Test disabling the duration bar of a toast"""

    toast_1 = Toast()
    toast_2 = Toast()
    toast_1.setFadeInDuration(0)
    toast_2.setFadeInDuration(0)
    toast_2.setShowDurationBar(False)
    toast_1.show()
    toast_2.show()
    qtbot.addWidget(toast_1)
    qtbot.addWidget(toast_2)

    assert toast_1.isShowDurationBar() == True
    assert toast_2.isShowDurationBar() == False
    assert toast_1.height() - toast_2.height() == 4


def test_set_title(qtbot):
    """Test setting the title of a toast"""

    toast = Toast()
    toast.setTitle('title')
    qtbot.addWidget(toast)

    assert toast.getTitle() == 'title'


def test_set_text(qtbot):
    """Test setting the text of a toast"""

    toast = Toast()
    toast.setText('text')
    qtbot.addWidget(toast)

    assert toast.getText() == 'text'


def test_set_icon(qtbot):
    """Test setting the icon of a toast"""

    SUCCESS_PIXMAP = QPixmap(ROOT_PATH + '/src/pyqttoast/icons/success.png')
    ERROR_PIXMAP = QPixmap(ROOT_PATH + '/src/pyqttoast/icons/error.png')

    toast = Toast()
    qtbot.addWidget(toast)

    toast.setIcon(ToastIcon.SUCCESS)
    assert toast.getIcon().toImage() == SUCCESS_PIXMAP.toImage()

    toast.setIcon(ERROR_PIXMAP)
    assert toast.getIcon().toImage() == ERROR_PIXMAP.toImage()


def test_set_show_icon(qtbot):
    """Test enabling icon of a toast"""

    toast_1 = Toast()
    toast_2 = Toast()
    toast_1.setFadeInDuration(0)
    toast_2.setFadeInDuration(0)
    toast_2.setShowIcon(True)
    toast_2.setIconMargins(QMargins(0, 0, 0, 0))
    toast_2.setIconSectionMargins(QMargins(0, 0, 0, 0))
    toast_2.setShowIconSeparator(False)
    toast_1.show()
    toast_2.show()
    qtbot.addWidget(toast_1)
    qtbot.addWidget(toast_2)

    assert toast_1.isShowIcon() == False
    assert toast_2.isShowIcon() == True
    assert toast_2.width() - toast_1.width() == toast_2.getIconSize().width()


def test_set_icon_size(qtbot):
    """Test setting the icon size of a toast"""

    toast_1 = Toast()
    toast_2 = Toast()
    toast_1.setFadeInDuration(0)
    toast_1.setShowIcon(True)
    toast_1.setIconMargins(QMargins(0, 0, 0, 0))
    toast_1.setIconSectionMargins(QMargins(0, 0, 0, 0))
    toast_1.setShowIconSeparator(False)
    toast_2.setFadeInDuration(0)
    toast_2.setShowIcon(True)
    toast_2.setIconSize(QSize(55, 55))
    toast_2.setIconMargins(QMargins(0, 0, 0, 0))
    toast_2.setIconSectionMargins(QMargins(0, 0, 0, 0))
    toast_2.setShowIconSeparator(False)
    toast_1.show()
    toast_2.show()
    qtbot.addWidget(toast_1)
    qtbot.addWidget(toast_2)

    icon_size_difference = toast_2.getIconSize().width() - toast_1.getIconSize().width()
    assert toast_2.getIconSize() == QSize(55, 55)
    assert toast_2.width() - toast_1.width() == icon_size_difference


def test_set_show_icon_separator(qtbot):
    """Test disabling the icon separator of a toast"""

    toast_1 = Toast()
    toast_2 = Toast()
    toast_1.setFadeInDuration(0)
    toast_1.setShowIcon(True)
    toast_1.setShowIconSeparator(False)
    toast_2.setFadeInDuration(0)
    toast_2.setShowIcon(True)
    toast_1.show()
    toast_2.show()
    qtbot.addWidget(toast_1)
    qtbot.addWidget(toast_2)

    assert toast_1.isShowIconSeparator() == False
    assert toast_2.isShowIconSeparator() == True
    assert toast_2.width() - toast_1.width() == toast_2.getIconSeparatorWidth()


def test_set_icon_separator_width(qtbot):
    """Test setting the icon separator width of a toast"""

    toast_1 = Toast()
    toast_2 = Toast()
    toast_1.setFadeInDuration(0)
    toast_1.setShowIcon(True)
    toast_2.setFadeInDuration(0)
    toast_2.setShowIcon(True)
    toast_2.setIconSeparatorWidth(5)
    toast_1.show()
    toast_2.show()
    qtbot.addWidget(toast_1)
    qtbot.addWidget(toast_2)

    assert toast_2.getIconSeparatorWidth() == 5
    assert toast_2.width() - toast_1.width() == 3


def test_set_close_button_icon(qtbot):
    """Test setting the close button icon of a toast"""

    close_pixmap = QPixmap(ROOT_PATH + '/src/pyqttoast/icons/close.png')
    error_pixmap = QPixmap(ROOT_PATH + '/src/pyqttoast/icons/error.png')

    toast = Toast()
    qtbot.addWidget(toast)

    toast.setCloseButtonIcon(ToastIcon.ERROR)
    assert toast.getCloseButtonIcon().toImage() == error_pixmap.toImage()

    toast.setCloseButtonIcon(close_pixmap)
    assert toast.getCloseButtonIcon().toImage() == close_pixmap.toImage()


def test_set_show_close_button(qtbot):
    """Test disabling the close button of a toast"""

    toast_1 = Toast()
    toast_2 = Toast()
    toast_1.setFadeInDuration(0)
    toast_1.setShowCloseButton(False)
    toast_2.setFadeInDuration(0)
    toast_1.show()
    toast_2.show()
    qtbot.addWidget(toast_1)
    qtbot.addWidget(toast_2)

    assert toast_1.isShowCloseButton() == False
    assert toast_2.width() - toast_1.width() == toast_1.getCloseButtonWidth()


def test_set_close_button_icon_size(qtbot):
    """Test setting the close button icon size of a toast"""

    toast = Toast()
    toast.setCloseButtonIconSize(QSize(55, 55))
    qtbot.addWidget(toast)

    assert toast.getCloseButtonIconSize() == QSize(55, 55)


def test_set_close_button_size(qtbot):
    """Test setting the close button size of a toast"""

    toast = Toast()
    toast.setCloseButtonSize(QSize(55, 55))
    qtbot.addWidget(toast)

    assert toast.getCloseButtonSize() == QSize(55, 55)


def test_set_close_button_width(qtbot):
    """Test setting the close button width of a toast"""

    toast = Toast()
    toast.setCloseButtonWidth(44)
    qtbot.addWidget(toast)

    assert toast.getCloseButtonWidth() == 44
    assert toast.getCloseButtonSize().width() == 44


def test_set_close_button_height(qtbot):
    """Test setting the close button height of a toast"""

    toast = Toast()
    toast.setCloseButtonHeight(44)
    qtbot.addWidget(toast)

    assert toast.getCloseButtonHeight() == 44
    assert toast.getCloseButtonSize().height() == 44


def test_set_close_button_alignment(qtbot):
    """Test setting the close button alignment of a toast"""

    toast = Toast()
    toast.setCloseButtonAlignment(ToastButtonAlignment.MIDDLE)
    qtbot.addWidget(toast)

    assert toast.getCloseButtonAlignment() == ToastButtonAlignment.MIDDLE


def test_set_fade_in_duration(qtbot):
    """Test setting the fade in duration of a toast"""

    toast = Toast()
    toast.setFadeInDuration(120)
    qtbot.addWidget(toast)

    assert toast.getFadeInDuration() == 120


def test_set_fade_out_duration(qtbot):
    """Test setting the fade out duration of a toast"""

    toast = Toast()
    toast.setFadeOutDuration(175)
    qtbot.addWidget(toast)

    assert toast.getFadeOutDuration() == 175


def test_set_reset_duration_on_hover(qtbot):
    """Test disabling the reset duration on hover option of a toast"""

    toast = Toast()
    toast.setResetDurationOnHover(False)
    qtbot.addWidget(toast)

    assert toast.isResetDurationOnHover() == False


def test_set_stay_on_top(qtbot):
    """Test disabling the stay on top option of a toast"""

    toast = Toast()
    toast.setStayOnTop(False)
    qtbot.addWidget(toast)

    assert toast.isStayOnTop() == False
    assert bool(toast.windowFlags() & Qt.WindowType.WindowStaysOnTopHint) == False


def test_set_border_radius(qtbot):
    """Test setting the border radius of a toast"""

    toast = Toast()
    toast.setBorderRadius(8)
    qtbot.addWidget(toast)

    assert toast.getBorderRadius() == 8


def test_set_colors(qtbot):
    """Test setting the colors of a toast"""

    toast = Toast()
    toast.setBackgroundColor(QColor('#d2ff41'))
    toast.setTitleColor(QColor('#36517d'))
    toast.setTextColor(QColor('#12de67'))
    toast.setIconColor(QColor('#1860d6'))
    toast.setIconSeparatorColor(QColor('#9dde12'))
    toast.setCloseButtonIconColor(QColor('#1fad96'))
    toast.setDurationBarColor(QColor('#cc640e'))
    qtbot.addWidget(toast)

    assert toast.getBackgroundColor() == QColor('#d2ff41')
    assert toast.getTitleColor() == QColor('#36517d')
    assert toast.getTextColor() == QColor('#12de67')
    assert toast.getIconColor() == QColor('#1860d6')
    assert toast.getIconSeparatorColor() == QColor('#9dde12')
    assert toast.getCloseButtonIconColor() == QColor('#1fad96')
    assert toast.getDurationBarColor() == QColor('#cc640e')


def test_set_fonts(qtbot):
    """Test setting the fonts of a toast"""

    title_font = QFont('Helvetica', 10, QFont.Weight.ExtraBold)
    text_font = QFont('Helvetica', 10, QFont.Weight.Light)

    toast = Toast()
    toast.setTitleFont(title_font)
    toast.setTextFont(text_font)
    qtbot.addWidget(toast)

    assert toast.getTitleFont() == title_font
    assert toast.getTextFont() == text_font


def test_set_margins(qtbot):
    """Test setting the margins of a toast"""

    toast = Toast()
    qtbot.addWidget(toast)

    toast.setMargins(QMargins(1, 2, 3, 4))
    assert toast.getMargins() == QMargins(1, 2, 3, 4)

    toast.setMarginLeft(5)
    toast.setMarginTop(6)
    toast.setMarginRight(7)
    toast.setMarginBottom(8)
    assert toast.getMargins() == QMargins(5, 6, 7, 8)
    assert toast.getMarginLeft() == 5
    assert toast.getMarginTop() == 6
    assert toast.getMarginRight() == 7
    assert toast.getMarginBottom() == 8


def test_set_icon_margins(qtbot):
    """Test setting the icon margins of a toast"""

    toast = Toast()
    qtbot.addWidget(toast)

    toast.setIconMargins(QMargins(1, 2, 3, 4))
    assert toast.getIconMargins() == QMargins(1, 2, 3, 4)

    toast.setIconMarginLeft(5)
    toast.setIconMarginTop(6)
    toast.setIconMarginRight(7)
    toast.setIconMarginBottom(8)
    assert toast.getIconMargins() == QMargins(5, 6, 7, 8)
    assert toast.getIconMarginLeft() == 5
    assert toast.getIconMarginTop() == 6
    assert toast.getIconMarginRight() == 7
    assert toast.getIconMarginBottom() == 8


def test_set_icon_section_margins(qtbot):
    """Test setting the icon section margins of a toast"""

    toast = Toast()
    qtbot.addWidget(toast)

    toast.setIconSectionMargins(QMargins(1, 2, 3, 4))
    assert toast.getIconSectionMargins() == QMargins(1, 2, 3, 4)

    toast.setIconSectionMarginLeft(5)
    toast.setIconSectionMarginTop(6)
    toast.setIconSectionMarginRight(7)
    toast.setIconSectionMarginBottom(8)
    assert toast.getIconSectionMargins() == QMargins(5, 6, 7, 8)
    assert toast.getIconSectionMargins() == QMargins(5, 6, 7, 8)
    assert toast.getIconSectionMarginLeft() == 5
    assert toast.getIconSectionMarginTop() == 6
    assert toast.getIconSectionMarginRight() == 7
    assert toast.getIconSectionMarginBottom() == 8


def test_set_text_section_margins(qtbot):
    """Test setting the text section margins of a toast"""

    toast = Toast()
    qtbot.addWidget(toast)

    toast.setTextSectionMargins(QMargins(1, 2, 3, 4))
    assert toast.getTextSectionMargins() == QMargins(1, 2, 3, 4)

    toast.setTextSectionMarginLeft(5)
    toast.setTextSectionMarginTop(6)
    toast.setTextSectionMarginRight(7)
    toast.setTextSectionMarginBottom(8)
    assert toast.getTextSectionMargins() == QMargins(5, 6, 7, 8)
    assert toast.getTextSectionMarginLeft() == 5
    assert toast.getTextSectionMarginTop() == 6
    assert toast.getTextSectionMarginRight() == 7
    assert toast.getTextSectionMarginBottom() == 8


def test_set_close_button_margins(qtbot):
    """Test setting the close button margins of a toast"""

    toast = Toast()
    qtbot.addWidget(toast)

    toast.setCloseButtonMargins(QMargins(1, 2, 3, 4))
    assert toast.getCloseButtonMargins() == QMargins(1, 2, 3, 4)

    toast.setCloseButtonMarginLeft(5)
    toast.setCloseButtonMarginTop(6)
    toast.setCloseButtonMarginRight(7)
    toast.setCloseButtonMarginBottom(8)
    assert toast.getCloseButtonMargins() == QMargins(5, 6, 7, 8)
    assert toast.getCloseButtonMarginLeft() == 5
    assert toast.getCloseButtonMarginTop() == 6
    assert toast.getCloseButtonMarginRight() == 7
    assert toast.getCloseButtonMarginBottom() == 8


def test_set_text_section_spacing(qtbot):
    """Test setting the text section spacing of a toast"""

    toast = Toast()
    toast.setTextSectionSpacing(25)
    qtbot.addWidget(toast)

    assert toast.getTextSectionSpacing() == 25


def test_set_fixed_size(qtbot):
    """Test setting a fixed size on a toast"""

    toast = Toast()
    toast.setFixedSize(QSize(300, 75))
    toast.show()
    qtbot.addWidget(toast)

    assert toast.size() == QSize(300 + DROP_SHADOW_SIZE * 2,
                                 75 + DROP_SHADOW_SIZE * 2)


def test_set_fixed_width(qtbot):
    """Test setting a fixed width on a toast"""

    toast = Toast()
    toast.setFixedWidth(400)
    toast.show()
    qtbot.addWidget(toast)

    assert toast.width() == 400 + DROP_SHADOW_SIZE * 2


def test_set_fixed_height(qtbot):
    """Test setting a fixed height on a toast"""

    toast = Toast()
    toast.setFixedHeight(100)
    toast.show()
    qtbot.addWidget(toast)

    assert toast.height() == 100 + 2 * DROP_SHADOW_SIZE


def test_set_maximum_width_height(qtbot):
    """Test setting a maximum width and height on a toast"""

    toast = Toast()
    toast.setMaximumWidth(300)
    toast.setMaximumHeight(100)
    toast.setText('Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
                  ' Vestibulum suscipit, neque vel porta ultricies, risus'
                  ' augue gravida magna, eu fermentum neque metus quis nulla.'
                  ' Donec sit amet eros a velit vestibulum ultrices.')
    toast.show()
    qtbot.addWidget(toast)

    assert toast.width() == 300 + 2 * DROP_SHADOW_SIZE
    assert toast.height() == 100 + 2 * DROP_SHADOW_SIZE


def test_set_minimum_width_height(qtbot):
    """Test setting a minimum width and height on a toast"""

    toast = Toast()
    toast.setMinimumWidth(500)
    toast.setMinimumHeight(250)
    toast.show()
    qtbot.addWidget(toast)

    assert toast.width() == 500 + 2 * DROP_SHADOW_SIZE
    assert toast.height() == 250 + 2 * DROP_SHADOW_SIZE


def test_apply_preset_light(qtbot):
    """Test applying light theme presets on a toast"""

    success_image = QPixmap(ROOT_PATH + '/src/pyqttoast/icons/success.png').toImage()
    warning_image = QPixmap(ROOT_PATH + '/src/pyqttoast/icons/warning.png').toImage()
    error_image = QPixmap(ROOT_PATH + '/src/pyqttoast/icons/error.png').toImage()
    information_image = QPixmap(ROOT_PATH + '/src/pyqttoast/icons/information.png').toImage()

    toast = Toast()
    qtbot.addWidget(toast)
    toast.setShowDurationBar(False)
    toast.setShowIconSeparator(False)
    toast.setIconSeparatorWidth(3)

    toast.applyPreset(ToastPreset.SUCCESS)
    assert toast.getIcon().toImage() == success_image
    assert toast.getIconColor() == QColor('#3E9141')
    assert toast.getDurationBarColor() == QColor('#3E9141')

    toast.applyPreset(ToastPreset.WARNING)
    assert toast.getIcon().toImage() == warning_image
    assert toast.getIconColor() == QColor('#E8B849')
    assert toast.getDurationBarColor() == QColor('#E8B849')

    toast.applyPreset(ToastPreset.ERROR)
    assert toast.getIcon().toImage() == error_image
    assert toast.getIconColor() == QColor('#BA2626')
    assert toast.getDurationBarColor() == QColor('#BA2626')

    toast.applyPreset(ToastPreset.INFORMATION)
    assert toast.getIcon().toImage() == information_image
    assert toast.getIconColor() == QColor('#007FFF')
    assert toast.getDurationBarColor() == QColor('#007FFF')

    assert toast.getBackgroundColor() == QColor('#E7F4F9')
    assert toast.getCloseButtonIconColor() == QColor('#000000')
    assert toast.getIconSeparatorColor() == QColor('#D9D9D9')
    assert toast.getTitleColor() == QColor('#000000')
    assert toast.getTextColor() == QColor('#5C5C5C')
    assert toast.isShowDurationBar() == True
    assert toast.isShowIcon() == True
    assert toast.isShowIconSeparator() == True
    assert toast.getIconSeparatorWidth() == 2


def test_apply_preset_dark(qtbot):
    """Test applying dark theme presets on a toast"""

    success_image = QPixmap(ROOT_PATH + '/src/pyqttoast/icons/success.png').toImage()
    warning_image = QPixmap(ROOT_PATH + '/src/pyqttoast/icons/warning.png').toImage()
    error_image = QPixmap(ROOT_PATH + '/src/pyqttoast/icons/error.png').toImage()
    information_image = QPixmap(ROOT_PATH + '/src/pyqttoast/icons/information.png').toImage()

    toast = Toast()
    qtbot.addWidget(toast)

    toast.applyPreset(ToastPreset.SUCCESS_DARK)
    assert toast.getIcon().toImage() == success_image
    assert toast.getIconColor() == QColor('#3E9141')
    assert toast.getDurationBarColor() == QColor('#3E9141')

    toast.applyPreset(ToastPreset.WARNING_DARK)
    assert toast.getIcon().toImage() == warning_image
    assert toast.getIconColor() == QColor('#E8B849')
    assert toast.getDurationBarColor() == QColor('#E8B849')

    toast.applyPreset(ToastPreset.ERROR_DARK)
    assert toast.getIcon().toImage() == error_image
    assert toast.getIconColor() == QColor('#BA2626')
    assert toast.getDurationBarColor() == QColor('#BA2626')

    toast.applyPreset(ToastPreset.INFORMATION_DARK)
    assert toast.getIcon().toImage() == information_image
    assert toast.getIconColor() == QColor('#007FFF')
    assert toast.getDurationBarColor() == QColor('#007FFF')

    assert toast.getBackgroundColor() == QColor('#292929')
    assert toast.getCloseButtonIconColor() == QColor('#C9C9C9')
    assert toast.getIconSeparatorColor() == QColor('#585858')
    assert toast.getTitleColor() == QColor('#FFFFFF')
    assert toast.getTextColor() == QColor('#D0D0D0')
    assert toast.isShowDurationBar() == True
    assert toast.isShowIcon() == True


def test_show_twice(qtbot):
    """Test showing a toast twice
     (Should not work since a toast can only be shown one)"""

    toast = Toast()
    toast.setDuration(100)
    toast.setFadeInDuration(0)
    toast.setFadeOutDuration(0)
    toast.show()
    qtbot.addWidget(toast)

    assert toast.isVisible() == True
    toast.hide()
    assert toast.isVisible() == False
    toast.show()
    assert toast.isVisible() == False


def test_hide(qtbot):
    """Test hiding a toast"""

    toast_1 = Toast()
    toast_2 = Toast()
    toast_1.setFadeInDuration(0)
    toast_1.setFadeOutDuration(0)
    toast_1.show()
    toast_2.setFadeInDuration(0)
    toast_2.setFadeOutDuration(0)
    toast_2.show()
    qtbot.addWidget(toast_1)
    qtbot.addWidget(toast_2)

    assert toast_1.isVisible() == True
    assert toast_2.isVisible() == True
    toast_1.hide()
    assert toast_1.isVisible() == False
    assert toast_2.isVisible() == True
