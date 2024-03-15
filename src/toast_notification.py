import math
import os
from enum import Enum
from qtpy.QtGui import QGuiApplication
from qtpy.QtCore import Qt, QPropertyAnimation, QPoint, QTimer, QSize, QMargins, QRect, Signal
from qtpy.QtGui import QPixmap, QIcon, QColor, QFont, QImage, qRgba, QFontMetrics
from qtpy.QtWidgets import QDialog, QPushButton, QLabel, QGraphicsOpacityEffect, QWidget


class ToastPreset(Enum):
    SUCCESS = 1
    WARNING = 2
    ERROR = 3
    INFORMATION = 4
    SUCCESS_DARK = 5
    WARNING_DARK = 6
    ERROR_DARK = 7
    INFORMATION_DARK = 8


class ToastIcon(Enum):
    SUCCESS = 1
    WARNING = 2
    ERROR = 3
    INFORMATION = 4
    CLOSE = 5


class ToastPosition(Enum):
    BOTTOM_RIGHT = 1
    BOTTOM_LEFT = 2
    BOTTOM_MIDDLE = 3
    TOP_RIGHT = 4
    TOP_LEFT = 5
    TOP_MIDDLE = 6


class ToastButtonAlignment(Enum):
    TOP = 1
    MIDDLE = 2
    BOTTOM = 3


