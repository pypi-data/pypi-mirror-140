import click
import pydash

from mb_waves.cli.helpers import print_json
from mb_waves.waves import account


@click.command(name="generate-accounts", help="Generate new accounts")
@click.option("--limit", "-l", type=int, default=5)
@click.option("--no-seed", is_flag=True, help="Don't output seed")
@click.option("--dict", "dict_", is_flag=True, help="Don't output seed")
def cli(limit: int, no_seed: bool, dict_: bool):
    accounts = [account.generate_new_account().dict() for _ in range(limit)]
    if dict_:
        print_json({a["address"]: a["private_key"] for a in accounts})
    else:
        if no_seed:
            accounts = [pydash.omit(a, "seed") for a in accounts]
        print_json(accounts)
