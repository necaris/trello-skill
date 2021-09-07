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
        # self.default_board = self.settings.get("default_board")

    # find lists
    #   /boards/{id}/lists
    # create a new Card
    #   POST /1/cards -- query parameters
    #   name
    #   desc
    #   pos oneOf [string, number] The position of the new card. top, bottom, or a positive float
    #   idList
    # GET /lists/{id}/cards

    @intent_file_handler("compliment.intent")
    def handle_compliment(self, message: Message):
        if message.data.get("name"):
            self.speak_dialog("compliment.named", message.data)
        else:
            self.speak_dialog("compliment")
