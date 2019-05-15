class Sha():
    def add(self,skills):
        skills['cards'].append('sha')
        return skills

    def hook(self,skill,players):
        if skill['name'] == 'sha':
            self.__function(skill,players)
        else:
            return None

    def __function(self,skill,players):
        if skill['response'] == None:
            skill_from = skill['from']
            skill_to = skill['to']
            if self.__check_distance(skill_from,skill_to,players):
                return [('order',{'name':'push_card','data':{'status':'failed','msg':'您的攻击距离不够'}},skill_from)]
            else:
                return [('order',{'name':'push_card','data':'OK'},skill_from),
                        ('order',{'name':'response','data':{'card':skill,'msg':'有人对你除了一张杀，请出闪'}},skill_to)]
        else:
            if skill['response'] == 'refused':
                return [('order',{'name':'push_card','data':{'status':'OK'}},skill_from),
                        ('order',{'name':'sub_hp','data':{'target':skill_to,'numb':1}},'all')]
            elif skill['response']['name'] =='shan':
                return [('order',{'name':'push_card','data':{'status':'OK'}},skill_from)]
            else:
                return [('order',{'name':'response','data':{'status':'failed','msg':'您只能出杀'}})]


    def __check_distance(self,skill_from,skill_to,players):
        distance = 2.5 - abs(abs(int(skill_from)-int(skill_to))-2.5)
        range = 1
        if distance > range:
            return False
        else:
            return True