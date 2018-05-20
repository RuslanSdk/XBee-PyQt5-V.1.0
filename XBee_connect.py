# -*- coding: utf-8 -*-
# Функции организации подкючения и передачи команд

from PyQt5.QtCore import (QObject, pyqtSlot, pyqtSignal, QAbstractTableModel, QModelIndex, Qt)
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
        self.node_id = ""
        self.mac = ""
        self.model = TableModel()

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
        self.parent.signal_coordinator_enable.connect(self.coord_en)
        self.parent.signal_router_enable.connect(self.router_en)
        self.parent.signal_end_dev_enable.connect(self.end_dev_en)

    @pyqtSlot()
    def start_connection(self):

        local_device = XBeeDevice(self.com, self.speed)
        try:
            local_device.open()
            self.connected = True

            # делаем для теста print
            print('ПОРТ ОТКРЫТ. Устройство готово к работе')

            local_device.type_device = hex_to_string(local_device.get_firmware_version())

            print("Firmware version: %s" % local_device.type_device)

            local_device.mac = str(local_device.get_64bit_addr())
            local_device.node_id = str(local_device.get_node_id())
            local_device.com = self.com

            self.model.modules[local_device.mac] = {"id": self.model.module_id, "module": local_device}
            self.successful_connection_signal.emit()
            self.update_table()

        except Exception as e:
            self.connected = False
            print(e)
            self.error_connection_signal.emit()
            local_device.close()

    def update_table(self, add=True):

        if add:
            self.model.insertRows(len(self.model.modules) - 1, 1)
            print(len(self.model.modules))
            mac = self.model.get_address_by_id(self.model.module_id)
            topLeft = self.model.createIndex(self.model.modules[mac]['id'], 0)
            bottomRight = self.model.createIndex(self.model.modules[mac]['id'], 3)
            print("dataChanged")
            self.model.module_id += 1
        else:
            topLeft = self.model.createIndex(0, 0)
            bottomRight = self.model.createIndex(0, 3)
            self.model.module_id -= 1

        self.model.dataChanged.emit(topLeft, bottomRight)

    def get_module_by_id(self, module_id):

        return self.model.modules[self.model.get_address_by_id(module_id)]["module"]

    def read_info(self, module_id):

        module = self.get_module_by_id(module_id)
        self.pan_id = module.get_parameter('ID')
        print(self.pan_id)
        self.node_id_current = module.get_node_id()
        print(self.node_id_current)

    def write_info(self, module_id, parameters):

        module = self.get_module_by_id(module_id)
        module.set_pan_id(hex_string_to_bytes(str(parameters[0])))
        module.set_parameter('NI', bytearray(str(parameters[1]), 'utf8'))
        module.apply_changes()
        module.write_changes()
        self.new_pan_id = module.get_parameter('ID')
        self.new_node_id = module.get_node_id()
        print('DLY TESTA OK NORM')

    def close_port(self, module_id):

        module = self.get_module_by_id(module_id)
        del self.model.modules[module.mac]
        module.close()
        print(self.model.modules)
        print('ПОРТ ЗАКРЫТ')
        self.update_table(add=False)

    def info_type_s2c_dev(self, module_id):

        module = self.get_module_by_id(module_id)
        module.coordinator_enabled = module.get_parameter('CE')
        module.sleep_mode = module.get_parameter('SM')

    def update_info_id(self, module_id):

        module = self.get_module_by_id(module_id)
        self.info_id = module.get_parameter('ID')

    def apply_change_id(self, module_id, id):

        module = self.get_module_by_id(module_id)
        module.set_pan_id(hex_string_to_bytes(str(id)))
        module.apply_changes()
        module.write_changes()
        self.new_id = module.get_parameter('ID')

    def update_info_ni(self, module_id):

        module = self.get_module_by_id(module_id)
        self.info_ni = module.get_node_id()

    def apply_change_ni(self, module_id, ni):

        module = self.get_module_by_id(module_id)
        module.set_parameter('NI', bytearray(str(ni), 'utf8'))
        module.apply_changes()
        module.write_changes()
        self.new_ni = module.get_node_id()

    def update_info_ce(self, module_id):

        module = self.get_module_by_id(module_id)
        module.info_ce = module.get_parameter('CE')

    def apply_change_ce(self, ce, module_id):

        module = self.get_module_by_id(module_id)
        module.set_parameter('CE', hex_string_to_bytes(str(ce)))
        module.apply_changes()
        module.write_changes()
        module.new_ce = module.get_parameter('CE')

    def update_info_jv(self, module_id):

        module = self.get_module_by_id(module_id)
        module.info_jv = module.get_parameter('JV')

    def apply_change_jv(self, jv, module_id):

        module = self.get_module_by_id(module_id)
        module.set_parameter('JV', hex_string_to_bytes(str(jv)))
        module.apply_changes()
        module.write_changes()
        module.new_jv = module.get_parameter('JV')

    def update_info_sm(self, module_id):

        module = self.get_module_by_id(module_id)
        module.info_sm = module.get_parameter('SM')

    def apply_change_sm(self, sm, module_id):

        module = self.get_module_by_id(module_id)
        module.set_parameter('SM', hex_string_to_bytes(str(sm)))
        module.apply_changes()
        module.write_changes()
        module.new_sm = module.get_parameter('SM')

    def coord_en(self, module_id):

        ce = '1'
        sm = '0'
        jv = '0'
        module = self.get_module_by_id(module_id)
        module.set_parameter('SM', hex_string_to_bytes(str(sm)))
        module.set_parameter('CE', hex_string_to_bytes(str(ce)))
        module.set_parameter('JV', hex_string_to_bytes(str(jv)))
        module.apply_changes()
        module.write_changes()

    def router_en(self, module_id):

        ce = '0'
        sm = '0'
        jv = '1'
        module = self.get_module_by_id(module_id)
        module.set_parameter('SM', hex_string_to_bytes(str(sm)))
        module.set_parameter('CE', hex_string_to_bytes(str(ce)))
        module.set_parameter('JV', hex_string_to_bytes(str(jv)))
        module.apply_changes()
        module.write_changes()

    def end_dev_en(self, module_id):

        ce = '0'
        sm = '4'
        jv = '0'
        module = self.get_module_by_id(module_id)
        module.set_parameter('CE', hex_string_to_bytes(str(ce)))
        module.set_parameter('JV', hex_string_to_bytes(str(jv)))
        module.set_parameter('SM', hex_string_to_bytes(str(sm)))
        module.apply_changes()
        module.write_changes()


