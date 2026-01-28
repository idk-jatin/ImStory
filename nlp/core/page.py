class PageDoc:
    def __init__(self, page_num, text):
        self.pn = page_num
        self.text = text
        self.doc = None
        self.sentences = []
        self.entities = []          
        self.characters = {}        
        self.locations = {}
        self.objects = {}
        self.coref_clusters = []
        self.embedding = None
        self.events = []
        self.world_ents = []
        self.noun_ents=[]
        self.mood = None
        self.summary = None
