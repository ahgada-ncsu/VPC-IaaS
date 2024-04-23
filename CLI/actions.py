"""
    Defines actions that will be triggered upon client actions
"""

from api import get_container_api_call, delete_container_api_call, register_api_call, login_api_call, create_vpc_api_call, list_vpc_api_call, get_vpc_info_api_call, create_vm_api_call, delete_vpc_api_call, delete_vm_api_call, inter_vpc_api_call, create_container_api_call, get_vm_api_call
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

def get_vm():
    VMID = int(input("VM ID: "))
    resp = get_vm_api_call(VMID)
    resp = json.loads(resp)
    if resp["val"]:
        print(resp["data"])
    return resp


def get_container():
    id = int(input("Container ID: "))
    resp = get_container_api_call(id)
    resp = json.loads(resp)
    if resp["val"]:
        print(resp["data"])
    


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
        provider2_sub = resp["data"]["add"]["provider2"]
        tenant2_sub = resp["data"]["add"]["transit2"]

        # create_namespace.yaml with tx-nsy x is tenant id y is the vpc id
        # unc
        os.system(f'ansible-playbook -i CLI/SBA/local_inv CLI/SBA/create_namespace.yaml --extra-vars="namespace_name=t{tenant_id}-ns{vpc_id}"')
        os.system(f'ansible-playbook -i CLI/SBA/remote_inv CLI/SBA/create_namespace.yaml --extra-vars="namespace_name=t{tenant_id}-ns{vpc_id}"')
        
        # create_vpc.yaml with valid args [transit_interface_ip (+2 .15 range)] [vpc_provider_interface_ip (+1 .16 range)] [vpc_provider_subnet= /30 subnet of the veth pair (w/o /30)]
        if resp["data"]["add"]["num_vpcs"] == 1:
            # unc
            os.system(f'ansible-playbook -i CLI/SBA/local_inv CLI/SBA/create_namespace.yaml --extra-vars="namespace_name=transit-{tenant_id}"')
            os.system(f'ansible-playbook -i CLI/SBA/remote_inv CLI/SBA/create_namespace.yaml --extra-vars="namespace_name=transit-{tenant_id}"')
            pass
        
        # unc
        os.system(f'ansible-playbook -i CLI/SBA/local_inv CLI/SBA/create_vpc.yaml --extra-vars="tenant_id={tenant_id} VPC_id={vpc_id} transit_interface_ip={tenant_sub[2]} vpc_provider_interface_ip={provider_sub[1]} provider_interface_ip={provider_sub[2]} vpc_transit_interface_ip={tenant_sub[1]} vpc_provider_subnet="{provider_sub[0].split("/")[0]} logical_provider_subnet={resp["data"]["ser"]["logical_provider_subnet"]}')
        os.system(f'ansible-playbook -i CLI/SBA/remote_inv CLI/SBA/create_vpc.yaml --extra-vars="tenant_id={tenant_id} VPC_id={vpc_id} transit_interface_ip={tenant2_sub[2]} vpc_provider_interface_ip={provider2_sub[1]} provider_interface_ip={provider2_sub[2]} vpc_transit_interface_ip={tenant2_sub[1]} vpc_provider_subnet="{provider2_sub[0].split("/")[0]} logical_provider_subnet={resp["data"]["ser"]["logical_provider_subnet"]}')

        temp = {}
        temp["z1"] = []
        temp["z2"] = []
        for s in resp["data"]["ser"]["PublicSubnet"]["list"]:
            if s["zone"] == 1:
                temp["z1"].append(s)
            else:
                temp["z2"].append(s)
        for s in resp["data"]["ser"]["PrivateSubnet"]["list"]:
            if s["zone"] == 1:
                temp["z1"].append(s)
            else:
                temp["z2"].append(s)

        ind = 0
        for s in temp["z1"]:
            subnet = s["subnet"]
            breakdown = get_ip_breakdown(subnet)
            ind+=1
            # print(breakdown)
            os.system(f'ansible-playbook -i CLI/SBA/local_inv CLI/SBA/create_l2_network.yaml --extra-vars="tenant_id={tenant_id} VPC_id={vpc_id} subnet_id={ind} vm_subnet_gateway_ip={breakdown["gateway"]} vm_subnet_prefix={breakdown["subnet_prefix"]} vm_subnet_prefix_mask={breakdown["mask"]} vm_subnet_broadcast={breakdown["broadcast"]} dhcp_start_range={breakdown["dhcp_start"]} dhcp_end_range={breakdown["dhcp_end"]}"')

        for s in temp["z2"]:
            subnet = s["subnet"]
            breakdown = get_ip_breakdown(subnet)
            ind+=1
            os.system(f'ansible-playbook -i CLI/SBA/remote_inv CLI/SBA/create_l2_network.yaml --extra-vars="tenant_id={tenant_id} VPC_id={vpc_id} subnet_id={ind} vm_subnet_gateway_ip={breakdown["gateway"]} vm_subnet_prefix={breakdown["subnet_prefix"]} vm_subnet_prefix_mask={breakdown["mask"]} vm_subnet_broadcast={breakdown["broadcast"]} dhcp_start_range={breakdown["dhcp_start"]} dhcp_end_range={breakdown["dhcp_end"]}"')
        

        # set gre for zone 1
        os.system(f'ansible-playbook -i CLI/SBA/local_inv CLI/SBA/enable_gre.yaml --extra-vars="tenant_id={tenant_id} vpc_id={vpc_id} gre_tunnel_ip=172.1.1.1/30 local_ip={provider_sub[1]} remote_ip={provider2_sub[1]}"')
        # set gre for zone 2
        os.system(f'ansible-playbook -i CLI/SBA/remote_inv CLI/SBA/enable_gre.yaml --extra-vars="tenant_id={tenant_id} vpc_id={vpc_id} gre_tunnel_ip=172.1.1.2/30 local_ip={provider2_sub[1]} remote_ip={provider_sub[1]}"')

        # add routes for gre in zone 1
        for s in temp["z2"]:
            subnet = s["subnet"]
            os.system(f'ansible-playbook -i CLI/SBA/local_inv CLI/SBA/set_gre_rules.yaml --extra-vars="tenant_id={tenant_id} vpc_id={vpc_id} remote_subnet={subnet} gre_remote_ip=172.1.1.2"')
        
        # add routes for gre in zone 2
        for s in temp["z1"]:
            subnet = s["subnet"]
            os.system(f'ansible-playbook -i CLI/SBA/remote_inv CLI/SBA/set_gre_rules.yaml --extra-vars="tenant_id={tenant_id} vpc_id={vpc_id} remote_subnet={subnet} gre_remote_ip=172.1.1.1"')
        

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


