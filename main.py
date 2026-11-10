import json
from quiz import Quiz


def load_state(filename="state.json"):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


def load_quizzes(state_data):
    quiz_list = []
    for quiz_data in state_data["quizzes"]:
        quiz = Quiz.from_dict(quiz_data)
        quiz_list.append(quiz)
    return quiz_list


def main():
    state_data = load_state()
    quizzes = load_quizzes(state_data)

    print(f"총 {len(quizzes)}개의 퀴즈를 불러왔습니다.")

    if quizzes:
        print("\n첫 번째 문제 미리보기:")
        quizzes[0].display()


if __name__ == "__main__":
    main()