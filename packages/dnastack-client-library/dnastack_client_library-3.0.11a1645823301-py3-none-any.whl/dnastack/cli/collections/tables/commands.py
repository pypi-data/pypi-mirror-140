from ...utils import catch_errors, get_client
from ....client.base_exceptions import ApiError
from ....exceptions import ServiceException
import json
import click


@click.group("tables")
def tables():
    pass


@tables.command("list")
@click.pass_context
@click.argument("collection_name")
@catch_errors((ApiError, ServiceException,))
def list_tables(ctx: click.Context, collection_name: str):
    click.echo(
        json.dumps(
            [t.dict() for t in get_client(ctx)
                .collections
                .get_data_connect_client(collection_name)
                .list_tables()],
            indent=4
        )
    )
