from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dispatch import BotDispatcher, QuizzManager


app = Flask(__name__)


@app.route('/bot', methods=['POST'])
def bot():
    # print(request.values) - se quiser ver os parâmetros recebidos
    original_msg = request.values.get('Body', '')

    dispatcher = BotDispatcher()
    botresponse = dispatcher.reply(original_msg)
    if botresponse == BotDispatcher.QUIZZ_FLOW:
        userid = request.values.get('WaId', None)
        quizzmanager = QuizzManager()
        botresponse = quizzmanager.reply(userid, original_msg)

    resp = MessagingResponse()
    msg = resp.message()

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


# def load_questions():
#     fp = open(os.path.join(DATA_DIR, 'questions.json'), 'r', encoding='utf-8')
#     q_dict = json.load(fp)
#     fp.close()
#     questions = []
#     for k, v in q_dict.items():
#         questions.append(
#             Question(v['id'], 
#                     v['text'], 
#                     v['alternatives'], 
#                     v['answer'], 
#                     v['category']))
#     return questions
    

# def current_question(userdata, questions):
#     current_id = userdata.get('last_question', 0)
#     if current_id == len(questions):
#         return None
#     return questions[current_id]

# def proccess_answer(usermsg):
#     MAP = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
#     answer = usermsg.strip()[-1].upper()
#     return MAP[answer]


# def quizz_ended_msg(userdata):
#     return {'body': f"Acabou! Sua pontuação: {userdata['points']}", 
#             'media': 'https://direct.rhapsody.com/imageserver/images/alb.483471959/500x500.jpg'}

# def next_question_msg(points, question):
#     txt = 'Acertou! 👏🏾👏🏾👏🏾' if points > 0 else 'Errou'
#     txt = f'{txt}\n{str(question)}'
#     return {'body': txt}

# def continue_quizz(userdata, usermsg, questions):
#     question = current_question(userdata, questions)
#     user_answer = proccess_answer(usermsg)
#     points = 0
#     if user_answer == question.answer:
#         points = question.points()
    
#     userdata.update({question.id: user_answer,
#                     'points': userdata.get('points', 0) + points,
#                     'last_question': question.id
#     })
#     save(userdata)

#     question = current_question(userdata, questions)
#     # acabou o quizz
#     return (quizz_ended_msg(userdata) if question is None 
#             else next_question_msg(points, question))

# def register_user(userid, username):
#     with open(userfilepath(userid), 'w') as userfile:
#         content = json.dumps({"id": userid, "username": username})
#         userfile.write(content)
#     return {'body': 'Show! Escolha **P** para receber a próxima pergunta e **R** para ver o ranking'}

# def ranking():
#     with open(os.path.join(DATA_DIR, 'ranking.json'), 'r', 
#                 encoding='utf-8') as rankfile:
#         rank_dict = json.load(rankfile)
#     top5 = sorted(rank_dict.items(), key=lambda x: x[1], reverse=True)[:10]
#     s = "**Ranking (Top 5)**\n"
#     prize = ['🏆', '🥈', '🥉', '👏🏾', '👏🏾']
#     for i, pair in enumerate(top5):
#         s = s + f'{prize[i]}. {pair[0]} - {pair[1]} pontos\n'
#     return {'body': s}