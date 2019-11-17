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
    QFileDialog,
)
from PyQt5.QtCore import pyqtSlot, QTimer, QPoint, Qt, QSettings
from PyQt5.QtGui import QCursor, QIcon, QPixmap, QPalette

import darkdetect
import sys
from image_selector import ImageSelector
from os.path import expanduser

class AppContext(ApplicationContext):
    def run(self):
        my_tray = TrayIcon(self)
        my_tray.show()

        return self.app.exec_()

    def config(self):
        return self.get_resource("config.ini")

    @cached_property
    def stock(self):
        """
        stock images to show when user first open the application.
        """
        return self.get_resource("stock")

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
        self.directories = []

        if self.configBool("config/show_stock"):
            self.imageSelector = ImageSelector([self.ctx.stock])
        else:
            source_directory = self.config.value("config/source_directory")
            if source_directory:
                self.directories = [source_directory]
            self.imageSelector = ImageSelector(self.directories)

        self.next_image = None
        self.last_theme = darkdetect.theme().lower()
        self.updateIcon()
        self._timer = None
        self.create_menu()

    def configBool(self, key):
        val = self.config.value(key)

        if not val:
            return False

        val = int(val)

        if val:
            return True
        else:
            return False


    def updateConfigBool(self, key, value):
        val = 0
        if value:
            val = 1

        self.updateConfig(key, val)

    def loadConfig(self):
        config = QSettings(self.ctx.config(), QSettings.IniFormat)
        return config

    def updateConfig(self, key, value):
        self.config.setValue(key, value)
        self.config.sync()
        self.reloadImageSelector()

    def reloadImageSelector(self):
        directories = []

        if self.configBool("config/show_stock"):
            directories = [self.ctx.stock]
        elif self.config.value("config/source_directory"):
            directories = [self.config.value("config/source_directory")]

        self.imageSelector = ImageSelector(directories)

    def create_menu(self):
        _menu = QMenu()

        self.statsLabel = QLabel("")
        self.imageLabel = QLabel()
        self.updateImageStats()
        self.updateImage()
        label_action = QWidgetAction(self.imageLabel)
        label_action.setDefaultWidget(self.imageLabel)
        _menu.addAction(label_action)

        # add stats label
        label_action = QWidgetAction(self.statsLabel)
        label_action.setDefaultWidget(self.statsLabel)
        _menu.addAction(label_action)

        _menu.addSeparator()

        _submenu = QMenu(_menu)
        _submenu.setTitle("Preferences")
        _switch_submenu = QMenu(_submenu)
        _switch_submenu.setTitle("Image change action")

        self.onOpenAction = QAction("On Open", _switch_submenu)
        self.onOpenAction.setCheckable(True)

        self.onOpenAction.setChecked(self.configBool("config/switch_on_open"))
        self.onOpenAction.triggered.connect(self.onOpen)
        _switch_submenu.addAction(self.onOpenAction)

        self.onTimerAction = QAction("Every 3sec", _switch_submenu)
        self.onTimerAction.setCheckable(True)

        self.onTimerAction.setChecked(self.configBool("config/switch_every_interval"))
        self.onTimerAction.triggered.connect(self.onTimer)
        _switch_submenu.addAction(self.onTimerAction)

        _submenu.addMenu(_switch_submenu)

        self.manageDirectoryAction = QAction(self.getSourceLabel())
        self.manageDirectoryAction.triggered.connect(self.manageDirectory)
        _submenu.addAction(self.manageDirectoryAction)

        self.showStockAction = QAction("Show stock images (ignore source)")
        self.showStockAction.setCheckable(True)

        self.showStockAction.setChecked(self.configBool("config/show_stock"))
        self.showStockAction.triggered.connect(self.showStock)
        _submenu.addAction(self.showStockAction)

        _menu.addMenu(_submenu)

        quiteA = QAction("Exit", _menu)
        quiteA.triggered.connect(self.exit_slot)
        _menu.addAction(quiteA)

        self._menu = _menu
        self.setContextMenu(self._menu)

    def getSourceLabel(self):
        label = "📌 Update source"
        config_value = self.config.value("config/source_directory")
        if config_value:
            label = label + f" ({self.trim(config_value)})"

        return label

    def trim(self, name):
        max_width = 30
        if len(name) > max_width:
            start = name[:max_width-15]
            end = name[-15:]
            name = start + '...' + end

        return name

    def manageDirectory(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.DirectoryOnly)
        file_dialog.setDirectory(expanduser("~"))

        if file_dialog.exec_():
            selected_dir = file_dialog.selectedFiles()[0]

            if not selected_dir:
                return

            if self.configBool("config/show_stock"):
                self.updateConfigBool("config/show_stock", False)
                self.showStockAction.setChecked(False)

            self.updateConfig("config/source_directory", selected_dir)
            self.manageDirectoryAction.setText(self.getSourceLabel())

    def updateImageStats(self):
        if not self.next_image:
            return None

        stats = self.next_image["stats"]
        self.statsLabel.setText(f'Image: <font face="tahoma" color="#45688E">{stats["name"]}</font> <span style="opacity:0.7">({stats["pos"]}/{stats["total"]})</span>')
        self.statsLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.statsLabel.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.statsLabel.setStyleSheet("QLabel {margin: 10px; margin-left: 20px;}")


    def updateImage(self):
        self.next_image = self.imageSelector.get_next_image_with_stats()
        if not self.next_image:
            self.imageLabel = QLabel("No Images Found")
            self.imageLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.imageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.imageLabel.setMargin(80)
            if self.last_theme == "dark":
                color = "white"
            else:
                color = "black"

            self.imageLabel.setStyleSheet(f"QLabel {{color: {color}; font-size: 20px}}")
        else:
            pixmap = QPixmap(self.next_image["img"])
            # pixmap = pixmap.scaledToWidth(400)
            pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio)
            self.imageLabel.setPixmap(pixmap)
            self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            self.imageLabel.setScaledContents(True)
            self.imageLabel.setAlignment(Qt.AlignCenter)
            self.imageLabel.setStyleSheet("QLabel {margin: 20px;  margin-bottom: 0px;}") # accomodate for the stats label
            self.updateImageStats()

    @pyqtSlot()
    def onOpen(self):
        self.updateConfigBool("config/switch_on_open", self.onOpenAction.isChecked())

    @pyqtSlot()
    def showStock(self):
        self.updateConfigBool("config/show_stock", self.showStockAction.isChecked())

    @pyqtSlot()
    def onTimer(self):
        self.updateConfigBool("config/switch_every_interval", self.onTimerAction.isChecked())

        if self.onTimerAction.isChecked():
            if self._timer:
                self._timer.stop()
            self._timer = QTimer()
            self._timer.setInterval(3000)
            self._timer.timeout.connect(self.recurring_timer)
            self._timer.start()
        else:
            if self._timer:
                self._timer.stop()


    @pyqtSlot()
    def exit_slot(self):
        reply = QMessageBox.question(
            None, "Message", "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self._timer:
                self._timer.stop()
            self._menu.deleteLater()
            self.hide()
            QApplication.instance().exit(0)

    @pyqtSlot()
    def recurring_timer(self):
        self.update()

    def update(self):
        theme = darkdetect.theme().lower()

        self.updateImage()

        if theme != self.last_theme:
            self.last_theme = theme
            self.updateIcon()

    def updateIcon(self):
        icon = f"icon-{self.last_theme}"

        self.setIcon(self.ctx.icons[icon])

    def icon_activated_slot(self, reason):
        if reason == QSystemTrayIcon.Unknown:
            pass
        elif reason == QSystemTrayIcon.Context:
            pass
        elif reason == QSystemTrayIcon.DoubleClick:
            pass
        elif reason == QSystemTrayIcon.Trigger or reason == QSystemTrayIcon.DoubleClick:
            if self.onOpenAction.isChecked():
                self.update()
        elif reason == QSystemTrayIcon.MiddleClick:
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

