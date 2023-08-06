import os
import click
import requests
import sys
from requests.auth import HTTPBasicAuth

valid_order_types = [
    "portins",
    "orders",
    "portouts",
    "disconnects",
    "dldas",
    "lsrorders",
    "e911s",
    "tnoptions",
    "externalTns",
    "lidb",
    "bulkPortins",
    "importtnorders",
    "removeImportedTnOrders",
    "csrs",
    "emergencyNotificationGroup",
    "emergencyEndpointGroup",
]


@click.command()
@click.argument("order-type", type=click.Choice(valid_order_types))
@click.argument("url", type=str)
@click.option(
    "--expiry",
    "-e",
    is_flag=False,
    default=3122064000,
    help="expiry seconds for subscription",
)
@click.option("--dry-run", "-n", is_flag=True, default=False, help="print XML only")
def create_subscription(
    url: str,
    order_type: str,
    expiry: str,
    dry_run: bool,
):
    """
    Create a Bandwidth webhook subscription.
    Note:  This subscription request does not allow for Callback Credentials

    """
    bandwidth_url = os.environ["bandwidth_url"]
    bandwidth_account_id = os.environ["bandwidth_account_id"]
    bandwidth_username = os.environ["bandwidth_username"]
    bandwidth_password = os.environ["bandwidth_password"]

    xml = f"""<Subscription>
        <OrderType>{order_type}</OrderType>
        <CallbackSubscription>
            <URL>{url}</URL>
            <Expiry>{expiry}</Expiry>
        </CallbackSubscription>
    </Subscription>"""

    if dry_run:
        print(xml)
        sys.exit(0)

    headers = {"Content-Type": "application/xml;charset=utf-8"}
    response = requests.post(
        f"{bandwidth_url}/accounts/{bandwidth_account_id}/subscriptions",
        data=xml,
        headers=headers,
        auth=HTTPBasicAuth(bandwidth_username, bandwidth_password),
    )
    response.raise_for_status()
    print(response.content)
