# -*- coding: utf-8 -*-
# Программа для конфигурирования модулей XBee

import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QAction, QDialog, QGridLayout,
                             QLabel, QLineEdit, QComboBox, QWidget, QVBoxLayout, QTabWidget, QGroupBox, QHBoxLayout,
                             QMessageBox, QTableView, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsItem,
                             QGraphicsPixmapItem, QGraphicsTextItem, QMenu, QTextEdit, QTreeView, QAbstractItemView)
from PyQt5.QtGui import (QIcon, QPixmap, QBrush, QPen, QStandardItemModel, QStandardItem)
from PyQt5.QtCore import (pyqtSignal, QThread, QSize, Qt, QRectF, QEvent, QPoint, QModelIndex)
from XBee_connect import XBeeConnect, TableModel
from digi.xbee.util.utils import hex_to_string
import time
import random
import logging
import XBee_commands

commands = []
commands_dict = {}
for i in XBee_commands.ALL_CLASSES:
    for command in [command for command in dir(i) if not command.startswith("__")]:
        commands.append(command)
        commands_dict[command] = i.__dict__.get(command)


class MainWindow(QMainWindow):

    signal_start_connect = pyqtSignal()
    signal_read_info = pyqtSignal(int)
    signal_write_info = pyqtSignal(int, tuple)
    signal_disconnect_module = pyqtSignal(int)
    signal_coordinator_enable = pyqtSignal(int)
    signal_router_enable = pyqtSignal(int)
    signal_end_dev_enable = pyqtSignal(int)
    signal_search_devices = pyqtSignal()
    signal_update = pyqtSignal(int, str, str)

    signal_test_remote = pyqtSignal(int)

    signal_test_speed = pyqtSignal(str)

    signal_download_list = pyqtSignal()

    signal_send_command = pyqtSignal(str, str, str)

    signal_close_program = pyqtSignal()

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
        self.xbee_connect.stop_test_speed_signal.connect(self.get_info_test_speed)

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

        self.signal_search_devices.emit()

    def send_command(self):
        #отправка команд из карты сети

        cmd = self.command_edit.text()
        param = self.parameter_edit.text()
        self.signal_send_command.emit(self.addr_mac, cmd, param)

    def closeEvent(self, event):
        self.signal_close_program.emit()

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
        self.graphics_scene_items = dict()
        self.graphics_scene_types = dict()
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
        self.download_list = QAction('Выгрузить', self)
        start_connect.triggered.connect(self.init_connect_dialog)

        self.search_devices.triggered.connect(self.search_devices_clicked)

        self.hide_log_action.triggered.connect(self.hide_log_button_clicked)
        self.download_list.triggered.connect(self.download_list_clicked)
        self.toolbar.addAction(start_connect)
        self.toolbar.addAction(self.search_devices)
        self.toolbar.addAction(self.hide_log_action)
        self.toolbar.addAction(self.download_list)

    def download_list_clicked(self):
        self.signal_download_list.emit()

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
        self.speed_list.setCurrentIndex(1)
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
        self.view.test_speed_pressed.connect(self.on_test_speed_pressed)

    def update_network_map(self):
        # Построение карты сети

        x = random.randrange(50, 800)
        y = random.randrange(50, 500)

        for k, v in self.model.modules.items():
            type_device = v["module"].firmware
            self.mac_address = v["module"].mac
            pixmap = QGraphicsPixmapItem()
            pixmap.setFlag(QGraphicsPixmapItem.ItemIsMovable)
            mac_address_item = QGraphicsTextItem(self.mac_address)
            self.graphics_scene_items[pixmap] = self.mac_address
            self.graphics_scene_types[pixmap] = type_device
            if type_device == "Coordinator":
                pixmap.setPixmap(QPixmap('images/xbee-coord-icon.png'))
                pixmap.setPos(x, y)
            if type_device == "Router":
                pixmap.setPixmap(QPixmap('images/xbee-router-icon.png'))
                pixmap.setPos(x + random.randint(-150, 150), y + random.randint(-250, 250))
            if type_device == "End Device":
                pixmap.setPixmap(QPixmap('images/xbee-end-dev-icon.png'))
                pixmap.setPos(x + random.randint(-150, 250), y + random.randint(-250, 350))
            self.scene.addItem(pixmap)

        self.search_devices.setDisabled(False)

    def on_context_menu_pressed(self, pos):

        try:
            self.addr_mac = self.graphics_scene_items[self.view.itemAt(pos)]
            print(self.addr_mac)
            self.init_context_settings_dialog()
        except KeyError:
            QMessageBox.warning(self, 'Внимание', 'Элементов не найдено!')

    def on_test_speed_pressed(self, pos):

        try:
            self.address = self.graphics_scene_items[self.view.itemAt(pos)]
            self.type_dev = self.graphics_scene_types[self.view.itemAt(pos)]
            print(self.address)
            print(self.type_dev)
            self.init_test_speed_dialog()
        except KeyError:
            QMessageBox.warning(self, 'Внимание', 'Элементов не найдено!')

    def init_context_settings_dialog(self):
        # Модальное окно отправки команд из графической сцены

        self.context_settings = QDialog(self)
        self.context_settings.resize(300, 320)
        self.context_settings.setWindowTitle('Управление')
        context_settings_layout = QVBoxLayout(self.context_settings)
        send_command_group = QGroupBox()
        send_command_layout = QGridLayout(send_command_group)
        command = QLabel('Команда:')
        command.setStyleSheet('font-size: 12px;')
        parameter = QLabel('Параметер:')
        parameter.setStyleSheet('font-size: 12px;')
        self.command_edit = QLineEdit()
        self.command_edit.setStyleSheet('font-size: 12px;')
        self.parameter_edit = QLineEdit()
        self.parameter_edit.setStyleSheet('font-size: 12px;')
        send_command_btn = QPushButton('Отправить')
        send_command_btn.setFixedHeight(30)
        send_command_btn.setStyleSheet('font-size: 12px;')
        cancel_context_dialog_btn = QPushButton('Отмена')
        cancel_context_dialog_btn.setFixedHeight(30)
        cancel_context_dialog_btn.setStyleSheet('font-size: 12px;')
        send_command_layout.addWidget(command, 1, 0)
        send_command_layout.addWidget(self.command_edit, 1, 1)
        send_command_layout.addWidget(parameter, 2, 0)
        send_command_layout.addWidget(self.parameter_edit, 2, 1)
        send_command_layout.addWidget(send_command_btn, 3, 0)
        send_command_layout.addWidget(cancel_context_dialog_btn, 3, 1)
        cancel_context_dialog_btn.clicked.connect(self.close_context_settings_clicked)
        modal_right_widget = QWidget()
        context_settings_layout.addWidget(modal_right_widget)
        modal_all_commands_widget = AllCommandsListWidget(self.command_edit)
        context_settings_layout.addWidget(send_command_group)
        context_settings_layout.addWidget(modal_all_commands_widget)

        send_command_btn.clicked.connect(self.send_command)
        self.context_settings.exec_()

    def init_test_speed_dialog(self):

        self.test_speed = QDialog(self)
        self.test_speed.resize(300, 150)
        self.test_speed.setWindowTitle('Тест скорости')
        test_speed_layout = QVBoxLayout(self.test_speed)
        info_data_for_test_box = QGroupBox()
        info_data_for_test_layout = QGridLayout(info_data_for_test_box)
        mac_address_remote_lbl = QLabel('MAC-адрес устройства: ')
        self.mac_address_remote_edit = QLineEdit()
        self.mac_address_remote_edit.setText(self.address)
        self.mac_address_remote_edit.setReadOnly(True)
        type_remote_dev_lbl = QLabel('Тип устройства: ')
        type_remote_dev_info_lbl = QLabel()
        type_remote_dev_info_lbl.setText(self.type_dev)
        self.info_speed_test = QLabel()
        start_test_speed_btn = QPushButton('Начать тест')
        start_test_speed_btn.setFixedHeight(40)
        start_test_speed_btn.setStyleSheet('font-size: 14px;')

        test_speed_layout.addWidget(info_data_for_test_box)

        info_data_for_test_layout.addWidget(mac_address_remote_lbl, 1, 0)
        info_data_for_test_layout.addWidget(self.mac_address_remote_edit, 1, 1)
        info_data_for_test_layout.addWidget(type_remote_dev_lbl, 2, 0)
        info_data_for_test_layout.addWidget(type_remote_dev_info_lbl, 2, 1)
        info_data_for_test_layout.addWidget(self.info_speed_test, 3, 0)
        test_speed_layout.addWidget(start_test_speed_btn)

        start_test_speed_btn.clicked.connect(self.test_speed_btn_clicked)

        self.test_speed.exec_()

    def test_speed_btn_clicked(self):
        try:

            self.signal_test_speed.emit(self.address)
        except Exception as e:
            QMessageBox.warning(self, 'Ошибка', 'Выберите координатор из списка!')
            print(e)

    def get_info_test_speed(self, result):
        self.info_speed_test.setText(str(result))

    def close_context_settings_clicked(self):
        self.context_settings.close()

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
    context_menu_pressed = pyqtSignal(QPoint)
    test_speed_pressed = pyqtSignal(QPoint)

    def __init__(self, *args, **kwargs):
        super(NetworkMapView, self).__init__(*args, **kwargs)

    def contextMenuEvent(self, event):
        menu = QMenu()
        settings_action = menu.addAction("Настройки")
        test_speed_action = menu.addAction("Тест скорости")
        action = menu.exec_(event.globalPos())
        if action == settings_action:
            self.context_menu_pressed.emit(event.pos())
        if action == test_speed_action:
            self.test_speed_pressed.emit(event.pos())


class NetworkMapScene(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super(NetworkMapScene, self).__init__(*args, **kwargs)


class AllCommandsListWidget(QWidget):

    def __init__(self, command_edit, parent=None):
        super(AllCommandsListWidget, self).__init__(parent)
        command_edit = command_edit
        self.commands_list_model = QStandardItemModel()
        self.view = QTreeView()
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.view.setModel(self.commands_list_model)
        self.commands_list_model.setHorizontalHeaderLabels([u'Выберите команду'])
        parent = self.commands_list_model.invisibleRootItem()
        for c in XBee_commands.ALL_CLASSES:
            class_name_item = QStandardItem(c.__name__[1:])
            parent.appendRow(class_name_item)
            for c_item in [QStandardItem(c) for c in dir(c) if not c.startswith("__")]:
                class_name_item.appendRow(c_item)
        layout = QHBoxLayout(self)
        layout.addWidget(self.view)

        def on_item_clicked(index):
            command_str = str(index.data(0))
            if index.parent().column() == 0:
                print(commands_dict[command_str].command)
                command_edit.setText(commands_dict[command_str].command)

        self.view.clicked.connect(on_item_clicked)


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
