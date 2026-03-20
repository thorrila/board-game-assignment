import time
import random
from game_engine import Kalaha, P1, P2
#from ai_mult_player_mult_eval import AI
from ai_mult_player_mult_eval_Tlim import AI, TimeLimit

class KalahaAIMatch:
    def __init__(self, stones_per_pit=6, depth_p1=6, depth_p2=6,
                 flag_p1=True, flag_p2=False, eval_p1=None, eval_p2=None, Tlim=0.5):
        self.game = Kalaha(stones_per_pit=stones_per_pit)
        self.state = self.game.initial_state()

        self.ai1 = AI(self.game, player=P1, max_depth=depth_p1,
                      flag=flag_p1, name="AI-1", eval_fn=eval_p1, Tlim=Tlim)
        self.ai2 = AI(self.game, player=P2, max_depth=depth_p2,
                      flag=flag_p2, name="AI-2", eval_fn=eval_p2, Tlim=Tlim)

        self.move_times = {P1: [], P2: []}
        self.move_count = 0

    def display_board(self):
        board = self.state.board
        p2_side = list(board[12:6:-1])
        p1_side = list(board[0:6])

        print()
        print(f"P2:    {p2_side}")
        print(f"Store: {board[13]:2d}{' ' * 16}{board[6]:2d}")
        print(f"P1:    {p1_side}")
        print("-" * 28)

    def play(self, show_board=True, Tlim=0.5):
        self.ai1.reset_metrics()
        self.ai2.reset_metrics()

        while not self.game.is_terminal(self.state):
            if show_board:
                self.display_board()

            if self.state.current_player == P1:
                ai = self.ai1
            else:
                ai = self.ai2

            t0 = time.perf_counter()
            action = ai.choose_action(self.state, time_limit = Tlim)
            t1 = time.perf_counter()

            self.move_times[self.state.current_player].append(t1 - t0)
            self.move_count += 1

            if show_board:
                if self.state.current_player == P1:
                    print(f"{ai.name} (P1) chooses pit {action + 1}")
                else:
                    print(f"{ai.name} (P2) chooses pit {5 - action + 1}")

            self.state = self.game.result(self.state, action)

        final_state = self.game.collect_remaining(self.state)
        self.state = final_state

        if show_board:
            self.display_board()

        return self.get_metrics()

    def get_metrics(self):
        p1_score = self.state.board[6]
        p2_score = self.state.board[13]

        winner = 0
        if p1_score > p2_score:
            winner = P1
        elif p2_score > p1_score:
            winner = P2

        metrics = {
            "winner": winner,
            "p1_score": p1_score,
            "p2_score": p2_score,
            "score_diff_p1_minus_p2": p1_score - p2_score,
            "total_moves": self.move_count,
            "p1_avg_move_time": (
                sum(self.move_times[P1]) / len(self.move_times[P1])
                if self.move_times[P1] else 0.0
            ),
            "p2_avg_move_time": (
                sum(self.move_times[P2]) / len(self.move_times[P2])
                if self.move_times[P2] else 0.0
            ),
            "p1_nodes_expanded": self.ai1.nodes_expanded,
            "p2_nodes_expanded": self.ai2.nodes_expanded,
            "p1_cutoffs": self.ai1.cutoffs,
            "p2_cutoffs": self.ai2.cutoffs,
            "p1_uses_alpha_beta": self.ai1.flag_alpha_beta,
            "p2_uses_alpha_beta": self.ai2.flag_alpha_beta,
            "p1_depth": self.ai1.max_depth,
            "p2_depth": self.ai2.max_depth,
        }
        return metrics


def print_metrics(metrics):
    print("\n=== Match Metrics ===")
    if metrics["winner"] == P1:
        print("Winner: Player 1")
    elif metrics["winner"] == P2:
        print("Winner: Player 2")
    else:
        print("Winner: Draw")

    print(f"P1 score: {metrics['p1_score']}")
    print(f"P2 score: {metrics['p2_score']}")
    print(f"Score diff (P1 - P2): {metrics['score_diff_p1_minus_p2']}")
    print(f"Total moves: {metrics['total_moves']}")
    print(f"P1 avg move time: {metrics['p1_avg_move_time']:.6f} s")
    print(f"P2 avg move time: {metrics['p2_avg_move_time']:.6f} s")
    print(f"P1 nodes expanded: {metrics['p1_nodes_expanded']}")
    print(f"P2 nodes expanded: {metrics['p2_nodes_expanded']}")
    print(f"P1 cutoffs: {metrics['p1_cutoffs']}")
    print(f"P2 cutoffs: {metrics['p2_cutoffs']}")
    print(f"P1 alpha-beta: {metrics['p1_uses_alpha_beta']}")
    print(f"P2 alpha-beta: {metrics['p2_uses_alpha_beta']}")
    print(f"P1 depth: {metrics['p1_depth']}")
    print(f"P2 depth: {metrics['p2_depth']}")

