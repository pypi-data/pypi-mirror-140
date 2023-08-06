import os
import click
from dotenv import load_dotenv
from commands import create
from commands import delete
from commands import get
from commands import retrieve

load_dotenv()

@click.group(help="CLI tool to manage Bandwidth Subscriptions")
def cli():
    pass


cli.add_command(create.create_subscription)
cli.add_command(retrieve.list_subscriptions)
cli.add_command(delete.delete_subscription)
cli.add_command(get.get_subscription)

if __name__ == "__main__":
    cli()
