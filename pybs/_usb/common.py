def prepare_feature_report(report_id, report_size, data):
    if isinstance(data, str):
        data = data.encode()
    elif isinstance(data, (list, tuple)):
        data = bytes(data)
    data = data or b''
    data = bytes([report_id]) + data + bytes(report_size - len(data))
    return data