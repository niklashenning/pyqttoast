import math
import os
from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint, QTimer, QSize, QMargins, QRect
from PyQt5.QtGui import QPixmap, QIcon, QColor, QFont, QImage, qRgba, QFontMetrics
from PyQt5.QtWidgets import QDialog, QPushButton, QLabel, QGraphicsOpacityEffect, QWidget, QApplication


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
        self.icon = QPixmap(ToastNotification.__get_directory() + '/icons/check-mark.png')
        self.showing_icon = True
        self.icon_size = QSize(16, 16)
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
        self.margins = QMargins(20, 18, 10, 18)
        self.icon_margins = QMargins(0, 0, 15, 0)
        self.icon_section_margins = QMargins(0, 0, 15, 0)
        self.text_section_margins = QMargins(0, 0, 15, 0)
        self.close_button_margins = QMargins(0, -8, 0, -8)
        self.text_section_spacing = 10

        self.elapsed_time = 0

        # Window settings
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.NoFocus)

        # Notification widget (QLabel because QWidget has weird behaviour with stylesheets)
        self.notification = QLabel(self)

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
        self.icon_label = QLabel(self.notification)

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
        # Setup UI
        self.__setup_ui()

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

    def __setup_ui(self):
        # Update widgets
        self.__update_stylesheet()

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
        duration_bar_height = 0 if not self.showing_duration_bar else self.duration_bar_container.height()

        # Calculate icon section width and height
        icon_section_width = 0
        icon_section_height = 0

        if self.showing_icon:
            icon_section_width = (self.icon_section_margins.left()
                                  + self.icon_margins.left() + self.icon_label.width()
                                  + self.icon_margins.right() + self.icon_separator.width()
                                  + self.icon_section_margins.right())
            icon_section_height = (self.icon_section_margins.top() + self.icon_margins.top()
                                   + self.icon_label.height() + self.icon_margins.bottom()
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

        # Resize window
        self.resize(width, height)
        self.notification.setFixedSize(width, height)

        # Calculate difference between height and height of icon section
        height_icon_section_height_difference = (max(icon_section_height,
                                                     text_section_height,
                                                     close_button_section_height)
                                                 - icon_section_height)

        if self.showing_icon:
            # Move icon
            self.icon_label.move(self.margins.left()
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
                                     + self.icon_label.width()
                                     + self.icon_margins.right(),
                                     self.margins.top()
                                     + self.icon_section_margins.top()
                                     + math.ceil(forced_additional_height / 2)
                                     - math.floor(forced_reduced_height / 2))

            # Show icon section
            self.icon_label.setVisible(True)
            self.icon_separator.setVisible(True)
        else:
            # Hide icon section
            self.icon_label.setVisible(False)
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
        if self.showing_icon:
            self.title_label.move(self.margins.left()
                                  + self.icon_section_margins.left()
                                  + self.icon_margins.left()
                                  + self.icon_label.width()
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
                                 + self.icon_label.width()
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

        # Move close button to top, middle, or bottom position
        if self.close_button_alignment == ToastNotification.CLOSE_BUTTON_TOP:
            self.close_button.move(width - self.close_button.width()
                                   - self.close_button_margins.right() - self.margins.right(),
                                   self.margins.top() + self.close_button_margins.top())
        elif self.close_button_alignment == ToastNotification.CLOSE_BUTTON_MIDDLE:
            self.close_button.move(width - self.close_button.width()
                                   - self.close_button_margins.right() - self.margins.right(),
                                   math.ceil((height - self.close_button.height()
                                              - duration_bar_height) / 2))
        elif self.close_button_alignment == ToastNotification.CLOSE_BUTTON_BOTTOM:
            self.close_button.move(width - self.close_button.width()
                                   - self.close_button_margins.right() - self.margins.right(),
                                   height - self.close_button.height()
                                   - self.margins.bottom()
                                   - self.close_button_margins.bottom() - duration_bar_height)

        # Resize, move, and show duration bar if enabled
        if self.showing_duration_bar:
            self.duration_bar_container.setFixedWidth(width)
            self.duration_bar_container.move(0, height - duration_bar_height)
            self.duration_bar.setFixedWidth(width)
            self.duration_bar_chunk.setFixedWidth(width)
            self.duration_bar_container.setVisible(True)
        else:
            self.duration_bar_container.setVisible(False)

    def setDuration(self, duration: int):
        self.duration = duration

    def showDurationBar(self, on: bool):
        self.showing_duration_bar = on

    def setTitle(self, title: str):
        self.title = title
        self.title_label.setText(title)

    def setText(self, text: str):
        self.text = text
        self.text_label.setText(text)

    def setIcon(self, icon: QPixmap):
        self.icon = icon
        self.icon_label.setPixmap(icon)
        self.setIconColor(self.icon_color)

    def setIconSize(self, size: QSize):
        self.icon_size = size
        self.icon = self.icon.scaled(size.width(), size.height())
        self.icon_label.setPixmap(self.icon)
        self.icon_label.setFixedSize(size)

    def setIconWidth(self, width: int):
        self.icon_size.setWidth(width)
        self.icon = self.icon.scaled(self.icon_size.width(), self.icon_size.height())
        self.icon_label.setPixmap(self.icon)
        self.icon_label.setFixedSize(self.icon_size)

    def setIconHeight(self, height: int):
        self.icon_size.setHeight(height)
        self.icon = self.icon.scaled(self.icon_size.width(), self.icon_size.height())
        self.icon_label.setPixmap(self.icon)
        self.icon_label.setFixedSize(self.icon_size)

    def showIcon(self, on: bool):
        self.showing_icon = on

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

    def setCloseButtonIcon(self, icon: QPixmap):
        self.close_button_icon = QIcon(icon)
        self.close_button.setIcon(self.close_button_icon)
        self.setCloseButtonColor(self.close_button_color)

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

    def setTextSectionSpacing(self, spacing: int):
        self.text_section_spacing = spacing

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