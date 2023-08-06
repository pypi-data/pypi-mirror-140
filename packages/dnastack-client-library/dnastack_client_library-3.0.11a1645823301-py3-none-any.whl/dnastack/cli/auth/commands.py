from time import sleep

import click

from ..utils import catch_errors, get_client
from ...auth import OAuthTokenAuth
from ...auth.session_store import UnknownSessionError
from ...exceptions import (
    LoginException,
    ServiceTypeNotFoundError,
    AuthException,
)


@click.group("auth")
def auth():
    pass


@auth.command("login")
@click.argument("service")
@click.option("--delay-init", type=int, required=False, default=0, help='Delay the authentication by seconds')
@click.option("--no-browser", "-b", is_flag=True, default=False, help='If used, the client will not launch the browser automatically for the device code flow.')
@click.option("--revoke-existing", is_flag=True, default=False, help='If used, the existing session will be automatically revoked before the re-authentication')
@click.option("--refresh-token", is_flag=True, default=False, help='If used, the client will refresh the tokens')
@click.pass_context
@catch_errors(
    error_types=(
        AuthException,
        LoginException,
    ),
    success_msg="Login successful!",
)
def cli_login(ctx: click.Context, service: str, delay_init: int, no_browser: bool, revoke_existing: bool, refresh_token: bool):
    if delay_init > 0:
        sleep(delay_init)

    client = get_client(ctx)

    if service == "data_connect":
        service_to_authorize = client.data_connect
    elif service == "collections":
        service_to_authorize = client.collections
    elif service == "wes":
        service_to_authorize = client.wes
    else:
        raise ServiceTypeNotFoundError(service)

    if not service_to_authorize:
        raise LoginException(msg="There is no configured service")
    elif not service_to_authorize.auth:
        raise LoginException(msg="The authentication information is not defined")

    authorizer: OAuthTokenAuth = service_to_authorize.auth

    if refresh_token:
        authorizer.refresh_session()
    else:
        try:
            if authorizer.session:
                if not revoke_existing:
                    click.secho(
                        f'This client has been authorized to access to the "{service}" API at {service_to_authorize.url}. '
                        'You can force the reauthorization process by adding "--force" to this command.',
                        bg='yellow',
                        fg='black'
                    )
                    return
                else:
                    authorizer.revoke_session()
        except UnknownSessionError:
            pass

        authorizer.authorize(service_to_authorize.url, open_browser=(not no_browser))

