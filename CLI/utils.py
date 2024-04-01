import json
import ipaddress


"""
    Defines utility functions
"""

def get_token():
    with open('CLI/files/tokens.json') as file:
        data = json.load(file)
    return data


def get_ip_breakdown(subnet):
    subnet_mask = int(subnet.split('/')[1])
    subnet_prefix = subnet.split('/')[0]
    host = ipaddress.IPv4Network(subnet)
    mask = ipaddress.IPv4Network(subnet).netmask
    net = ipaddress.IPv4Network(subnet_prefix + '/' + str(mask), False)
    broadcast = net.broadcast_address
    gateway = host[0]
    first = host[1]
    last = host[-2]

    return {
        "mask": subnet_mask,
        "subnet_prefix": subnet_prefix,
        "broadcast": broadcast,
        "gateway": gateway,
        "dhcp_start": first,
        "dhcp_end": last
    }