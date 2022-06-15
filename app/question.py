class Question:
    def __init__(self, id:int, text:str, 
                    alternatives:list, answer: str, 
                    category:str, 
                    media_url = None) -> None:
        self.id = id
        self.text = text
        self.alternatives = alternatives
        self.answer = answer
        self.category = category
        self.media_url = media_url

    def points(self):
        return 10 

    def __str__(self) -> str:
        s = f"{self.id}. {self.text}\n"

        for i, opt in enumerate(self.alternatives, start=ord('a')):
            s = s + f"{chr(i).upper()}) {opt}\n"
        return s