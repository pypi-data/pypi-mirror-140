import click
from dotenv import load_dotenv
from commands.create import create_subscription
from commands.delete import delete_subscription
from commands.get import get_subscription
from commands.retrieve import list_subscriptions

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
