#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fbs_runtime.application_context.PyQt5 import ApplicationContext
from fbs_runtime.application_context import cached_property

from PyQt5.QtWidgets import (
    QApplication,
    QMessageBox,
    QSystemTrayIcon,
    QMenu,
    QAction,
    QWidgetAction,
    QLabel,
    QSizePolicy,
    QScrollArea,
)
from PyQt5.QtCore import pyqtSlot, QTimer, QPoint, Qt, QSettings
from PyQt5.QtGui import QCursor, QIcon, QPixmap, QPalette

import darkdetect
import sys
from image_selector import ImageSelector

class AppContext(ApplicationContext):
    def run(self):
        my_tray = TrayIcon(self)
        my_tray.show()

        return self.app.exec_()

    def config(self):
        return self.get_resource("config.ini")

    @cached_property
    def icons(self):
        return {
            "icon-light": QIcon(
                self.get_resource("images/icon-light.png")
            ),
            "icon-dark": QIcon(
                self.get_resource("images/icon-dark.png")
            )
        }


class TrayIcon(QSystemTrayIcon):
    def __init__(self, ctx, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.activated.connect(self.icon_activated_slot)
        self.messageClicked.connect(self.message_clicked_slot)
        self.ctx = ctx

        self.config = self.loadConfig()
        self.imageSelector = ImageSelector(['/tmp/test_with_images'])
        self.last_theme = darkdetect.theme().lower()
        self.updateIcon()
        self._timer = QTimer()
        self._timer.setInterval(3000)
        self._timer.timeout.connect(self.recurring_timer)
        self._timer.start()
        self.create_menu()

    def loadConfig(self):
        config = QSettings(self.ctx.config(), QSettings.IniFormat)
        return config

    def updateConfig(self, key, value):
        self.config.setValue(key, value)
        self.config.sync()

    def create_menu(self):
        _menu = QMenu()

        self.imageLabel = QLabel()
        self.updateImage()
        label_action = QWidgetAction(self.imageLabel)
        label_action.setDefaultWidget(self.imageLabel)
        _menu.addAction(label_action)

        _menu.addSeparator()

        quiteA = QAction("Exit", _menu)
        quiteA.triggered.connect(self.exit_slot)
        _menu.addAction(quiteA)

        self._menu = _menu
        self.setContextMenu(self._menu)

    def updateImage(self):
        # pixmap = QPixmap(self.ctx.get_resource("images/img.jpg"))
        pixmap = QPixmap(self.imageSelector.get_next_image())
        pixmap = pixmap.scaledToWidth(400)
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setStyleSheet("QLabel {margin: 20px;}")

    @pyqtSlot()
    def exit_slot(self):
        reply = QMessageBox.question(
            None, "Message", "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._timer.stop()
            self._menu.deleteLater()
            self.hide()
            QApplication.instance().exit(0)

    @pyqtSlot()
    def recurring_timer(self):
        theme = darkdetect.theme().lower()

        img = self.imageSelector.get_next_image()
        print(f"changing image to {img} ...")
        self.updateImage()

        if theme != self.last_theme:
            self.last_theme = theme
            self.updateIcon()

    def updateIcon(self):
        icon = f"icon-{self.last_theme}"

        self.setIcon(self.ctx.icons[icon])

    def icon_activated_slot(self, reason):
        # print("icon_activated_slot")
        if reason == QSystemTrayIcon.Unknown:
            # print("QSystemTrayIcon.Unknown")
            pass
        elif reason == QSystemTrayIcon.Context:
            # print("QSystemTrayIcon.Context")
            pass
        elif reason == QSystemTrayIcon.DoubleClick:
            # print("QSystemTrayIcon.DoubleClick")
            pass
        elif reason == QSystemTrayIcon.Trigger:
            # print("QSystemTrayIcon.Trigger")
            pass
        elif reason == QSystemTrayIcon.MiddleClick:
            # print("QSystemTrayIcon.MiddleClick")
            current_mouse_cursor = QCursor.pos() - QPoint(50, 50)
            menu = self.contextMenu()
            menu.popup(current_mouse_cursor)

    @pyqtSlot()
    def message_clicked_slot(self):
        pass
        # print("message was clicked")

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Message", "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._timer.stop()
            self._menu.deleteLater()
            self.hide()
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    appctxt = AppContext()

    exit_code = appctxt.run()
    sys.exit(exit_code)
