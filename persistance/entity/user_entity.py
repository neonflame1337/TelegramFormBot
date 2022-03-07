class UserEntity:
    def __init__(self, id: int, username: str, current_question: int, ready: int = 0, processed: int = 0, contact_info: str = None):
        self.id: int = id
        self.current_question: int = current_question
        self.ready: int = ready
        self.processed: int = processed
        self.username: str = username
        self.contact_info: str = contact_info
