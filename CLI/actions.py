"""
    Defines actions that will be triggered upon client actions
"""

from api import register_api_call, login_api_call, create_vpc_api_call, list_vpc_api_call, get_vpc_info_api_call
import json
import os
from pprint import pprint


def create_account():
    username = input("Username: ")
    password = input("Password: ")
    resp = register_api_call(username, password)
    print(resp)
    print()



def login():
    username = input("Username: ")
    password = input("Password: ")
    resp = login_api_call(username, password)
    resp = json.loads(resp)
    if resp["data"]["val"]:
        tokens = resp["data"]["tokens"]
        with open("CLI/files/tokens.json", "w") as file:
            json.dump(tokens, file)
        print("Login Successful")
    else:
        print("Login Failed")
    print()



def list_VPCs():
    resp = list_vpc_api_call()
    resp = json.loads(resp)
    if resp["val"]:
        for i in resp["data"]:
            pprint(i)



def list_VMs_in_VPC():
    print("list VMs in VPC")



def create_VPC():
    with open("CLI/files/vpc.json", "r") as file:
        vpc_data = json.load(file)
    data = {}
    data["Name"] = vpc_data["Name"]
    data["Zone"] = vpc_data["Zone"]
    data["subnet"] = vpc_data["subnet"]
    data["PublicSubnet"] = json.dumps(vpc_data["PublicSubnet"])
    data["PrivateSubnet"] = json.dumps(vpc_data["PrivateSubnet"])
    resp = create_vpc_api_call(data)
    if json.loads(resp)["val"]:
        print("Call southbound API for creating VPCs")
        print("Success")
    else:
        print("Failed")
        print(resp)



def get_VPC_info():
    id = input("VPC ID: ")
    resp = get_vpc_info_api_call(id)
    resp = json.loads(resp)
    if resp["val"]:
        pprint(resp["data"])
    else:
        print("Success")


def create_VM():
    VPCID = input("VPCID: ")
    Subnet = input("Subnet: ")
    with open("CLI/files/vm.json", "r") as file:
        vpc_data = json.load(file)
    data = {}
    data["Name"] = vpc_data["Name"]
    data["Image"] = vpc_data["Image"]
    data["KeyPair"] = vpc_data["KeyPair"]
    data["vRAM"] = vpc_data["vRAM"]
    data["vCPU"] = vpc_data["vCPU"]
    data["diskSize"] = vpc_data["diskSize"]
    data["State "] = vpc_data["State "]
    data["SecurityGroup"] = json.dumps(vpc_data["SecurityGroup"])



def access_VM():
    print("access VM -> To be implemented")


def logout():
    try:
        os.remove("CLI/files/tokens.json")
    except:
        pass
    print("Logout Successful")


def quit():
    logout()
    exit()