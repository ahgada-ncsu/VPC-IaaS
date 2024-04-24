import os
import json

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
    peer_private_key = os.popen(f'cat /etc/wireguard/{name}_private.key').read()
    peer_public_key = os.popen(f'cat /etc/wireguard/{name}_public.key').read()
    server_public_key = os.popen('cat /etc/wireguard/server_public.key').read()
    
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

    # write the file to CLI/peer_configs/name.conf
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

def apply_acl():
    print("Applying access control list")

def quit():
    print("Quitting")
    exit()