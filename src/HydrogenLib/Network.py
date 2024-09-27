import re
import socket

import ping3


def _ipa():
    """
    返回一个A类IP地址的迭代器
    :return:
    """
    i1 = 10
    for i2 in range(256):
        for i3 in range(256):
            for i4 in range(256):
                yield f"{i1}.{i2}.{i3}.{i4}"


def _ipb():
    """
    返回一个B类IP地址的迭代器
    :return:
    """
    i1 = 172
    for i2 in range(16, 32):
        for i3 in range(256):
            for i4 in range(256):
                yield f"{i1}.{i2}.{i3}.{i4}"


def _ipc():
    """
    返回一个C类IP地址的迭代器
    :return:
    """
    i1 = 192
    i2 = 168
    for i3 in range(256):
        for i4 in range(256):
            yield f"{i1}.{i2}.{i3}.{i4}"


def _ipd():
    """
    返回一个D类IP地址的迭代器
    :return:
    """
    for i1 in range(110, 132):
        for i2 in range(256):
            for i3 in range(256):
                for i4 in range(256):
                    yield f"{i1}.{i2}.{i3}.{i4}"


def _ipe():
    """
    返回一个E类IP地址的迭代器
    :return:
    """
    i1 = 127
    for i2 in range(256):
        for i3 in range(256):
            for i4 in range(256):
                yield f"{i1}.{i2}.{i3}.{i4}"


def _ipf():
    """
    返回一个F类IP地址的迭代器
    :return:
    """
    i1 = 169
    i2 = 254
    for i3 in range(256):
        for i4 in range(256):
            yield f"{i1}.{i2}.{i3}.{i4}"


def _getIP(IPClass: str):
    IPClass = IPClass.upper()[0]
    if IPClass == "A":
        return _ipa()
    elif IPClass == "B":
        return _ipb()
    elif IPClass == "C":
        return _ipc()
    elif IPClass == "D":
        return _ipd()
    elif IPClass == "E":
        return _ipe()
    elif IPClass == "F":
        return _ipf()
    else:
        return None


def getIP(IPClass: str):
    """
    IP范围：\n
    - A: 10.0.0.0-10.255.255.255\n
    - B: 172.16.0.0-172.31.255.255\n
    - C: 192.168.0.0-192.168.255.255\n
    - D: 110.0.0.0-127.255.255.255\n
    - E: 127.0.0.0-127.255.255.255\n
    - F: 169.254.0.0-169.254.255.255\n
    :param IPClass: A, B, C, D, E, F
    :return:
    """
    for i in _getIP(IPClass):
        yield i


def ping(name, timeout=1):
    """
    检查网络连通性
    :param name:
    :param timeout:
    :return:
    """
    return ping3.ping(name, timeout=timeout)


def can_ping(name, timeout=1):
    """
    是否能ping通
    :param name:
    :param timeout:
    :return:
    """
    return bool(ping(name, timeout))


def getIPseq(ip1a, ip1b, ip2a, ip2b, ip3a, ip3b, ip4a, ip4b):
    for ip1 in range(ip1a, ip1b):
        for ip2 in range(ip2a, ip2b):
            for ip3 in range(ip3a, ip3b):
                for ip4 in range(ip4a, ip4b):
                    yield f"{ip1}.{ip2}.{ip3}.{ip4}"


