from __future__ import annotations

import os
from qtpy.QtWidgets import QWidget


class Utils:

    @staticmethod
    def get_current_directory() -> str:
        """Get the current directory path

        :return: directory path
        """

        return os.path.dirname(os.path.realpath(__file__))

    @staticmethod
    def get_top_level_parent(widget: QWidget) -> QWidget:
        """Get the top level parent of a widget. If the widget has no parent,
        the widget itself is considered the top level parent.

        :param widget: widget to calculate the top level parent on
        :return: top level parents
        """

        if widget.parent() is None:
            return widget

        parent = widget.parent()

        while parent.parent() is not None:
            parent = parent.parent()
        return parent

    @staticmethod
    def get_parents(widget: QWidget) -> list[QWidget]:
        """Get all the parents of a widget

        :param widget: the widget to get the parents of
        :return: parents of the widget
        """

        parents = []

        while widget.parent() is not None:
            parents.append(widget.parent())
            widget = widget.parent()
        return parents
