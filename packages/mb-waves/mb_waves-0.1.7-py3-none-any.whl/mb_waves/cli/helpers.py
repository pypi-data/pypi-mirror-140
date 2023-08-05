import json

import click
from mb_std.json import CustomJSONEncoder
from pydantic import BaseModel


def print_json(obj: dict | list | BaseModel):
    click.echo(json.dumps(obj, indent=2, cls=CustomJSONEncoder))
