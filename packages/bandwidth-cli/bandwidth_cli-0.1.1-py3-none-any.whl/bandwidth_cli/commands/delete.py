import os
import click
import requests
import sys
from requests.auth import HTTPBasicAuth


@click.command()
@click.option("--subscription_id", help="Subscription ID")
@click.option("--confirm", prompt='Are you sure you wish to delete this subscription?', is_flag=True)
def delete_subscription(subscription_id: int, confirm: bool):
    """
    Delete a subscription

    Args:
        subscription_id:

    Returns:

    """
    if not confirm:
        print("Nope, not doing it")
        sys.exit(0)

    bandwidth_url = os.environ["bandwidth_url"]
    bandwidth_account_id = os.environ["bandwidth_account_id"]
    bandwidth_username = os.environ["bandwidth_username"]
    bandwidth_password = os.environ["bandwidth_password"]

    response = requests.delete(
        f"{bandwidth_url}/accounts/{bandwidth_account_id}/subscriptions/{subscription_id}",
        auth=HTTPBasicAuth(bandwidth_username, bandwidth_password),
    )
    response.raise_for_status()
    print(response.content)
