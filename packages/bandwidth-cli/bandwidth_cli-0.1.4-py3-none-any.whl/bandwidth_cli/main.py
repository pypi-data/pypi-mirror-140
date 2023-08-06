import click
from dotenv import load_dotenv
from bandwidth_cli.commands.create import create_subscription
from bandwidth_cli.commands.delete import delete_subscription
from bandwidth_cli.commands.get import get_subscription
from bandwidth_cli.commands.retrieve import list_subscriptions

load_dotenv()

@click.group(help="CLI tool to manage Bandwidth Subscriptions")
def cli():
    pass


cli.add_command(create_subscription)
cli.add_command(list_subscriptions)
cli.add_command(delete_subscription)
cli.add_command(get_subscription)

if __name__ == "__main__":
    cli()
