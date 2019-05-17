class Tao():
    def add(self,skills):
        skills['cards'].append('tao')
        return skills

    def hook(self,skill,players):
        if skill['name'] == 'Tao':
            result =  self.__function(skill,players)
            return result
        else:
            return None

    def __function(self,skill,players):
        skill_from = skill['from']
        return [('order',{'name':'add_hp','data':{'target':skill_from}},'all'),('msg','玩家%s增加了一点血'%skill_from,'all')]