class TableModel(QAbstractTableModel):

    def __init__(self, parent=None):

        super(TableModel, self).__init__(parent)
        self.columnNames = ['Тип устройства', 'Идентификатор узла', 'MAC-адрес', 'COM-порт']
        self.modules = dict()
        self.module_id = 0

    def rowCount(self, parent=None, *args, **kwargs):

        return len(self.modules)

    def columnCount(self, parent=None, *args, **kwargs):

        return len(self.columnNames)

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid():
            print('not valid')
            return None
        if role == Qt.DisplayRole:
            module_address = self.get_address_by_id(index.row())
            module = self.modules[module_address]["module"]
            if index.column() == 0:
                device_type = module.type_device
                print(device_type)
                return "{}".format(device_type)
            if index.column() == 1:
                node_id = module.node_id
                print(node_id)
                return "{}".format(node_id)
            if index.column() == 2:
                return str(module_address)
            if index.column() == 3:
                return str(module.com)

    def insertRows(self, pos=0, count=1, parent=None):

        self.beginInsertRows(QModelIndex(), pos, pos + count - 1)
        self.endInsertRows()
        return True

    def headerData(self, section, orientation, role=Qt.DisplayRole):

        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            for i in range(self.columnCount()):
                if section == i:
                    return self.columnNames[i]

        return None

    def get_address_by_id(self, id):

        for k, v in self.modules.items():
            if v["id"] == id:
                return k