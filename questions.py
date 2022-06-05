

class Questions:
    def __init__(self, id:int, text:str, 
                    alternatives:list, category:str, 
                    media_url = None) -> None:
        self.id = id
        self.text = text
        self.alternatives = alternatives
        self.category = category
        self.media_url = media_url