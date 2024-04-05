"""
    Defines actions that will be triggered upon client actions
"""

from api import register_api_call, login_api_call, create_vpc_api_call, list_vpc_api_call, get_vpc_info_api_call, create_vm_api_call, delete_vpc_api_call, delete_vm_api_call, inter_vpc_api_call
import json
import os
from pprint import pprint
from utils import *


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
    print(resp)
    if resp["data"]["val"]:
        tokens = resp["data"]["tokens"]
        with open("CLI/files/tokens.json", "w") as file:
            json.dump(tokens, file)
        with open("CLI/files/tenant.json", "w") as file:
            json.dump(resp["data"]["details"], file)
        
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
    resp = json.loads(resp)
    if resp["val"]:
        
        vpc_id = resp["data"]["ser"]["id"]
        tenant_id = resp["data"]["add"]["tenant_id"]
        provider_sub = resp["data"]["add"]["provider"]
        tenant_sub = resp["data"]["add"]["transit"]

        # create_namespace.yaml with tx-nsy x is tenant id y is the vpc id
        os.system(f'ansible-playbook CLI/SBA/create_namespace.yaml --extra-vars="namespace_name=t{tenant_id}-ns{vpc_id}"')
        
        # create_vpc.yaml with valid args [transit_interface_ip (+2 .15 range)] [vpc_provider_interface_ip (+1 .16 range)] [vpc_provider_subnet= /30 subnet of the veth pair (w/o /30)]
        if resp["data"]["add"]["num_vpcs"] == 1:
            #create_namespace.yaml with transit-xh
            #print("Call Southbound API for Creating first VPC -> With Transit gateway")
            os.system(f'ansible-playbook CLI/SBA/create_namespace.yaml --extra-vars="namespace_name=transit-{tenant_id}"')
        
        os.system(f'ansible-playbook CLI/SBA/create_vpc.yaml --extra-vars="tenant_id={tenant_id} VPC_id={vpc_id} transit_interface_ip={tenant_sub[2]} vpc_provider_interface_ip={provider_sub[1]} provider_interface_ip={provider_sub[2]} vpc_transit_interface_ip={tenant_sub[1]} vpc_provider_subnet="{provider_sub[0].split("/")[0]}')

        # for each subnet call:
            # create_l2_network.yaml with net utilities
            # DC os.system('ansible-playbook CLI/SBA/create_l2_networks.yaml --extra-vars="tenant_id=x VPC_id=y subnet_id=z(from loop) vm_subnet_gateway_ip=10.10.5.1 vm_subnet_prefix=10.10.5.0 vm_subnet_prefix_mask=24 vm_subnet_broadcast=10.10.5.255 dhcp_start_range=10.10.5.2 dhcp_end_range=10.10.5.254"')
        ind = 0
        for s in resp["data"]["ser"]["PublicSubnet"]["list"]:
            subnet = s["subnet"]
            breakdown = get_ip_breakdown(subnet)
            ind+=1
            os.system(f'ansible-playbook CLI/SBA/create_l2_network.yaml --extra-vars="tenant_id={tenant_id} VPC_id={vpc_id} subnet_id={ind} vm_subnet_gateway_ip={breakdown["gateway"]} vm_subnet_prefix={breakdown["subnet_prefix"]} vm_subnet_prefix_mask={breakdown["mask"]} vm_subnet_broadcast={breakdown["broadcast"]} dhcp_start_range={breakdown["dhcp_start"]} dhcp_end_range={breakdown["dhcp_end"]}"')
        for s in resp["data"]["ser"]["PrivateSubnet"]["list"]:
            ind+=1
            subnet = s["subnet"]
            breakdown = get_ip_breakdown(subnet)
            os.system(f'ansible-playbook CLI/SBA/create_l2_network.yaml --extra-vars="tenant_id={tenant_id} VPC_id={vpc_id} subnet_id={ind} vm_subnet_gateway_ip={breakdown["gateway"]} vm_subnet_prefix={breakdown["subnet_prefix"]} vm_subnet_prefix_mask={breakdown["mask"]} vm_subnet_broadcast={breakdown["broadcast"]} dhcp_start_range={breakdown["dhcp_start"]} dhcp_end_range={breakdown["dhcp_end"]}"')
        print("Success")
        print(resp)
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
 
