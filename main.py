from pyodide.http import pyfetch
import asyncio
import json
from typing import Union, List


class ApiClient:
    async def login(self, email: str = "", password: str = "") -> dict:
        """ Enter the LernSax session """
        if not email or not password:
            email, password = self.email, self.password
        results_raw = await self.post(
            self.jsonrpc(
                [
                    [
                        1,
                        "login",
                        {"login": email, "password": password,
                            "get_miniature": True},
                    ],
                    [999, "get_information", {}],
                ]
            )
        )

        return results_raw


class Client(ApiClient):
    """ Main object for handling LernSax access and responses. """

    def jsonrpc(self, data: list):
        """
        Prepares Data to be sent to the API in correct jsonrpc format
        """
        return [{"id": k[0], "jsonrpc": "2.0", "method": k[1], "params": k[2]} for k in data]

    def __init__(self, email: str, password: str):
        self.email: str = email
        self.password: str = password
        self.sid: str = ""
        self.member_of: List[str] = []
        self.root_url: str = "https://www.lernsax.de"
        self.api: str = f"{self.root_url}/jsonrpc.php"

    async def post(self, _json: Union[dict, str, list]):
        res = await pyfetch(
            self.api,
            body=json.dumps(_json),
            method="POST"
        )
        return await res.json()


client = Client(
    input("Email: "),
    input("Passwort: ")
)

await client.login()
