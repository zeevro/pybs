import hid
import webcolors
import colorsys
import random
import time
from collections import namedtuple


__all__ = ['BlinkStick', 'DeviceNotFound', 'parse_color', 'random_color']


class DeviceNotFound(Exception):
    pass


class HIDDevice(hid.device):
    def __init__(self, description):
        super().__init__()
        self.open_path(description['path'])

    def __del__(self):
        self.close()


class BlinkStick:
    VID = 0x20a0
    PID = 0x41e5

    Report = namedtuple('Report', ['id', 'size'])

    _reports = {'color': Report(1, 4),
                'name': Report(2, 33),
                'data': Report(3, 33)}

    def __init__(self, serial=None, name=None, brightness=100):
        device_descriptions = hid.enumerate(self.VID, self.PID)
        if not device_descriptions:
            raise DeviceNotFound('No devices connected!')

        if name:
            for desc in device_descriptions:
                self._dev = HIDDevice(desc)
                if self.get_name() == name:
                    break
            else:
                raise DeviceNotFound('Device not found!')
        elif serial:
            for desc in device_descriptions:
                if desc['serial_number'] == serial:
                    self._dev = HIDDevice(desc)
                    break
            else:
                raise DeviceNotFound('Device not found!')
        else:
            self._dev = HIDDevice(device_descriptions[0])

        self.brightness = max(0, min(brightness or 100, 100))

    def _send_feature_report(self, name, data=None):
        report = self._reports[name]
        if isinstance(data, str):
            data = data.encode()
        elif isinstance(data, (list, tuple)):
            data = bytes(data)
        data = data or b''
        data = bytes([report.id]) + data + bytes(report.size - len(data))
        sent = self._dev.send_feature_report(data)
        if sent == -1:
            raise DeviceNotFound('Device was disconnected')

    def _get_feature_report(self, name):
        report = self._reports[name]
        res = self._dev.get_feature_report(report.id, report.size)
        if not res:
            raise DeviceNotFound('Device was disconnected')
        return res[1:report.size]

    @classmethod
    def get_all_device_serials(cls):
        return [desc['serial_number'] for desc in hid.enumerate(cls.VID, cls.PID)]

    @property
    def serial(self):
        return self._dev.get_serial_number_string()

    @property
    def connected(self):
        try:
            self.get_color()
        except DeviceNotFound:
            return False

        return True

    def _get_brightness_factor(self):
        return ((self.brightness / 10) ** 2) / 100

    def _get_brightness_adjusted_color(self, color):
        w = self._get_brightness_factor()
        return [int(n * w) for n in color]

    def _set_absolute_color(self, color):
        self._send_feature_report('color', color)

    def turn_off(self):
        self._set_absolute_color([0, 0, 0])

    def set_color(self, color):
        self._set_absolute_color(self._get_brightness_adjusted_color(color))

    def get_color(self):
        return self._get_feature_report('color')

    def set_name(self, name):
        self._send_feature_report('name', name)

    def get_name(self):
        data = bytes(self._get_feature_report('name'))
        return data[:data.index(0)].decode()

    def blink(self, color, repeats=1, delay=0.5):
        color = self._get_brightness_adjusted_color(color)
        for i in range(repeats):
            if i:
                time.sleep(delay)
            self._set_absolute_color(*color)
            time.sleep(delay)
            self.turn_off()

    def morph(self, color, duration=1.0, steps=50):
        delay = duration / steps
        from_color = self.get_color()
        to_color = self._get_brightness_adjusted_color(color)
        difference = [t - f for f, t in zip(from_color, to_color)]
        transformation = [[int(f + step / steps * d) for f, d in zip(from_color, difference)] for step in range(1, steps)] + [to_color]
        for color in transformation:
            time.sleep(delay)
            self._set_absolute_color(color)

    def pulse(self, color, repeats=1, duration=1.0, steps=50):
        self.turn_off()
        for _ in range(repeats):
            self.morph(color, duration, steps)
            self.morph([0, 0, 0], duration, steps)


def random_color():
    return list(map(int, colorsys.hsv_to_rgb(random.random(), 0.5 + random.random() / 2, random.randint(128, 255))))


def parse_color(input):
    if input == 'off':
        return [0, 0, 0]
    if input in ('rnd', 'random'):
        return random_color()
    return webcolors.html5_parse_legacy_color(input)


def main():
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument('-n', '--name')
    p.add_argument('-s', '--serial')
    p.add_argument('-f', '--first', action='store_true')
    p.add_argument('-N', '--set-name')
    p.add_argument('-gn', '--get-name', action='store_true')
    p.add_argument('-gs', '--get-serial', action='store_true')
    p.add_argument('-gc', '--get-color', action='store_true')
    p.add_argument('-e', '--echo-color', action='store_true')
    p.add_argument('-b', '--brightness', type=int, default=100)
    p.add_argument('-d', '--duration', type=float, default=1.0)
    p.add_argument('-k', '--blink', dest='color_action', action='store_const', const='blink')
    p.add_argument('-m', '--morph', dest='color_action', action='store_const', const='morph')
    p.add_argument('-p', '--pulse', dest='color_action', action='store_const', const='pulse')
    p.add_argument('-w', '--rainbow', dest='color_action', action='store_const', const='rainbow')
    p.add_argument('-o', '--color-wheel', dest='color_action', action='store_const', const='color_wheel')
    p.add_argument('-r', '--repeats', type=int, default=1)
    p.add_argument('color', nargs='?', type=parse_color)
    args = p.parse_args()

    if args.name or args.serial or args.first:
        sticks = [BlinkStick(name=args.name, serial=args.serial, brightness=args.brightness)]
    else:
        sticks = [BlinkStick(serial=serial, brightness=args.brightness) for serial in BlinkStick.get_all_device_serials()]

    for stick in sticks:
        if args.get_serial:
            print('Serial: {}'.format(stick.serial))

        if args.get_name:
            print('Name: {}'.format(stick.get_name()))

        if args.get_color:
            print('Color: {}'.format(stick.get_color()))

        if args.set_name:
            if len(sticks) > 1:
                print('Will not set identical names to multiple sticks!')
            else:
                stick.set_name(args.set_name)

        if args.color or args.color_action:
            if args.color_action == 'blink':
                stick.blink(args.color, args.repeats, args.duration / 2)
            elif args.color_action == 'morph':
                stick.morph(args.color, args.duration)
            elif args.color_action == 'pulse':
                stick.pulse(args.color, args.repeats, args.duration)
            elif args.color_action == 'rainbow':
                stick.turn_off()
                for _ in range(args.repeats):
                    stick.morph(parse_color('#FF0000'), args.duration)
                    stick.morph(parse_color('#FF7F00'), args.duration)
                    stick.morph(parse_color('#FFFF00'), args.duration)
                    stick.morph(parse_color('#00FF00'), args.duration)
                    stick.morph(parse_color('#0000FF'), args.duration)
                    stick.morph(parse_color('#8B00FF'), args.duration)
                stick.morph([0, 0, 0], args.duration)
            elif args.color_action == 'color_wheel':
                for _ in range(args.repeats):
                    steps = int(args.duration * 100)
                    for step in range(steps):
                        color = list(map(int, colorsys.hsv_to_rgb(step / steps, 1, 255)))
                        stick.set_color(color)
                        time.sleep(0.01)
                stick.turn_off()
            else:
                stick.set_color(args.color)

            if args.echo_color:
                print('New color: {}'.format(stick.get_color()))


if __name__ == "__main__":
    main()
