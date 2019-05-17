import json

class SkillReleaser():
    def __init__(self,players):
        self.players = players
        self.skills = {}
        self.skills['cards'] = []
        for i in ['beginning', 'judgment', 'get_card', 'push_card', 'drop_card', 'ending']:
            self.skills[i] = {}
            for key in players.keys():
                self.skills[i][key] = []
        with open('setting/setting_skill.json', 'r') as f:
            skills = json.loads(f.read(), encoding='utf-8')
        for key, value in skills.items():
            exec('from setting.skill.%s import %s' % (key, value))
            exec('self.%s = %s()'%(key,value))
            exec('self.skills = self.%s.add(self.skills)'%key)


    def beginning(self):
        pass

    def judgment(self):
        pass

    def get_card(self):
        pass

    def push_card(self,card,players):
        for skill in self.skills['cards']:
            # response = self.tao.hook(card,players)
            exec('self.response = self.%s.hook(card,players)'%skill)
            print(self.response)
            if self.response != None:
                return self.response
        return None
    def drop_card(self):
        pass

    def ending(self):
        pass

# players = {'01':None,'02':None,'03':None,'04':None,'05':None}
# skillreleaser = SkillReleaser(players)
# skillreleaser.push_card({'name':'Tao'})