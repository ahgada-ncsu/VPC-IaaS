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
    file = open("server_config.json", "r")
    server_config = file.read()
    server_config = json.loads(server_config)
    file.close()
    VPN_IP = server_config["VPN_IP"]    
    # write the file "/etc/wireguard/wg0.conf"
    file = open("/etc/wireguard/wg0.conf", "w")
    file.write(f"""
[Interface]
PrivateKey = {server_private_key}
Address = {VPN_IP}/24
SaveConfig = true
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT
ListenPort = 51820
""")





def create_peer():
    print("Creating Peer")

def apply_acl():
    print("Applying access control list")

def quit():
    print("Quitting")
    exit()