def create_container():
    VPCID = input("VPCID: ")
    Subnet = input("Subnet: ")
    data = {}
    data["State"] = "DOWN"
    data["VPCID"] = VPCID
    data["Subnet"] = Subnet
    data["Name"] = "container"

    resp = create_container_api_call(data)
    resp = json.loads(resp)

    if resp["val"]:
        tenant_id = resp["add"]["tenant_id"]
        container_id = resp["data"]["id"]
        subnet_id = resp["add"]["subnetID"]
        zone = resp["add"]["zone"]
        br = get_ip_breakdown(Subnet)
        if zone == "zone1":
            os.system(f'ansible-playbook -i CLI/SBA/local_inv CLI/SBA/create_container.yaml --extra-vars="tenant_id={tenant_id} container_id={container_id} vpc_id={VPCID} subnet_id={subnet_id} gateway={br["gateway"]}"')
        else:
            pass
            # os.system(f'ansible-playbook -i CLI/SBA/remote_inv CLI/SBA/create_vm.yaml --extra-vars="name={vm_id} tenant_id={tenant_id} VPC_id={VPCID} subnet_id={subnet_id} ram={vpc_data["vRAM"]} vcpu={vpc_data["vCPU"]} disk_space={vpc_data["diskSize"]}G"')
        
        if resp["data"]["logical_provider_ip"] == "":
            print("Run private VM creation SBA")
        else:
            vm_ip = get_container_ip(f"t{tenant_id}-con{container_id}", "docker-br")
            os.system(f'ansible-playbook -i CLI/SBA/local_inv CLI/SBA/dnat.yaml --extra-vars="tenant_id={tenant_id} vpc_id={VPCID} public_ip_mapped={resp["data"]["logical_provider_ip"]} public_subnet_vm_ip={vm_ip} "')
        
        print(resp)
    else:
        print("Error in creating container: ", resp)

