
class KalahaGame:
    """
    Simplified game, where the player can only choose from the first 6 pits on their side. 
    After one turn the player switches.
    The game ends when one of the sides is empty. 
    The player with the most marbles in their kalaha wins.
    """
     
    def __init__(self):
        # Initialize the game state here
        self.board = [6] * 6 + [0] + [6] * 6 + [0]
        self.player = 1  # Player 1 starts
        # store indices
        self.pit_hum = 6
        self.pit_ai = 13

    def play(self):
        # Implement the game loop
        
        while not self.is_game_over():
            
            if self.player == 1: # Human player
                action = self.get_human_input()

            else: # AI player = 2
                action = self.get_ai_move()

            self.result(action)
            self.player = 3 - self.player  # Switch player (1 -> 2, 2 -> 1)

    
    def result(self, action):
        # Map 0-5 input to actual board index
        idx = action if self.player == 1 else action + 7

        # grab marbles
        marbles = self.board[idx]
        self.board[idx] = 0

        curr = idx
        while marbles > 0:
            # move to the next pit - going around the board
            curr = (curr + 1) % 14

            # Skip opponent's store
            if (self.player == 1 and curr == 13) or (self.player == 2 and curr == 6):
                continue

            # Drop one marble
            self.board[curr] += 1
            marbles -= 1
        return self

    def is_game_over(self):

        # Side A empty
        if sum(self.board[0:6]) == 0:
            # add rest of the marbles to the opponent's store
            self.board[6] += sum(self.board[7:13])
            return True
        # Side B empty
        if sum(self.board[7:13]) == 0:
            self.board[13] += sum(self.board[0:6])
            return True
        return False
    
    def get_human_input(self):
        while True:
            try:
                # 1. Get the raw input
                self.display_board() # Show the board before asking for input
                move = int(input(f"Player {self.player}(human), choose a pit (0-5): "))
                
                # 2. Check if the index is within the allowed 0-5 range
                if not (0 <= move <= 5):
                    print("Invalid choice!")
                    continue
                
                # 3. Check if the chosen pit actually has marbles
                if self.board[move] == 0:
                    print("That pit is empty! Pick another one.")
                    continue
                
                # If we reach here, the move is valid
                return move
                
            except ValueError:
                # Handles non-integer inputs like "apple"
                print("Invalid input!")
    
    def get_ai_move(self):
        while True:
            try:
                # Change prompt to 0-5
                self.display_board() # Show the board before asking for input
                move = int(input(f"Player {self.player}(human), choose a pit (0-5): "))

                if not (0 <= move <= 5):
                    print("Invalid choice!")
                    continue
                
                # Map to board index 7-12 to check if it's empty
                actual_idx = move + 7 
                if self.board[actual_idx] == 0:
                    print("That pit is empty!")
                    continue
                
                return move # Return 0-5
            
            except ValueError:
                # Handles non-integer inputs like "apple"
                print("Invalid input!")
    
    def display_board(self):
        p2_side = self.board[12:6:-1] # Reverse P2 pits for alignment
        print(f"P2:    {p2_side}")
        print(f"Store: {self.board[13]}                {self.board[6]}")
        print(f"P1:    {self.board[0:6]}")
        print("-" * 20)

if __name__ == "__main__":

    game = KalahaGame()

    game.play()
