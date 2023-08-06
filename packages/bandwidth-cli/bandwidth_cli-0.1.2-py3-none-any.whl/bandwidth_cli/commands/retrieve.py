import os
import click
import requests
import xmltodict
from requests.auth import HTTPBasicAuth


@click.command()
def list_subscriptions():
    """
    List subscriptions

    Returns:

    """
    bandwidth_account_id = os.environ["bandwidth_account_id"]
    bandwidth_username = os.environ["bandwidth_username"]
    bandwidth_password = os.environ["bandwidth_password"]
    bandwidth_url = os.environ["bandwidth_url"]

    response = requests.get(
        f"{bandwidth_url}/accounts/{bandwidth_account_id}/subscriptions",
        auth=HTTPBasicAuth(bandwidth_username, bandwidth_password),
    )
    response.raise_for_status()
    print("response", xmltodict.parse(response.content))
