# -*- coding: utf-8 -*-
# Программа для конфигурирования модулей XBee

import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QAction, QDialog, QGridLayout,
                             QLabel, QLineEdit, QComboBox, QWidget, QVBoxLayout, QTabWidget, QGroupBox, QHBoxLayout,
                             QMessageBox)
from PyQt5.QtGui import (QIcon, QPixmap)
from PyQt5.QtCore import (pyqtSignal, QThread)
from XBee_connect import XBeeConnect
from digi.xbee.util.utils import hex_to_string
import time


module_type_dict = {'21': 'S2B ZigBee Coordinator API',
                    '23': 'S2B ZigBee Router API',
                    '26': 'S2B ZigBee Router/End Device, Analog I/O Adapter',
                    '27': 'S2B ZigBee Router/End Device, Digital I/O Adapter',
                    '29': 'S2B ZigBee End Device API',
                    '40': 'S2C Common Firmware'}


class MainWindow(QMainWindow):

    signal_start_connect = pyqtSignal()
    signal_read_info = pyqtSignal()
    signal_write_info = pyqtSignal(tuple)
    signal_disconnect_module = pyqtSignal()
    signal_info_type_s2c_dev = pyqtSignal()

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.init_ui()

        # создаем экзмепляр класса XBeeConnect
        self.xbee_connect = XBeeConnect(self)

    def start_connect_to_module_clicked(self):
        # создаем и подключаем поток
        self.connection_thread = QThread()
        self.xbee_connect.moveToThread(self.connection_thread)

        self.read_values()
        self.connection_thread.start()

        self.xbee_connect.successful_connection_signal.connect(self.success_connect)
        self.xbee_connect.error_connection_signal.connect(self.error_connect)

        self.signal_start_connect.emit()

    def read_info_clicked(self):

        self.signal_read_info.emit()

        self.pan_id_edit.setText(str(hex_to_string(self.xbee_connect.pan_id)))
        #self.coord_en_edit.setText(str(hex_to_string(self.xbee_connect.coord_en)))
        self.node_id_edit.setText(str(self.xbee_connect.node_id))

    def write_info_clicked(self):

        param_pan_id = self.pan_id_edit.text()
        #param_coord_en = self.coord_en_edit.text()
        param_node_id = self.node_id_edit.text()

        parameters_tuple = (param_pan_id, param_node_id)

        self.signal_write_info.emit(parameters_tuple)

        self.pan_id_edit.setText(str(hex_to_string(self.xbee_connect.new_pan_id)))
        #self.coord_en_edit.setText(str(hex_to_string(self.xbee_connect.new_coord_en)))
        self.node_id_edit.setText(str(self.xbee_connect.new_node_id))

    def disconnect_module_clicked(self):

        self.signal_disconnect_module.emit()
        self.connection_thread.quit()
        self.read_btn.setDisabled(True)
        self.write_btn.setDisabled(True)
        time.sleep(2)
        self.disconnect_module_btn.setDisabled(True)
        self.icon_connect_disconnect.setPixmap(self.icon_disconnect)
        print('ПОТОК ОСТАНОВЛЕН')

    def read_values(self):

        # функция считывания значений COM и Speed для подключения к модулю

        com = self.com_list.currentText()
        speed = self.speed_list.currentText()

        print('COM-порт: {}, Скорость: {}'.format(com, speed))

        if com:
            self.xbee_connect.com = "COM" + com
        else:
            print("Ошбика проверьте COM-порт")
            return
        if speed:
            self.xbee_connect.speed = int(speed)
        else:
            print("Ошибка проверьте Скорость")
            return

    def success_connect(self):

        self.connect_dialog.close()
        self.read_btn.setDisabled(False)
        self.write_btn.setDisabled(False)
        self.disconnect_module_btn.setDisabled(False)
        self.icon_connect_disconnect.setPixmap(self.icon_connect)

        if self.xbee_connect.type_device[0:2] == '21':
            self.info_type_device.setText(module_type_dict.get('21'))
            print(module_type_dict.get('21'))
        if self.xbee_connect.type_device[0:2] == '23':
            self.info_type_device.setText(module_type_dict.get('23'))
            print(module_type_dict.get('23'))
        if self.xbee_connect.type_device[0:2] == '29':
            self.info_type_device.setText(module_type_dict.get('29'))
            print(module_type_dict.get('29'))
        elif self.xbee_connect.type_device[0:2] == '40':
            self.signal_info_type_s2c_dev.emit()
            if str(hex_to_string(self.xbee_connect.coordinator_enabled)) == '01':
                self.info_type_device.setText(module_type_dict.get('40') + ': ' + 'Coordinator')
            else:
                self.info_type_device.setText(module_type_dict.get('40') + ': ' + 'Router')

    def error_connect(self):

        QMessageBox.warning(self, 'Ошибка', 'COM-порт не найден или уже используется')

    def init_ui(self):

        self.resize(600, 600)
        self.setWindowTitle('Конфигуратор модулей XBee')
        self.setWindowIcon(QIcon("images/zigbee_logo.png"))
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.setCentralWidget(self.main_widget)
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        self.init_toolbar()
        self.one_tab_settings()
        self.show()

    def init_toolbar(self):
        # Верхняя панель управления

        self.toolbar = self.addToolBar('Меню')
        start_connect = QAction(QIcon('images/icon_plus.png'), 'Добавить XBee модуль', self)
        start_connect.triggered.connect(self.init_connect_dialog)

        self.toolbar.addAction(start_connect)

    def init_connect_dialog(self):
        # Модальное окно подключения

        self.connect_dialog = QDialog(self)
        self.connect_dialog.resize(200, 130)
        self.connect_dialog.setWindowTitle('Подключение')
        connect_dialog_layout = QGridLayout(self.connect_dialog)
        self.com_lbl = QLabel('COM-порт:')
        self.speed_lbl = QLabel('Скорость:')
        self.com_list = QComboBox()
        self.speed_list = QComboBox()
        self.com_list.addItems([str(x) for x in range(1, 20)])

        # часто используемый com порт
        self.com_list.setCurrentIndex(2)

        self.speed_list.addItems(['9600', '115200'])
        self.connect_btn = QPushButton('Подключиться')
        self.cancel_btn = QPushButton('Отмена')

        connect_dialog_layout.addWidget(self.com_lbl, 1, 0)
        connect_dialog_layout.addWidget(self.com_list, 1, 1)
        connect_dialog_layout.addWidget(self.speed_lbl, 2, 0)
        connect_dialog_layout.addWidget(self.speed_list, 2, 1)
        connect_dialog_layout.addWidget(self.connect_btn, 3, 0)
        connect_dialog_layout.addWidget(self.cancel_btn, 3, 1)

        self.connect_btn.clicked.connect(self.start_connect_to_module_clicked)
        self.cancel_btn.clicked.connect(self.close_connect_dialog)

        self.connect_dialog.exec_()

    def close_connect_dialog(self):
        # Функция закрытия окна подключения по нажатию кнопки Отмена

        self.connect_dialog.close()

    def one_tab_settings(self):
        # Первый таб: первичные настройки модуля

        self.tab_settings = QWidget()
        self.tabs.addTab(self.tab_settings, 'Настройки')
        self.tab_settings_layout = QVBoxLayout(self.tab_settings)
        self.panel_control_box = QGroupBox()
        self.panel_control_layout = QHBoxLayout(self.panel_control_box)
        self.panel_parameters_box = QGroupBox()
        self.panel_parameters_layout = QGridLayout(self.panel_parameters_box)
        self.panel_info_box = QGroupBox()
        self.panel_info_layout = QHBoxLayout(self.panel_info_box)

        self.pan_id_lbl = QLabel('PAN ID сети:')
        self.pan_id_edit = QLineEdit()
        self.coord_en_lbl = QLabel('Функции координатора:')
        self.coord_en_edit = QLineEdit()
        self.node_id_lbl = QLabel('Идентификатор узла:')
        self.node_id_edit = QLineEdit()
        self.read_btn = QPushButton('Обновить')
        self.write_btn = QPushButton('Записать')
        self.disconnect_module_btn = QPushButton('Отключить')
        self.info_type_device = QLabel()
        self.icon_connect = QPixmap('images/connect_icon.png')
        self.icon_disconnect = QPixmap('images/disconnect_icon.png')
        self.icon_connect_disconnect = QLabel()
        self.icon_connect_disconnect.setPixmap(self.icon_disconnect)

        self.read_btn.setDisabled(True)
        self.write_btn.setDisabled(True)
        self.disconnect_module_btn.setDisabled(True)

        self.panel_info_layout.addWidget(self.info_type_device)
        self.panel_info_layout.addWidget(self.icon_connect_disconnect)

        self.panel_control_layout.addWidget(self.read_btn)
        self.panel_control_layout.addWidget(self.write_btn)
        self.panel_control_layout.addWidget(self.disconnect_module_btn)

        self.panel_parameters_layout.addWidget(self.pan_id_lbl, 1, 0)
        self.panel_parameters_layout.addWidget(self.pan_id_edit, 1, 1)
        self.panel_parameters_layout.addWidget(self.coord_en_lbl, 2, 0)
        self.panel_parameters_layout.addWidget(self.coord_en_edit, 2, 1)
        self.panel_parameters_layout.addWidget(self.node_id_lbl, 3, 0)
        self.panel_parameters_layout.addWidget(self.node_id_edit, 3, 1)

        self.tab_settings_layout.addWidget(self.panel_info_box)
        self.tab_settings_layout.addWidget(self.panel_control_box)
        self.tab_settings_layout.addWidget(self.panel_parameters_box)

        self.read_btn.clicked.connect(self.read_info_clicked)
        self.write_btn.clicked.connect(self.write_info_clicked)
        self.disconnect_module_btn.clicked.connect(self.disconnect_module_clicked)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())