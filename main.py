from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse
import os
from question import Question

app = Flask(__name__)


def retrieve_data(userid):
    return {}

def current_question(userdata):
    return Question(1, "biscoito", [4, 3, 2, 1], 2, "Teste")

def proccess_answer(usermsg):
    MAP = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    answer = usermsg.strip()[-1].upper()
    return MAP[answer]

def save(userdata):
    pass

def quizz_ended_msg():
    return {'body': 'Acabou', 
            'media': 'https://direct.rhapsody.com/imageserver/images/alb.483471959/500x500.jpg'}

def next_question_msg(points, question):
    txt = 'Acertou!' if points > 0 else 'Errou'
    txt = f'{txt}\n{question.text}\n'

def continue_quizz(userid, usermsg):
    userdata = retrieve_data(userid)
    question = current_question(userdata)
    user_answer = proccess_answer(usermsg)
    points = 0
    if user_answer == question.answer:
        points = question.points()
    
    userdata.update({question.id: user_answer,
                    'points': userdata.get('points', 0) + points
    })
    save(userdata)

    question = current_question(userdata)
    # acabou o quizz
    if question is None:
        quizz_ended_msg()
    else:
        next_question_msg(points, question)

def get_unauth_response():
    return {'body': 'Usuário Desconhecido',
            'media': 'https://upload.wikimedia.org/wikipedia/commons/0/09/Unknown_curve_animated.gif'
            }

def user_authenticated(userid):
    DATA_DIR = 'E:\Workspace\pgdinamica\\twillio\data'
    if os.path.exists(os.path.join(DATA_DIR, userid)):
        return True
    return False

@app.route('/bot', methods=['POST'])
def bot():
    # print(request.values) - se quiser ver os parâmetros recebidos
    incoming_msg = request.values.get('Body', '').lower()
    userid = request.values.get('WaId', None)
    resp = MessagingResponse()
    msg = resp.message()
    if user_authenticated(userid):
        botresponse = continue_quizz(userid, incoming_msg)
    else:
        botresponse = get_unauth_response()

    msg.body(botresponse['body'])
    if botresponse.get('media', None):
        msg.media(botresponse['media'])
    print(str(resp)) #- se quiser ver o formato do XML esperado pela Twilio
    return str(resp)

@app.route('/')
def index():
    return "É isso aqui x 2!"

if __name__ == '__main__':
    app.run()