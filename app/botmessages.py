class Replies:
    PGDINAMICA = ("https://youtube.com/programacaodinamica", None)
    TWILIO = ("https://www.twilio.com/pt-br/", None)
    REGISTER_USER = ("7", None)
    REBOOT_QUIZZ = ('Pronto! Digite **P** para próxima pergunta do Quizz; **R** para ver o ranking; ou **V** para voltar ao menu inicial.', None)
    DEFAULT = ("Olá, eu me chamo Quizzy 🤓 e por aqui eu posso te ajudar com uma dessas opções:\n1- Quizz do Programação Dinâmica\n2- Mais informações sobre o Programação Dinâmica\n3- Mais informações sobre a Twilio", None)

    def format(reply_pair):
        text, media = reply_pair
        r = {'body': text}
        if media is not None:
            r['media'] = media
        return r

    def quizz_error():
        return {'body': 'Não entendi a resposta. Por favor, tente novamente. Digite **P** para pergunta; **R** para Ranking; ou **V** para voltar ao menu inicial.'}

    def quizz_ended(userdata):
        return {'body': f"Você finalizou o quizz do Programação Dinâmica!👏🏾 Sua pontuação foi: {userdata['points']} pontos. Digite **8** se quiser responder novamente ou **V** para voltar ao menu inicial."}

    def reboot_success():
        return Replies.format(Replies.REBOOT_QUIZZ)

    def next_question(points, question):
        txt = 'Acertou! 👏🏾👏🏾👏🏾' if points > 0 else 'Errou'
        txt = f'{txt}\n{str(question)}'
        return {'body': txt, 'media': question.media_url}

    def user_registered():
        return {'body': 'Show, você se cadastrou! Envie **P** para receber a próxima pergunta; **R** para ver o ranking; ou **V** para voltar ao menu inicial.'}

    def display_question(question):
        return  {'body': str(question), 'media': question.media_url}

    def ranking(topN):
        s = f"**Ranking (Top {len(topN) if len(topN) > 5 else 5})**\n"
        prize = ['🏆', '🥈', '🥉'] + ['👏🏾'] * (len(topN) - 3)
        for i, pair in enumerate(topN):
            s = s + f'{prize[i]}. {pair[0]} - {pair[1]} pontos\n'
        warning = 'Envie **V para voltar ao menu inicial ou **P** para retomar o quizz.'
        s = s + f'\n{warning}'
        return {'body': s}
    
    def no_ranking():
        return {'body': 'Ranking indisponível! Neste momento, não há nenhum jogador está participando do quizz.'}

    def unauth_response():
        return {'body': 'Para participar do Quiz, é preciso se registrar. Digite **7** seguido de um nome de usuário para se registrar. Ex: *7 Justu*'
            }
