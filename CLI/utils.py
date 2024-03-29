import json

"""
    Defines utility functions
"""

def get_token():
    with open('CLI/files/tokens.json') as file:
        data = json.load(file)
    return data