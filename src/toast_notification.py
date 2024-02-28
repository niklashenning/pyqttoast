import os
from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint, QTimer, QSize
from PyQt5.QtGui import QPixmap, QIcon, QColor, QFont, QImage, qRgba
from PyQt5.QtWidgets import QDialog, QPushButton, QLabel, QGraphicsOpacityEffect, QWidget, QHBoxLayout, QVBoxLayout, QApplication


class ToastNotification(QDialog):
    # Positions Enum
    BOTTOM_RIGHT = 0
    BOTTOM_LEFT = 1
    BOTTOM_MIDDLE = 2
    TOP_RIGHT = 3
    TOP_LEFT = 4
    TOP_MIDDLE = 5

    # Static variables
    max_stacked_notifications = 3
    notification_spacing = 10
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
        self.notification.setGraphicsEffect(self.opacity_effect)

        # Close button
        self.close_button = QPushButton(self.notification)
        self.close_button.setIcon(QIcon(ToastNotification.__get_directory() + '/icons/cross.png'))
        self.close_button.setIconSize(QSize(10, 10))
        self.close_button.setFixedSize(24, 24)
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.clicked.connect(self.__fade_out)
        self.close_button.setStyleSheet('background: transparent;')

        # Title label
        title_font = QFont()
        title_font.setFamily('Arial')
        title_font.setPointSize(9)
        title_font.setBold(True)
        self.title_label = QLabel(self.notification)
        self.title_label.setFont(title_font)

        # Text label
        text_font = QFont()
        text_font.setFamily('Arial')
        text_font.setPointSize(9)
        self.text_label = QLabel(self.notification)
        self.text_label.setFont(text_font)

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
        self.button_layout.setAlignment(Qt.AlignTop)

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
        if ToastNotification.max_stacked_notifications > len(ToastNotification.currently_shown):
            ToastNotification.currently_shown.append(self)

            # Start duration timer
            if self.duration != 0:
                self.duration_timer.start(self.duration)

            # Start duration bar update timer
            if self.duration != 0 and self.showing_duration_bar:
                self.duration_bar_timer.start(ToastNotification.DURATION_BAR_UPDATE_INTERVAL)

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
            y_offset += n.height() + ToastNotification.notification_spacing

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
        if ToastNotification.position == ToastNotification.BOTTOM_RIGHT:
            x = (current_screen.geometry().width() - self.width()
                 - 20 + current_screen.geometry().x())
            y = (current_screen.geometry().height()
                 - ToastNotification.currently_shown[0].height()
                 - 40 + current_screen.geometry().y() - y_offset)

        elif ToastNotification.position == ToastNotification.BOTTOM_LEFT:
            x = current_screen.geometry().x() + 20
            y = (current_screen.geometry().height()
                 - ToastNotification.currently_shown[0].height()
                 - 40 + current_screen.geometry().y() - y_offset)

        elif ToastNotification.position == ToastNotification.BOTTOM_MIDDLE:
            x = (current_screen.geometry().x()
                 + current_screen.geometry().width() / 2 - self.width() / 2)
            y = (current_screen.geometry().height()
                 - ToastNotification.currently_shown[0].height()
                 - 40 + current_screen.geometry().y() - y_offset)

        elif ToastNotification.position == ToastNotification.TOP_RIGHT:
            x = (current_screen.geometry().width() - self.width()
                 - 20 + current_screen.geometry().x())
            y = (current_screen.geometry().y()
                 + ToastNotification.currently_shown[0].height()
                 + 40 + y_offset)

        elif ToastNotification.position == ToastNotification.TOP_LEFT:
            x = current_screen.geometry().x() + 20
            y = (current_screen.geometry().y()
                 + ToastNotification.currently_shown[0].height()
                 + 40 + y_offset)

        elif ToastNotification.position == ToastNotification.TOP_MIDDLE:
            x = (current_screen.geometry().x()
                 + current_screen.geometry().width() / 2
                 - self.width() / 2)
            y = (current_screen.geometry().y()
                 + ToastNotification.currently_shown[0].height()
                 + 40 + y_offset)

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

    def setBackgroundColor(self, background_color: QColor):
        self.background_color = background_color

        self.notification.setStyleSheet('background: {};'
                                        'border-radius: {}px;'
                                        .format(background_color.name(),
                                                self.border_radius))

    def setTitleColor(self, title_color: QColor):
        self.title_color = title_color
        self.title_label.setStyleSheet('color: {};'.format(title_color.name()))

    def setTextColor(self, text_color: QColor):
        self.text_color = text_color
        self.text_label.setStyleSheet('color: {};'.format(text_color.name()))

    def setIconColor(self, icon_color: QColor):
        self.icon_color = icon_color

        recolored_image = self.__recolor_image(self.icon_label.pixmap().toImage(),
                                               self.icon_label.width(),
                                               self.icon_label.height(),
                                               icon_color)
        self.icon_label.setPixmap(QPixmap(recolored_image))

    def setIconSeparatorColor(self, icon_separator_color: QColor):
        self.icon_separator_color = icon_separator_color
        self.icon_separator.setStyleSheet('background: {};'
                                          .format(icon_separator_color.name()))

    def setCloseButtonColor(self, close_button_color: QColor):
        self.close_button_color = close_button_color

        recolored_image = self.__recolor_image(self.close_button.icon().pixmap(
                                               self.close_button.iconSize()).toImage(),
                                               self.close_button.iconSize().width(),
                                               self.close_button.iconSize().height(),
                                               close_button_color)
        self.close_button.setIcon(QIcon(QPixmap(recolored_image)))

    def setDurationBarColor(self, duration_bar_color: QColor):
        self.duration_bar_color = duration_bar_color

        self.duration_bar.setStyleSheet('background: rgba({}, {}, {}, 100);'
                                        'border-radius: {}px;'
                                        .format(duration_bar_color.red(),
                                                duration_bar_color.green(),
                                                duration_bar_color.blue(),
                                                self.border_radius))

        self.duration_bar_chunk.setStyleSheet('background: rgba({}, {}, {}, 255);'
                                              'border-bottom-left-radius: {}px;'
                                              'border-bottom-right-radius: 0px;'
                                              .format(duration_bar_color.red(),
                                                      duration_bar_color.green(),
                                                      duration_bar_color.blue(),
                                                      self.border_radius))

    @staticmethod
    def __recolor_image(image: QImage, width: int, height: int, color: QColor):
        for x in range(0, width):
            for y in range(0, height):
                current_color = image.pixelColor(x, y)
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
    def setMaxStackedNotifications(max_stacked_notifications: int):
        ToastNotification.max_stacked_notifications = max_stacked_notifications

    @staticmethod
    def setNotificationSpacing(spacing_in_px: int):
        ToastNotification.notification_spacing = spacing_in_px

    @staticmethod
    def setAlwaysOnMainScreen(on: bool):
        ToastNotification.always_on_main_screen = on
