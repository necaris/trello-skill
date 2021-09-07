# trello api interface
# for now, quick & dirty, using httpx
import typing

from httpx import Auth, Client, Request, Response


class TokenAuth(Auth):
    """
    Allows the 'auth' argument to be passed as a (username, password) pair,
    and uses HTTP Basic authentication.
    """

    def __init__(self, key: str, token: str):
        self.key = key
        self.token = token

    def auth_flow(self, request: Request) -> typing.Generator[Request, Response, None]:
        request.url = request.url.copy_merge_params(
            params={"key": self.key, "token": self.token}
        )
        yield request


def make_client(key: str, token: str) -> Client:
    return Client(base_url="https://api.trello.com/1", auth=TokenAuth(key, token))
