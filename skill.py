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

    # find lists
    #   /boards/{id}/lists
    # create a new Card
    #   POST /1/cards -- query parameters
    #   name
    #   desc
    #   pos oneOf [string, number] The position of the new card. top, bottom, or a positive float
    #   idList
    # GET /lists/{id}/cards

    @intent_file_handler("new-card.intent")
    def handle_add_card(self, message: Message):
        # if "board" not in message.data and not self.default_board_id:
        #     self.speak_dialog('insufficient.dialog')
        # TODO find the list
        self.log.info(f"Trying to add {message.data}")
        r = self.client.post(
            "/cards",
            params={
                "idList": "59bf0557f88fc9a1d9b4f58b",
                "name": message.data.get("item"),
            },
        )
        self.log.info(f"Got a response: {r.status_code}, {r.json()}")
        # TODO check return status
        self.speak_dialog(
            "added-card",
            {"item": "item", "list": "your list", "board": "default of boards"},
        )
