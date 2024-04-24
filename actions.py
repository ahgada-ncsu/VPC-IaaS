import os
import json
import pandas as pd
import subprocess
from datetime import datetime

"""
    Create the wireguard private key for the server
    Set permissions
    Create the wireguard public key

    Read the user config file to get the private IP range.

    Create the wireguard config file

"""
def create_vpn_server():
    print("Creating VPN Server")
    os.system("wg genkey | sudo tee /etc/wireguard/server_private.key")
    os.system("sudo chmod go= /etc/wireguard/server_private.key")
    os.system("sudo cat /etc/wireguard/server_private.key | wg pubkey | sudo tee /etc/wireguard/server_public.key")
    server_private_key = os.popen('cat /etc/wireguard/server_private.key').read()
    # server_public_key = os.popen('cat /etc/wireguard/server_public.key').read()
    # listen_port = 51820
    # read the file "server_config.json"
    file = open("CLI/server_config.json", "r")
    server_config = file.read()
    server_config = json.loads(server_config)
    file.close()
    VPN_IP = server_config["VPN_IP"]    
    # write the file "/etc/wireguard/wg0.conf"
    file = open("/etc/wireguard/wg0.conf", "w")
    file.write(f"""
[Interface]
PrivateKey = {server_private_key}
Address = {VPN_IP}
SaveConfig = true
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT
ListenPort = 51820
""")
    os.system("sudo wg-quick up wg0")



"""
    Get peer name
    Get peer IP

    Create peer public key 
    Create peer private key

    Read server public key
    Add peer to server

    Create a peer config file to share with client
"""
def create_peer():
    name = input("Peer Name: ")
    peer_IP = input("Peer IP: ")

    # read the file "peer_config.json"
    file = open("CLI/peer_config.json", "r")
    peer_config = file.read()
    peer_config = json.loads(peer_config)
    file.close()

    if name in peer_config:
        print("Peer already exists")
        return

    os.system(f"wg genkey | sudo tee /etc/wireguard/{name}_private.key")
    os.system(f"sudo chmod go= /etc/wireguard/{name}_private.key")
    os.system(f"sudo cat /etc/wireguard/{name}_private.key | wg pubkey | sudo tee /etc/wireguard/{name}_public.key")
    peer_private_key = os.popen(f'cat /etc/wireguard/{name}_private.key').read().strip()
    peer_public_key = os.popen(f'cat /etc/wireguard/{name}_public.key').read().strip()
    server_public_key = os.popen('cat /etc/wireguard/server_public.key').read().strip()
    
    # read the file "server_config.json"
    file = open("CLI/server_config.json", "r")
    server_config = file.read()
    server_config = json.loads(server_config)
    file.close()
    fp = server_config["Container FP IP"]
    vpn_ip = server_config["VPN_IP"]

    peer_config[name] = {}
    peer_config[name]["IP"] = peer_IP
    peer_config[name]["PublicKey"] = peer_public_key
    peer_config[name]["PrivateKey"] = peer_private_key
    peer_config[name]["ServerPublicKey"] = server_public_key

    # write the file "peer_config.json"
    file = open("CLI/peer_config.json", "w")
    file.write(json.dumps(peer_config))
    file.close()

    file = open(f"CLI/peer_configs/{name}.conf", "w")
    file.write(f"""[Interface]
PrivateKey={peer_private_key}
Address={peer_IP}
PostUp = ip route del default via 172.17.0.1 dev eth0; ip route add default via {vpn_ip.split("/")[0]} dev wg0
PostDown = ip route del default via {vpn_ip.split("/")[0]} dev wg0; ip route add default via 172.17.0.1 dev eth0

[Peer]
PublicKey={server_public_key}
AllowedIPs=0.0.0.0/0
Endpoint={fp}:51820
""")
    file.close()
    os.system(f"sudo wg set wg0 peer {peer_public_key} allowed-ips {peer_IP.split('/')[0]}")
    os.system("sudo wg-quick down wg0")
    os.system("sudo wg-quick up wg0")

def apply_acl():
    print("Applying access control list")
    os.system(f'iptables -t filter -F FORWARD')
    config = {}
    with open("CLI/acl.json", 'r') as file:
        config = json.load(file)
    for acl_rule in config['acl']:
        cip = acl_rule['cip']
        allowed_subnets = set(config['pvt'][index] for index in acl_rule.get('allow', []))
        if cip:  # Check if cip is specified
            for subnet in config['pvt']:
                if subnet not in allowed_subnets:
                    os.system(f'iptables -I FORWARD 1 -i wg0 -s {cip} -d {subnet} -j DROP')
        else:
            print("Warning: 'cip' is not specified for ACL rule.")
    print("ACL applied!")


def monitor_cpu():
    print("Get result for past N seconds")
    n = input("N: ")
    f = input("Output csv file name: ")
    df = pd.read_csv("logs/cpu.csv")
    df1 = df[0:1]
    df = pd.concat([ df1, df.tail(int(n))])
    df.to_csv(f)
    

def monitor_memory():
    print("Get result for past N seconds")
    n = input("N: ")
    f = input("Output csv file name: ")
    df = pd.read_csv("logs/mem.csv")
    df1 = df[0:1]
    df = pd.concat([ df1, df.tail(int(n))])
    df.to_csv(f)

def monitor_traffic():
    print("Get result for past N seconds")
    n = input("N: ")
    f = input("Output csv file name: ")
    df = pd.read_csv("logs/traffic.csv")
    df1 = df[0:1]
    df = pd.concat([ df1, df.tail(int(n))])
    df.to_csv(f)

def net_band():
    command = ['sudo', 'iftop', '-t', '-s', '5']
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    with open('iftop_output_parsed.txt', 'a') as output_file:
        while True:
            line = process.stdout.readline().strip()
            if not line:
                break
            parsed_output = line.strip()
            output_file.write(f"{datetime.now()} - {parsed_output}\n")
    os.system("cat iftop_output_parsed.txt")

def audit_net():
    print("Get last N records")
    n = input("N: ")
    f = input("Output csv file name: ")
    df = pd.read_csv("logs/audit.csv")
    df1 = df[0:1]
    df = pd.concat([ df1, df.tail(int(n))])
    df.to_csv(f)


def quit():
    print("Quitting")
    exit()