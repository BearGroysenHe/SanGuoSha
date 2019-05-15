class Tao():
    def add(self,skills):
        skills['cards'].append('tao')
        return skills

    def hook(self,skill,players):
        if skill['name'] == 'tao':
            self.__function(skill,players)
        else:
            return None

    def function(self,skill,players):
        if players['hero']['hp_max'] == players['hero']['max_hp']:
            return [('order',{'name':'push_card','data':{'status':'failed','msg':'您已达到血量上限，无法加血'}},players)]
        else:
            return [('order',{'name':'push_card','data':{'status':'OK'}},players),
                    ('order',{'name':'add_hp','data':{'target':players,'numb':1}},'all')]