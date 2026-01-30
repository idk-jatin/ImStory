class Event:
    def __init__(self,verb,subj=None,obj=None,iobj=None,location=None,modifiers=None,sentence=None,page=None,):
        self.verb_token = verb 
        self.verb = verb.text
        self.lemma = verb.lemma_
        self.tense = verb.morph.get("Tense")

        self.subject = subj
        self.object = obj
        self.indirect = iobj
        self.location = location
        self.modifiers = modifiers or {}
        self.sentence = sentence
        self.page = page
