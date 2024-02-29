import os
from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint, QTimer, QSize
from PyQt5.QtGui import QPixmap, QIcon, QColor, QFont, QImage, qRgba
from PyQt5.QtWidgets import QDialog, QPushButton, QLabel, QGraphicsOpacityEffect, QWidget, QHBoxLayout, QVBoxLayout, QApplication


class ToastNotification(QDialog):
    # Positions enum
    BOTTOM_RIGHT = 0
    BOTTOM_LEFT = 1
    BOTTOM_MIDDLE = 2
    TOP_RIGHT = 3
    TOP_LEFT = 4
    TOP_MIDDLE = 5

    # Close button alignment enum
    CLOSE_BUTTON_TOP = 0
    CLOSE_BUTTON_MIDDLE = 1
    CLOSE_BUTTON_BOTTOM = 2

    # Static variables
    maximum_on_screen = 3
    spacing = 10
    offset_x = 20
    offset_y = 40
    always_on_main_screen = False
    position = BOTTOM_RIGHT

    currently_shown = []
    queue = []

    DURATION_BAR_UPDATE_INTERVAL = 10

    def __init__(self, parent):

        super(ToastNotification, self).__init__(parent)

        # Init attributes
        self.duration = 5000
        self.showing_duration_bar = True
        self.title = ''
        self.text = ''
        self.border_radius = 0
        self.fade_in_duration = 250
        self.fade_out_duration = 250
        self.reset_countdown_on_hover = True
        self.stay_on_top = False
        self.background_color = QColor('#E7F4F9')
        self.title_color = QColor('#000000')
        self.text_color = QColor('#515151')
        self.icon_color = QColor('#228b22')
        self.icon_separator_color = QColor('#D9D9D9')
        self.close_button_color = QColor('#000000')
        self.duration_bar_color = QColor('#228b22')
        self.title_font = QFont()
        self.title_font.setFamily('Arial')
        self.title_font.setPointSize(9)
        self.title_font.setBold(True)
        self.text_font = QFont()
        self.text_font.setFamily('Arial')
        self.text_font.setPointSize(9)
        self.close_button_icon = QIcon(ToastNotification.__get_directory() + '/icons/cross.png')
        self.close_button_icon_size = QSize(10, 10)
        self.close_button_size = QSize(24, 24)
        self.close_button_alignment = ToastNotification.CLOSE_BUTTON_TOP

        self.elapsed_time = 0

        # Window settings
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.NoFocus)

        # Notification widget
        self.notification = QWidget(self)

        # Opacity effect for fading animations
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(1)
        self.setGraphicsEffect(self.opacity_effect)

        # Close button
        self.close_button = QPushButton(self.notification)
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.clicked.connect(self.__fade_out)
        self.close_button.setStyleSheet('background: transparent;')

        # Title label
        self.title_label = QLabel(self.notification)

        # Text label
        self.text_label = QLabel(self.notification)

        # Icon
        icon_pixmap = QPixmap(ToastNotification.__get_directory() + '/icons/check-mark.png')
        self.icon_label = QLabel(self.notification)
        self.icon_label.setPixmap(icon_pixmap)
        self.icon_label.setFixedSize(icon_pixmap.width(), icon_pixmap.height())

        # Icon separator
        self.icon_separator = QWidget(self.notification)
        self.icon_separator.setFixedWidth(2)

        # Duration bar container (used to make border radius possible on 4 px high widget)
        self.duration_bar_container = QWidget(self.notification)
        self.duration_bar_container.setFixedHeight(4)
        self.duration_bar_container.setStyleSheet('background: transparent;')

        # Duration bar
        self.duration_bar = QWidget(self.duration_bar_container)
        self.duration_bar.setFixedHeight(20)
        self.duration_bar.move(0, -16)

        # Duration bar chunk
        self.duration_bar_chunk = QWidget(self.duration_bar_container)
        self.duration_bar_chunk.setFixedHeight(20)
        self.duration_bar_chunk.move(0, -16)

        # Layout for icon and separator
        self.icon_layout = QHBoxLayout()
        self.icon_layout.addWidget(self.icon_label)
        self.icon_layout.addWidget(self.icon_separator)
        self.icon_layout.setSpacing(12)
        self.icon_layout.setContentsMargins(10, 0, 8, 0)

        # Layout for title and text
        self.text_layout = QVBoxLayout()
        self.text_layout.addWidget(self.title_label)
        self.text_layout.addWidget(self.text_label)
        self.text_layout.setAlignment(Qt.AlignVCenter)
        self.text_layout.setContentsMargins(0, 8, 15, 8)

        # Layout for close button
        self.button_layout = QVBoxLayout()
        self.button_layout.addWidget(self.close_button)

        # Layout to combine everything
        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.icon_layout)
        self.main_layout.addLayout(self.text_layout)
        self.main_layout.addLayout(self.button_layout)
        self.main_layout.setContentsMargins(8, 8, 8, 12)

        # Set main layout
        self.notification.setLayout(self.main_layout)

        # Set default colors
        self.setBackgroundColor(self.background_color)
        self.setTitleColor(self.title_color)
        self.setTextColor(self.text_color)
        self.setIconColor(self.icon_color)
        self.setIconSeparatorColor(self.icon_separator_color)
        self.setCloseButtonColor(self.close_button_color)
        self.setDurationBarColor(self.duration_bar_color)
        self.setTitleFont(self.title_font)
        self.setTextFont(self.text_font)
        self.setCloseButtonIcon(self.close_button_icon)
        self.setCloseButtonIconSize(self.close_button_icon_size)
        self.setCloseButtonSize(self.close_button_size)
        self.setCloseButtonAlignment(self.close_button_alignment)

        # Timer for hiding the notification after set duration
        self.duration_timer = QTimer(self)
        self.duration_timer.timeout.connect(self.hide)

        # Timer for updating the duration bar
        self.duration_bar_timer = QTimer(self)
        self.duration_bar_timer.timeout.connect(self.__update_duration_bar)

    def enterEvent(self, event):
        # Reset timer if hovered and resetting is enabled
        if self.duration != 0 and self.duration_timer.isActive() and self.reset_countdown_on_hover:
            self.duration_timer.stop()

            # Reset duration bar if enabled
            if self.showing_duration_bar:
                self.duration_bar_timer.stop()
                self.duration_bar_chunk.setFixedWidth(self.width())
                self.elapsed_time = 0

    def leaveEvent(self, event):
        # Start timer again when leaving notification and reset is enabled
        if self.duration != 0 and not self.duration_timer.isActive() and self.reset_countdown_on_hover:
            self.duration_timer.start(self.duration)

            # Restart duration bar animation if enabled
            if self.showing_duration_bar:
                self.duration_bar_timer.start(ToastNotification.DURATION_BAR_UPDATE_INTERVAL)

    def show(self):
        # Enable word wrapping if notification would be too long without it
        if self.notification.layout().sizeHint().width() > self.maximumWidth():
            self.title_label.setWordWrap(True)
            self.text_label.setWordWrap(True)
            self.title_label.setMinimumWidth(0)
            self.text_label.setMinimumWidth(0)
            self.notification.layout().activate()

            # Break lines only when it's really necessary to not go over max width
            while self.notification.layout().sizeHint().width() <= self.maximumWidth() - 10:
                self.title_label.setMinimumWidth(self.title_label.minimumWidth() + 10)
                self.text_label.setMinimumWidth(self.text_label.minimumWidth() + 10)
                self.notification.layout().activate()

        # Adjust window and notification widget
        self.setFixedSize(self.notification.layout().sizeHint())
        self.notification.setFixedSize(self.notification.layout().sizeHint())

        # Adjust duration bar and container
        self.duration_bar_container.setFixedWidth(self.width())
        self.duration_bar_container.move(0, self.height() - 4)
        self.duration_bar.setFixedWidth(self.width())
        self.duration_bar_chunk.setFixedWidth(self.width())

        # Adjust icon separator
        self.icon_separator.setFixedHeight(int(self.height() * 0.5))

        # If max notifications on screen not reached, show notification
        if ToastNotification.maximum_on_screen > len(ToastNotification.currently_shown):
            ToastNotification.currently_shown.append(self)

            # Calculate position and show (animate position too if not first notification)
            x, y = self.__calculate_position()

            if len(ToastNotification.currently_shown) != 1:
                if (ToastNotification.position == ToastNotification.BOTTOM_RIGHT
                        or ToastNotification.position == ToastNotification.BOTTOM_LEFT
                        or ToastNotification.position == ToastNotification.BOTTOM_MIDDLE):
                    self.move(x, y - int(self.height() / 1.5))

                elif (ToastNotification.position == ToastNotification.TOP_RIGHT
                        or ToastNotification.position == ToastNotification.TOP_LEFT
                        or ToastNotification.position == ToastNotification.TOP_MIDDLE):
                    self.move(x, y + int(self.height() / 1.5))

                self.pos_animation = QPropertyAnimation(self, b"pos")
                self.pos_animation.setEndValue(QPoint(x, y))
                self.pos_animation.setDuration(250)
                self.pos_animation.start()
            else:
                self.move(x, y)

            # Fade in
            super().show()
            self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.fade_in_animation.setDuration(self.fade_in_duration)
            self.fade_in_animation.setStartValue(0)
            self.fade_in_animation.setEndValue(1)
            self.fade_in_animation.finished.connect(self.__fade_in_finished)
            self.fade_in_animation.start()

            # Make sure title bar of parent is not grayed out
            self.parent().activateWindow()

            # Update every other currently shown notification
            for n in ToastNotification.currently_shown:
                n.__update_position_xy()
        else:
            # Add notification to queue instead
            ToastNotification.queue.append(self)

    def hide(self):
        if self.duration != 0:
            self.duration_timer.stop()
        self.__fade_out()

    def __fade_in_finished(self):
        # Start duration timer
        if self.duration != 0:
            self.duration_timer.start(self.duration)

        # Start duration bar update timer
        if self.duration != 0 and self.showing_duration_bar:
            self.duration_bar_timer.start(ToastNotification.DURATION_BAR_UPDATE_INTERVAL)

    def __fade_out(self):
        self.fade_out_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out_animation.setDuration(self.fade_out_duration)
        self.fade_out_animation.setStartValue(1)
        self.fade_out_animation.setEndValue(0)
        self.fade_out_animation.finished.connect(self.__hide)
        self.fade_out_animation.start()

    def __hide(self):
        self.close()

        if self in ToastNotification.currently_shown:
            ToastNotification.currently_shown.remove(self)

            # Update every other currently shown notification
            for n in ToastNotification.currently_shown:
                n.__update_position_y()

            # Show next item from queue after updating
            timer = QTimer(self)
            timer.timeout.connect(self.__handle_queue)
            timer.start(self.fade_in_duration)

    def __update_duration_bar(self):
        self.elapsed_time += ToastNotification.DURATION_BAR_UPDATE_INTERVAL

        if self.elapsed_time >= self.duration:
            self.duration_bar_timer.stop()
            return

        new_chunk_width = int(self.width() - self.elapsed_time / self.duration * self.width())
        self.duration_bar_chunk.setFixedWidth(new_chunk_width)

    def __update_position_xy(self):
        x, y = self.__calculate_position()

        # Animate position change
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setEndValue(QPoint(x, y))
        self.pos_animation.setDuration(self.fade_out_duration)
        self.pos_animation.start()

    def __update_position_y(self):
        x, y = self.__calculate_position()

        # Animate position change
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setEndValue(QPoint(self.x(), y))
        self.pos_animation.setDuration(self.fade_out_duration)
        self.pos_animation.start()

    def __handle_queue(self):
        if len(ToastNotification.queue) > 0:
            n = ToastNotification.queue.pop()
            n.show()

    def __calculate_position(self):
        # Calculate vertical space taken up by all the currently showing notifications
        y_offset = 0
        for n in ToastNotification.currently_shown:
            if n == self:
                break
            y_offset += n.height() + ToastNotification.spacing

        # Get screen
        primary_screen = QApplication.desktop().screen(QApplication.desktop().primaryScreen())
        current_screen = None

        if ToastNotification.always_on_main_screen:
            current_screen = primary_screen
        else:
            for i in range(QApplication.desktop().screenCount()):
                if self.parent().geometry().intersects(QApplication.desktop().screen(i).geometry()):
                    if current_screen is None:
                        current_screen = QApplication.desktop().screen(i)
                    else:
                        current_screen = primary_screen
                        break

        # Calculate x and y position of notification
        x = 0
        y = 0

        if ToastNotification.position == ToastNotification.BOTTOM_RIGHT:
            x = (current_screen.geometry().width() - self.width()
                 - ToastNotification.offset_x + current_screen.geometry().x())
            y = (current_screen.geometry().height()
                 - ToastNotification.currently_shown[0].height()
                 - ToastNotification.offset_y + current_screen.geometry().y() - y_offset)

        elif ToastNotification.position == ToastNotification.BOTTOM_LEFT:
            x = current_screen.geometry().x() + ToastNotification.offset_x
            y = (current_screen.geometry().height()
                 - ToastNotification.currently_shown[0].height()
                 - ToastNotification.offset_y + current_screen.geometry().y() - y_offset)

        elif ToastNotification.position == ToastNotification.BOTTOM_MIDDLE:
            x = (current_screen.geometry().x()
                 + current_screen.geometry().width() / 2 - self.width() / 2)
            y = (current_screen.geometry().height()
                 - ToastNotification.currently_shown[0].height()
                 - ToastNotification.offset_y + current_screen.geometry().y() - y_offset)

        elif ToastNotification.position == ToastNotification.TOP_RIGHT:
            x = (current_screen.geometry().width() - self.width()
                 - ToastNotification.offset_x + current_screen.geometry().x())
            y = (current_screen.geometry().y()
                 + ToastNotification.currently_shown[0].height()
                 + ToastNotification.offset_y + y_offset)

        elif ToastNotification.position == ToastNotification.TOP_LEFT:
            x = current_screen.geometry().x() + ToastNotification.offset_x
            y = (current_screen.geometry().y()
                 + ToastNotification.currently_shown[0].height()
                 + ToastNotification.offset_y + y_offset)

        elif ToastNotification.position == ToastNotification.TOP_MIDDLE:
            x = (current_screen.geometry().x()
                 + current_screen.geometry().width() / 2
                 - self.width() / 2)
            y = (current_screen.geometry().y()
                 + ToastNotification.currently_shown[0].height()
                 + ToastNotification.offset_y + y_offset)

        return int(x), int(y)

    def setDuration(self, duration: int):
        self.duration = duration

    def setTitle(self, title: str):
        self.title = title
        self.title_label.setText(title)

    def setText(self, text: str):
        self.text = text
        self.text_label.setText(text)

    def setBorderRadius(self, border_radius: int):
        self.border_radius = border_radius
        self.__update_stylesheet()

    def setFadeInDuration(self, duration: int):
        self.fade_in_duration = duration

    def setFadeOutDuration(self, duration: int):
        self.fade_out_duration = duration

    def setResetCountdownOnHover(self, on: bool):
        self.reset_countdown_on_hover = on

    def setStayOnTop(self, on: bool):
        self.stay_on_top = on
        if on:
            self.setWindowFlags(Qt.Window |
                                Qt.CustomizeWindowHint |
                                Qt.FramelessWindowHint |
                                Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(Qt.Window |
                                Qt.CustomizeWindowHint |
                                Qt.FramelessWindowHint)

    def setBackgroundColor(self, color: QColor):
        self.background_color = color
        self.__update_stylesheet()

    def setTitleColor(self, color: QColor):
        self.title_color = color
        self.__update_stylesheet()

    def setTextColor(self, color: QColor):
        self.text_color = color
        self.__update_stylesheet()

    def setIconColor(self, color: QColor):
        self.icon_color = color

        recolored_image = self.__recolor_image(self.icon_label.pixmap().toImage(),
                                               self.icon_label.width(),
                                               self.icon_label.height(),
                                               color)
        self.icon_label.setPixmap(QPixmap(recolored_image))

    def setIconSeparatorColor(self, color: QColor):
        self.icon_separator_color = color
        self.__update_stylesheet()

    def setCloseButtonColor(self, color: QColor):
        self.close_button_color = color

        recolored_image = self.__recolor_image(self.close_button.icon().pixmap(
                                               self.close_button.iconSize()).toImage(),
                                               self.close_button.iconSize().width(),
                                               self.close_button.iconSize().height(),
                                               color)
        self.close_button.setIcon(QIcon(QPixmap(recolored_image)))

    def setDurationBarColor(self, color: QColor):
        self.duration_bar_color = color
        self.__update_stylesheet()

    def setTitleFont(self, font: QFont):
        self.title_font = font
        self.title_label.setFont(font)

    def setTextFont(self, font: QFont):
        self.text_font = font
        self.text_label.setFont(font)

    def setCloseButtonIcon(self, icon: QIcon):
        self.close_button_icon = icon
        self.close_button.setIcon(icon)

    def setCloseButtonIconSize(self, size: QSize):
        self.close_button_icon_size = size
        self.close_button.setIconSize(size)

    def setCloseButtonIconWidth(self, width: int):
        self.close_button_icon_size.setWidth(width)
        self.close_button.setIconSize(self.close_button_icon_size)

    def setCloseButtonIconHeight(self, height: int):
        self.close_button_icon_size.setHeight(height)
        self.close_button.setIconSize(self.close_button_icon_size)

    def setCloseButtonSize(self, size: QSize):
        self.close_button_size = size
        self.close_button.setFixedSize(size)

    def setCloseButtonWidth(self, width: int):
        self.close_button_size.setWidth(width)
        self.close_button.setFixedSize(self.close_button_size)

    def setCloseButtonHeight(self, height: int):
        self.close_button_size.setHeight(height)
        self.close_button.setFixedSize(self.close_button_size)

    def setCloseButtonAlignment(self, alignment: int):
        if (alignment == ToastNotification.CLOSE_BUTTON_TOP
                or alignment == ToastNotification.CLOSE_BUTTON_MIDDLE
                or alignment == ToastNotification.CLOSE_BUTTON_BOTTOM):
            self.close_button_alignment = alignment

        if alignment == ToastNotification.CLOSE_BUTTON_TOP:
            self.button_layout.setAlignment(Qt.AlignTop)
        elif alignment == ToastNotification.CLOSE_BUTTON_MIDDLE:
            self.button_layout.setAlignment(Qt.AlignVCenter)
        elif alignment == ToastNotification.CLOSE_BUTTON_BOTTOM:
            self.button_layout.setAlignment(Qt.AlignBottom)

    def __update_stylesheet(self):
        self.notification.setStyleSheet('background: {};'
                                        'border-radius: {}px;'
                                        .format(self.background_color.name(),
                                                self.border_radius))

        self.duration_bar.setStyleSheet('background: rgba({}, {}, {}, 100);'
                                        'border-radius: {}px;'
                                        .format(self.duration_bar_color.red(),
                                                self.duration_bar_color.green(),
                                                self.duration_bar_color.blue(),
                                                self.border_radius))

        self.duration_bar_chunk.setStyleSheet('background: rgba({}, {}, {}, 255);'
                                              'border-bottom-left-radius: {}px;'
                                              'border-bottom-right-radius: 0px;'
                                              .format(self.duration_bar_color.red(),
                                                      self.duration_bar_color.green(),
                                                      self.duration_bar_color.blue(),
                                                      self.border_radius))

        self.icon_separator.setStyleSheet('background: {};'
                                          .format(self.icon_separator_color.name()))

        self.title_label.setStyleSheet('color: {};'.format(self.title_color.name()))
        self.text_label.setStyleSheet('color: {};'.format(self.text_color.name()))

    @staticmethod
    def __recolor_image(image: QImage, width: int, height: int, color: QColor):
        # Loop through every pixel
        for x in range(0, width):
            for y in range(0, height):
                # Get current color of the pixel
                current_color = image.pixelColor(x, y)
                # Replace the rgb values with rgb of new color and keep alpha the same
                new_color_r = color.red()
                new_color_g = color.green()
                new_color_b = color.blue()
                new_color = QColor.fromRgba(
                    qRgba(new_color_r, new_color_g, new_color_b, current_color.alpha()))
                image.setPixelColor(x, y, new_color)
        return image

    @staticmethod
    def __get_directory():
        return os.path.dirname(os.path.realpath(__file__))

    @staticmethod
    def setPosition(position: int):
        if (position == ToastNotification.BOTTOM_RIGHT
                or position == ToastNotification.BOTTOM_LEFT
                or position == ToastNotification.BOTTOM_MIDDLE
                or position == ToastNotification.TOP_RIGHT
                or position == ToastNotification.TOP_LEFT
                or position == ToastNotification.TOP_MIDDLE):
            ToastNotification.position = position

    @staticmethod
    def setMaximumOnScreen(maximum_on_screen: int):
        ToastNotification.maximum_on_screen = maximum_on_screen

    @staticmethod
    def setSpacing(spacing: int):
        ToastNotification.spacing = spacing

    @staticmethod
    def setOffsetX(offset_x: int):
        ToastNotification.offset_x = offset_x

    @staticmethod
    def setOffsetY(offset_y: int):
        ToastNotification.offset_y = offset_y

    @staticmethod
    def setOffset(offset_x: int, offset_y: int):
        ToastNotification.offset_x = offset_x
        ToastNotification.offset_y = offset_y

    @staticmethod
    def setAlwaysOnMainScreen(on: bool):
        ToastNotification.always_on_main_screen = on
