class Sha():
    def add(self,skills):
        skills['cards'].append('sha')
        return skills

    def hook(self,skill,players):
        if skill['name'] == 'Sha':
            result = self.__function(skill,players)
            return result
        else:
            return None

    def __function(self,skill,players):
        if skill['response'] == None:
            skill_from = skill['from']
            skill_to = skill['to']
            return [('order',{'name':'response','data':skill},skill_to)]
        else:
            skill_from = skill['from']
            skill_to = skill['to']
            if skill['response'] == 'failed':
                return [('order',{'name':'sub_hp','data':skill_to},'all'),('msg','玩家%s受到了一点伤害'%skill_to,'all')]
            elif skill['response'] =='OK':
                return [('msg','玩家%s打出了一张闪'%skill_to,'all')]

