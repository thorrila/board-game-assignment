from dataclasses import dataclass
import random

P1 = 1
P2 = 2


@dataclass(frozen=True)
class GameState:
    board: tuple
    current_player: int


class Kalaha:
    def __init__(self, stones_per_pit=6):
        self.stones_per_pit = stones_per_pit

    def initial_state(self):
        board = [self.stones_per_pit] * 6 + [0] + [self.stones_per_pit] * 6 + [0]
        first = random.choice([P1, P2])
        return GameState(tuple(board), first)

    def legal_actions(self, state):
        board = state.board
        if state.current_player == P1:
            return [i for i in range(6) if board[i] > 0]
        else:
            return [i for i in range(6) if board[7 + i] > 0]

    def is_terminal(self, state):
        p1_empty = all(state.board[i] == 0 for i in range(6))
        p2_empty = all(state.board[i] == 0 for i in range(7, 13))
        return p1_empty or p2_empty

    def collect_remaining(self, state):
        if not self.is_terminal(state):
            return state

        board = list(state.board)
        p1_remaining = sum(board[0:6])
        p2_remaining = sum(board[7:13])

        if all(board[i] == 0 for i in range(6)):
            for i in range(7, 13):
                board[i] = 0
            board[6] += p2_remaining
        elif all(board[i] == 0 for i in range(7, 13)):
            for i in range(0, 6):
                board[i] = 0
            board[13] += p1_remaining

        return GameState(tuple(board), state.current_player)

    def utility(self, state, player):
        final_state = self.collect_remaining(state)
        p1_score = final_state.board[6]
        p2_score = final_state.board[13]
        return p1_score - p2_score if player == P1 else p2_score - p1_score

    def result(self, state, action):
        board = list(state.board)
        player = state.current_player

        if player == P1:
            pit_idx = action
            own_store = 6
            opp_store = 13
            own_pits = set(range(0, 6))
        else:
            pit_idx = 7 + action
            own_store = 13
            opp_store = 6
            own_pits = set(range(7, 13))

        stones = board[pit_idx]
        board[pit_idx] = 0
        current_idx = pit_idx

        while stones > 0:
            current_idx = (current_idx + 1) % 14
            if current_idx == opp_store:
                continue
            board[current_idx] += 1
            stones -= 1

        if current_idx in own_pits and board[current_idx] == 1:
            opposite = 12 - current_idx
            if board[opposite] > 0:
                captured = board[opposite] + board[current_idx]
                board[opposite] = 0
                board[current_idx] = 0
                board[own_store] += captured

        next_player = player if current_idx == own_store else (P2 if player == P1 else P1)

        new_state = GameState(tuple(board), next_player)
        return self.collect_remaining(new_state)