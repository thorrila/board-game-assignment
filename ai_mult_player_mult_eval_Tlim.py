from math import inf
from game_engine import P1, P2
import time


class TimeLimit(Exception):
    pass

class AI:
    def __init__(self, game, player, max_depth=6, flag=True, name="AI", eval_fn=None, Tlim=0.5):
        self.game = game
        self.player = player
        self.max_depth = max_depth
        self.flag_alpha_beta = flag
        self.name = name
        self.eval_fn = eval_fn if eval_fn is not None else self.default_evaluate
        self.Tlimit = Tlim

        self.nodes_expanded = 0
        self.cutoffs = 0
        self.moves_chosen = 0

    def reset_metrics(self):
        self.nodes_expanded = 0
        self.cutoffs = 0
        self.moves_chosen = 0

    def _check_time(self):
        if time.perf_counter() >= self.Tlimit:
            raise TimeLimit

    def choose_action(self, state, time_limit=1.0):
        legal = self.game.legal_actions(state)
        if not legal:
            raise ValueError("No legal moves available.")

        self.moves_chosen += 1
        self.Tlimit = time.perf_counter() + time_limit

        best_action = legal[0]

        # Iterative deepening: keep improving answer until time runs out
        for depth in range(1, self.max_depth + 1):
            try:
                current_best = legal[0]

                if state.current_player == self.player:
                    best_value = -inf
                    alpha, beta = -inf, inf

                    for action in legal:
                        self._check_time()
                        child = self.game.result(state, action)

                        if self.flag_alpha_beta:
                            value = self.alphabeta(child, depth - 1, alpha, beta)
                        else:
                            value = self.minimax(child, depth - 1)

                        if value > best_value:
                            best_value = value
                            current_best = action

                        alpha = max(alpha, best_value)
                else:
                    best_value = inf
                    alpha, beta = -inf, inf

                    for action in legal:
                        self._check_time()
                        child = self.game.result(state, action)

                        if self.flag_alpha_beta:
                            value = self.alphabeta(child, depth - 1, alpha, beta)
                        else:
                            value = self.minimax(child, depth - 1)

                        if value < best_value:
                            best_value = value
                            current_best = action

                        beta = min(beta, best_value)

                best_action = current_best

            except TimeLimit:
                break

        return best_action

    def minimax(self, state, depth):
        self._check_time()
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
        self._check_time()
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
                if alpha >= beta:
                    self.cutoffs += 1
                    break
            return value
        else:
            value = inf
            for action in legal:
                child = self.game.result(state, action)
                value = min(value, self.alphabeta(child, depth - 1, alpha, beta))
                beta = min(beta, value)
                if alpha >= beta:
                    self.cutoffs += 1
                    break
            return value

    def evaluate(self, state):
        return self.eval_fn(state, self)

    def default_evaluate(self, state, ai=None):
        board = state.board

        if self.game.is_terminal(state):
            return self.game.utility(state, self.player)

        if self.player == P1:
            own_store, opp_store = 6, 13
            own_side = board[0:6]
            opp_side = board[7:13]
        else:
            own_store, opp_store = 13, 6
            own_side = board[7:13]
            opp_side = board[0:6]

        store_diff = board[own_store] - board[opp_store]
        side_diff = sum(own_side) - sum(opp_side)

        return 5 * store_diff + side_diff