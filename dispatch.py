from tkinter import BOTH
from botmessages import Replies

class BotOptions:
    QUIZZ = "1"
    PGDINAMICA = "2"
    TWILIO = "3"
    REGISTER_USER = "7"
    REBOOT_QUIZZ = "8"

    QUESTION = "p"
    RANKING = "r"

    ALTERNATIVES = ['a', 'b', 'c', 'd']


class BotDispatcher:
    QUIZZ_FLOW = 7777

    def __init__(self, lang='br') -> None:
        self.lang = lang

    def format(self, reply_pair):
        text, media = reply_pair
        r = {'body': text}
        if media is not None:
            r['media'] = media
        return r

    def reply(self, usermessage):
        message = usermessage.lower()
        if message == BotOptions.QUIZZ:
            return BotDispatcher.QUIZZ_FLOW
        elif message == BotOptions.PGDINAMICA:
            return self.format(Replies.PGDINAMICA)
        elif message == BotOptions.TWILIO:
            return self.format(Replies.TWILIO)
        elif message == BotOptions.REGISTER_USER:
            return self.format(Replies.REGISTER_USER)
        elif message == BotOptions.REBOOT_QUIZZ:
            return self.format(Replies.REBOOT_QUIZZ)
        else:
            return self.format(Replies.DEFAULT)
