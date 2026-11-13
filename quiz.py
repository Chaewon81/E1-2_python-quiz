class Quiz:
    """A four-choice quiz question."""

    def __init__(self, question, choices, answer, points=10, category="일반"):
        if not isinstance(question, str) or not question.strip():
            raise ValueError("문제는 비어 있을 수 없습니다.")
        if not isinstance(choices, list) or len(choices) != 4:
            raise ValueError("선택지는 정확히 4개여야 합니다.")
        if not all(isinstance(choice, str) and choice.strip() for choice in choices):
            raise ValueError("선택지는 비어 있지 않은 문자열이어야 합니다.")
        if type(answer) is not int or answer not in range(1, 5):
            raise ValueError("정답 번호는 1~4의 정수여야 합니다.")
        if type(points) is not int or points < 1:
            raise ValueError("점수는 1 이상의 정수여야 합니다.")
        if not isinstance(category, str) or not category.strip():
            raise ValueError("분류는 비어 있을 수 없습니다.")
        self.question = question.strip()
        self.choices = [choice.strip() for choice in choices]
        self.answer = answer
        self.points = points
        self.category = category.strip()

    def display(self):
        print(self.question)
        for index, choice in enumerate(self.choices, start=1):
            print(f"{index}. {choice}")

    def check_answer(self, user_answer):
        return user_answer == self.answer

    def to_dict(self):
        return {"question": self.question, "choices": self.choices,
                "answer": self.answer, "points": self.points,
                "category": self.category}

    @classmethod
    def from_dict(cls, data):
        return cls(data["question"], data["choices"], data["answer"],
                   data.get("points", 10), data.get("category", "일반"))
