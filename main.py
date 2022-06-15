from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse
import os
from question import Question
import json
import dispatch

app = Flask(__name__)

DATA_DIR = 'E:\Workspace\pgdinamica\\twillio\data'


def load_questions():
    fp = open(os.path.join(DATA_DIR, 'questions.json'), 'r', encoding='utf-8')
    q_dict = json.load(fp)
    fp.close()
    questions = []
    for k, v in q_dict.items():
        questions.append(
            Question(v['id'], 
                    v['text'], 
                    v['alternatives'], 
                    v['answer'], 
                    v['category']))
    return questions
    
def userfilepath(userid):
    return os.path.join(DATA_DIR, 'users', f'{userid}.json')

def retrieve_data(userid):
    fp = open(userfilepath(userid), 'r', encoding='utf-8')
    userdata = json.load(fp)
    fp.close()
    return userdata

def current_question(userdata, questions):
    current_id = userdata.get('last_question', 0)
    if current_id == len(questions):
        return None
    return questions[current_id]

def proccess_answer(usermsg):
    MAP = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
    answer = usermsg.strip()[-1].upper()
    return MAP[answer]

def save(userdata):
    data = json.dumps(userdata)
    with open(userfilepath(userdata['id']), 'w') as userfile:
        userfile.write(data)
    
    rankpath = os.path.join(DATA_DIR, 'ranking.json')
    if os.path.exists(rankpath):
        fp = open(rankpath, 'r', encoding='utf-8')
        rank_dict = json.load(fp)
        fp.close()
    else:
        rank_dict = {}
    rank_dict.update({userdata['username']: userdata['points']})
    with open(rankpath, 'w') as rankfile:
        json.dump(rank_dict, rankfile)

def quizz_ended_msg(userdata):
    return {'body': f"Acabou! Sua pontuação: {userdata['points']}", 
            'media': 'https://direct.rhapsody.com/imageserver/images/alb.483471959/500x500.jpg'}

def next_question_msg(points, question):
    txt = 'Acertou! 👏🏾👏🏾👏🏾' if points > 0 else 'Errou'
    txt = f'{txt}\n{str(question)}'
    return {'body': txt}

def continue_quizz(userdata, usermsg, questions):
    question = current_question(userdata, questions)
    user_answer = proccess_answer(usermsg)
    points = 0
    if user_answer == question.answer:
        points = question.points()
    
    userdata.update({question.id: user_answer,
                    'points': userdata.get('points', 0) + points,
                    'last_question': question.id
    })
    save(userdata)

    question = current_question(userdata, questions)
    # acabou o quizz
    return (quizz_ended_msg(userdata) if question is None 
            else next_question_msg(points, question))

def get_unauth_response():
    return {'body': 'Para participar do Quiz, é preciso se registrar. Digite **7** seguido de um nome de usuário para se registrar. Ex: *7 Justu*',
            'media': 'https://live.staticflickr.com/1828/41997990765_2024b9bacc_b.jpg'
            }

def register_user(userid, username):
    with open(userfilepath(userid), 'w') as userfile:
        content = json.dumps({"id": userid, "username": username})
        userfile.write(content)
    return {'body': 'Show! Escolha **P** para receber a próxima pergunta e **R** para ver o ranking'}

def user_authenticated(userid):
    if os.path.exists(os.path.join(DATA_DIR, f'{userid}.json')):
        return True
    return False

def ranking():
    with open(os.path.join(DATA_DIR, 'ranking.json'), 'r', 
                encoding='utf-8') as rankfile:
        rank_dict = json.load(rankfile)
    top5 = sorted(rank_dict.items(), key=lambda x: x[1], reverse=True)[:10]
    s = "**Ranking (Top 5)**\n"
    prize = ['🏆', '🥈', '🥉', '👏🏾', '👏🏾']
    for i, pair in enumerate(top5):
        s = s + f'{prize[i]}. {pair[0]} - {pair[1]} pontos\n'
    return {'body': s}

REGISTER_CODE = "7"

from dispatch import BotDispatcher

@app.route('/bot', methods=['POST'])
def bot():
    # print(request.values) - se quiser ver os parâmetros recebidos
    original_msg = request.values.get('Body', '')
    incoming_msg = original_msg.lower()

    dispatcher = BotDispatcher()
    botresponse = dispatcher.reply(original_msg)
    if botresponse == BotDispatcher.QUIZZ_FLOW:
        userid = request.values.get('WaId', None)
        botresponse = {'body': 'Ainda não tem quizz'}

    resp = MessagingResponse()
    msg = resp.message()
    # if user_authenticated(userid):
    #     userdata = retrieve_data(userid)
    #     questions = load_questions()
    #     if incoming_msg == 'p':    
    #         question = current_question(userdata, questions)
    #         if question is None:
    #             botresponse = {'body': f"Acabou pra ti. Pontuação: {userdata['points']}. Digite **8** se quiser tentar de novo."}
    #         else:
    #             botresponse = {'body': str(question), 'media': question.media_url}
    #     elif incoming_msg == 'r':
    #         botresponse = ranking()
    #     elif incoming_msg == '8':
    #         with open(userfilepath(userid), 'w') as cleanfile:
    #             json.dump({'id': userid, 
    #                         'username': userdata['username']}, cleanfile) 
    #         botresponse = {'body': 'Pronto! **P** para pergunta; **R** para Ranking'}
    #     elif incoming_msg in ['a', 'b', 'c', 'd']:
    #         botresponse = continue_quizz(userdata, incoming_msg, questions)
    #     else:
    #         botresponse = {'body': 'Não entendi, tente de novo. **P** para pergunta; **R** para Ranking'}
    # else:
    #     if incoming_msg[0] == REGISTER_CODE:
    #         parts = original_msg.split()
    #         botresponse = register_user(userid, parts[1])
    #     else:
    #         botresponse = get_unauth_response()

    msg.body(botresponse['body'])
    if botresponse.get('media', None):
        msg.media(botresponse['media'])
    print(str(resp)) #- se quiser ver o formato do XML esperado pela Twilio
    return str(resp)

@app.route('/')
def index():
    return "É isso aqui x 3!"

if __name__ == '__main__':
    app.run()