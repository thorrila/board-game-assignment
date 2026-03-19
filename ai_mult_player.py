from math import inf
from game_engine import P1, P2


class AI:
    def __init__(self, game, player, max_depth=6, flag=True, name="AI"):
        self.game = game
        self.player = player
        self.max_depth = max_depth
        self.flag_alpha_beta = flag
        self.name = name

        # Metrics
        self.nodes_expanded = 0
        self.cutoffs = 0
        self.moves_chosen = 0

    def reset_metrics(self):
        self.nodes_expanded = 0
        self.cutoffs = 0
        self.moves_chosen = 0

    def choose_action(self, state):
        legal = self.game.legal_actions(state)
        if not legal:
            raise ValueError("No legal moves available.")

        self.moves_chosen += 1
        best_action = legal[0]
        alpha, beta = -inf, inf

        # In practice this will usually be the AI's turn when called
        if state.current_player == self.player:
            best_value = -inf
            for action in legal:
                child = self.game.result(state, action)

                if self.flag_alpha_beta:
                    value = self.alphabeta(child, self.max_depth - 1, alpha, beta)
                else:
                    value = self.minimax(child, self.max_depth - 1)

                if value > best_value:
                    best_value = value
                    best_action = action

                alpha = max(alpha, best_value)
        else:
            best_value = inf
            for action in legal:
                child = self.game.result(state, action)

                if self.flag_alpha_beta:
                    value = self.alphabeta(child, self.max_depth - 1, alpha, beta)
                else:
                    value = self.minimax(child, self.max_depth - 1)

                if value < best_value:
                    best_value = value
                    best_action = action

                beta = min(beta, best_value)

        return best_action

    def minimax(self, state, depth):
        self.nodes_expanded += 1

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

    def alphabeta(self, state, depth, alpha, beta):
        self.nodes_expanded += 1

        if depth == 0 or self.game.is_terminal(state):
            return self.evaluate(state)

        legal = self.game.legal_actions(state)

        if state.current_player == self.player:
            value = -inf
            for action in legal:
                child = self.game.result(state, action)
                value = max(value, self.alphabeta(child, depth - 1, alpha, beta))
                alpha = max(alpha, value)
                if beta <= alpha:
                    self.cutoffs += 1
                    break
            return value
        else:
            value = inf
            for action in legal:
                child = self.game.result(state, action)
                value = min(value, self.alphabeta(child, depth - 1, alpha, beta))
                beta = min(beta, value)
                if beta <= alpha:
                    self.cutoffs += 1
                    break
            return value

    def evaluate(self, state):
        board = state.board

        if self.game.is_terminal(state):
            return self.game.utility(state, self.player)

        if self.player == P1:
            k1, k2 = 6, 13
            side1 = board[0:6]
            side2 = board[7:13]
        else:
            k1, k2 = 13, 6
            side1 = board[7:13]
            side2 = board[0:6]

        kalaha_diff = board[k1] - board[k2]
        side_diff = sum(side1) - sum(side2)

        return 5 * kalaha_diff + side_diff