def run_experiment(num_games=10, stones_per_pit=6,
                   depth_p1=6, depth_p2=6,
                   flag_p1=True, flag_p2=False,
                   eval_p1=None, eval_p2=None,
                   Tlim = 0.5):
    results = {
        "p1_wins": 0,
        "p2_wins": 0,
        "draws": 0,
        "score_diffs": [],
        "p1_times": [],
        "p2_times": [],
        "p1_nodes": [],
        "p2_nodes": [],
        "p1_cutoffs": [],
        "p2_cutoffs": [],
    }

    for X in range(num_games):
        #print("Game: ", X)
        match = KalahaAIMatch(
            stones_per_pit=stones_per_pit,
            depth_p1=depth_p1,
            depth_p2=depth_p2,
            flag_p1=flag_p1,
            flag_p2=flag_p2,
            eval_p1=eval_p1,
            eval_p2=eval_p2,
            Tlim=Tlim
        )
        metrics = match.play(show_board=False, Tlim = Tlim)

        if metrics["winner"] == P1:
            results["p1_wins"] += 1
        elif metrics["winner"] == P2:
            results["p2_wins"] += 1
        else:
            results["draws"] += 1

        results["score_diffs"].append(metrics["score_diff_p1_minus_p2"])
        results["p1_times"].append(metrics["p1_avg_move_time"])
        results["p2_times"].append(metrics["p2_avg_move_time"])
        results["p1_nodes"].append(metrics["p1_nodes_expanded"])
        results["p2_nodes"].append(metrics["p2_nodes_expanded"])
        results["p1_cutoffs"].append(metrics["p1_cutoffs"])
        results["p2_cutoffs"].append(metrics["p2_cutoffs"])

    print("\n=== Experiment Summary ===")
    print(f"Games: {num_games}")
    print(f"P1 wins: {results['p1_wins']}")
    print(f"P2 wins: {results['p2_wins']}")
    print(f"Draws: {results['draws']}")
    print(f"Avg score diff (P1 - P2): {sum(results['score_diffs']) / num_games:.3f}")
    print(f"Avg P1 move time: {sum(results['p1_times']) / num_games:.6f} s")
    print(f"Avg P2 move time: {sum(results['p2_times']) / num_games:.6f} s")
    print(f"Avg P1 nodes expanded: {sum(results['p1_nodes']) / num_games:.1f}")
    print(f"Avg P2 nodes expanded: {sum(results['p2_nodes']) / num_games:.1f}")
    print(f"Avg P1 cutoffs: {sum(results['p1_cutoffs']) / num_games:.1f}")
    print(f"Avg P2 cutoffs: {sum(results['p2_cutoffs']) / num_games:.1f}")


def eval_store_heavy(state, ai):
    board = state.board

    if ai.game.is_terminal(state):
        return ai.game.utility(state, ai.player)

    if ai.player == P1:
        own_store, opp_store = 6, 13
        #own_side = board[0:6]
        #opp_side = board[7:13]
    else:
        own_store, opp_store = 13, 6
        #own_side = board[7:13]
        #opp_side = board[0:6]

    store_diff = board[own_store] - board[opp_store]
    
    return store_diff


def eval_side_heavy(state, ai):
    M = 12 * ai.game.stones_per_pit
    board = state.board

    if ai.game.is_terminal(state):
        return ai.game.utility(state, ai.player)

    if ai.player == P1:
        own_store, opp_store = 6, 13
        own_side = board[0:6]
        opp_side = board[7:13]
    else:
        own_store, opp_store = 13, 6
        own_side = board[7:13]
        opp_side = board[0:6]

    store_diff = board[own_store] - board[opp_store]
    side_diff = - sum(own_side) + sum(opp_side)

    #linear
    w1 = M #testing for 1
    w2 = M / (M + 1 - (own_store + opp_store)) # +1 so we don't devide by 0

    #exponential
    #progress = 1 - ((M - own_store - opp_store) / M)
    #w1 = 5
    #w2 = 0.1 + 2.5 * (progress ** 2)

    return w1 * store_diff + w2 * side_diff

