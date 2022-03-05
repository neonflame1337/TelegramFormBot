class AnswerEntity:
    def __init__(self, user_id: int, question_id: int, text: str):
        self.user_id: int = user_id
        self.question_id: int = question_id
        self.text: str = text
