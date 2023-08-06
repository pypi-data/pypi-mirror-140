import os
import click
import requests
from requests.auth import HTTPBasicAuth


@click.command()
@click.argument("subscription_id")
def get_subscription(subscription_id: int):
    """
    Get info for a specific subscription

    Returns:

    """
    bandwidth_account_id = os.environ["bandwidth_account_id"]
    bandwidth_username = os.environ["bandwidth_username"]
    bandwidth_password = os.environ["bandwidth_password"]
    bandwidth_url = os.environ["bandwidth_url"]

    response = requests.get(
        f"{bandwidth_url}/accounts/{bandwidth_account_id}/subscriptions/{subscription_id}",
        auth=HTTPBasicAuth(bandwidth_username, bandwidth_password),
    )
    response.raise_for_status()
    print("response", response.content)