def eval_extra_turns(state, ai):
    M = 12 * ai.game.stones_per_pit
    board = state.board

    if ai.game.is_terminal(state):
        return ai.game.utility(state, ai.player)

    if ai.player == P1:
        own_store, opp_store = 6, 13
        own_side = board[0:6]
        opp_side = board[7:13]
    else:
        own_store, opp_store = 13, 6
        own_side = board[7:13]
        opp_side = board[0:6]

    store_diff = board[own_store] - board[opp_store]
    side_diff = - sum(own_side) + sum(opp_side)

    extra_turn_pits = 0
    for action in ai.game.legal_actions(state):
        if ai.player == P1:
            stones = board[action]
            distance_to_store = 6 - action
        else:
            pit_idx = 7 + action
            stones = board[pit_idx]
            distance_to_store = 13 - pit_idx

        if stones == distance_to_store:
            extra_turn_pits += 1

    #w1 = M #testing for 1
    #w2 = M / (M + 1 - (own_store + opp_store)) # +1 so we don't devide by 0
    #w3 = M

    # non-linear
    progress = 1 - ((M - own_store - opp_store) / M)
    w1 = 1
    w2 = 0.1 + 2.5 * (progress ** 2)
    w3 = 5

    return w1 * store_diff + w2 * side_diff + w3 * extra_turn_pits

def eval_extra_turns_13pit(state, ai):
    M = 12 * ai.game.stones_per_pit
    board = state.board

    if ai.game.is_terminal(state):
        return ai.game.utility(state, ai.player)

    if ai.player == P1:
        own_store, opp_store = 6, 13
        own_side = board[0:6]
        opp_side = board[7:13]
    else:
        own_store, opp_store = 13, 6
        own_side = board[7:13]
        opp_side = board[0:6]

    store_diff = board[own_store] - board[opp_store]
    side_diff = - sum(own_side) + sum(opp_side)

    extra_turn_pits = 0
    pit_with_13 = 0
    for action in ai.game.legal_actions(state):
        if ai.player == P1:
            stones = board[action]
            distance_to_store = 6 - action
        else:
            pit_idx = 7 + action
            stones = board[pit_idx]
            distance_to_store = 13 - pit_idx

        if stones == distance_to_store:
            extra_turn_pits += 1
        
        if stones == 13:
            pit_with_13 += 1

    #w1 = M #testing for 1
    #w2 = M / (M + 1 - (own_store + opp_store)) # +1 so we don't devide by 0
    #w3 = M

    # non-linear
    progress = 1 - ((M - own_store - opp_store) / M)
    w1 = 1
    w2 = 0.1 + 2.5 * (progress ** 2)
    w3 = 5
    w4 = 7

    return w1 * store_diff + w2 * side_diff + w3 * extra_turn_pits + w4 * pit_with_13


if __name__ == "__main__":

    # true is using alpha beta prunning
    # false is normal search tree
    detph = 10
    Tlim = 0.1
    depth1, flag1, eval1 = detph, True, eval_store_heavy
    #depth2, flag2, eval2 = detph, True, eval_side_heavy
    #depth2, flag2, eval2 = detph, True, eval_extra_turns
    depth2, flag2, eval2 = detph, True, eval_extra_turns_13pit

    print("using timelit pr. choose action (s): ", Tlim)
    print("Using (w1,exp growth rate,w3,w4)=(1,0,5,7)")
    print("First player using method: ", flag1, " with search depth: ", depth1, "with eval func: ", eval1.__name__)
    print("Second player using method: ", flag2, " with search depth: ", depth2, "with eval func: ", eval2.__name__)

    run_experiment(
        num_games=50,
        stones_per_pit=6,
        depth_p1=depth1,
        depth_p2=depth2,
        flag_p1=flag1, 
        flag_p2=flag2,
        eval_p1=eval1,
        eval_p2=eval2,
        Tlim = Tlim
    )
