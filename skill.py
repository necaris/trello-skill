import typing

from mycroft import MycroftSkill, intent_file_handler
from mycroft.messagebus import Message
from fuzzywuzzy import fuzz

from . import api


class ListNotFoundError(ValueError):
    def __init__(self, name, board_id=None):
        self.name = name
        self.board_id = board_id

    def __str__(self):
        return f"List not found: No list with name {self.name} in board {self.board_id}"


class Trello(MycroftSkill):
    def __init__(self):
        super().__init__()

    def initialize(self):
        self.client = api.make_client(
            key=self.settings.get("key"), token=self.settings.get("token")
        )
        self.settings_change_callback = self.on_settings_changed
        self.on_settings_changed()

    def on_settings_changed(self):
        self.default_board_id = self.settings.get("default_board_id")

    def _find_list_by_name(self, name: str, board_id: str = None):
        board_id = board_id or self.settings.get("default_board_id")
        if not board_id:
            raise AssertionError("Cannot find list without a board")
        r = self.client.get(f"/boards/{board_id}/lists", params={"fields": "name"})
        for l in r.json():
            if fuzz.ratio(name, l["name"].lower()) > 99:
                return l
        self.log.info(
            f"Could not find list: {name} among: {[l['name'] for l in r.json()]}"
        )
        raise ListNotFoundError(name, board_id)

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

    @intent_file_handler("list-boards.intent")
    def handle_list_boards(self, _: Message):
        r = self.client.get("/members/me/boards", params={"fields": "name"})
        r.raise_for_status()
        self.log.info(f"Got response: {r.json()}")
        boards = r.json()
        self.speak(f"You have {len(boards)} boards:")
        for b in boards:
            self.speak(b["name"])

    @intent_file_handler("clear-list.intent")
    def handle_clear_list(self, message: Message):
        # archive all items in named list
        pass

    # GET /lists/{id}/cards

    @intent_file_handler("query-list.intent")
    def handle_query_list(self, message: Message):
        # is X on the shopping list?
        pass

    @intent_file_handler("remove-card.intent")
    def handle_remove_from_list(self, message: Message):
        # is X on the shopping list?
        pass
