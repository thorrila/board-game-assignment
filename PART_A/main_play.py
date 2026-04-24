from game_engine import Kalaha, P1, P2
from ai_player import AI


class KalahaGame:
    """
    Human player = P1 (bottom row)
    AI player    = P2 (top row)
    """

    def __init__(self, stones_per_pit=6, max_depth=6,flag = True):
        self.game = Kalaha(stones_per_pit=stones_per_pit)
        self.state = self.game.initial_state()
        self.ai = AI(self.game, player=P2, max_depth=max_depth, flag = flag)

    def play(self):
        while not self.game.is_terminal(self.state):
            # Human
            if self.state.current_player == P1:
                action = self.get_human_input()
                print(f"Player 1 (human) chooses pit {action + 1}")
            # AI
            else:
                self.display_board()
                action = self.ai.choose_action(self.state)
                print(f"Player 2 (AI) chooses pit {5-action + 1}")

            self.state = self.game.result(self.state, action)

        self.display_result()


    def get_human_input(self):
        while True:
            try:
                self.display_board()

                legal = self.game.legal_actions(self.state)
                display_moves = [m + 1 for m in legal]
                print(f"Legal moves: {display_moves}")

                move = int(input("Player 1 (human), choose a pit: ")) - 1

                if move not in legal:
                    print("That move is not allowed!")
                    continue

                return move

            except ValueError:
                print("Invalid input!")
    

    def display_board(self):
        board = self.state.board
        p2_side = list(board[12:6:-1])
        p1_side = list(board[0:6])

        print()
        print(f"P2:    {p2_side}")
        print(f"Store: {board[13]:2d}{' ' * 16}{board[6]:2d}")
        print(f"P1:    {p1_side}")
        print("-" * 28)

    def display_result(self):
        final_state = self.game.collect_remaining(self.state)
        self.state = final_state
        self.display_board()

        p1_score = final_state.board[6]
        p2_score = final_state.board[13]

        print(f"Final score -> Player 1: {p1_score}, Player 2: {p2_score}")

        if p1_score > p2_score:
            print("Player 1 (human) wins!")
        elif p2_score > p1_score:
            print("Player 2 (AI) wins!")
        else:
            print("It's a draw!")


if __name__ == "__main__":
    # flag = True => use alpha beta prunning and flag = False => normal search tree with max depth.
    game = KalahaGame(stones_per_pit=6, max_depth=6, flag = True)
    game.play()