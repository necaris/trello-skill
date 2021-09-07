import typing

from mycroft import MycroftSkill, intent_file_handler
from mycroft.messagebus import Message

from . import api


class Trello(MycroftSkill):
    def __init__(self):
        super().__init__()

    def initialize(self):
        self.client = api.make_client(
            key=self.settings.get("key"), token=self.settings.get("token")
        )
        self.default_board_id = self.settings.get("default_board_id")

    def _find_list_by_name(self, name: str, board_id: str = None):
        board_id = board_id or self.default_board_id
        if not board_id:
            raise AssertionError("Cannot find list without a board")
        r = self.client.get(f"/boards/{board_id}/lists", params={"fields": "name"})
        for l in r.json():
            if l["name"] == name:
                return l
        raise ValueError(f"No list with name {name} in board {board_id}")

    def _add_card(
        self,
        list_id: str,
        name: str,
        desc: str = None,
        pos: typing.Union[str, int] = None,
    ):
        params = {"idList": list_id, "name": name}
        if desc is not None:
            params["desc"] = desc
        if pos is not None:
            params["pos"] = str(pos)

        r = self.client.post("/cards", params=params)
        r.raise_for_status()
        return r.json()

    # GET /lists/{id}/cards

    @intent_file_handler("new-card.intent")
    def handle_add_card(self, message: Message):
        # if "board" not in message.data and not self.default_board_id:
        #     self.speak_dialog('insufficient.dialog')
        try:
            list_ = self._find_list_by_name(message.data.get("list"))
        except ValueError:
            return self.speak_dialog("no-such-list")

        self._add_card(list_id=list_["id"], name=message.data["item"])
        self.speak_dialog(
            "added-card",
            {
                "item": message.data["item"],
                "list": list_["name"],
                "board": "default board",
            },
        )
