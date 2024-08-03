import random
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (QMainWindow, QPushButton, QComboBox, QVBoxLayout, QCheckBox, QWidget,
                             QGroupBox, QGridLayout, QSpinBox, QLineEdit, QHBoxLayout, QLabel, QFormLayout)
from pyqttoast import Toast, ToastPreset, ToastIcon, ToastPosition, ToastButtonAlignment


class Window(QMainWindow):
    def __init__(self):
        super().__init__(parent=None)

        # Window settings
        self.setFixedSize(650, 360)
        self.setWindowTitle('PyQt Toast Demo')

        # Create grid layout
        grid = QGridLayout()
        grid.addWidget(self.create_static_settings_group(), 0, 0)
        grid.addWidget(self.create_toast_preset_group(), 1, 0)
        grid.addWidget(self.create_toast_custom_group(), 0, 1, 2, 1, Qt.AlignmentFlag.AlignTop)

        # Apply layout
        central_widget = QWidget()
        central_widget.setLayout(grid)
        self.setCentralWidget(central_widget)
        self.setFocus()

    def create_static_settings_group(self):
        group_box = QGroupBox("Static Settings")

        # Create widgets
        self.maximum_on_screen_spinbox = QSpinBox()
        self.maximum_on_screen_spinbox.setRange(1, 10)
        self.maximum_on_screen_spinbox.setValue(Toast.getMaximumOnScreen())
        self.maximum_on_screen_spinbox.setFixedHeight(24)

        self.spacing_spinbox = QSpinBox()
        self.spacing_spinbox.setRange(0, 100)
        self.spacing_spinbox.setValue(Toast.getSpacing())
        self.spacing_spinbox.setFixedHeight(24)

        self.offset_x_spinbox = QSpinBox()
        self.offset_x_spinbox.setRange(0, 500)
        self.offset_x_spinbox.setValue(Toast.getOffsetX())
        self.offset_x_spinbox.setFixedHeight(24)

        self.offset_y_spinbox = QSpinBox()
        self.offset_y_spinbox.setRange(0, 500)
        self.offset_y_spinbox.setValue(Toast.getOffsetY())
        self.offset_y_spinbox.setFixedHeight(24)

        self.always_on_main_screen_checkbox = QCheckBox('Always on main screen')

        self.position_dropdown = QComboBox()
        self.position_dropdown.addItems(['BOTTOM_LEFT', 'BOTTOM_MIDDLE',
                                         'BOTTOM_RIGHT', 'TOP_LEFT',
                                         'TOP_MIDDLE', 'TOP_RIGHT', 'CENTER'])
        self.position_dropdown.setCurrentIndex(2)
        self.position_dropdown.setFixedHeight(26)

        self.update_button = QPushButton('Update')
        self.update_button.setFixedHeight(32)
        self.update_button.clicked.connect(self.update_static_settings)

        # Add widgets to layout
        form_layout = QFormLayout()
        form_layout.addRow('Max on screen:', self.maximum_on_screen_spinbox)
        form_layout.addRow('Spacing:', self.spacing_spinbox)
        form_layout.addRow('Offset X:', self.offset_x_spinbox)
        form_layout.addRow('Offset Y:', self.offset_y_spinbox)
        form_layout.addRow('Position:', self.position_dropdown)

        # Add layout and widgets to main layout
        vbox_layout = QVBoxLayout()
        vbox_layout.addLayout(form_layout)
        vbox_layout.addWidget(self.always_on_main_screen_checkbox)
        vbox_layout.addWidget(self.update_button)
        vbox_layout.addStretch(1)
        group_box.setLayout(vbox_layout)

        return group_box

    def create_toast_preset_group(self):
        group_box = QGroupBox("Toast Presets")

        # Create widgets
        self.preset_dropdown = QComboBox()
        self.preset_dropdown.addItems(['SUCCESS', 'WARNING',
                                       'ERROR', 'INFORMATION',
                                       'SUCCESS_DARK', 'WARNING_DARK',
                                       'ERROR_DARK', 'INFORMATION_DARK'])
        self.preset_dropdown.setFixedHeight(26)

        self.show_preset_toast_button = QPushButton('Show preset toast')
        self.show_preset_toast_button.clicked.connect(self.show_preset_toast)
        self.show_preset_toast_button.setFixedHeight(32)

        # Add widgets to layout
        vbox_layout = QVBoxLayout()
        vbox_layout.addWidget(self.preset_dropdown)
        vbox_layout.addWidget(self.show_preset_toast_button)
        vbox_layout.addStretch(1)
        group_box.setLayout(vbox_layout)

        return group_box

    def create_toast_custom_group(self):
        group_box = QGroupBox("Custom Toast")

        # Create widgets
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setRange(0, 50000)
        self.duration_spinbox.setValue(5000)
        self.duration_spinbox.setFixedHeight(24)

        self.title_input = QLineEdit('Lorem ipsum dolor sit')
        self.title_input.setFixedHeight(24)

        self.text_input = QLineEdit('Lorem ipsum dolor sit amet consetetur')
        self.text_input.setFixedHeight(24)

        self.border_radius_spinbox = QSpinBox()
        self.border_radius_spinbox.setRange(0, 20)
        self.border_radius_spinbox.setValue(2)
        self.border_radius_spinbox.setFixedHeight(24)

        self.show_icon_checkbox = QCheckBox('Show icon')

        self.icon_dropdown = QComboBox()
        self.icon_dropdown.addItems(['SUCCESS', 'WARNING', 'ERROR',
                                     'INFORMATION', 'CLOSE'])
        self.icon_dropdown.setFixedHeight(24)

        self.icon_size_spinbox = QSpinBox()
        self.icon_size_spinbox.setRange(5, 50)
        self.icon_size_spinbox.setValue(18)
        self.icon_size_spinbox.setFixedHeight(24)

        self.show_duration_bar_checkbox = QCheckBox('Show duration bar')
        self.show_duration_bar_checkbox.setChecked(True)

        self.reset_on_hover_checkbox = QCheckBox('Reset duration on hover')
        self.reset_on_hover_checkbox.setChecked(True)

        self.close_button_settings_dropdown = QComboBox()
        self.close_button_settings_dropdown.addItems(['TOP', 'MIDDLE', 'BOTTOM', 'DISABLED'])
        self.close_button_settings_dropdown.setFixedHeight(24)

        self.min_width_spinbox = QSpinBox()
        self.min_width_spinbox.setRange(0, 1000)
        self.min_width_spinbox.setFixedHeight(24)

        self.max_width_spinbox = QSpinBox()
        self.max_width_spinbox.setRange(0, 1000)
        self.max_width_spinbox.setValue(1000)
        self.max_width_spinbox.setFixedHeight(24)

        self.min_height_spinbox = QSpinBox()
        self.min_height_spinbox.setRange(0, 1000)
        self.min_height_spinbox.setFixedHeight(24)

        self.max_height_spinbox = QSpinBox()
        self.max_height_spinbox.setRange(0, 1000)
        self.max_height_spinbox.setValue(1000)
        self.max_height_spinbox.setFixedHeight(24)

        self.fade_in_duration_spinbox = QSpinBox()
        self.fade_in_duration_spinbox.setRange(0, 1000)
        self.fade_in_duration_spinbox.setValue(250)
        self.fade_in_duration_spinbox.setFixedHeight(24)

        self.fade_out_duration_spinbox = QSpinBox()
        self.fade_out_duration_spinbox.setRange(0, 1000)
        self.fade_out_duration_spinbox.setValue(250)
        self.fade_out_duration_spinbox.setFixedHeight(24)

        self.custom_toast_button = QPushButton('Show custom toast')
        self.custom_toast_button.setFixedHeight(32)
        self.custom_toast_button.clicked.connect(self.show_custom_toast)

        # Add widgets to layouts
        form_layout = QFormLayout()
        form_layout.addRow('Duration:', self.duration_spinbox)
        form_layout.addRow('Title:', self.title_input)
        form_layout.addRow('Text:', self.text_input)

        icon_size_layout = QFormLayout()
        icon_size_layout.addRow('Icon size:', self.icon_size_spinbox)
        icon_size_layout.setContentsMargins(20, 0, 0, 0)

        icon_layout = QHBoxLayout()
        icon_layout.addWidget(self.show_icon_checkbox)
        icon_layout.addWidget(self.icon_dropdown)
        icon_layout.addLayout(icon_size_layout)
        icon_layout.setContentsMargins(0, 5, 0, 3)

        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(self.show_duration_bar_checkbox)
        checkbox_layout.addWidget(self.reset_on_hover_checkbox)
        checkbox_layout.setContentsMargins(0, 0, 0, 5)

        double_form_layout_1 = QHBoxLayout()
        double_form_layout_1.addWidget(QLabel('Border radius:'))
        double_form_layout_1.addWidget(self.border_radius_spinbox)
        double_form_layout_1.addWidget(QLabel('Close button:'))
        double_form_layout_1.addWidget(self.close_button_settings_dropdown)

        double_form_layout_2 = QHBoxLayout()
        double_form_layout_2.addWidget(QLabel('Min width:'))
        double_form_layout_2.addWidget(self.min_width_spinbox)
        double_form_layout_2.addWidget(QLabel('Max width:'))
        double_form_layout_2.addWidget(self.max_width_spinbox)

        double_form_layout_3 = QHBoxLayout()
        double_form_layout_3.addWidget(QLabel('Min height:'))
        double_form_layout_3.addWidget(self.min_height_spinbox)
        double_form_layout_3.addWidget(QLabel('Max height:'))
        double_form_layout_3.addWidget(self.max_height_spinbox)

        double_form_layout_4 = QHBoxLayout()
        double_form_layout_4.addWidget(QLabel('Fade in duration:'))
        double_form_layout_4.addWidget(self.fade_in_duration_spinbox)
        double_form_layout_4.addWidget(QLabel('Fade out duration:'))
        double_form_layout_4.addWidget(self.fade_out_duration_spinbox)
        double_form_layout_4.setContentsMargins(0, 0, 0, 3)

        # Add layouts and widgets to main layout
        vbox_layout = QVBoxLayout()
        vbox_layout.addLayout(form_layout)
        vbox_layout.addLayout(icon_layout)
        vbox_layout.addLayout(checkbox_layout)
        vbox_layout.addLayout(double_form_layout_1)
        vbox_layout.addLayout(double_form_layout_2)
        vbox_layout.addLayout(double_form_layout_3)
        vbox_layout.addLayout(double_form_layout_4)
        vbox_layout.addWidget(self.custom_toast_button)
        vbox_layout.addStretch(1)
        group_box.setLayout(vbox_layout)

        return group_box

    def update_static_settings(self):
        # Update the static settings of the Toast class
        Toast.setMaximumOnScreen(self.maximum_on_screen_spinbox.value())
        Toast.setSpacing(self.spacing_spinbox.value())
        Toast.setOffset(self.offset_x_spinbox.value(), self.offset_y_spinbox.value())
        Toast.setAlwaysOnMainScreen(self.always_on_main_screen_checkbox.isChecked())

        position = self.position_dropdown.currentText()
        if position == 'BOTTOM_LEFT':
            Toast.setPosition(ToastPosition.BOTTOM_LEFT)
        elif position == 'BOTTOM_MIDDLE':
            Toast.setPosition(ToastPosition.BOTTOM_MIDDLE)
        elif position == 'BOTTOM_RIGHT':
            Toast.setPosition(ToastPosition.BOTTOM_RIGHT)
        elif position == 'TOP_LEFT':
            Toast.setPosition(ToastPosition.TOP_LEFT)
        elif position == 'TOP_MIDDLE':
            Toast.setPosition(ToastPosition.TOP_MIDDLE)
        elif position == 'TOP_RIGHT':
            Toast.setPosition(ToastPosition.TOP_RIGHT)
        elif position == 'CENTER':
            Toast.setPosition(ToastPosition.CENTER)

    def show_preset_toast(self):
        # Show toast with selected preset and random duration
        toast = Toast(self)
        toast.setDuration(random.randint(2000, 5000))

        selected_preset = self.preset_dropdown.currentText()

        if selected_preset == 'SUCCESS':
            toast.setTitle('Success! Confirmation email sent.')
            toast.setText('Check your email to complete signup.')
            toast.applyPreset(ToastPreset.SUCCESS)

        elif selected_preset == 'SUCCESS_DARK':
            toast.setTitle('Success! Confirmation email sent.')
            toast.setText('Check your email to complete signup.')
            toast.applyPreset(ToastPreset.SUCCESS_DARK)

        elif selected_preset == 'WARNING':
            toast.setTitle('Warning! Passwords do not match.')
            toast.setText('Please confirm your password again.')
            toast.applyPreset(ToastPreset.WARNING)

        elif selected_preset == 'WARNING_DARK':
            toast.setTitle('Warning! Passwords do not match.')
            toast.setText('Please confirm your password again.')
            toast.applyPreset(ToastPreset.WARNING_DARK)

        elif selected_preset == 'ERROR':
            toast.setTitle('Error! Cannot complete request.')
            toast.setText('Please try again in a few minutes.')
            toast.applyPreset(ToastPreset.ERROR)

        elif selected_preset == 'ERROR_DARK':
            toast.setTitle('Error! Cannot complete request.')
            toast.setText('Please try again in a few minutes.')
            toast.applyPreset(ToastPreset.ERROR_DARK)

        elif selected_preset == 'INFORMATION':
            toast.setTitle('Info: Restart required.')
            toast.setText('Please restart the application.')
            toast.applyPreset(ToastPreset.INFORMATION)

        elif selected_preset == 'INFORMATION_DARK':
            toast.setTitle('Info: Restart required.')
            toast.setText('Please restart the application.')
            toast.applyPreset(ToastPreset.INFORMATION_DARK)

        toast.show()

    def show_custom_toast(self):
        # Show custom toast with selected settings
        toast = Toast(self)
        toast.setDuration(self.duration_spinbox.value())
        toast.setTitle(self.title_input.text())
        toast.setText(self.text_input.text())
        toast.setBorderRadius(self.border_radius_spinbox.value())
        toast.setShowIcon(self.show_icon_checkbox.isChecked())
        toast.setIconSize(QSize(self.icon_size_spinbox.value(), self.icon_size_spinbox.value()))
        toast.setShowDurationBar(self.show_duration_bar_checkbox.isChecked())
        toast.setResetDurationOnHover(self.reset_on_hover_checkbox.isChecked())
        toast.setMinimumWidth(self.min_width_spinbox.value())
        toast.setMaximumWidth(self.max_width_spinbox.value())
        toast.setMinimumHeight(self.min_height_spinbox.value())
        toast.setMaximumHeight(self.max_height_spinbox.value())
        toast.setFadeInDuration(self.fade_in_duration_spinbox.value())
        toast.setFadeOutDuration(self.fade_out_duration_spinbox.value())

        selected_icon = self.icon_dropdown.currentText()
        if selected_icon == 'SUCCESS':
            toast.setIcon(ToastIcon.SUCCESS)
        elif selected_icon == 'WARNING':
            toast.setIcon(ToastIcon.WARNING)
        elif selected_icon == 'ERROR':
            toast.setIcon(ToastIcon.ERROR)
        elif selected_icon == 'INFORMATION':
            toast.setIcon(ToastIcon.INFORMATION)
        elif selected_icon == 'CLOSE':
            toast.setIcon(ToastIcon.CLOSE)

        selected_close_button_setting = self.close_button_settings_dropdown.currentText()
        if selected_close_button_setting == 'TOP':
            toast.setCloseButtonAlignment(ToastButtonAlignment.TOP)
        elif selected_close_button_setting == 'MIDDLE':
            toast.setCloseButtonAlignment(ToastButtonAlignment.MIDDLE)
        elif selected_close_button_setting == 'BOTTOM':
            toast.setCloseButtonAlignment(ToastButtonAlignment.BOTTOM)
        elif selected_close_button_setting == 'DISABLED':
            toast.setShowCloseButton(False)

        toast.show()