class ToastNotification(QDialog):

    # Static attributes
    maximum_on_screen = 3
    spacing = 10
    offset_x = 20
    offset_y = 45
    always_on_main_screen = False
    position = ToastPosition.BOTTOM_RIGHT

    currently_shown = []
    queue = []

    # Constants
    DURATION_BAR_UPDATE_INTERVAL = 10
    DROP_SHADOW_SIZE = 5
    SUCCESS_ACCENT_COLOR = QColor('#3E9141')
    WARNING_ACCENT_COLOR = QColor('#E8B849')
    ERROR_ACCENT_COLOR = QColor('#BA2626')
    INFORMATION_ACCENT_COLOR = QColor('#007FFF')
    DEFAULT_ACCENT_COLOR = QColor('#5C5C5C')
    DEFAULT_BACKGROUND_COLOR = QColor('#E7F4F9')
    DEFAULT_TITLE_COLOR = QColor('#000000')
    DEFAULT_TEXT_COLOR = QColor('#5C5C5C')
    DEFAULT_ICON_SEPARATOR_COLOR = QColor('#D9D9D9')
    DEFAULT_CLOSE_BUTTON_COLOR = QColor('#000000')
    DEFAULT_BACKGROUND_COLOR_DARK = QColor('#292929')
    DEFAULT_TITLE_COLOR_DARK = QColor('#FFFFFF')
    DEFAULT_TEXT_COLOR_DARK = QColor('#D0D0D0')
    DEFAULT_ICON_SEPARATOR_COLOR_DARK = QColor('#585858')
    DEFAULT_CLOSE_BUTTON_COLOR_DARK = QColor('#C9C9C9')

    # Close event
    closed = Signal()

    def __init__(self, parent):

        super(ToastNotification, self).__init__(parent)

        # Init attributes
        self.duration = 5000
        self.show_duration_bar = True
        self.title = ''
        self.text = ''
        self.icon = self.__get_icon_from_enum(ToastIcon.INFORMATION)
        self.show_icon = False
        self.icon_size = QSize(18, 18)
        self.border_radius = 0
        self.fade_in_duration = 250
        self.fade_out_duration = 250
        self.reset_countdown_on_hover = True
        self.stay_on_top = False
        self.background_color = ToastNotification.DEFAULT_BACKGROUND_COLOR
        self.title_color = ToastNotification.DEFAULT_TITLE_COLOR
        self.text_color = ToastNotification.DEFAULT_TEXT_COLOR
        self.icon_color = ToastNotification.DEFAULT_ACCENT_COLOR
        self.icon_separator_color = ToastNotification.DEFAULT_ICON_SEPARATOR_COLOR
        self.close_button_icon_color = ToastNotification.DEFAULT_CLOSE_BUTTON_COLOR
        self.duration_bar_color = ToastNotification.DEFAULT_ACCENT_COLOR
        self.title_font = QFont()
        self.title_font.setFamily('Arial')
        self.title_font.setPointSize(9)
        self.title_font.setBold(True)
        self.text_font = QFont()
        self.text_font.setFamily('Arial')
        self.text_font.setPointSize(9)
        self.close_button_icon = self.__get_icon_from_enum(ToastIcon.CLOSE)
        self.close_button_icon_size = QSize(10, 10)
        self.close_button_size = QSize(24, 24)
        self.close_button_alignment = ToastButtonAlignment.TOP
        self.margins = QMargins(20, 18, 10, 18)
        self.icon_margins = QMargins(0, 0, 15, 0)
        self.icon_section_margins = QMargins(0, 0, 15, 0)
        self.text_section_margins = QMargins(0, 0, 15, 0)
        self.close_button_margins = QMargins(0, -8, 0, -8)
        self.text_section_spacing = 10

        self.elapsed_time = 0
        self.fading_out = False

        # Window settings
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.NoFocus)

        # Notification widget (QLabel because QWidget has weird behaviour with stylesheets)
        self.notification = QLabel(self)

        # Drop shadow (has to be drawn manually since only one graphics effect can be applied)
        self.drop_shadow_layer_1 = QWidget(self)
        self.drop_shadow_layer_1.setObjectName('toast-drop-shadow-layer-1')

        self.drop_shadow_layer_2 = QWidget(self)
        self.drop_shadow_layer_2.setObjectName('toast-drop-shadow-layer-2')

        self.drop_shadow_layer_3 = QWidget(self)
        self.drop_shadow_layer_3.setObjectName('toast-drop-shadow-layer-3')

        self.drop_shadow_layer_4 = QWidget(self)
        self.drop_shadow_layer_4.setObjectName('toast-drop-shadow-layer-4')

        self.drop_shadow_layer_5 = QWidget(self)
        self.drop_shadow_layer_5.setObjectName('toast-drop-shadow-layer-5')

        # Opacity effect for fading animations
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(1)
        self.setGraphicsEffect(self.opacity_effect)

        # Close button
        self.close_button = QPushButton(self.notification)
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.clicked.connect(self.hide)
        self.close_button.setObjectName('toast-close-button')

        # Title label
        self.title_label = QLabel(self.notification)

        # Text label
        self.text_label = QLabel(self.notification)

        # Icon (QPushButton instead of QLabel to get better icon quality)
        self.icon_widget = QPushButton(self.notification)
        self.icon_widget.setObjectName('toast-icon-widget')

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

        # Set default colors
        self.setIcon(self.icon)
        self.setIconSize(self.icon_size)
        self.setIconColor(self.icon_color)
        self.setBackgroundColor(self.background_color)
        self.setTitleColor(self.title_color)
        self.setTextColor(self.text_color)
        self.setBorderRadius(self.border_radius)
        self.setIconSeparatorColor(self.icon_separator_color)
        self.setCloseButtonIconColor(self.close_button_icon_color)
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

        # Apply stylesheet
        self.setStyleSheet(open(self.__get_directory() + '/css/toast_notification.css').read())

    def enterEvent(self, event):
        # Reset timer if hovered and resetting is enabled
        if self.duration != 0 and self.duration_timer.isActive() and self.reset_countdown_on_hover:
            self.duration_timer.stop()

            # Reset duration bar if enabled
            if self.show_duration_bar:
                self.duration_bar_timer.stop()
                self.duration_bar_chunk.setFixedWidth(self.width())
                self.elapsed_time = 0

    def leaveEvent(self, event):
        # Start timer again when leaving notification and reset is enabled
        if self.duration != 0 and not self.duration_timer.isActive() and self.reset_countdown_on_hover:
            self.duration_timer.start(self.duration)

            # Restart duration bar animation if enabled
            if self.show_duration_bar:
                self.duration_bar_timer.start(ToastNotification.DURATION_BAR_UPDATE_INTERVAL)

    def show(self):
        # Setup UI
        self.__setup_ui()

        # If max notifications on screen not reached, show notification
        if ToastNotification.maximum_on_screen > len(ToastNotification.currently_shown):
            ToastNotification.currently_shown.append(self)

            # Start duration timer
            if self.duration != 0:
                self.duration_timer.start(self.duration)

            # Start duration bar update timer
            if self.duration != 0 and self.show_duration_bar:
                self.duration_bar_timer.start(ToastNotification.DURATION_BAR_UPDATE_INTERVAL)

            # Calculate position and show (animate position too if not first notification)
            x, y = self.__calculate_position()

            if len(ToastNotification.currently_shown) != 1:
                if (ToastNotification.position == ToastPosition.BOTTOM_RIGHT
                        or ToastNotification.position == ToastPosition.BOTTOM_LEFT
                        or ToastNotification.position == ToastPosition.BOTTOM_MIDDLE):
                    self.move(x, y - int(self.height() / 1.5))

                elif (ToastNotification.position == ToastPosition.TOP_RIGHT
                        or ToastNotification.position == ToastPosition.TOP_LEFT
                        or ToastNotification.position == ToastPosition.TOP_MIDDLE):
                    self.move(x, y + int(self.height() / 1.5))

                self.pos_animation = QPropertyAnimation(self, b"pos")
                self.pos_animation.setEndValue(QPoint(x, y))
                self.pos_animation.setDuration(self.fade_in_duration)
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
        if not self.fading_out:
            if self.duration != 0:
                self.duration_timer.stop()
                self.fading_out = True
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
            self.elapsed_time = 0
            self.fading_out = False

            # Emit signal
            self.closed.emit()

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
            y_offset += n.notification.height() + ToastNotification.spacing

        # Get screen
        primary_screen = QGuiApplication.primaryScreen()
        current_screen = None

        if ToastNotification.always_on_main_screen:
            current_screen = primary_screen
        else:
            screens = QGuiApplication.screens()
            for screen in screens:
                if self.parent().geometry().intersects(screen.geometry()):
                    if current_screen is None:
                        current_screen = screen
                    else:
                        current_screen = primary_screen
                        break

        # Calculate x and y position of notification
        x = 0
        y = 0

        if ToastNotification.position == ToastPosition.BOTTOM_RIGHT:
            x = (current_screen.geometry().width() - self.notification.width()
                 - ToastNotification.offset_x + current_screen.geometry().x())
            y = (current_screen.geometry().height()
                 - ToastNotification.currently_shown[0].notification.height()
                 - ToastNotification.offset_y + current_screen.geometry().y() - y_offset)

        elif ToastNotification.position == ToastPosition.BOTTOM_LEFT:
            x = current_screen.geometry().x() + ToastNotification.offset_x
            y = (current_screen.geometry().height()
                 - ToastNotification.currently_shown[0].notification.height()
                 - ToastNotification.offset_y + current_screen.geometry().y() - y_offset)

        elif ToastNotification.position == ToastPosition.BOTTOM_MIDDLE:
            x = (current_screen.geometry().x()
                 + current_screen.geometry().width() / 2 - self.notification.width() / 2)
            y = (current_screen.geometry().height()
                 - ToastNotification.currently_shown[0].notification.height()
                 - ToastNotification.offset_y + current_screen.geometry().y() - y_offset)

        elif ToastNotification.position == ToastPosition.TOP_RIGHT:
            x = (current_screen.geometry().width() - self.notification.width()
                 - ToastNotification.offset_x + current_screen.geometry().x())
            y = (current_screen.geometry().y()
                 + ToastNotification.offset_y + y_offset)

        elif ToastNotification.position == ToastPosition.TOP_LEFT:
            x = current_screen.geometry().x() + ToastNotification.offset_x
            y = (current_screen.geometry().y()
                 + ToastNotification.offset_y + y_offset)

        elif ToastNotification.position == ToastPosition.TOP_MIDDLE:
            x = (current_screen.geometry().x()
                 + current_screen.geometry().width() / 2
                 - self.notification.width() / 2)
            y = (current_screen.geometry().y()
                 + ToastNotification.offset_y + y_offset)

        x = int(x - ToastNotification.DROP_SHADOW_SIZE)
        y = int(y - ToastNotification.DROP_SHADOW_SIZE)

        return x, y

    def __setup_ui(self):
        # Calculate title and text width and height
        title_font_metrics = QFontMetrics(self.title_font)
        title_width = title_font_metrics.width(self.title_label.text())
        title_height = title_font_metrics.tightBoundingRect(self.title_label.text()).height()
        text_font_metrics = QFontMetrics(self.text_font)
        text_width = text_font_metrics.width(self.text_label.text())
        text_height = text_font_metrics.boundingRect(self.text_label.text()).height()

        text_section_height = (self.text_section_margins.top()
                               + title_height + self.text_section_spacing
                               + text_height + self.text_section_margins.bottom())

        # Calculate duration bar height
        duration_bar_height = 0 if not self.show_duration_bar else self.duration_bar_container.height()

        # Calculate icon section width and height
        icon_section_width = 0
        icon_section_height = 0

        if self.show_icon:
            icon_section_width = (self.icon_section_margins.left()
                                  + self.icon_margins.left() + self.icon_widget.width()
                                  + self.icon_margins.right() + self.icon_separator.width()
                                  + self.icon_section_margins.right())
            icon_section_height = (self.icon_section_margins.top() + self.icon_margins.top()
                                   + self.icon_widget.height() + self.icon_margins.bottom()
                                   + self.icon_section_margins.bottom())

        # Calculate height and close button section
        close_button_section_height = (self.close_button_margins.top()
                                       + self.close_button.height()
                                       + self.close_button_margins.bottom())

        # Calculate needed width and height
        width = (self.margins.left() + icon_section_width + self.text_section_margins.left()
                 + max(title_width, text_width) + self.text_section_margins.right()
                 + self.close_button_margins.left() + self.close_button.width()
                 + self.close_button_margins.right() + self.margins.right())

        height = (self.margins.top()
                  + max(icon_section_height, text_section_height, close_button_section_height)
                  + self.margins.bottom() + duration_bar_height)

        forced_additional_height = 0
        forced_reduced_height = 0

        # Handle width greater than maximum width
        if width > self.maximumWidth():
            # Enable line break for title and text and recalculate size
            title_width = text_width = title_width - (width - self.maximumWidth())

            self.title_label.setMinimumWidth(title_width)
            self.title_label.setWordWrap(True)
            title_height = self.title_label.sizeHint().height()
            self.title_label.resize(title_width, title_height)

            self.text_label.setMinimumWidth(text_width)
            self.text_label.setWordWrap(True)
            text_height = self.text_label.sizeHint().height()
            self.text_label.resize(text_width, text_height)

            # Recalculate width and height
            width = self.maximumWidth()

            text_section_height = (self.text_section_margins.top()
                                   + title_height + self.text_section_spacing
                                   + text_height + self.text_section_margins.bottom())

            height = (self.margins.top()
                      + max(icon_section_height, text_section_height, close_button_section_height)
                      + self.margins.bottom() + duration_bar_height)

        # Handle height less than minimum height
        if height < self.minimumHeight():
            # Enable word wrap for title and text labels
            self.title_label.setWordWrap(True)
            self.text_label.setWordWrap(True)

            # Calculate height with initial label width
            title_width = (self.title_label.fontMetrics().boundingRect(
                QRect(0, 0, 0, 0), Qt.TextWordWrap, self.title_label.text()).width())
            text_width = (self.text_label.fontMetrics().boundingRect(
                QRect(0, 0, 0, 0), Qt.TextWordWrap, self.text_label.text()).width())
            temp_width = max(title_width, text_width)

            title_width = (self.title_label.fontMetrics().boundingRect(
                QRect(0, 0, temp_width, 0), Qt.TextWordWrap, self.title_label.text()).width())
            title_height = (self.title_label.fontMetrics().boundingRect(
                QRect(0, 0, temp_width, 0), Qt.TextWordWrap, self.title_label.text()).height())
            text_width = (self.text_label.fontMetrics().boundingRect(
                QRect(0, 0, temp_width, 0), Qt.TextWordWrap, self.text_label.text()).width())
            text_height = (self.text_label.fontMetrics().boundingRect(
                QRect(0, 0, temp_width, 0), Qt.TextWordWrap, self.text_label.text()).height())

            text_section_height = (self.text_section_margins.top()
                                   + title_height + self.text_section_spacing
                                   + text_height + self.text_section_margins.bottom())

            height = (self.margins.top()
                      + max(icon_section_height, text_section_height, close_button_section_height)
                      + self.margins.bottom() + duration_bar_height)

            while temp_width <= width:
                # Recalculate height with different text widths to find optimal value
                temp_title_width = (self.title_label.fontMetrics().boundingRect(
                    QRect(0, 0, temp_width, 0), Qt.TextWordWrap, self.title_label.text()).width())
                temp_title_height = (self.title_label.fontMetrics().boundingRect(
                    QRect(0, 0, temp_width, 0), Qt.TextWordWrap, self.title_label.text()).height())
                temp_text_width = (self.text_label.fontMetrics().boundingRect(
                    QRect(0, 0, temp_width, 0), Qt.TextWordWrap, self.text_label.text()).width())
                temp_text_height = (self.text_label.fontMetrics().boundingRect(
                    QRect(0, 0, temp_width, 0), Qt.TextWordWrap, self.text_label.text()).height())

                temp_text_section_height = (self.text_section_margins.top()
                                            + temp_title_height + self.text_section_spacing
                                            + temp_text_height + self.text_section_margins.bottom())

                temp_height = (self.margins.top()
                               + max(icon_section_height, temp_text_section_height,
                                     close_button_section_height)
                               + self.margins.bottom() + duration_bar_height)

                # Store values if calculated height is greater than or equal to min height
                if temp_height >= self.minimumHeight():
                    title_width = temp_title_width
                    title_height = temp_title_height
                    text_width = temp_text_width
                    text_height = temp_text_height
                    text_section_height = temp_text_section_height
                    height = temp_height
                    temp_width += 1

                # Exit loop if calculated height is less than min height
                else:
                    break

            # Recalculate width
            width = (self.margins.left() + icon_section_width + self.text_section_margins.left()
                     + max(title_width, text_width) + self.text_section_margins.right()
                     + self.close_button_margins.left() + self.close_button.width()
                     + self.close_button_margins.right() + self.margins.right())

            # If min height not met, set height to min height
            if height < self.minimumHeight():
                forced_additional_height = self.minimumHeight() - height
                height = self.minimumHeight()

        # Handle width less than minimum width
        if width < self.minimumWidth():
            width = self.minimumWidth()

        # Handle height greater than maximum height
        if height > self.maximumHeight():
            forced_reduced_height = height - self.maximumHeight()
            height = self.maximumHeight()

        # Calculate width and height including space for drop shadow
        total_width = width + (ToastNotification.DROP_SHADOW_SIZE * 2)
        total_height = height + (ToastNotification.DROP_SHADOW_SIZE * 2)

        # Resize drop shadow
        self.drop_shadow_layer_1.resize(total_width, total_height)
        self.drop_shadow_layer_1.move(0, 0)
        self.drop_shadow_layer_2.resize(total_width - 2, total_height - 2)
        self.drop_shadow_layer_2.move(1, 1)
        self.drop_shadow_layer_3.resize(total_width - 4, total_height - 4)
        self.drop_shadow_layer_3.move(2, 2)
        self.drop_shadow_layer_4.resize(total_width - 6, total_height - 6)
        self.drop_shadow_layer_4.move(3, 3)
        self.drop_shadow_layer_5.resize(total_width - 8, total_height - 8)
        self.drop_shadow_layer_5.move(4, 4)

        # Resize window
        self.resize(total_width, total_height)
        self.notification.setFixedSize(width, height)
        self.notification.move(ToastNotification.DROP_SHADOW_SIZE,
                               ToastNotification.DROP_SHADOW_SIZE)
        self.notification.raise_()

        # Calculate difference between height and height of icon section
        height_icon_section_height_difference = (max(icon_section_height,
                                                     text_section_height,
                                                     close_button_section_height)
                                                 - icon_section_height)

        if self.show_icon:
            # Move icon
            self.icon_widget.move(self.margins.left()
                                  + self.icon_section_margins.left()
                                  + self.icon_margins.left(),
                                  self.margins.top()
                                  + self.icon_section_margins.top()
                                  + self.icon_margins.top()
                                  + math.ceil(height_icon_section_height_difference / 2)
                                  + math.ceil(forced_additional_height / 2)
                                  - math.floor(forced_reduced_height / 2))

            # Move and resize icon separator
            self.icon_separator.setFixedHeight(text_section_height)
            self.icon_separator.move(self.margins.left()
                                     + self.icon_section_margins.left()
                                     + self.icon_margins.left()
                                     + self.icon_widget.width()
                                     + self.icon_margins.right(),
                                     self.margins.top()
                                     + self.icon_section_margins.top()
                                     + math.ceil(forced_additional_height / 2)
                                     - math.floor(forced_reduced_height / 2))

            # Show icon section
            self.icon_widget.setVisible(True)
            self.icon_separator.setVisible(True)
        else:
            # Hide icon section
            self.icon_widget.setVisible(False)
            self.icon_separator.setVisible(False)

        # Calculate difference between height and height of text section
        height_text_section_height_difference = (max(icon_section_height,
                                                     text_section_height,
                                                     close_button_section_height)
                                                 - text_section_height)

        # Resize title and text labels
        self.title_label.resize(title_width, title_height)
        self.text_label.resize(text_width, text_height)

        # Move title and text labels
        if self.show_icon:
            self.title_label.move(self.margins.left()
                                  + self.icon_section_margins.left()
                                  + self.icon_margins.left()
                                  + self.icon_widget.width()
                                  + self.icon_margins.right()
                                  + self.icon_section_margins.right()
                                  + self.text_section_margins.left(),
                                  self.margins.top()
                                  + self.text_section_margins.top()
                                  + math.ceil(height_text_section_height_difference / 2)
                                  + math.ceil(forced_additional_height / 2)
                                  - math.floor(forced_reduced_height / 2))

            self.text_label.move(self.margins.left()
                                 + self.icon_section_margins.left()
                                 + self.icon_margins.left()
                                 + self.icon_widget.width()
                                 + self.icon_margins.right()
                                 + self.icon_section_margins.right()
                                 + self.text_section_margins.left(),
                                 self.margins.top()
                                 + self.text_section_margins.top()
                                 + title_height + self.text_section_spacing
                                 + math.ceil(height_text_section_height_difference / 2)
                                 + math.ceil(forced_additional_height / 2)
                                 - math.floor(forced_reduced_height / 2))

        # Position is different if icon hidden
        else:
            self.title_label.move(self.margins.left()
                                  + self.text_section_margins.left(),
                                  self.margins.top()
                                  + self.text_section_margins.top()
                                  + math.ceil(height_text_section_height_difference / 2)
                                  + math.ceil(forced_additional_height / 2)
                                  - math.floor(forced_reduced_height / 2))

            self.text_label.move(self.margins.left()
                                 + self.text_section_margins.left(),
                                 self.margins.top()
                                 + self.text_section_margins.top()
                                 + title_height + self.text_section_spacing
                                 + math.ceil(height_text_section_height_difference / 2)
                                 + math.ceil(forced_additional_height / 2)
                                 - math.floor(forced_reduced_height / 2))

        # Adjust label position if either title or text is empty
        if self.title == '' and self.text != '':
            self.text_label.move(self.text_label.x(),
                                 int((height - text_height - duration_bar_height) / 2))

        elif self.title != '' and self.text == '':
            self.title_label.move(self.title_label.x(),
                                  int((height - title_height - duration_bar_height) / 2))

        # Move close button to top, middle, or bottom position
        if self.close_button_alignment == ToastButtonAlignment.TOP:
            self.close_button.move(width - self.close_button.width()
                                   - self.close_button_margins.right() - self.margins.right(),
                                   self.margins.top() + self.close_button_margins.top())
        elif self.close_button_alignment == ToastButtonAlignment.MIDDLE:
            self.close_button.move(width - self.close_button.width()
                                   - self.close_button_margins.right() - self.margins.right(),
                                   math.ceil((height - self.close_button.height()
                                              - duration_bar_height) / 2))
        elif self.close_button_alignment == ToastButtonAlignment.BOTTOM:
            self.close_button.move(width - self.close_button.width()
                                   - self.close_button_margins.right() - self.margins.right(),
                                   height - self.close_button.height()
                                   - self.margins.bottom()
                                   - self.close_button_margins.bottom() - duration_bar_height)

        # Resize, move, and show duration bar if enabled
        if self.show_duration_bar:
            self.duration_bar_container.setFixedWidth(width)
            self.duration_bar_container.move(0, height - duration_bar_height)
            self.duration_bar.setFixedWidth(width)
            self.duration_bar_chunk.setFixedWidth(width)
            self.duration_bar_container.setVisible(True)
        else:
            self.duration_bar_container.setVisible(False)

    def getDuration(self) -> int:
        return self.duration

    def setDuration(self, duration: int):
        self.duration = duration

    def isShowDurationBar(self) -> bool:
        return self.show_duration_bar

    def setShowDurationBar(self, on: bool):
        self.show_duration_bar = on

    def getTitle(self) -> str:
        return self.title

    def setTitle(self, title: str):
        self.title = title
        self.title_label.setText(title)

    def getText(self) -> str:
        return self.text

    def setText(self, text: str):
        self.text = text
        self.text_label.setText(text)

    def getIcon(self) -> QPixmap:
        return self.icon_widget.pixmap()

    def setIcon(self, icon: QPixmap | ToastIcon):
        if type(icon) == ToastIcon:
            self.icon = self.__get_icon_from_enum(icon)
        else:
            self.icon = icon

        self.icon_widget.setIcon(QIcon(self.icon))
        self.setIconColor(self.icon_color)

    def isShowIcon(self) -> bool:
        return self.show_icon

    def setShowIcon(self, on: bool):
        self.show_icon = on

    def getIconSize(self) -> QSize:
        return self.icon_size

    def setIconSize(self, size: QSize):
        self.icon_size = size
        self.icon_widget.setFixedSize(size)
        self.icon_widget.setIconSize(size)
        self.setIcon(self.icon)

    def getBorderRadius(self) -> int:
        return self.border_radius

    def setBorderRadius(self, border_radius: int):
        self.border_radius = border_radius
        self.__update_stylesheet()

    def getFadeInDuration(self) -> int:
        return self.fade_in_duration

    def setFadeInDuration(self, duration: int):
        self.fade_in_duration = duration

    def getFadeOutDuration(self) -> int:
        return self.fade_out_duration

    def setFadeOutDuration(self, duration: int):
        self.fade_out_duration = duration

    def isResetCountdownOnHover(self) -> bool:
        return self.reset_countdown_on_hover

    def setResetCountdownOnHover(self, on: bool):
        self.reset_countdown_on_hover = on

    def isStayOnTop(self) -> bool:
        return self.stay_on_top

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

    def getBackgroundColor(self) -> QColor:
        return self.background_color

    def setBackgroundColor(self, color: QColor):
        self.background_color = color
        self.__update_stylesheet()

    def getTitleColor(self) -> QColor:
        return self.title_color

    def setTitleColor(self, color: QColor):
        self.title_color = color
        self.__update_stylesheet()

    def getTextColor(self) -> QColor:
        return self.text_color

    def setTextColor(self, color: QColor):
        self.text_color = color
        self.__update_stylesheet()

    def getIconColor(self) -> QColor:
        return self.icon_color

    def setIconColor(self, color: QColor):
        self.icon_color = color

        recolored_image = self.__recolor_image(self.icon_widget.icon().pixmap(
                                               self.icon_widget.iconSize()).toImage(),
                                               self.icon_widget.iconSize().width(),
                                               self.icon_widget.iconSize().height(),
                                               color)
        self.icon_widget.setIcon(QIcon(QPixmap(recolored_image)))

    def getIconSeparatorColor(self) -> QColor:
        return self.icon_separator_color

    def setIconSeparatorColor(self, color: QColor):
        self.icon_separator_color = color
        self.__update_stylesheet()

    def getCloseButtonColor(self) -> QColor:
        return self.close_button_icon_color

    def setCloseButtonIconColor(self, color: QColor):
        self.close_button_icon_color = color

        recolored_image = self.__recolor_image(self.close_button.icon().pixmap(
                                               self.close_button.iconSize()).toImage(),
                                               self.close_button.iconSize().width(),
                                               self.close_button.iconSize().height(),
                                               color)
        self.close_button.setIcon(QIcon(QPixmap(recolored_image)))

    def getDurationBarColor(self) -> QColor:
        return self.duration_bar_color

    def setDurationBarColor(self, color: QColor):
        self.duration_bar_color = color
        self.__update_stylesheet()

    def getTitleFont(self) -> QFont:
        return self.title_font

    def setTitleFont(self, font: QFont):
        self.title_font = font
        self.title_label.setFont(font)

    def getTextFont(self) -> QFont:
        return self.text_font

    def setTextFont(self, font: QFont):
        self.text_font = font
        self.text_label.setFont(font)

    def getCloseButtonIcon(self) -> QPixmap:
        return self.close_button_icon

    def setCloseButtonIcon(self, icon: QPixmap | ToastIcon):
        if type(icon) == ToastIcon:
            self.close_button_icon = self.__get_icon_from_enum(icon)
        else:
            self.close_button_icon = icon

        self.close_button.setIcon(QIcon(self.close_button_icon))
        self.setCloseButtonIconColor(self.close_button_icon_color)

    def getCloseButtonIconSize(self) -> QSize:
        return self.close_button_icon_size

    def setCloseButtonIconSize(self, size: QSize):
        self.close_button_icon_size = size
        self.close_button.setIconSize(size)
        self.setCloseButtonIcon(self.close_button_icon)

    def getCloseButtonSize(self) -> QSize:
        return self.close_button_size

    def setCloseButtonSize(self, size: QSize):
        self.close_button_size = size
        self.close_button.setFixedSize(size)

    def getCloseButtonWidth(self) -> int:
        return self.close_button_size.width()

    def setCloseButtonWidth(self, width: int):
        self.close_button_size.setWidth(width)
        self.close_button.setFixedSize(self.close_button_size)

    def getCloseButtonHeight(self) -> int:
        return self.close_button_size.height()

    def setCloseButtonHeight(self, height: int):
        self.close_button_size.setHeight(height)
        self.close_button.setFixedSize(self.close_button_size)

    def getCloseButtonAlignment(self) -> ToastButtonAlignment:
        return self.close_button_alignment

    def setCloseButtonAlignment(self, alignment: ToastButtonAlignment):
        if (alignment == ToastButtonAlignment.TOP
                or alignment == ToastButtonAlignment.MIDDLE
                or alignment == ToastButtonAlignment.BOTTOM):
            self.close_button_alignment = alignment

    def getMargins(self) -> QMargins:
        return self.margins

    def setMargins(self, margins: QMargins):
        self.margins = margins

    def getMarginLeft(self) -> int:
        return self.margins.left()

    def setMarginLeft(self, margin: int):
        self.margins.setLeft(margin)

    def getMarginTop(self) -> int:
        return self.margins.top()

    def setMarginTop(self, margin: int):
        self.margins.setTop(margin)

    def getMarginRight(self) -> int:
        return self.margins.right()

    def setMarginRight(self, margin: int):
        self.margins.setRight(margin)

    def getMarginBottom(self) -> int:
        return self.margins.bottom()

    def setMarginBottom(self, margin: int):
        self.margins.setBottom(margin)

    def getIconMargins(self) -> QMargins:
        return self.icon_margins

    def setIconMargins(self, margins: QMargins):
        self.icon_margins = margins

    def getIconMarginLeft(self) -> int:
        return self.icon_margins.left()

    def setIconMarginLeft(self, margin: int):
        self.icon_margins.setLeft(margin)

    def getIconMarginTop(self) -> int:
        return self.icon_margins.top()

    def setIconMarginTop(self, margin: int):
        self.icon_margins.setTop(margin)

    def getIconMarginRight(self) -> int:
        return self.icon_margins.right()

    def setIconMarginRight(self, margin: int):
        self.icon_margins.setRight(margin)

    def getIconMarginBottom(self) -> int:
        return self.icon_margins.bottom()

    def setIconMarginBottom(self, margin: int):
        self.icon_margins.setBottom(margin)

    def getIconSectionMargins(self) -> QMargins:
        return self.icon_section_margins

    def setIconSectionMargins(self, margins: QMargins):
        self.icon_section_margins = margins

    def getIconSectionMarginLeft(self) -> int:
        return self.icon_section_margins.left()

    def setIconSectionMarginLeft(self, margin: int):
        self.icon_section_margins.setLeft(margin)

    def getIconSectionMarginTop(self) -> int:
        return self.icon_section_margins.top()

    def setIconSectionMarginTop(self, margin: int):
        self.icon_section_margins.setTop(margin)

    def getIconSectionMarginRight(self) -> int:
        return self.icon_section_margins.right()

    def setIconSectionMarginRight(self, margin: int):
        self.icon_section_margins.setRight(margin)

    def getIconSectionMarginBottom(self) -> int:
        return self.icon_section_margins.bottom()

    def setIconSectionMarginBottom(self, margin: int):
        self.icon_section_margins.setBottom(margin)

    def getTextSectionMargins(self) -> QMargins:
        return self.text_section_margins

    def setTextSectionMargins(self, margins: QMargins):
        self.text_section_margins = margins

    def getTextSectionMarginLeft(self) -> int:
        return self.text_section_margins.left()

    def setTextSectionMarginLeft(self, margin: int):
        self.text_section_margins.setLeft(margin)

    def getTextSectionMarginTop(self) -> int:
        return self.text_section_margins.top()

    def setTextSectionMarginTop(self, margin: int):
        self.text_section_margins.setTop(margin)

    def getTextSectionMarginRight(self) -> int:
        return self.text_section_margins.right()

    def setTextSectionMarginRight(self, margin: int):
        self.text_section_margins.setRight(margin)

    def getTextSectionMarginBottom(self) -> int:
        return self.text_section_margins.bottom()

    def setTextSectionMarginBottom(self, margin: int):
        self.text_section_margins.setBottom(margin)

    def getCloseButtonMargins(self) -> QMargins:
        return self.close_button_margins

    def setCloseButtonMargins(self, margins: QMargins):
        self.close_button_margins = margins

    def getCloseButtonMarginLeft(self) -> int:
        return self.close_button_margins.left()

    def setCloseButtonMarginLeft(self, margin: int):
        self.close_button_margins.setLeft(margin)

    def getCloseButtonMarginTop(self) -> int:
        return self.close_button_margins.top()

    def setCloseButtonMarginTop(self, margin: int):
        self.close_button_margins.setTop(margin)

    def getCloseButtonMarginRight(self) -> int:
        return self.close_button_margins.right()

    def setCloseButtonMarginRight(self, margin: int):
        self.close_button_margins.setRight(margin)

    def getCloseButtonMarginBottom(self) -> int:
        return self.close_button_margins.bottom()

    def setCloseButtonMarginBottom(self, margin: int):
        self.close_button_margins.setBottom(margin)

    def getTextSectionSpacing(self) -> int:
        return self.text_section_spacing

    def setTextSectionSpacing(self, spacing: int):
        self.text_section_spacing = spacing

    def applyPreset(self, preset: ToastPreset):
        if preset == ToastPreset.SUCCESS or preset == ToastPreset.SUCCESS_DARK:
            self.setIcon(ToastIcon.SUCCESS)
            self.setIconColor(ToastNotification.SUCCESS_ACCENT_COLOR)
            self.setDurationBarColor(ToastNotification.SUCCESS_ACCENT_COLOR)

        elif preset == ToastPreset.WARNING or preset == ToastPreset.WARNING_DARK:
            self.setIcon(ToastIcon.WARNING)
            self.setIconColor(ToastNotification.WARNING_ACCENT_COLOR)
            self.setDurationBarColor(ToastNotification.WARNING_ACCENT_COLOR)

        elif preset == ToastPreset.ERROR or preset == ToastPreset.ERROR_DARK:
            self.setIcon(ToastIcon.ERROR)
            self.setIconColor(ToastNotification.ERROR_ACCENT_COLOR)
            self.setDurationBarColor(ToastNotification.ERROR_ACCENT_COLOR)

        elif preset == ToastPreset.INFORMATION or preset == ToastPreset.INFORMATION_DARK:
            self.setIcon(ToastIcon.INFORMATION)
            self.setIconColor(ToastNotification.INFORMATION_ACCENT_COLOR)
            self.setDurationBarColor(ToastNotification.INFORMATION_ACCENT_COLOR)

        if (preset == ToastPreset.SUCCESS
                or preset == ToastPreset.WARNING
                or preset == ToastPreset.ERROR
                or preset == ToastPreset.INFORMATION):
            self.setBackgroundColor(ToastNotification.DEFAULT_BACKGROUND_COLOR)
            self.setCloseButtonIconColor(ToastNotification.DEFAULT_CLOSE_BUTTON_COLOR)
            self.show_icon = True
            self.setIconSeparatorColor(ToastNotification.DEFAULT_ICON_SEPARATOR_COLOR)
            self.setShowDurationBar(True)
            self.setTitleColor(ToastNotification.DEFAULT_TITLE_COLOR)
            self.setTextColor(ToastNotification.DEFAULT_TEXT_COLOR)

        elif (preset == ToastPreset.SUCCESS_DARK
                or preset == ToastPreset.WARNING_DARK
                or preset == ToastPreset.ERROR_DARK
                or preset == ToastPreset.INFORMATION_DARK):
            self.setBackgroundColor(ToastNotification.DEFAULT_BACKGROUND_COLOR_DARK)
            self.setCloseButtonIconColor(ToastNotification.DEFAULT_CLOSE_BUTTON_COLOR_DARK)
            self.show_icon = True
            self.setIconSeparatorColor(ToastNotification.DEFAULT_ICON_SEPARATOR_COLOR_DARK)
            self.setShowDurationBar(True)
            self.setTitleColor(ToastNotification.DEFAULT_TITLE_COLOR_DARK)
            self.setTextColor(ToastNotification.DEFAULT_TEXT_COLOR_DARK)

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
                                              'border-bottom-right-radius: {}px;'
                                              .format(self.duration_bar_color.red(),
                                                      self.duration_bar_color.green(),
                                                      self.duration_bar_color.blue(),
                                                      self.border_radius,
                                                      self.border_radius if self.duration == 0 else 0))

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
    def __get_icon_from_enum(enum_icon: ToastIcon):
        if enum_icon == ToastIcon.SUCCESS:
            return QPixmap(ToastNotification.__get_directory() + '/icons/success.png')
        elif enum_icon == ToastIcon.WARNING:
            return QPixmap(ToastNotification.__get_directory() + '/icons/warning.png')
        elif enum_icon == ToastIcon.ERROR:
            return QPixmap(ToastNotification.__get_directory() + '/icons/error.png')
        elif enum_icon == ToastIcon.INFORMATION:
            return QPixmap(ToastNotification.__get_directory() + '/icons/information.png')
        elif enum_icon == ToastIcon.CLOSE:
            return QPixmap(ToastNotification.__get_directory() + '/icons/close.png')
        else:
            return None

    @staticmethod
    def getMaximumOnScreen():
        return ToastNotification.maximum_on_screen

    @staticmethod
    def setMaximumOnScreen(maximum_on_screen: int):
        ToastNotification.maximum_on_screen = maximum_on_screen

    @staticmethod
    def getSpacing():
        return ToastNotification.spacing

    @staticmethod
    def setSpacing(spacing: int):
        ToastNotification.spacing = spacing

    @staticmethod
    def getOffsetX() -> int:
        return ToastNotification.offset_x

    @staticmethod
    def setOffsetX(offset_x: int):
        ToastNotification.offset_x = offset_x

    @staticmethod
    def getOffsetY() -> int:
        return ToastNotification.offset_y

    @staticmethod
    def setOffsetY(offset_y: int):
        ToastNotification.offset_y = offset_y

    @staticmethod
    def getOffset() -> tuple[int, int]:
        return ToastNotification.offset_x, ToastNotification.offset_y

    @staticmethod
    def setOffset(offset_x: int, offset_y: int):
        ToastNotification.offset_x = offset_x
        ToastNotification.offset_y = offset_y

    @staticmethod
    def isAlwaysOnMainScreen() -> bool:
        return ToastNotification.always_on_main_screen

    @staticmethod
    def setAlwaysOnMainScreen(on: bool):
        ToastNotification.always_on_main_screen = on

    @staticmethod
    def getPosition() -> ToastPosition:
        return ToastNotification.position

    @staticmethod
    def setPosition(position: int):
        if (position == ToastPosition.BOTTOM_RIGHT
                or position == ToastPosition.BOTTOM_LEFT
                or position == ToastPosition.BOTTOM_MIDDLE
                or position == ToastPosition.TOP_RIGHT
                or position == ToastPosition.TOP_LEFT
                or position == ToastPosition.TOP_MIDDLE):
            ToastNotification.position = position

    @staticmethod
    def getCount() -> int:
        return len(ToastNotification.currently_shown) + len(ToastNotification.queue)

    @staticmethod
    def getVisibleCount() -> int:
        return len(ToastNotification.currently_shown)

    @staticmethod
    def getQueueCount() -> int:
        return len(ToastNotification.queue)
