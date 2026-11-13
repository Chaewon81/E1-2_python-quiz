from quiz_game import QuizGame


def main():
    game = QuizGame()
    try:
        game.run()
    except (KeyboardInterrupt, EOFError):
        print("\n입력이 중단되어 현재 데이터를 저장하고 종료합니다.")
        game.save_state()


if __name__ == "__main__":
    main()
