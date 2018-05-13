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
        self.parent.signal_update_info_id.connect(self.update_info_id)
        self.parent.signal_apply_change_id.connect(self.apply_change_id)
        self.parent.signal_update_info_ni.connect(self.update_info_ni)
        self.parent.signal_apply_change_ni.connect(self.apply_change_ni)
        self.parent.signal_update_info_ce.connect(self.update_info_ce)
        self.parent.signal_apply_change_ce.connect(self.apply_change_ce)
        self.parent.signal_update_info_jv.connect(self.update_info_jv)
        self.parent.signal_apply_change_jv.connect(self.apply_change_jv)
        self.parent.signal_update_info_sm.connect(self.update_info_sm)
        self.parent.signal_apply_change_sm.connect(self.apply_change_sm)

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

    def update_info_id(self):

        self.info_id = self.local_device.get_parameter('ID')

    def apply_change_id(self, id):

        self.local_device.set_pan_id(hex_string_to_bytes(str(id)))
        self.local_device.apply_changes()
        self.local_device.write_changes()
        self.new_id = self.local_device.get_parameter('ID')

    def update_info_ni(self):

        self.info_ni = self.local_device.get_node_id()

    def apply_change_ni(self, ni):

        self.local_device.set_parameter('NI', bytearray(str(ni), 'utf8'))
        self.local_device.apply_changes()
        self.local_device.write_changes()
        self.new_ni = self.local_device.get_node_id()

    def update_info_ce(self):

        self.info_ce = self.local_device.get_parameter('CE')

    def apply_change_ce(self, ce):

        self.local_device.set_parameter('CE', hex_string_to_bytes(str(ce)))
        self.local_device.apply_changes()
        self.local_device.write_changes()
        self.new_ce = self.local_device.get_parameter('CE')

    def update_info_jv(self):

        self.info_jv = self.local_device.get_parameter('JV')

    def apply_change_jv(self, jv):

        self.local_device.set_parameter('JV', hex_string_to_bytes(str(jv)))
        self.local_device.apply_changes()
        self.local_device.write_changes()
        self.new_jv = self.local_device.get_parameter('JV')

    def update_info_sm(self):

        self.info_sm = self.local_device.get_parameter('SM')

    def apply_change_sm(self, sm):

        self.local_device.set_parameter('SM', hex_string_to_bytes(str(sm)))
        self.local_device.apply_changes()
        self.local_device.write_changes()
        self.new_sm = self.local_device.get_parameter('SM')

#TODO Привязать функции update_info_jv, apply_change_jv, update_info_sm, apply_change_sm к кнопкам соотвественно