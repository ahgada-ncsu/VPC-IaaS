"""
    Defines the client interactions
"""

import os
from api import *
from actions import login, create_account, list_VPCs, list_VMs_in_VPC, create_VPC, create_VM, logout, access_VM, quit, get_VPC_info, delete_vpc, delete_vm, connect_vpcs

auth_user_actions = [
    "Create Account",
    "Login"
]

auth_cli_actions = [
    create_account,
    login
]

user_actions = [
    "Create VPC",
    "Create VM",
    "List_VPCs",
    "Get VPC Info",
    "List VMs in VPC",
    "Connect VPCs",
    "Access VM",
    "Delete VPC",
    "Delete VM",
    "Logout",
    "Quit"
]

# fill this with imported actionsl

cli_actions = [
    create_VPC,
    create_VM,
    list_VPCs,
    get_VPC_info,
    list_VMs_in_VPC,
    connect_vpcs,
    access_VM,
    delete_vpc,
    delete_vm,
    logout,
    quit
]

while True:
    # code to check if file "files/token.json" exists
    # if not, then create account or login
    # else, proceed with the actions
    if not os.path.exists("CLI/files/tokens.json"):
        print("CHOOSE ACTION")
        for index, action in enumerate(auth_user_actions):
            print(f"{index+1}. {action}")

        print()

        action = int(input("Index: "))

        auth_cli_actions[action-1]()
    else:
        print("CHOOSE ACTION")
        for index, action in enumerate(user_actions):
            print(f"{index+1}. {action}")
        
        print()

        action = int(input("Index: "))

        cli_actions[action-1]()

    print("====================================================================")
    print()
