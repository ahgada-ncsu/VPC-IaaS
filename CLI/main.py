"""
    Defines the client interactions
"""

from api import *
from actions import login, create_account, list_VPCs, list_VMs_in_VPC, create_VPC, create_VM, logout, access_VM, quit, get_VPC_info

user_actions = [
    "create account",
    "login",
    "create VPC",
    "create VM",
    "list_VPCs",
    "Get VPC Info",
    "list VMs in VPC",
    "access VM",
    "logout",
    "quit"
]

# fill this with imported actions

cli_actions = [
    create_account,
    login,
    create_VPC,
    create_VM,
    list_VPCs,
    get_VPC_info,
    list_VMs_in_VPC,
    access_VM,
    logout,
    quit
]

while True:
    # print user action list along with index
    print("CHOOSE ACTION")
    for index, action in enumerate(user_actions):
        print(f"{index+1}. {action}")
    
    print()

    action = int(input("Index: "))

    cli_actions[action-1]()

    print("====================================================================")
    print()
