"""
    Defines the API calls to the North Bound API
"""
import requests
from utils import get_token
import json

url = "http://127.0.0.1:8000/"

def register_api_call(username, password):
    data = {
        'username': username,
        'password': password
    }
    response = requests.post(url + 'auth/register/', data=data)
    return response.text


def login_api_call(username, password):
    global tokens
    data = {
        'username': username,
        'password': password
    }
    response = requests.post(url + 'auth/token/', data=data)
    return response.text


def create_vpc_api_call(data):
    tokens = get_token()
    response = requests.post(url + 'config/vpc/', data=data, headers={'Authorization': 'Bearer '+tokens["access"]})
    return response.text


def list_vpc_api_call():
    tokens = get_token()
    response = requests.get(url + 'config/vpc/', headers={'Authorization': 'Bearer '+tokens["access"]})
    return response.text


def get_vpc_info_api_call(id):
    tokens = get_token()
    response = requests.put(url + 'config/vpc/', data={"id": id}, headers={'Authorization': 'Bearer '+tokens["access"]})
    return response.text

def create_vm_api_call(data):
    tokens = get_token()
    response = requests.post(url + 'config/vm/', data=data, headers={'Authorization': 'Bearer '+tokens["access"]})
    return response.text

def get_vm_api_call(id):
    tokens = get_token()
    response = requests.put(url + 'config/vm/', data={"id": id}, headers={'Authorization': 'Bearer '+tokens["access"]})
    return response.text

def get_container_api_call(id):
    tokens = get_token()
    response = requests.delete(url + 'config/container/', data={"id": id}, headers={'Authorization': 'Bearer '+tokens["access"]})
    return response.text

def create_container_api_call(data):
    tokens = get_token()
    response = requests.post(url + 'config/container/', data=data, headers={'Authorization': 'Bearer '+tokens["access"]})
    return response.text

def delete_container_api_call(id):
    tokens = get_token()
    response = requests.put(url + 'config/container/', data={"id": id}, headers={'Authorization': 'Bearer '+tokens["access"]})
    return response.text

def delete_vpc_api_call(id):
    tokens = get_token()
    response = requests.post(url + 'config/delete/', data={"id": id}, headers={'Authorization': 'Bearer '+tokens["access"]})
    return response.text

def delete_vm_api_call(id):
    tokens = get_token()
    response = requests.put(url + 'config/delete/', data={"id": id}, headers={'Authorization': 'Bearer '+tokens["access"]})
    return response.text

def inter_vpc_api_call(vpc1, vpc2):
    tokens = get_token()
    response = requests.post(url + 'config/intervpc/', data={"VPCID1": vpc1, "VPCID2": vpc2}, headers={'Authorization': 'Bearer '+tokens["access"]})
    return response.text