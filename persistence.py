import os
import json
from question import Question


QUESTIONS_FILE = 'questions.json'

class BasePersistence:
    def load_questions(self):
        pass
    
    def retrieve_userdata(self, userid):
        pass
    
    def register_user(self, userid, username):
        pass

    def remove_user(self, userid):
        pass

    def reboot_userdata(self, userdata):
        pass

    def update_user(self, userdata):
        pass



class LocalPersistence(BasePersistence):
    def __init__(self, datadir) -> None:
        super().__init__()
        self.basedir = datadir
        self._questions = None

    @property
    def questions(self):
        if self._questions is None:
            self.load_questions()
        return self._questions
    
    def load_questions(self):
        with open(os.path.join(self.basedir, QUESTIONS_FILE), 
                    'r', encoding='utf-8') as fp:
            q_dict = json.load(fp)
        
        questions = []
        for k, v in q_dict.items():
            questions.append(
                Question(v['id'], 
                        v['text'], 
                        v['alternatives'], 
                        v['answer'], 
                        v['category']))
        self._questions
    
    def current_question(self, userdata):
        current_id = userdata.get('last_question', 0)
        if current_id == len(self.questions):
            return None
        return self.questions[current_id]

    def userfilepath(self, userid):
        return os.path.join(self.basedir, 'users', f'{userid}.json')

    def retrieve_userdata(self, userid):
        fp = open(self.userfilepath(userid), 'r', encoding='utf-8')
        userdata = json.load(fp)
        fp.close()
        return userdata

    def register_user(self, userid, username):
        with open(self.userfilepath(userid), 'w') as userfile:
            content = json.dumps({"id": userid, "username": username})
            userfile.write(content)
        return True

    def is_registered_user(self, userid):
        if os.path.exists(os.path.join(self.basedir, f'{userid}.json')):
            return True
        return False

    def reboot_userdata(self, userdata):
        with open(self.userfilepath(userdata['id']), 'w') as cleanfile:
                    json.dump({'id': userdata['id'], 
                                'username': userdata['username']}, cleanfile) 
        return True

    def retrieve_ranking(self, topn=5):
        with open(os.path.join(self.basedir, 'ranking.json'), 'r', 
                    encoding='utf-8') as rankfile:
            rank_dict = json.load(rankfile)
        top = sorted(rank_dict.items(), 
                        key=lambda x: x[1], reverse=True)[:topn]
        return top

    def update_user(self, userdata):
        data = json.dumps(userdata)
        with open(self.userfilepath(userdata['id']), 'w') as userfile:
            userfile.write(data)
        
        rankpath = os.path.join(self.basedir, 'ranking.json')
        if os.path.exists(rankpath):
            fp = open(rankpath, 'r', encoding='utf-8')
            rank_dict = json.load(fp)
            fp.close()
        else:
            rank_dict = {}
        rank_dict.update({userdata['username']: userdata['points']})
        with open(rankpath, 'w') as rankfile:
            json.dump(rank_dict, rankfile)