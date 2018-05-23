# -*- coding: utf-8 -*-
# Программа для конфигурирования модулей XBee

import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QAction, QDialog, QGridLayout,
                             QLabel, QLineEdit, QComboBox, QWidget, QVBoxLayout, QTabWidget, QGroupBox, QHBoxLayout,
                             QMessageBox, QTableView, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsItem,
                             QGraphicsPixmapItem, QGraphicsTextItem, QMenu, QTextEdit)
from PyQt5.QtGui import (QIcon, QPixmap, QBrush, QPen)
from PyQt5.QtCore import (pyqtSignal, QThread, QSize, Qt, QRectF, QEvent)
from XBee_connect import XBeeConnect, TableModel
from digi.xbee.util.utils import hex_to_string
import time
import random
import logging


class MainWindow(QMainWindow):

    signal_start_connect = pyqtSignal()
    signal_read_info = pyqtSignal(int)
    signal_write_info = pyqtSignal(int, tuple)
    signal_disconnect_module = pyqtSignal(int)
    signal_coordinator_enable = pyqtSignal(int)
    signal_router_enable = pyqtSignal(int)
    signal_end_dev_enable = pyqtSignal(int)
    signal_search_devices = pyqtSignal(int)
    signal_update = pyqtSignal(int, str, str)

    signal_test_remote = pyqtSignal(int)

    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)
        self.xbee_connect = XBeeConnect(self)
        self.connection_thread = QThread()
        self.xbee_connect.moveToThread(self.connection_thread)
        self.connection_thread.start()
        self.xbee_connect.successful_connection_signal.connect(self.success_connect)
        self.xbee_connect.error_connection_signal.connect(self.error_connect)
        self.xbee_connect.signal_updated.connect(self.updated_param)

        self.xbee_connect.start_discovered_signal.connect(self.on_start_discovery)
        self.xbee_connect.signal_discovered_finished.connect(self.update_network_map)

        self.init_ui()

    def start_connect_to_module_clicked(self):
        # создаем экзмепляр класса XBeeConnect

        self.read_values()
        self.signal_start_connect.emit()

    def read_info_clicked(self):

        try:
            index = self.table.selectedIndexes()[0].row()
            print(index)
            self.signal_read_info.emit(index)
            self.pan_id_edit.setText(str(hex_to_string(self.xbee_connect.pan_id)))
            self.node_id_edit.setText(str(self.xbee_connect.node_id_current))
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', 'Не выбран модуль из таблицы!!!')
            print(e)

    def write_info_clicked(self):

        try:
            index = self.table.selectedIndexes()[0].row()

            param_pan_id = self.pan_id_edit.text()
            param_node_id = self.node_id_edit.text()
            parameters_tuple = (param_pan_id, param_node_id)

            self.signal_write_info.emit(index, parameters_tuple)

            self.pan_id_edit.setText(str(hex_to_string(self.xbee_connect.new_pan_id)))
            self.node_id_edit.setText(str(self.xbee_connect.new_node_id))
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', 'Не выбран модуль из таблицы!!!')
            print(e)

    def disconnect_module_clicked(self):
        try:
            index = self.table.selectedIndexes()[0].row()
            print(index)
            self.signal_disconnect_module.emit(index)
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', 'Не выбран модуль из таблицы!!!')
            print(e)

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

    def update_info_id_clicked(self):

        command = 'ID'
        self.current_field = self.pan_id_edit
        print('command id no send')
        self.update_clicked(command)

    def write_info_id_clicked(self):

        command = 'ID'
        self.current_field = self.pan_id_edit
        parameter = self.pan_id_edit.text()
        self.update_clicked(command, parameter)

    def update_clicked(self, comm, parameter=""):

        index = self.table.selectedIndexes()[0].row()
        print(index)
        if index is None:
            QMessageBox.warning(self, 'Ошибка', 'Не выбран модуль из таблицы!!!')
        else:
            self.signal_update.emit(index, comm, parameter)
            print('signal update send')

    def updated_param(self, result):
        self.current_field.setText(str(result))

    def update_info_ni_clicked(self):

        command = 'NI'
        self.current_field = self.node_id_edit
        print('command id no send')
        self.update_clicked(command)

    def write_info_ni_clicked(self):

        command = 'NI'
        self.current_field = self.node_id_edit
        parameter = self.node_id_edit.text()
        self.update_clicked(command, parameter)

    def coordinator_enable_clicked(self):

        try:
            index = self.table.selectedIndexes()[0].row()
            self.signal_coordinator_enable.emit(index)
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', 'Не выбран модуль из таблицы!!!')
            print(e)

    def router_enable_clicked(self):

        try:
            index = self.table.selectedIndexes()[0].row()
            self.signal_router_enable.emit(index)
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', 'Не выбран модуль из таблицы!!!')
            print(e)

    def end_dev_enable_clicked(self):

        try:
            index = self.table.selectedIndexes()[0].row()
            self.signal_end_dev_enable.emit(index)
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', 'Не выбран модуль из таблицы!!!')
            print(e)

    def search_devices_clicked(self):

        index = self.table.selectedIndexes()[0].row()
        self.signal_search_devices.emit(index)

    def success_connect(self):

        self.connect_dialog.close()
        self.read_btn.setDisabled(False)
        self.write_btn.setDisabled(False)
        self.disconnect_module_btn.setDisabled(False)
        self.on_all_btn()
        self.search_devices.setDisabled(False)

    def error_connect(self):

        self.connection_thread.quit()
        QMessageBox.warning(self, 'Ошибка', 'COM-порт не найден или уже используется')

    def on_start_discovery(self):
        print("Started")
        self.log_message('Поиск...')
        self.search_devices.setDisabled(True)

    def init_ui(self):

        self.resize(890, 600)
        self.setWindowTitle('Конфигуратор модулей XBee')
        self.setWindowIcon(QIcon("images/zigbee_logo.png"))
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.setCentralWidget(self.main_widget)
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        self.init_toolbar()
        self.one_tab_settings()
        self.two_tab_network_map()
        self.init_log(self.main_layout)
        self.show()

    def init_table(self, layout):
        # Таблица: список подключенных устройств по com-порт

        self.model = self.xbee_connect.model
        self.table = TableView()
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setMinimumSectionSize(200)
        self.table.resizeColumnsToContents()
        try:
            self.table.setModel(self.model)
        except Exception as e:
            print(e)
        layout.addWidget(self.table)

    def init_log(self, layout):
        self.log_visible = True
        self.logger = TextLogger(self)
        self.logger.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S"))
        logging.getLogger().addHandler(self.logger)
        logging.getLogger().setLevel(logging.DEBUG)
        layout.addWidget(self.logger.widget)

    def init_toolbar(self):
        # Верхняя панель управления

        self.toolbar = self.addToolBar('Меню')
        start_connect = QAction(QIcon('images/icon_plus.png'), 'Добавить XBee модуль', self)
        self.search_devices = QAction(QIcon('images/search_dev_icon'), 'Поиск устройств', self)
        self.hide_log_action = QAction(QIcon('images/hide-log-button-icon.png'), "Скрыть/Показать логи", self)
        self.search_devices.setDisabled(True)
        test_btn = QAction('TEST', self)
        start_connect.triggered.connect(self.init_connect_dialog)
        #search_devices.triggered.connect(self.update_network_map)
        self.search_devices.triggered.connect(self.search_devices_clicked)
        test_btn.triggered.connect(self.test_remote_device)
        self.hide_log_action.triggered.connect(self.hide_log_button_clicked)
        self.toolbar.addAction(start_connect)
        self.toolbar.addAction(self.search_devices)
        self.toolbar.addAction(test_btn)
        self.toolbar.addAction(self.hide_log_action)

    def log_message(self, msg):
        """
        Везде, где нужно вывести сообщение в лог, вызываем эту функцию
        """
        logging.debug(msg)

    def hide_log_button_clicked(self):
        if self.log_visible:
            self.log_visible = False
            self.logger.widget.setVisible(False)
            self.hide_log_action.setChecked(True)
        else:
            self.log_visible = True
            self.logger.widget.setVisible(True)
            self.hide_log_action.setChecked(False)

    def test_remote_device(self):

        index = self.table.selectedIndexes()[0].row()
        self.signal_test_remote.emit(index)

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
        self.panel_parameters_layout = QHBoxLayout(self.panel_parameters_box)
        self.basic_param_box = QGroupBox()
        self.basic_param_layout = QHBoxLayout(self.basic_param_box)
        self.list_devices_group = QGroupBox('Радио модули')
        self.list_devices_layout = QVBoxLayout(self.list_devices_group)
        self.init_table(self.list_devices_layout)

        # Поле: PAN ID
        self.pan_id_lbl = QLabel('PAN ID сети:')
        self.pan_id_edit = QLineEdit()

        self.update_info_id_btn = QPushButton()
        self.update_info_id_btn.setToolTip('Обновить значение')
        self.update_info_id_btn.setIcon(QIcon('images/refresh_parameter_icon.png'))
        self.update_info_id_btn.setIconSize(QSize(20, 20))

        self.apply_change_id_btn = QPushButton()
        self.apply_change_id_btn.setToolTip('Записать значение')
        self.apply_change_id_btn.setIcon(QIcon('images/write_update_icon.png'))
        self.apply_change_id_btn.setIconSize(QSize(20, 20))

        # Поле: Идентификатор узла
        self.node_id_lbl = QLabel('Идентификатор узла:')
        self.node_id_edit = QLineEdit()

        self.update_info_ni_btn = QPushButton()
        self.update_info_ni_btn.setToolTip('Обновить значение')
        self.update_info_ni_btn.setIcon(QIcon('images/refresh_parameter_icon.png'))
        self.update_info_ni_btn.setIconSize(QSize(20, 20))

        self.apply_change_ni_btn = QPushButton()
        self.apply_change_ni_btn.setToolTip('Записать значение')
        self.apply_change_ni_btn.setIcon(QIcon('images/write_update_icon.png'))
        self.apply_change_ni_btn.setIconSize(QSize(20, 20))

        self.coordinator_enable_btn = QPushButton('Назначить роль: Координатор')
        self.coordinator_enable_btn.setFixedHeight(40)
        self.coordinator_enable_btn.setStyleSheet('font-size: 14px;')
        self.router_enable_btn = QPushButton('Назначить роль: Роутер')
        self.router_enable_btn.setFixedHeight(40)
        self.router_enable_btn.setStyleSheet('font-size: 14px;')
        self.end_device_enable_btn = QPushButton('Назначить роль: Конечное устройство')
        self.end_device_enable_btn.setFixedHeight(40)
        self.end_device_enable_btn.setStyleSheet('font-size: 14px;')

        self.read_btn = QPushButton('Обновить')
        self.read_btn.setFixedHeight(40)
        self.read_btn.setStyleSheet('font-size: 14px;')

        self.write_btn = QPushButton('Записать')
        self.write_btn.setFixedHeight(40)
        self.write_btn.setStyleSheet('font-size: 14px;')

        self.disconnect_module_btn = QPushButton('Отключить')
        self.disconnect_module_btn.setFixedHeight(40)
        self.disconnect_module_btn.setStyleSheet('font-size: 14px;')

        # pan id
        self.basic_param_layout.addWidget(self.pan_id_lbl)
        self.basic_param_layout.addWidget(self.pan_id_edit)
        self.basic_param_layout.addWidget(self.update_info_id_btn)
        self.basic_param_layout.addWidget(self.apply_change_id_btn)
        # node id
        self.basic_param_layout.addWidget(self.node_id_lbl)
        self.basic_param_layout.addWidget(self.node_id_edit)
        self.basic_param_layout.addWidget(self.update_info_ni_btn)
        self.basic_param_layout.addWidget(self.apply_change_ni_btn)

        self.panel_control_layout.addWidget(self.read_btn)
        self.panel_control_layout.addWidget(self.write_btn)
        self.panel_control_layout.addWidget(self.disconnect_module_btn)

        self.panel_parameters_layout.addWidget(self.coordinator_enable_btn)
        self.panel_parameters_layout.addWidget(self.router_enable_btn)
        self.panel_parameters_layout.addWidget(self.end_device_enable_btn)

        self.tab_settings_layout.addWidget(self.list_devices_group)
        self.tab_settings_layout.addWidget(self.panel_control_box)
        self.tab_settings_layout.addWidget(self.basic_param_box)
        self.tab_settings_layout.addWidget(self.panel_parameters_box)

        self.read_btn.clicked.connect(self.read_info_clicked)
        self.write_btn.clicked.connect(self.write_info_clicked)
        self.disconnect_module_btn.clicked.connect(self.disconnect_module_clicked)
        self.update_info_id_btn.clicked.connect(self.update_info_id_clicked)
        self.apply_change_id_btn.clicked.connect(self.write_info_id_clicked)
        self.update_info_ni_btn.clicked.connect(self.update_info_ni_clicked)
        self.apply_change_ni_btn.clicked.connect(self.write_info_ni_clicked)
        self.coordinator_enable_btn.clicked.connect(self.coordinator_enable_clicked)
        self.router_enable_btn.clicked.connect(self.router_enable_clicked)
        self.end_device_enable_btn.clicked.connect(self.end_dev_enable_clicked)

        self.off_all_btn()

    def two_tab_network_map(self):

        self.tab_network_map = QWidget()
        self.tabs.addTab(self.tab_network_map, "Карта сети")
        self.tab_network_map_layout = QVBoxLayout(self.tab_network_map)

        self.scene = QGraphicsScene()
        self.scene.setItemIndexMethod(1)

        self.view = NetworkMapView(self.scene, self.tab_network_map)
        self.view.resize(866, 522)
        self.scene.setSceneRect(QRectF())

        self.view.context_menu_pressed.connect(self.on_context_menu_pressed)

    def update_network_map(self):
        # Построение карты сети

        x = random.randrange(50, 800)
        y = random.randrange(50, 500)

        for k, v in self.model.modules.items():
            type_device = v["module"].firmware
            print(v["module"].mac)
            mac_address = v["module"].mac
            pixmap = QGraphicsPixmapItem()
            #pixmap.setFlag(QGraphicsPixmapItem.ItemIsMovable)
            mac_address_item = QGraphicsTextItem(mac_address)
            if type_device == "S2C Firmware: Coordinator":
                pixmap.setPixmap(QPixmap('images/xbee-coord-icon.png'))
                pixmap.setPos(x, y)
                mac_address_item.setPos(x - 18, y + 55)
            if type_device == "S2B ZigBee Router API":
                pixmap.setPixmap(QPixmap('images/xbee-router-icon.png'))
                pixmap.setPos(x + random.randint(-150, 150), y + random.randint(-250, 250))
            if type_device == "S2B ZigBee End Device API":
                pixmap.setPixmap(QPixmap('images/xbee-end-dev-icon.png'))
                pixmap.setPos(x + 70, y + 80)
            self.scene.addItem(pixmap)
            self.scene.addItem(mac_address_item)

        self.search_devices.setDisabled(False)

    def on_context_menu_pressed(self):
        self.init_context_settings_dialog()


    def read_info_for_scene(self, address):

        print('тестттттттттт')
        print(address)

    def init_context_settings_dialog(self):
        # Модальное окно отправки команд из графической сцены

        self.context_settings = QDialog(self)
        self.context_settings.resize(200, 130)
        self.context_settings.setWindowTitle('Управление')
        context_settings_layout = QGridLayout(self.context_settings)
        command = QLabel('Команда:')
        parameter = QLabel('Параметер:')
        command_edit = QLineEdit()
        parameter_edit = QLineEdit()
        send_command_btn = QPushButton('Отправить')
        cancel_btn = QPushButton('Отмена')
        context_settings_layout.addWidget(command, 1, 0)
        context_settings_layout.addWidget(command_edit, 1, 1)
        context_settings_layout.addWidget(parameter, 2, 0)
        context_settings_layout.addWidget(parameter_edit, 2, 1)
        context_settings_layout.addWidget(send_command_btn, 3, 0)
        context_settings_layout.addWidget(cancel_btn, 3, 1)

        self.context_settings.exec_()

    def off_all_btn(self):
        # Отключение кнопок при отсуствии подключения к модулю

        self.read_btn.setDisabled(True)
        self.write_btn.setDisabled(True)
        self.disconnect_module_btn.setDisabled(True)
        self.update_info_id_btn.setDisabled(True)
        self.apply_change_id_btn.setDisabled(True)
        self.update_info_ni_btn.setDisabled(True)
        self.apply_change_ni_btn.setDisabled(True)
        self.coordinator_enable_btn.setDisabled(True)
        self.router_enable_btn.setDisabled(True)
        self.end_device_enable_btn.setDisabled(True)

    def on_all_btn(self):
        # Включение кнопок при успешном подключении к модулю

        self.read_btn.setDisabled(False)
        self.write_btn.setDisabled(False)
        self.disconnect_module_btn.setDisabled(False)
        self.update_info_id_btn.setDisabled(False)
        self.apply_change_id_btn.setDisabled(False)
        self.update_info_ni_btn.setDisabled(False)
        self.apply_change_ni_btn.setDisabled(False)
        self.coordinator_enable_btn.setDisabled(False)
        self.router_enable_btn.setDisabled(False)
        self.end_device_enable_btn.setDisabled(False)


class TableView(QTableView):

    def __init__(self, parent=None):
        super(TableView, self).__init__(parent=parent)


class NetworkMapView(QGraphicsView):
    context_menu_pressed = pyqtSignal(QEvent)

    def __init__(self, *args, **kwargs):
        super(NetworkMapView, self).__init__(*args, **kwargs)

    def contextMenuEvent(self, event):
        menu = QMenu()
        settings_action = menu.addAction("Настройки")
        action = menu.exec_(event.globalPos())
        if action == settings_action:
            self.context_menu_pressed.emit(event)


class NetworkMapScene(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super(NetworkMapScene, self).__init__(*args, **kwargs)

class TextLogger(logging.Handler):
    """
    Handler for logger
    """
    def __init__(self, parent):
        logging.Handler.__init__(self)
        self.widget = QGroupBox('Логи')
        layout = QVBoxLayout(self.widget)
        self.text_widget = QTextEdit()
        self.text_widget.setReadOnly(True)
        layout.addWidget(self.text_widget)

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.append(msg)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())
