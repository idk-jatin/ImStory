PRONOUNS = {
    "i", "me", "we", "us", "you", "he", "him", "she", "her", "it", "they", "them",
    "mine", "ours", "yours", "his", "hers", "theirs", "its", "their",
    "myself", "ourselves", "yourself", "yourselves", "himself", "herself",
    "itself", "themselves", "oneself",
    "this", "that", "these", "those", "such", "one", "ones",
    "each", "either", "neither", "every", "none",
    "who", "whom", "whose", "which", "that",
    "each other", "one another",
    "everybody", "somebody", "nobody", "anybody", "someone", "no one", "anyone",
    "everything", "something", "nothing", "anything",
    "all", "some", "any", "both", "another", "much", "few", "little",
}

CLOTHING_KEYWORDS = {
    "coat", "jacket", "shirt", "pants", "dress", "suit", "hat", "cap", 
    "glasses", "scarf", "gloves", "shoes", "boots", "hoodie", "sweater", 
    "vest", "uniform", "robe", "cloak", "tunic", "armor", "helmet",
    "denim", "leather", "silk", "velvet"
}

ATMOSPHERE_ANTONYMS = {
    "rain": {"dry", "clear", "sun", "sunny"},
    "storm": {"calm", "clear", "sun", "quiet"},
    "fog": {"clear", "visibility", "sun", "bright"},
    "mist": {"clear", "sun"},
    "darkness": {"light", "sun", "day", "lamp", "bright"},
    "night": {"day", "sun", "morning", "noon"},
    "silence": {"noise", "sound", "music", "laughter", "voice", "scream", "shout"},
    "cold": {"warm", "hot", "fire", "heat", "summer"},
    "decay": {"new", "fresh", "clean", "pristine", "modern"},
}

RELATION_VERBS = {
    "POSSESSES": "holding",
    "IS": "being",
    "FEELS": "looking", 
    "OBSERVES": "watching",
    "INTERACTS": "facing", 
    "FOLLOWS": "following",
    "NEAR": "standing near",
    "WEARS": "wearing",
}

VISUAL_VERBS = {
    "walk", "run", "step", "stand", "sit", "look", "stare", "watch",
    "hold", "carry", "grab", "touch", "wear", "face", "turn", "move",
    "fall", "lie", "rise", "open", "close", "lean", "crouch", "point",
    "nod", "smile", "frown", "laugh", "cry", "shout", "whisper",
    "reach", "pull", "push", "lift", "drop", "throw", "emerge",
    "disappear", "vanish", "enter", "leave", "cross", "follow",
    "wait", "stop", "pause", "gesture", "aim", "fire", "shoot",
    "hit", "strike", "climb", "jump", "crawl", "kneel", "bow",
    "hit", "strike", "climb", "jump", "crawl", "kneel", "bow",
    "embrace", "hug", "kiss", "dance", "drive", "ride", "eat", "drink"
}

ABSTRACT_MAP = {
    "silence": "empty, no people, still",
    "quiet": "still, calm",
    "sadness": "muted tones, overcast",
    "fear": "dim lighting, long shadows, high contrast",
    "joy": "vibrant colors, bright",
    "cold": "blue tones, frost",
    "warmth": "golden light, warm tones",
    "mystery": "fog, obscured background",
    "chaos": "cluttered, active",
    "loneliness": "solitary figure, wide space",
    "tension": "tight composition, low angle",
    "nostalgia": "faded color tones, soft focus",
}

ATMOSPHERE_CLUSTERS = {
    "fog": {"fog", "mist", "haze", "steam"},
    "rain": {"rain", "drizzle", "storm", "downpour"},
    "dark": {"darkness", "gloom", "shadows", "night"},
    "light": {"glow", "shine", "lamp", "neon"},
    "dirty": {"dust", "decay", "ruins", "dirt"},
}

ATM_PHRASES = {
    "fog": "foggy atmosphere",
    "rain": "rainy weather",
    "dark": "dark moody lighting",
    "light": "glowing lights",
    "dirty": "weathered environment",
    "mist": "misty atmosphere",
    "haze": "hazy air",
    "storm": "stormy weather",
    "drizzle": "light drizzle",
    "gloom": "gloomy atmosphere",
    "shadows": "heavy shadows",
    "night": "night time",
    "neon": "neon glow",
    "decay": "decaying textures",
}

LIGHTING_TEMPLATES = {
    frozenset(["lamp", "shadow"]): "dim lamp lighting with soft shadows",
    frozenset(["neon"]): "neon glow lighting",
    frozenset(["dawn"]): "soft dawn lighting",
    frozenset(["sun", "day"]): "bright daylight",
    frozenset(["moon", "night"]): "cold moonlight",
    frozenset(["fire"]): "warm fire glow",
}

GROUP_INDICATORS = {"two", "three", "four", "five", "six", "many", "several", "group", "pair", "couple", "few", "crowd"}

EMOTION_ANCHORS = {
    "joy": "happiness warmth comfort relief safety",
    "sadness": "loss grief loneliness emptiness regret",
    "fear": "threat danger suspense unease anxiety",
    "anger": "conflict frustration hostility tension",
    "calm": "stillness quiet peace reflection silence",
}

