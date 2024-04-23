import json
import ipaddress
import pexpect
import subprocess
import re


"""
    Defines utility functions
"""

def get_token():
    with open('CLI/files/tokens.json') as file:
        data = json.load(file)
    return data

def get_tenantid():
    with open('CLI/files/tenant.json') as file:
        data = json.load(file)
    return data["tenant_id"]


def get_ip_breakdown(subnet):
    subnet_mask = int(subnet.split('/')[1])
    subnet_prefix = subnet.split('/')[0]
    host = ipaddress.IPv4Network(subnet)
    mask = ipaddress.IPv4Network(subnet).netmask
    net = ipaddress.IPv4Network(subnet_prefix + '/' + str(mask), False)
    broadcast = net.broadcast_address
    gateway = host[1]
    first = host[2]
    last = host[-2]

    return {
        "mask": subnet_mask,
        "subnet_prefix": subnet_prefix,
        "broadcast": broadcast,
        "gateway": gateway,
        "dhcp_start": first,
        "dhcp_end": last
    }

def get_vm_ip(vm_name):
    try:
        child = pexpect.spawn(f"sudo virsh console {vm_name}", timeout=180)
        child.expect(b'Escape character is')
        child.sendline()
        index = child.expect([b'login:', b'#'])
        if index == 0:
            child.sendline(b'root')
            child.expect(b'Password:')
            child.sendline(b'root')
            child.expect(b'#')
        child.sendline(b'ip a')
        child.expect(b'#')
        ip_a_output = child.before.decode()
        child.close()
        lines = ip_a_output.split('\n')
        enp1s0_index = lines.index(next((line for line in lines if 'enp1s0:' in line), None))
        inet_line = next((line for line in lines[enp1s0_index + 1:] if 'inet ' in line), None)
        if inet_line:
            ip_address = inet_line.split()[1].split('/')[0]
            return ip_address
        else:
            return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


def get_container_ip(container_name, interface):
    try:
        command = f'sudo docker exec -it {container_name} bash -c "ip addr show {interface}"'
        output = subprocess.check_output(command, shell=True, encoding='utf-8')
        match = re.search(r'inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/\d{1,2}', output)
        if match:
            inet_address = match.group(1)
            return inet_address
        else:
            return "No inet address found"
    except subprocess.CalledProcessError as e:
        return f"An error occurred: {e}"