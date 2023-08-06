#VLAN Change CLI
#2021 - Angelo Poggi

import click
from vlanchange import vlan_change

@click.group(help =
            '''Change a VLAN to a new VLAN on a switch with that VLAN tagged''')
def cli():
    pass

@click.command()
@click.option(
    '--source', '-s', help="Source VLAN you want to change",
    required=True,
    type=str
)
@click.option(
    '--destination', '-d', help="Vlan you want to currently use",
    required=True,
    type=str
)
@click.option(
    '--name', '-n', help="Name of the Vlan",
    required=True,
    type=str
)
@click.option(
    '--switch', '-sw', help="Switch you want to make the changes on",
    required=True,
    type=str
)
def modify():
    return vlan_change()
