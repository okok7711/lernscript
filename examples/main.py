from pyodide.http import pyfetch
import asyncio
import json
from typing import Union, List, Type
from abc import ABC
from box import Box

class ConsequentialError(Exception):
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)


class NotLoggedIn(Exception):
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)


class AccessDenied(Exception):
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)


class InvalidSession(Exception):
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)


class MailError(Exception):
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)


class FolderNotFound(Exception):
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)


class EntryNotFound(Exception):
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)


class UnkownError(Exception):
    def __init__(*args, **kwargs):
        Exception.__init__(*args, **kwargs)


def error_handler(errno: str) -> Type[Exception]:
    """
    returns an Exception for the given error code
    """
    err_dict = {
        "107": AccessDenied,
        "103": AccessDenied,
        "106": InvalidSession,
        "111": MailError,
        "247": FolderNotFound,
        "117": EntryNotFound,
        "9999": ConsequentialError
    }
    if errno in err_dict:
        return err_dict[errno]
    else:
        return UnkownError


class ApiClient(ABC):
    def pack_responses(self, results: list, main_answer_index: int) -> dict:
        """
        Packs multiple method responses together.
        The main response is accessible through the "result" key.
        Helper method responses are accessible through the "helpers" key of the returned dict.
        """
        packed_results = Box({"result": results.pop(
            main_answer_index), "helpers": results})
        return packed_results.to_dict()

    def jsonrpc(self, data: list):
        """
        Prepares Data to be sent to the API in correct jsonrpc format
        """
        return [{"id": k[0], "jsonrpc": "2.0", "method": k[1], "params": k[2]} for k in data]

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
        results = [Box(res) for res in results_raw]

        if results[0].result["return"] != "OK":
            raise error_handler(
                results[0].result.errno)(results_raw[0]["result"])

        self.sid, self.email, self.password, self.member_of = (
            results[1].result.session_id,
            email,
            password,
            [member.login for member in results[0].result.member],
        )
        return self.pack_responses(results_raw, 0)

    async def refresh_session(self) -> dict:
        """ Refreshes current LernSax session. """
        if not self.sid:
            raise NotLoggedIn()
        results_raw = await self.post(self.jsonrpc([[1, "set_session", {"session_id": self.sid}]]))
        return self.pack_responses(results_raw, 0)

    async def logout(self) -> dict:
        """ Exit the LernSax session """
        results_raw = await self.post(
            self.jsonrpc(
                [
                    [1, "set_session", {"session_id": self.sid}],
                    [2, "set_focus", {"object": "settings"}],
                    [3, "logout", {}],
                ]
            )
        )
        results = [Box(res) for res in results_raw]
        if results[-1].result["return"] != "OK":
            raise error_handler(
                results[-1].result.errno)(results_raw[-1]["result"])
        self.sid = ""
        return self.pack_responses(results_raw, 2)

    async def get_tasks(self, group: str) -> dict:
        """ Get LernSax tasks, thanks to  TKFRvisionOfficial for finding the json rpc request """
        if not self.sid:
            raise NotLoggedIn()
        results_raw = await self.post(
            self.jsonrpc(
                [
                    [1, "set_session", {"session_id": self.sid}],
                    [2, "set_focus", {"login": group, "object": "tasks"}],
                    [3, "get_entries", {}],
                ]
            )
        )
        return self.pack_responses(results_raw, 2)

    # FileRequest

    async def get_download_url(self, login: str, id: str) -> dict:
        """ Gets download id with the file id """
        if not self.sid:
            raise NotLoggedIn()
        results_raw = await self.post(
            self.jsonrpc(
                [
                    [1, "set_session", {"session_id": self.sid}],
                    [2, "set_focus", {"login": login, "object": "files"}],
                    [3, "get_file_download_url", {"id": id}],
                ]
            )
        )
        return self.pack_responses(results_raw, 2)

    # ForumRequest

    async def get_board(self, login: str) -> dict:
        """ Gets messages board for specified login """
        if not self.sid:
            raise NotLoggedIn()
        results_raw = await self.post(
            self.jsonrpc(
                [
                    [1, "set_session", {"session_id": self.sid}],
                    [2, "set_focus", {"login": login, "object": "files"}],
                    [3, "get_entries", {}],
                ]
            )
        )
        return self.pack_responses(results_raw, 2)

    async def add_board_entry(self, login: str, title: str, text: str, color: str) -> dict:
        """Adds board entry for specified (group-)login.
        color must be a hexadecimal color code
        """
        if not self.sid:
            raise NotLoggedIn()
        results_raw = await self.post(
            self.jsonrpc(
                [
                    [1, "set_session", {"session_id": self.sid}],
                    [2, "set_focus", {"login": login, "object": "board"}],
                    [
                        3,
                        "add_entry",
                        {"title": title, "text": text, "color": color},
                    ],
                ]
            )
        )
        results = [Box(res) for res in results_raw]
        if results[-1].result["return"] != "OK":
            raise error_handler(
                results[-1].result.errno)(results_raw[-1]["result"])
        return self.pack_responses(results_raw, 2)

    # NotesRequest

    async def get_notes(self, login: str) -> dict:
        """ Gets notes for specified login """
        if not self.sid:
            raise NotLoggedIn()
        results_raw = await self.post(
            self.jsonrpc(
                [
                    [1, "set_session", {"session_id": self.sid}],
                    [2, "set_focus", {"login": login, "object": "notes"}],
                    [3, "get_entries", {}],
                ]
            )
        )
        return self.pack_responses(results_raw, 2)

    async def add_note(self, title: str, text: str) -> dict:
        """ adds a note """
        if not self.sid:
            raise NotLoggedIn()
        results_raw = await self.post(
            self.jsonrpc(
                [
                    [1, "set_session", {"session_id": self.sid}],
                    [2, "set_focus", {"object": "notes"}],
                    [3, "add_entry", {"text": text, "title": title}],
                ]
            )
        )
        results = [Box(res) for res in results_raw]
        if results[-1].result["return"] != "OK":
            raise error_handler(
                results[-1].result.errno)(results_raw[-1]["result"])
        return self.pack_responses(results_raw, 2)

    async def delete_note(self, id: str) -> dict:
        """ deletes a note """
        if not self.sid:
            raise NotLoggedIn()
        results_raw = await self.post(
            self.jsonrpc(
                [
                    [1, "set_session", {"session_id": self.sid}],
                    [2, "set_focus", {"object": "notes"}],
                    [3, "delete_entry", {"id": id}],
                ]
            )
        )
        results = [Box(res) for res in results_raw]
        if results[-1].result["return"] != "OK":
            raise error_handler(
                results[-1].result.errno)(results_raw[-1]["result"])
        return self.pack_responses(results_raw, 2)

    #  EmailRequest

    async def send_email(self, to: str, subject: str, body: str) -> dict:
        """ Sends an email """
        if not self.sid:
            raise NotLoggedIn()
        results_raw = await self.post(
            self.jsonrpc(
                [
                    [1, "set_session", {"session_id": self.sid}],
                    [2, "set_focus", {"object": "mailbox"}],
                    [3, "send_mail", {
                        "to": to, "subject": subject, "body_plain": body}],
                ]
            )
        )
        results = [Box(res) for res in results_raw]
        if  results[-1].result["return"] != "OK":
            raise error_handler(
                results[-1].result.errno)(results_raw[-1]["result"])
        return self.pack_responses(results_raw, 2)

    async def get_emails(self, folder_id: str) -> dict:
        """ Gets emails from a folder id """
        if not self.sid:
            raise NotLoggedIn()
        results_raw = await self.post(
            self.jsonrpc(
                [
                    [1, "set_session", {"session_id": self.sid}],
                    [2, "set_focus", {"object": "mailbox"}],
                    [3, "get_messages", {"folder_id": folder_id}],
                ]
            )
        )
        return self.pack_responses(results_raw, 2)

    async def read_email(self, folder_id: str, message_id: int) -> dict:
        """ reads an email with a certain message id """
        if not self.sid:
            raise NotLoggedIn()
        results_raw = await self.post(
            self.jsonrpc(
                [
                    [1, "set_session", {"session_id": self.sid}],
                    [2, "set_focus", {"object": "mailbox"}],
                    [3, "read_message", {
                        "folder_id": folder_id, "message_id": message_id}],
                ]
            )
        )
        results = [Box(res) for res in results_raw]
        if results[-1].result["return"] != "OK":
            raise error_handler(
                results[-1].result.errno)(results_raw[-1])["result"]
        return self.pack_responses(results_raw, 2)

    async def get_email_folders(self):
        """ returns the folders to get the id """
        if not self.sid:
            raise NotLoggedIn()
        results_raw = await self.post(
            self.jsonrpc(
                [
                    [1, "set_session", {"session_id": self.sid}],
                    [2, "set_focus", {"object": "mailbox"}],
                    [3, "get_folders", {}],
                ]
            )
        )

        return self.pack_responses(results_raw, 2)

    # MessengerRequest

    async def read_quickmessages(self) -> dict:
        """ returns quickmessages """
        if not self.sid:
            raise NotLoggedIn()
        results_raw = await self.post(
            self.jsonrpc(
                [
                    [1, "set_session", {"session_id": self.sid}],
                    [2, "set_focus", {"object": "messenger"}],
                    [3, "read_quick_messages", {"export_session_file": 0}],
                ]
            )
        )
        return self.pack_responses(results_raw, 2)

    async def send_quickmessage(self, login: str, text: str) -> dict:
        """ Sends a quickmessage to an email holder """
        if not self.sid:
            raise NotLoggedIn()
        results_raw = await self.post(
            self.jsonrpc(
                [
                    [1, "set_session", {"session_id": self.sid}],
                    [2, "set_focus", {"object": "messenger"}],
                    [3, "send_quick_message", {
                        "login": login, "text": text, "import_session_file": 0}],
                ]
            )
        )
        results = [Box(res) for res in results_raw]
        if results[-1].result["return"] != "OK":
            raise error_handler(
                results[-1].result.errno)(results_raw[-1]["result"])
        return self.pack_responses(results_raw, 2)

    async def get_quickmessage_history(self, start_id: int) -> dict:
        """ get quickmessage history """
        if not self.sid:
            raise NotLoggedIn()
        results_raw = await self.post(
            self.jsonrpc(
                [
                    [1, "set_session", {"session_id": self.sid}],
                    [2, "set_focus", {"object": "messenger"}],
                    [3, "get_history", {
                        "start_id": start_id, "export_session_file": 0}],
                ]
            )
        )
        results = [Box(res) for res in results_raw]
        if (results[-1].result["return"] != "OK") and (results[-1].result.errno == "107" or results[-1].result.errno == "103"):
            raise error_handler(
                results[-1].result.errno)(results_raw[-1]["result"])
        return self.pack_responses(results_raw, 2)




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