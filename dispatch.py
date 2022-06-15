from botmessages import Replies
from persistence import LocalPersistence


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

DATA_DIR = 'E:\Workspace\pgdinamica\\twillio\data'

class QuizzManager:
    ALT_MAP = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    
    def __init__(self) -> None:
        self.persistence = LocalPersistence(DATA_DIR)
        self.questions = []

    def reply(self, userid, usermessage):
        message = usermessage.lower()
        if self.persistence.is_registered_user(userid):
            userdata = self.persistence.retrieve_userdata(userid)
            
            if message == 'p':    
                question = self.persistence.current_question(userdata)
                if question is None:
                    botresponse = Replies.quizz_ended(userdata)
                else:
                    botresponse = Replies.display_question(question)
            elif message == 'r':
                topN = self.persistence.retrieve_ranking()
                botresponse = Replies.ranking(topN)
            elif message in BotOptions.ALTERNATIVES:
                botresponse = self.continue_quizz(userdata, message)
            else:
                botresponse = Replies.quizz_error()
        else:
            if message[0] == BotOptions.REGISTER_USER:
                parts = usermessage.split()
                self.persistence.register_user(userid, parts[1])
                botresponse = Replies.user_registered()
            else:
                botresponse = Replies.unauth_response()
        # elif message == BotOptions.REGISTER_USER:
        #     return self.format(Replies.REGISTER_USER)
        # elif message == BotOptions.REBOOT_QUIZZ:
        #     return self.format(Replies.REBOOT_QUIZZ)

        return botresponse

    def proccess_answer(usermsg):
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

        question = self.persistence.current_question(userdata)
        # acabou o quizz
        return (Replies.quizz_ended(userdata) if question is None 
                else Replies.next_question(points, question))



    # def quizz_ended_msg(userdata):
    #     return {'body': f"Acabou! Sua pontuação: {userdata['points']}", 
    #             'media': 'https://direct.rhapsody.com/imageserver/images/alb.483471959/500x500.jpg'}

# def next_question_msg(points, question):
    #     txt = 'Acertou! 👏🏾👏🏾👏🏾' if points > 0 else 'Errou'
    #     txt = f'{txt}\n{str(question)}'
    #     return {'body': txt}