ATMOSPHERE_ANCHORS = {
    "rain": "heavy rain storm wet gentle drizzle water soaking splashing pours",
    "fog": "fog mist haze cloudy smoke opaque dim visibility steam vapor",
    "cold": "freezing cold ice chill frost shiver temperature low breath visible snow",
    "darkness": "dark night shadow black dim gloom obscure hidden unlit moonless",
    "silence": "silence quiet mute still hushed soundless echoless dead",
    "decay": "ruin rust broken crumbling peeling old abandoned debris moldy rotting",
    "wind": "windy breeze gust blow storm air moving gale flutter",
    "warmth": "sunlight golden glow fire amber haze summer warm light heat heatwave",
}

SCORE_NOUN_MATCH = 5.0      
SCORE_VERB_AGENT = 2.0     
SCORE_VERB_MOTION = 1.0 
SCORE_FALLBACK = 0.1   

TYPE_HIERARCHY = {
    "unknown": 0,
    "ABSTRACT": 1,
    "OBJECT": 2,
    "PLACE": 3,    
    "CHARACTER": 4  
}

AGENTIVE_DOMAINS = {
    "verb.cognition", "verb.communication", "verb.emotion",
    "verb.perception", "verb.social", "verb.competition",
    "verb.consumption", "verb.body", "verb.motion" 
}

PERSON_NOUNS = {"man", "woman", "boy", "girl", "person", "figure", "silhouette", "stranger", "someone"}
PLACE_NOUNS = {"room", "place", "area", "spot", "side", "center", "corner"}
OBJECT_NOUNS = {"thing", "item", "object", "stuff"}
REPRESENTATION_NOUNS = {"photograph", "photo", "picture", "image", "portrait", "sketch", "drawing", "painting", "poster", "sign", "billboard", "note", "letter"}

INTENTIONAL_VERBS = {
    "decide", "choose", "speak", "say", "whisper", "shout", "ask", "reply",
    "think", "wonder", "know", "believe", "remember", "forget",
    "grab", "hold", "carry", "take", "lift", "drop", "throw",
    "walk", "run", "jump", "climb", "step", "turn", "look", "stare", "glance"
}

PHYSICAL_VERBS = {
    "sway", "swing", "hang", "dangle", "drift", "float", "fall", "drop",
    "glow", "shine", "flicker", "dim", "brighten", "fade",
    "rustle", "creak", "bang", "thud", "click", "hum", "buzz",
    "reflect", "cast", "stand", "lie", "rest", "sit", 
    "flutter", "slide", "slip", "roll", "bounce", "vibrate", "shake", "shiver"
}

LIGHT_OBJECTS = {
    "lantern", "lamp", "candle", "torch", "light", "bulb", "neon", "sign",
    "streetlight", "headlight", "spotlight", "fire", "flame"
}

NATURAL_ELEMENTS = {
    "wind", "rain", "storm", "snow", "fog", "mist", "cloud", "sky", "sun", "moon",
    "river", "ocean", "sea", "lake", "water", "tree", "forest", "shadow", "darkness"
}

LIGHTING_TOKENS = {
    "lamp", "light", "sun", "moon", "glow", "shine", "dim", "dark", 
    "shadow", "bright", "neon", "fluorescent", "lantern", "beam", 
    "ray", "dusk", "dawn", "twilight", "candle", "torch", "bulb",
    "glare", "fade", "blackness"
}

WEATHER_TOKENS = {
    "rain", "fog", "mist", "snow", "storm", "wind", "cloud", "thunder", 
    "lightning", "haze", "smog", "overcast", "drizzle", "pour", 
    "humid", "cold", "freeze", "frost", "ice"
}

MATERIAL_TOKENS = {
    "wood", "stone", "concrete", "metal", "steel", "iron", "glass", 
    "plastic", "rubber", "mud", "dirt", "grass", "sand", "water", 
    "brick", "marble", "chrome", "leather", "fabric", "denim", 
    "velvet", "silk", "paper", "cardboard"
}

CONDITION_TOKENS = {
    "wet", "dry", "crack", "rust", "decay", "broken", "dirty", 
    "clean", "shiny", "dull", "rough", "smooth", "worn", "old", 
    "new", "dusty", "stained", "polished", "weathered", "crumbled",
    "ruined", "abandoned", "empty"
}

SPATIAL_PREPS = {
    "on", "in", "under", "near", "by", "behind", "above",
    "beside", "inside", "outside", "between", "facing", "across",
    "against", "around"
}

CONTINUOUS_TYPES = {"POSSESSES", "IS", "LOCATED", "WEARS", "HAS_ATTRIBUTE"}

STATE_HALF_LIFE = 6       
ACTION_HALF_LIFE = 2       
MAX_STATE_PERSIST = 12     
SPAN_BOOST_SCALE = 0.15   

LOCATION_PREPOSITIONS = {
    "in","on","at","into","toward","towards",
    "from","near","inside","outside",
    "beside","through","under","over"
}
