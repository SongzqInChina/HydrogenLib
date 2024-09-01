import decimal


def mapping(stream, in_min, in_max, out_min, out_max):
    stream, in_min, in_max, out_min, out_max = map(decimal.Decimal, (stream, in_min, in_max, out_min, out_max))
    return (stream - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


