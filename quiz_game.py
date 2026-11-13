import json
import random
import shutil
from datetime import datetime
from pathlib import Path

from quiz import Quiz


DEFAULT_QUIZZES = [
    Quiz("파이썬에서 여러 값을 순서대로 저장하는 자료형은?", ["dict", "list", "set", "int"], 2, 10, "Python"),
    Quiz("문자열을 정수로 바꾸는 함수는?", ["str()", "list()", "int()", "bool()"], 3, 10, "Python"),
    Quiz("조건에 따라 실행 흐름을 나누는 키워드는?", ["if", "for", "def", "import"], 1, 10, "Python"),
    Quiz("함수에서 결과를 돌려주는 키워드는?", ["break", "return", "class", "with"], 2, 10, "Python"),
    Quiz("키와 값의 쌍으로 데이터를 저장하는 자료형은?", ["tuple", "list", "dict", "str"], 3, 10, "Python"),
]


class QuizGame:
    def __init__(self, filename="state.json", input_fn=input):
        self.filename = Path(filename)
        self.input = input_fn
        self.quizzes = list(DEFAULT_QUIZZES)
        self.best_score = 0
        self.score_history = []
        self.load_state()

    def load_state(self):
        backup = self.filename.with_suffix(self.filename.suffix + ".bak")
        try:
            self._load_state_file(self.filename)
        except FileNotFoundError:
            try:
                self._load_state_file(backup)
                print("저장 파일이 없어 백업에서 데이터를 복구했습니다.")
                self.save_state()
            except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
                print("저장 파일이 없어 기본 퀴즈를 사용합니다.")
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            print(f"저장 파일을 읽지 못했습니다 ({error}). 백업을 확인합니다.")
            try:
                self._load_state_file(backup)
                print("백업 파일에서 데이터를 복구했습니다.")
                self.save_state()
            except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
                print("사용 가능한 백업이 없어 기본 퀴즈로 시작합니다.")

    def _load_state_file(self, path):
        self.quizzes, self.best_score, self.score_history = self._read_state_file(path)

    @staticmethod
    def _read_state_file(path):
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict) or not isinstance(data.get("quizzes"), list):
            raise ValueError("저장 데이터 구조가 올바르지 않습니다.")
        quizzes = [Quiz.from_dict(item) for item in data["quizzes"]]
        if not quizzes:
            raise ValueError("퀴즈 목록이 비어 있습니다.")
        score = data.get("best_score", 0)
        if type(score) is not int or score < 0:
            raise ValueError("최고 점수 형식이 올바르지 않습니다.")
        history = data.get("score_history", [])
        if (not isinstance(history, list) or
                any(not isinstance(item, dict) or
                    type(item.get("score")) is not int or item["score"] < 0 or
                    type(item.get("question_count")) is not int or item["question_count"] < 0
                    for item in history)):
            raise ValueError("점수 기록 형식이 올바르지 않습니다.")
        return quizzes, score, history

    def save_state(self):
        data = {"quizzes": [quiz.to_dict() for quiz in self.quizzes],
                "best_score": self.best_score, "score_history": self.score_history}
        try:
            self.filename.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.filename.with_suffix(self.filename.suffix + ".tmp")
            with temporary.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            backup = self.filename.with_suffix(self.filename.suffix + ".bak")
            backup_temporary = backup.with_suffix(backup.suffix + ".tmp")
            if self.filename.exists():
                try:
                    self._read_state_file(self.filename)
                except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
                    pass
                else:
                    shutil.copy2(self.filename, backup_temporary)
                    backup_temporary.replace(backup)
            temporary.replace(self.filename)
        except OSError as error:
            print(f"저장에 실패했습니다: {error}")

    def get_int_input(self, prompt, minimum, maximum):
        while True:
            raw = self.input(prompt).strip()
            try:
                value = int(raw)
            except ValueError:
                print("숫자를 입력해 주세요.")
                continue
            if minimum <= value <= maximum:
                return value
            print(f"{minimum}~{maximum} 사이의 숫자를 입력해 주세요.")

    def show_menu(self):
        print("\n=== 퀴즈 게임 ===")
        print("1. 퀴즈 풀기\n2. 퀴즈 추가\n3. 퀴즈 목록\n4. 최고 점수 및 기록")
        print("5. 퀴즈 삭제\n6. 종료")

    def run(self):
        while True:
            self.show_menu()
            choice = self.get_int_input("메뉴 선택: ", 1, 6)
            if choice == 1:
                self.play_quiz()
            elif choice == 2:
                self.add_quiz()
            elif choice == 3:
                self.show_list()
            elif choice == 4:
                self.show_score()
            elif choice == 5:
                self.delete_quiz()
            else:
                self.save_state()
                print("게임을 종료합니다.")
                return

    def play_quiz(self):
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return
        order = list(self.quizzes)
        random.shuffle(order)
        count = self.get_int_input(f"풀 문제 수 (1~{len(order)}): ", 1, len(order))
        score = 0
        for index, quiz in enumerate(order[:count], 1):
            print(f"\n문제 {index}/{count} [{quiz.category}, {quiz.points}점]")
            quiz.display()
            answer = self.get_int_input("정답 번호 (1~4): ", 1, 4)
            if quiz.check_answer(answer):
                score += quiz.points
                print(f"정답! +{quiz.points}점")
            else:
                print(f"오답입니다. 정답은 {quiz.answer}번: {quiz.choices[quiz.answer - 1]}")
        print(f"이번 점수: {score}점")
        self.best_score = max(self.best_score, score)
        self.score_history.append({"date": datetime.now().astimezone().isoformat(timespec="seconds"),
                                   "score": score, "question_count": count})
        self.save_state()

    def add_quiz(self):
        question = self.input("문제: ").strip()
        choices = [self.input(f"선택지 {index}: ").strip() for index in range(1, 5)]
        answer = self.get_int_input("정답 번호 (1~4): ", 1, 4)
        category = self.input("분류 (Enter는 일반): ").strip() or "일반"
        points = self.get_int_input("배점 (1~100): ", 1, 100)
        try:
            quiz = Quiz(question, choices, answer, points, category)
        except ValueError as error:
            print(f"퀴즈를 추가하지 못했습니다: {error}")
            return
        self.quizzes.append(quiz)
        self.save_state()
        print("퀴즈를 저장했습니다.")

    def show_list(self):
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return
        for index, quiz in enumerate(self.quizzes, 1):
            print(f"{index}. [{quiz.category}, {quiz.points}점] {quiz.question}")

    def show_score(self):
        print(f"최고 점수: {self.best_score}점")
        if not self.score_history:
            print("아직 플레이 기록이 없습니다.")
            return
        print("최근 플레이 기록:")
        for record in self.score_history[-10:][::-1]:
            print(f"- {record.get('date', '날짜 미상')}: {record.get('score', 0)}점 / "
                  f"{record.get('question_count', 0)}문제")

    def delete_quiz(self):
        if not self.quizzes:
            print("삭제할 퀴즈가 없습니다.")
            return
        self.show_list()
        index = self.get_int_input(f"삭제할 번호 (1~{len(self.quizzes)}, 취소는 0): ",
                                   0, len(self.quizzes))
        if index == 0:
            print("삭제를 취소했습니다.")
            return
        removed = self.quizzes.pop(index - 1)
        self.save_state()
        print(f"퀴즈를 삭제했습니다: {removed.question}")