def _getIPv6seq(ip_ranges):
    def parse_hex_range(hex_range: str):
        match = re.match(r'^0x([0-9a-fA-F]+)-0x([0-9a-fA-F]+)$', hex_range)
        if match:
            return int(match.group(1), 16), int(match.group(2), 16)
        else:
            raise ValueError(f"Invalid hexadecimal range: {hex_range}")

    parsed_ranges = [parse_hex_range(hr) for hr in ip_ranges]

    for ip1 in range(parsed_ranges[0][0], parsed_ranges[0][1]):
        for ip2 in range(parsed_ranges[1][0], parsed_ranges[1][1]):
            for ip3 in range(parsed_ranges[2][0], parsed_ranges[2][1]):
                for ip4 in range(parsed_ranges[3][0], parsed_ranges[3][1]):
                    for ip5 in range(parsed_ranges[4][0], parsed_ranges[4][1]):
                        for ip6 in range(parsed_ranges[5][0], parsed_ranges[5][1]):
                            for ip7 in range(parsed_ranges[6][0], parsed_ranges[6][1]):
                                for ip8 in range(parsed_ranges[7][0], parsed_ranges[7][1]):
                                    hex_ip1 = format(ip1, '04x')
                                    hex_ip2 = format(ip2, '04x')
                                    hex_ip3 = format(ip3, '04x')
                                    hex_ip4 = format(ip4, '04x')
                                    hex_ip5 = format(ip5, '04x')
                                    hex_ip6 = format(ip6, '04x')
                                    hex_ip7 = format(ip7, '04x')
                                    hex_ip8 = format(ip8, '04x')

                                    yield \
                                        f"{hex_ip1}:{hex_ip2}:{hex_ip3}:{hex_ip4}:{hex_ip5}:{hex_ip6}:{hex_ip7}:{hex_ip8}"


def getIPv6seq(
        ip1='0x0-0xffff',
        ip2='0x0-0xffff',
        ip3='0x0-0xffff',
        ip4='0x0-0xffff',
        ip5='0x0-0xffff',
        ip6='0x0-0xffff',
        ip7='0x0-0xffff',
        ip8='0x0-0xffff'
):
    return _getIPv6seq([ip1, ip2, ip3, ip4, ip5, ip6, ip7, ip8])


def getIPv6seqi(
        ip1='0-65536',
        ip2='0-65536',
        ip3='0-65536',
        ip4='0-65536',
        ip5='0-65536',
        ip6='0-65536',
        ip7='0-65536',
        ip8='0-65536'
):
    # Convert integer ranges to hexadecimal format for compatibility with _getIPv6seq function
    hex_ip_ranges = [f"0x{ip1[0]:04x}-0x{ip1[1]:04x}",
                     f"0x{ip2[0]:04x}-0x{ip2[1]:04x}",
                     f"0x{ip3[0]:04x}-0x{ip3[1]:04x}",
                     f"0x{ip4[0]:04x}-0x{ip4[1]:04x}",
                     f"0x{ip5[0]:04x}-0x{ip5[1]:04x}",
                     f"0x{ip6[0]:04x}-0x{ip6[1]:04x}",
                     f"0x{ip7[0]:04x}-0x{ip7[1]:04x}",
                     f"0x{ip8[0]:04x}-0x{ip8[1]:04x}"]

    # Validate the input ranges
    for range_str in hex_ip_ranges:
        start, end = range_str.split('-')
        if int(start, 16) < 0 or int(end, 16) > 0xffff:
            raise ValueError(f"Invalid IPv6 sequence integer range: {range_str}")

    return _getIPv6seq(hex_ip_ranges)


def IP4to6(ip4):
    ipv4_bytes = ip4.split('.')

    # 将每个字节转换为十六进制并补足到四位（例如 '0' + '123' -> '0123'）
    ipv4_hex = [hex(int(byte))[2:].zfill(2) for byte in ipv4_bytes]

    # IPv4地址内嵌到IPv6地址的格式为 ::ffff:0a0b:0c0d，其中0a0b:0c0d是IPv4地址的十六进制形式
    ipv6_prefix = "ffff:"
    ipv6_mapped = ipv6_prefix + ":".join(ipv4_hex)

    # 前面添加 "::" 表示高位部分全为0
    full_ipv6_address = "::" + ipv6_mapped

    return full_ipv6_address


def toip(url):
    try:
        ip = socket.gethostbyname(url)
    except socket.gaierror:
        ip = None
    return ip


def toname(ip):
    # 尝试将IP地址解析为域名
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except socket.herror:
        # 如果出现无法反向解析IP地址的情况，返回错误信息
        return None
