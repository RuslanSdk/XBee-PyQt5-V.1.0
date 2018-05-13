# -*- coding: utf-8 -*-
# Функции организации подкючения и передачи команд

from PyQt5.QtCore import (QObject, pyqtSlot, pyqtSignal)
from digi.xbee.devices import (XBeeDevice)
from digi.xbee.util.utils import hex_string_to_bytes
import time
from digi.xbee.util.utils import hex_to_string


class XBeeConnect(QObject):

    successful_connection_signal = pyqtSignal()
    error_connection_signal = pyqtSignal()

    def __init__(self, parent=None):

        super(XBeeConnect, self).__init__(parent)

        self.local_device = None
        self.com = ''
        self.speed = ''
        self.connected = False
        self.parent = parent

        self.parent.signal_start_connect.connect(self.start_connection)
        self.parent.signal_read_info.connect(self.read_info)
        self.parent.signal_write_info.connect(self.write_info)
        self.parent.signal_disconnect_module.connect(self.close_port)
        self.parent.signal_info_type_s2c_dev.connect(self.info_type_s2c_dev)

    @pyqtSlot()
    def start_connection(self):

        self.local_device = XBeeDevice(self.com, self.speed)

        try:
            self.local_device.open()
            self.connected = True

            # делаем для теста print
            print('ПОРТ ОТКРЫТ. Устройство готово к работе')

            self.type_device = hex_to_string(self.local_device.get_firmware_version())

            print("Firmware version: %s" % self.type_device)

            self.successful_connection_signal.emit()

        except Exception as e:
            self.connected = False
            print(e)
            self.error_connection_signal.emit()
            self.local_device.close()

    def read_info(self):

        self.pan_id = self.local_device.get_parameter('ID')
        self.channel_ver = self.local_device.get_parameter('JV')
        #self.coord_en = self.local_device.get_parameter("CE")
        self.node_id = self.local_device.get_node_id()

    def write_info(self, parameters):

        self.local_device.set_pan_id(hex_string_to_bytes(str(parameters[0])))
        #self.local_device.set_parameter('CE', hex_string_to_bytes(str(parameters[1])))
        self.local_device.set_parameter('NI', bytearray(str(parameters[1]), 'utf8'))

        time.sleep(1)
        self.local_device.apply_changes()
        time.sleep(1)
        self.local_device.write_changes()
        time.sleep(1)
        self.new_pan_id = self.local_device.get_parameter('ID')
        #self.new_coord_en = self.local_device.get_parameter('CE')
        self.new_node_id = self.local_device.get_node_id()

        print('ПАРАМЕТРЫ ОБНОВЛЕНЫ')

    def close_port(self):

        self.local_device.close()
        print('ПОРТ ЗАКРЫТ')

    def info_type_s2c_dev(self):
        self.coordinator_enabled = self.local_device.get_parameter('CE')
        self.sleep_mode = self.local_device.get_parameter('SM')