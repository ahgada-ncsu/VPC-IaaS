"""
    Defines the client interactions with VPN
"""
from actions import *


user_actions = [
    "Create VPN Server",
    "Create Peers",
    "Apply access control list",
    "Quit"
]

# fill this with imported actionsl

cli_actions = [
    create_vpn_server,
    create_peer,
    apply_acl,
    quit
]

while True:

    print("CHOOSE ACTION")
    for index, action in enumerate(user_actions):
        print(f"{index+1}. {action}")
    
    print()

    action = int(input("Index: "))

    cli_actions[action-1]()

    print("====================================================================")
    print()