def access_container():
    print("AC")
    return ""

def delete_container():
    id = int(input("Container ID: "))
    resp = delete_container_api_call(id)
    resp = json.loads(resp)
    tenant_id = get_tenantid()
    print(resp)
    if resp["data"]["zone"] == 1:
        # pass
        os.system(f'ansible-playbook -i CLI/SBA/local_inv CLI/SBA/delete_container.yaml -vv --extra-vars="tenant_id={tenant_id} container_id={id}"')
    else:
        pass
        # os.system(f'ansible-playbook -i CLI/SBA/remote_inv CLI/SBA/delete_vm.yaml -vv --extra-vars="tenant_id={tenant_id} vm_id={id}"')
    print(resp)


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

    # resp = {'val': True, 'data': {'id': 2, 'Name': 'vm1', 'Image': 'ubuntu', 'SecurityGroup': {}, 'KeyPair': '~/.ssh/id_rsa', 'State': 'DOWN', 'vRAM': 1048576, 'vCPU': 1, 'diskSize': 10, 'logical_provider_ip': '100.64.0.3', 'VPCID': 1, 'subnet': '192.168.4.0/24', 'zone': 1}, 'add': {'tenant_id': 0, 'subnetID': 1, 'zone': 'zone1'}}

    if resp["val"]:
        tenant_id = resp["add"]["tenant_id"]
        vm_id = resp["data"]["id"]
        subnet_id = resp["add"]["subnetID"]
        zone = resp["add"]["zone"]
        if zone == "zone1":
            # pass
            os.system(f'ansible-playbook -i CLI/SBA/local_inv CLI/SBA/create_vm.yaml --extra-vars="name={vm_id} tenant_id={tenant_id} VPC_id={VPCID} subnet_id={subnet_id} ram={vpc_data["vRAM"]} vcpu={vpc_data["vCPU"]} disk_space={vpc_data["diskSize"]}G"')
        else:
            # pass
            os.system(f'ansible-playbook -i CLI/SBA/remote_inv CLI/SBA/create_vm.yaml --extra-vars="name={vm_id} tenant_id={tenant_id} VPC_id={VPCID} subnet_id={subnet_id} ram={vpc_data["vRAM"]} vcpu={vpc_data["vCPU"]} disk_space={vpc_data["diskSize"]}G"')
        
        if resp["data"]["logical_provider_ip"] == "":
            pass
        else:
            vm_ip = get_vm_ip(f"t{tenant_id}-vm{vm_id}")
            os.system(f'ansible-playbook -i CLI/SBA/local_inv CLI/SBA/dnat.yaml --extra-vars="tenant_id={tenant_id} vpc_id={VPCID} public_ip_mapped={resp["data"]["logical_provider_ip"]} public_subnet_vm_ip={vm_ip} "')

    print(resp)