#  gatewaydisti

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
    data["State"] = "DOWN"
    data["SecurityGroup"] = json.dumps(vpc_data["SecurityGroup"])
    data["VPCID"] = VPCID
    data["Subnet"] = Subnet

    resp = create_vm_api_call(data)
    resp = json.loads(resp)

    if resp["val"]:
        # call create_vm with valid args
        tenant_id = resp["add"]["tenant_id"]
        vm_id = resp["data"]["id"]
        subnet_id = resp["add"]["subnetID"]
        os.system(f'ansible-playbook CLI/SBA/create_vm.yaml --extra-vars="name={vm_id} tenant_id={tenant_id} VPC_id={VPCID} subnet_id={subnet_id} ram={vpc_data["vRAM"]} vcpu={vpc_data["vCPU"]} disk_space={vpc_data["diskSize"]}G"')
        if resp["data"]["logical_provider_ip"] == "":
            print("Run private VM creation SBA")
        else:
            print("Run public VM creation SBA")

    print(resp)

def connect_vpcs():
    VPCID1 = int(input("VPCID1: "))
    VPCID2 = int(input("VPCID2: "))
    resp = inter_vpc_api_call(VPCID1, VPCID2)
    resp = json.loads(resp)
    if resp["val"]:
        # transit_rules.yaml with valid args
        # os.system('ansible-playbook CLI/SBA/transit_rules.yaml --extra-vars="tenant_id=x VPC_ID1=y1 VPC_ID2=y2 subnet_TID_VPC_ID1_transit=172.15.1.0/30 subnet_TID_VPC_ID2_transit=172.15.1.4/30 subnet_in_TID_VPC_ID1=10.10.5.0/24 subnet_in_TID_VPC_ID2=10.10.6.0/24 addr_TID_VPC_ID1_VETH2=172.15.1.1 addr_TID_VPC_ID1_VETH3=172.15.1.2 addr_TID_VPC_ID2_VETH2=172.15.1.5 addr_TID_VPC_ID2_VETH3=172.15.1.6"')
        print("Success")
        print("Call southbound API for Inter connecting VPCs here")
    else:
        print("Failed")
    print(resp)

# 172.168.1.18
# 172.167.2.169

def access_VM():
    tid = get_tenantid()
    vm_id = input("VM ID: ")
    os.system(f"sudo virsh console t{tid}-vm{vm_id}")

def delete_vpc():
    id = input("VPC ID: ")
    resp = delete_vpc_api_call(id)
    resp = json.loads(resp)
    # call delete_vpc ansible playbook
    tenant_id = resp["add"]["tenant_id"]
    vpc_id = resp["add"]["id"]
    num_bridges = 0
    num_bridges += len(resp["data"]["PublicSubnet"]["list"])
    num_bridges += len(resp["data"]["PrivateSubnet"]["list"])
    if resp["val"]:
        os.system(f'ansible-playbook CLI/SBA/delete_vpc.yaml -vv --extra-vars="tenant_id={tenant_id} vpc_id={vpc_id} num_bridges={num_bridges} last_vpc=true"')
    print(resp)

def delete_vm():
    id = input("VM ID: ")
    resp = delete_vm_api_call(id)
    resp = json.loads(resp)
    # call delete_vm ansible playbook
    tenant_id = get_tenantid()
    os.system(f'ansible-playbook CLI/SBA/delete_vm.yaml -vv --extra-vars="tenant_id={tenant_id} vm_id={id}"')
    print(resp)


def logout():
    try:
        os.remove("CLI/files/tokens.json")
        os.remove("CLI/files/tenant.json")
    except:
        pass
    print("Logout Successful")


def quit():
    logout()
    exit()