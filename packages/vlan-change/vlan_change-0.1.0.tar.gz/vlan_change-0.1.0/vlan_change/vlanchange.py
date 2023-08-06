#VLAN change
#2021 - Angelo Poggi

import click
from vlan_change.creds import ROUTER_PASSWORD, ROUTER_USERNAME, SECRET
from netmiko import ConnectHandler

def vlan_change(source, target,name, switch):
    device = {
        'device_type' : 'cisco_ios',
        'ip' : switch,
        'username' : ROUTER_USERNAME,
        'password' : ROUTER_PASSWORD,
        'secret' : SECRET
    }

    net_connect = ConnectHandler(**device)
    net_connect.enable()

    trunking_vlan = "4000"
    vlan_check = "none"

    vlan_status = net_connect.send_command("show vlan", use_textfsm=True)
    for vlan in vlan_status:
        if vlan['vlan_id'] == target:
            vlan_check = "exists"
            print(f"Vlan {target} exists. No need to create")
            break
        else:
            vlan_check = "not-exist"
            print(f"Vlan {target} does not exist. Need to create")

    # create target vlan if it doesn't exist
    if vlan_check == "not-exist":
        vlan_commands = [
            f'vlan {target}',
            f'name {name}',
            'end'
        ]
        print(f"Need to create vlan {target}")
        net_connect.send_config_set(vlan_commands)

    # change access ports from source vlan to target vlan
    inter_status = net_connect.send_command("show interface status", use_textfsm=True)
    for iface in inter_status:
        access_config_commands = [
            f"interface {iface['port']}",
            'switchport mode access',
            f'switchport access vlan {target}',
            'end'
        ]
        if iface['vlan'] == source:
            print(f"Need to change vlan on {iface['port']}")
            net_connect.send_config_set(access_config_commands)
        else:
            print("Do NOT need to change vlan on " + iface['port'])

    # trunk target vlan
    trunk_status = net_connect.send_command(f"show spanning-tree vlan {trunking_vlan}", use_textfsm=True)
    for iface in trunk_status:
        if iface['type'] == "Shr " or iface['type'] == "P2p ":
            trunk_config_commands = [
                f"interface {iface['interface']}",
                f'switchport trunk allowed vlan add {target}',
                'end'
            ]
            print(f"Need to trunk vlan on {iface['interface']}")
            net_connect.send_config_set(trunk_config_commands)
        else:
            print(f"Do NOT need to trunk vlan on {iface['interface']}")