import os
from pathlib import Path

import click
from click import Context
from dotenv import load_dotenv

from mb_waves import __version__

from . import generate_accounts_cmd

_env_file = Path(os.getcwd()).joinpath(".env")
if _env_file.is_file():
    load_dotenv(_env_file)


@click.group()
@click.version_option(__version__, help="Show the version and exit")
@click.help_option(help="Show this message and exit")
@click.pass_context
def cli(ctx: Context):
    ctx.ensure_object(dict)


cli.add_command(generate_accounts_cmd.cli)  # noqa
