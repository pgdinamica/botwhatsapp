from .botmessages import Replies
from .persistence import LocalPersistence
from pathlib import Path

BASE_DIR = Path(".").absolute().parents[0]
DATA_DIR = BASE_DIR.joinpath('data')
TEMP_DIR = BASE_DIR.joinpath('temp')
USER_DIR = TEMP_DIR.joinpath('users')
USER_DIR.mkdir(parents=True, exist_ok=True)

class BotOptions:
    QUIZZ = "1"
    PGDINAMICA = "2"
    TWILIO = "3"
    REGISTER_USER = "7"
    REBOOT_QUIZZ = "8"

    QUESTION = "p"
    RANKING = "r"

    ALTERNATIVES = ['a', 'b', 'c', 'd']
    QUIZZ_FLOW = [QUIZZ, REGISTER_USER, 
                    REBOOT_QUIZZ, QUESTION, RANKING] + ALTERNATIVES

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
        if message[0] in BotOptions.QUIZZ_FLOW:
            return BotDispatcher.QUIZZ_FLOW
        elif message == BotOptions.PGDINAMICA:
            return self.format(Replies.PGDINAMICA)
        elif message == BotOptions.TWILIO:
            return self.format(Replies.TWILIO)
        else:
            return self.format(Replies.DEFAULT)

class QuizzManager:
    ALT_MAP = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    
    def __init__(self) -> None:
        self.persistence = LocalPersistence(DATA_DIR, TEMP_DIR)
        self.questions = []

    def reply(self, userid, usermessage):
        message = usermessage.lower()
        if self.persistence.is_registered_user(userid):
            userdata = self.persistence.retrieve_user(userid)
            
            if message == 'p':    
                question = self.persistence.current_question(userdata)
                if question is None:
                    botresponse = Replies.quizz_ended(userdata)
                else:
                    botresponse = Replies.display_question(question)
            elif message == 'r':
                topN = self.persistence.retrieve_ranking()
                botresponse = (Replies.ranking(topN) if len(topN) > 0 
                                else Replies.no_ranking())
            elif message in BotOptions.ALTERNATIVES:
                botresponse = self.continue_quizz(userdata, message)
            elif message == BotOptions.REBOOT_QUIZZ:
                self.persistence.reboot_user(userdata)
                botresponse = Replies.reboot_success()
            else:
                botresponse = Replies.quizz_error()
        else:
            if message[0] == BotOptions.REGISTER_USER:
                parts = usermessage.split()
                self.persistence.register_user(userid, parts[1])
                botresponse = Replies.user_registered()
            else:
                botresponse = Replies.unauth_response()

        return botresponse

    def proccess_answer(self, usermsg):
        answer = usermsg.strip()[-1].upper()
        return QuizzManager.ALT_MAP[answer]

    def continue_quizz(self, userdata, usermsg):
        question = self.persistence.current_question(userdata)
        user_answer = self.proccess_answer(usermsg)
        points = question.points() if user_answer == question.answer else 0
        
        userdata.update({question.id: user_answer,
                        'points': userdata.get('points', 0) + points,
                        'last_question': question.id
        })
        self.persistence.update_user(userdata)
        record = {userdata['username']: userdata['points']}
        self.persistence.update_ranking(record)

        question = self.persistence.current_question(userdata)
        # acabou o quizz
        return (Replies.quizz_ended(userdata) if question is None 
                else Replies.next_question(points, question))