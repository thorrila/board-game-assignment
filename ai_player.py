from math import inf
from game_engine import Kalaha, GameState, P1, P2


class AI:
    def __init__(self, game, player, max_depth=6):
        self.game = game
        self.player = player
        self.max_depth = max_depth

    def choose_action(self, state):
        # IMPORTANT note - this function goes depth first in the tree search. 
        legal = self.game.legal_actions(state)
        best_action = legal[0]

        if state.current_player == self.player:
            best_value = -inf
            for action in legal:
                child = self.game.result(state, action)
                value = self.minimax(child, self.max_depth - 1)
                if value > best_value:
                    best_value = value
                    best_action = action
        else:
            best_value = inf
            for action in legal:
                child = self.game.result(state, action)
                value = self.minimax(child, self.max_depth - 1)
                if value < best_value:
                    best_value = value
                    best_action = action

        return best_action

    def minimax(self, state, depth):
        if depth == 0 or self.game.is_terminal(state):
            return self.evaluate(state)

        legal = self.game.legal_actions(state)

        if state.current_player == self.player:
            value = -inf
            for action in legal:
                child = self.game.result(state, action)
                value = max(value, self.minimax(child, depth - 1))
            return value
        else:
            value = inf
            for action in legal:
                child = self.game.result(state, action)
                value = min(value, self.minimax(child, depth - 1))
            return value

    def evaluate(self, state):
        board = state.board

        if self.game.is_terminal(state):
            return self.game.utility(state, self.player)

        if self.player == P1:
            k1, k2 = 6, 13
            #side1 = board[0:6]
            #side2 = board[7:13]
        else:
            k1, k2 = 13, 6
            #side1 = board[7:13]
            #side2 = board[0:6]

        kalaha_diff = board[k1] - board[k2]
        #side_diff = sum(side1) - sum(side2)

        return kalaha_diff #+ side_diff