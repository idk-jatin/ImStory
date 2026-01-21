class Story:
    def __init__(self, story_id, title, pages):
        self.story_id = story_id
        self.title = title
        self.pages = pages        
        self.scenes = []  
        self.characters = set()
        self.locations = set()


class Scene:
    def __init__(self, scene_id, text, start_page, end_page, char_start, char_end):
        self.scene_id = scene_id
        self.text = text
        self.start_page = start_page
        self.end_page = end_page
        self.char_start = char_start
        self.char_end = char_end
        self.summary = None
        self.entities = []
        self.mood = None
        self.prompt = None
        self.image_path = None
        self.clip_score = None
