from pywinusb import hid

from .common import prepare_feature_report
from ..exceptions import DeviceNotFound


class HIDDevice(hid.core.HidDevice):
    @property
    def serial(self):
        return self.serial_number

    def send_feature_report(self, report_id, report_size, data):
        report = prepare_feature_report(report_id, report_size, data)
        success = super().send_feature_report(report)
        if (not success) and (not self.is_plugged()):
            raise DeviceNotFound('Device was disconnected')
        return success

    def get_feature_report(self, report_id, report_size):
        report = self.find_feature_reports()[report_id - 1].get()
        if (not report) and (not self.is_plugged()):
            raise DeviceNotFound('Device was disconnected')
        return report[1:report_size]


def enumerate_devices(vid, pid, serial=None):
    orig_hid_device_cls = hid.core.HidDevice
    hid.core.HidDevice = HIDDevice

    ret = [d
           for d in hid.find_all_hid_devices()
           if (d.vendor_id == vid)
           and (d.product_id == pid)
           and (serial is None or d.serial_number == serial)]

    hid.core.HidDevice = orig_hid_device_cls

    return ret
