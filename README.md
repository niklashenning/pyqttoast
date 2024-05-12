# PyQt Toast

[![PyPI](https://img.shields.io/badge/pypi-v1.2.0-blue)](https://pypi.org/project/pyqt-toast-notification/)
[![Python](https://img.shields.io/badge/python-3.7+-blue)](https://github.com/niklashenning/pyqttoast)
[![Build](https://img.shields.io/badge/build-passing-neon)](https://github.com/niklashenning/pyqttoast)
[![Coverage](https://img.shields.io/badge/coverage-95%25-green)](https://github.com/niklashenning/pyqttoast)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/niklashenning/pyqttoast/blob/master/LICENSE)

A fully customizable and modern toast notification library for PyQt and PySide

![pyqt-toast](https://github.com/niklashenning/pyqt-toast/assets/58544929/c104f10e-08df-4665-98d8-3785822a20dc)

## Features
* Supports showing multiple toasts at the same time
* Supports queueing of toasts
* Supports 7 different positions
* Supports multiple screens
* Modern and fully customizable UI
* Works with `PyQt5`, `PyQt6`, `PySide2`, and `PySide6`

## Installation
```
pip install pyqt-toast-notification
```

## Usage
Import the `Toast` class, instantiate it, and show the toast notification with the `show()` method:

```python
from PyQt6.QtWidgets import QMainWindow, QPushButton
from pyqttoast import Toast, ToastPreset


class Window(QMainWindow):
    def __init__(self):
        super().__init__(parent=None)

        # Add button and connect click event
        self.button = QPushButton(self)
        self.button.setText('Show toast')
        self.button.clicked.connect(self.show_toast)
    
    # Shows a toast notification every time the button is clicked
    def show_toast(self):
        toast = Toast(self)
        toast.setDuration(5000)  # Hide after 5 seconds
        toast.setTitle('Success! Confirmation email sent.')
        toast.setText('Check your email to complete signup.')
        toast.applyPreset(ToastPreset.SUCCESS)  # Apply style preset
        toast.show()
```

> **IMPORTANT:** <br>An instance of `Toast` can only be shown **once**. If you want to show another one, even if the content is exactly the same, you have to create another instance.


## Customization

* **Setting the position of the toasts (<u>static</u>):**
```python
Toast.setPosition(ToastPosition.BOTTOM_MIDDLE)  # Default: ToastPosition.BOTTOM_RIGHT
```
> **AVAILABLE POSITIONS:** <br> `BOTTOM_LEFT`, `BOTTOM_MIDDLE`, `BOTTOM_RIGHT`, `TOP_LEFT`, `TOP_MIDDLE`, `TOP_RIGHT`, `CENTER`


* **Setting a limit on how many toasts can be shown at the same time (<u>static</u>):**
```python
Toast.setMaximumOnScreen(5)  # Default: 3
```
> If you try to show more toasts than the maximum amount on screen, they will get added to a queue and get shown as soon as one of the currently showing toasts is closed.


* **Setting the vertical spacing between the toasts (<u>static</u>):**
```python
Toast.setSpacing(20)  # Default: 10
```

* **Setting the x and y offset of the toast position (<u>static</u>):**
```python
Toast.setOffset(30, 55)  # Default: 20, 45
```

* **Setting whether the toasts should always be shown on the main screen (<u>static</u>):**
```python
Toast.setAlwaysOnMainScreen(True)  # Default: False
```

* **Making the toast show forever until it is closed:**
```python
toast.setDuration(0)  # Default: 5000
```

* **Enabling or disabling the duration bar:**
```python
toast.setShowDurationBar(False)  # Default: True
```

* **Adding an icon:**
```python
toast.setIcon(ToastIcon.SUCCESS)  # Default: ToastIcon.INFORMATION
toast.setShowIcon(True)

# Or setting a custom icon:
toast.setIcon(QPixmap('path/to/your/icon.png'))
```
> **AVAILABLE ICONS:** <br> `SUCCESS`, `WARNING`, `ERROR`, `INFORMATION`, `CLOSE`

* **Setting the icon size:**
```python
toast.setIconSize(QSize(14, 14))  # Default: QSize(18, 18)
```

* **Enabling or disabling the icon separator:**
```python
toast.setShowIconSeparator(False)  # Default: True
```

* **Setting the close button alignment:**
```python
toast.setCloseButtonAlignment(ToastButtonAlignment.MIDDLE)  # Default: ToastButtonAlignment.TOP
```
> **AVAILABLE ALIGNMENTS:** <br> `TOP`, `MIDDLE`, `BOTTOM`

* **Enabling or disabling the close button:**
```python
toast.setShowCloseButton(False)  # Default: True
```

* **Customizing the duration of the fade animations (milliseconds):**
```python
toast.setFadeInDuration(100)   # Default: 250
toast.setFadeOutDuration(150)  # Default: 250
```

* **Enabling or disabling duration reset on hover:**

```python
toast.setResetDurationOnHover(False)  # Default: True
```

* **Making the corners rounded:**
```python
toast.setBorderRadius(3)  # Default: 0
```

* **Setting custom colors:**
```python
toast.setBackgroundColor(QColor('#292929'))       # Default: #E7F4F9
toast.setTitleColor(QColor('#FFFFFF'))            # Default: #000000
toast.setTextColor(QColor('#D0D0D0'))             # Default: #5C5C5C
toast.setDurationBarColor(QColor('#3E9141'))      # Default: #5C5C5C
toast.setIconColor(QColor('#3E9141'))             # Default: #5C5C5C
toast.setIconSeparatorColor(QColor('#585858'))    # Default: #D9D9D9
toast.setCloseButtonIconColor(QColor('#C9C9C9'))  # Default: #000000
```

* **Setting custom fonts:**
```python
# Init font
font = QFont()
font.setFamily('Times')
font.setPointSize(10)
font.setBold(True)

# Set fonts
toast.setTitleFont(font)
toast.setTextFont(font)
```

* **Applying a style preset:**
```python
toast.applyPreset(ToastPreset.ERROR)
```
> **AVAILABLE PRESETS:** <br> `SUCCESS`, `WARNING`, `ERROR`, `INFORMATION`, `SUCCESS_DARK`, `WARNING_DARK`, `ERROR_DARK`, `INFORMATION_DARK`

* **Setting toast size constraints:**
```python
# Minimum and maximum size
toast.setMinimumWidth(100)
toast.setMaximumWidth(350)
toast.setMinimumHeight(50)
toast.setMaximumHeight(120)

# Fixed size (not recommended)
toast.setFixedSize(QSize(350, 80))
```


**<br>Other customization options:**

| Option                     | Description                                                                     | Default                    |
|----------------------------|---------------------------------------------------------------------------------|----------------------------|
| `setFixedScreen()`         | Fixed screen where the toasts will be shown (static)                            | `None`                     |
| `setIconSeparatorWidth()`  | Width of the icon separator that separates the icon and text section            | `2`                        |
| `setCloseButtonIcon()`     | Icon of the close button                                                        | `ToastIcon.CLOSE`          |
| `setCloseButtonIconSize()` | Size of the close button icon                                                   | `QSize(10, 10)`            |
| `setCloseButtonSize()`     | Size of the close button                                                        | `QSize(24, 24)`            |
| `setStayOnTop()`           | Whether the toast stays on top of other windows even when they are focused      | `True`                     |
| `setTextSectionSpacing()`  | Vertical spacing between the title and the text                                 | `8`                        |
| `setMargins()`             | Margins around the whole toast content                                          | `QMargins(20, 18, 10, 18)` |
| `setIconMargins()`         | Margins around the icon                                                         | `QMargins(0, 0, 15, 0)`    |
| `setIconSectionMargins()`  | Margins around the icon section (the area with the icon and the icon separator) | `QMargins(0, 0, 15, 0)`    |
| `setTextSectionMargins()`  | Margins around the text section (the area with the title and the text)          | `QMargins(0, 0, 15, 0)`    |
| `setCloseButtonMargins()`  | Margins around the close button                                                 | `QMargins(0, -8, 0, -8)`   |

## Demo
https://github.com/niklashenning/pyqt-toast/assets/58544929/f4d7f4a4-6d69-4087-ae19-da54b6da499d

The demos for PyQt5, PyQt6, and PySide6 can be found in the [demo](demo) folder.

## Tests
Installing the required test dependencies [PyQt6](https://pypi.org/project/PyQt6/), [pytest](https://github.com/pytest-dev/pytest), and [coveragepy](https://github.com/nedbat/coveragepy):
```
pip install PyQt6 pytest coverage
```

To run the tests with coverage, clone this repository, go into the main directory and run:
```
coverage run -m pytest
coverage report --ignore-errors -m
```

## License
This software is licensed under the [MIT license](https://github.com/niklashenning/pyqttoast/blob/master/LICENSE).
