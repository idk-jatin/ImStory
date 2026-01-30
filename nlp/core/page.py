class PageDoc:
    def __init__(self, page_num, text):
        self.pn = page_num
        self.text = text
        self.resolved_text = None   
        self.doc = None
        self.sentences = []        
        self.entities = []          
        self.coref_clusters = []    
        self.noun_ents = []     
        self.world_ents = []        
        self.characters = {}    
        self.locations = {}
        self.objects = {}
        self.embedding = None
        self.events = []      
        self.mood = None
        self.summary = None