def connect_vpcs():
    VPCID1 = int(input("VPCID1: "))
    VPCID2 = int(input("VPCID2: "))
    resp = inter_vpc_api_call(VPCID1, VPCID2)
    resp = json.loads(resp)
    print(resp)
    if resp["val"]:
        # transit_rules.yaml with valid args
        tenant_id = get_tenantid()
        resp["data"]
        os.system(f'ansible-playbook CLI/SBA/transit_rules.yaml --extra-vars="tenant_id={tenant_id} VPC_ID1={VPCID1} VPC_ID2={VPCID2} subnet_TID_VPC_ID1_transit={resp["data"]["vpc1"]["transit_subnet"]["iplist"][0]} subnet_TID_VPC_ID2_transit={resp["data"]["vpc2"]["transit_subnet"]["iplist"][0]} subnet_in_TID_VPC_ID1={resp["data"]["vpc1"]["subnet"]} subnet_in_TID_VPC_ID2={resp["data"]["vpc2"]["subnet"]} addr_TID_VPC_ID1_VETH2={resp["data"]["vpc1"]["transit_subnet"]["iplist"][1]} addr_TID_VPC_ID1_VETH3={resp["data"]["vpc1"]["transit_subnet"]["iplist"][2]} addr_TID_VPC_ID2_VETH2={resp["data"]["vpc2"]["transit_subnet"]["iplist"][1]} addr_TID_VPC_ID2_VETH3={resp["data"]["vpc2"]["transit_subnet"]["iplist"][2]}"')
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
    resp = get_vm_api_call(vm_id)
    resp = json.loads(resp)
    if resp["data"]["zone"] == 1:
        os.system(f"sudo virsh console t{tid}-vm{vm_id}")
    else:
        os.system(f"ssh -t vmadm@192.168.38.3 -i ~/.ssh/hwssh sudo virsh console t{tid}-vm{vm_id}")

def delete_vpc():
    id = input("VPC ID: ")
    resp = delete_vpc_api_call(id)
    resp = json.loads(resp)
    if resp["val"]:
        # call delete_vpc ansible playbook
        tenant_id = resp["add"]["tenant_id"]
        vpc_id = resp["add"]["id"]
        # num_bridges = 0
        # num_bridges += len(resp["data"]["PublicSubnet"]["list"])
        # num_bridges += len(resp["data"]["PrivateSubnet"]["list"])

        temp = {}
        temp["z1"] = []
        temp["z2"] = []
        for s in resp["data"]["PublicSubnet"]["list"]:
            if s["zone"] == 1:
                temp["z1"].append(s)
            else:
                temp["z2"].append(s)
        for s in resp["data"]["PrivateSubnet"]["list"]:
            if s["zone"] == 1:
                temp["z1"].append(s)
            else:
                temp["z2"].append(s)
        
        z1_start = 1
        z1_end = z1_start + len(temp["z1"]) - 1
        z2_start = z1_end + 1
        z2_end = z2_start + len(temp["z2"]) - 1
        
        if len(temp["z1"]) > 0:
            os.system(f'ansible-playbook -i CLI/SBA/local_inv CLI/SBA/delete_vpc.yaml -vv --extra-vars="tenant_id={tenant_id} vpc_id={vpc_id} zone=zone1 z1_num_bridges={z1_end} z2_start={z2_start} z2_num_bridges={z2_end}"')
        
        if len(temp["z2"]) > 0:
            os.system(f'ansible-playbook -i CLI/SBA/remote_inv CLI/SBA/delete_vpc.yaml -vv --extra-vars="tenant_id={tenant_id} vpc_id={vpc_id} zone=zone2 z1_num_bridges={z1_end} z2_start={z2_start} z2_num_bridges={z2_end}"')

    print(resp)

def delete_vm():
    id = input("VM ID: ")
    resp = delete_vm_api_call(id)
    resp = json.loads(resp)
    # call delete_vm ansible playbook
    tenant_id = get_tenantid()
    if resp["data"]["zone"] == 1:
        os.system(f'ansible-playbook -i CLI/SBA/local_inv CLI/SBA/delete_vm.yaml -vv --extra-vars="tenant_id={tenant_id} vm_id={id}"')
    else:
        os.system(f'ansible-playbook -i CLI/SBA/remote_inv CLI/SBA/delete_vm.yaml -vv --extra-vars="tenant_id={tenant_id} vm_id={id}"')
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