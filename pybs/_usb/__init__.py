for backend in ['pywinusb', 'hidapi']:
    try:
        exec('from .{}_backend import HIDDevice, enumerate_devices'.format(backend))
    except ImportError:
        continue
    break
