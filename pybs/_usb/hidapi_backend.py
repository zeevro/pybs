import hid

from .common import prepare_feature_report
from ..exceptions import DeviceNotFound


class HIDDevice(hid.device):
    def __init__(self, description):
        super().__init__()
        self._desc = description

    def __del__(self):
        self.close()

    @property
    def serial(self):
        return self._desc['serial_number']

    def open(self):
        self.open_path(self._desc['path'])

    def send_feature_report(self, report_id, report_size, data=None):
        report = prepare_feature_report(report_id, report_size, data)
        sent = super().send_feature_report(report)  # pylint: disable=assignment-from-no-return
        if sent == -1:
            if 'connect' in self.error():
                raise DeviceNotFound('Device was disconnected')
            return False
        return True

    def get_feature_report(self, report_id, report_size):
        res = super().get_feature_report(report_id, report_size)
        if not res and 'connect' in self.error():
            raise DeviceNotFound('Device was disconnected')
        return res[1:report_size]


def enumerate_devices(vid, pid, serial=None):
    return [HIDDevice(d)
            for d in hid.enumerate(vid, pid)
            if serial is None or d['serial_number'] == serial]