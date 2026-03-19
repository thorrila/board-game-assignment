# Kalaha AI

A Python implementation of the classic board game Kalaha, featuring a playable terminal interface and an AI opponent.

## Overview

This project provides a complete engine for playing Kalaha, along with an AI that uses **Minimax with Alpha-Beta pruning** to decide on the best possible moves. You can play directly against the AI in your terminal.

## Project Structure

- **`main_play.py`**: The main entry point to run the game. It handles the game loop, takes input from the human player, and prints the current state of the board to the terminal.
- **`game_engine.py`**: The core game logic. It manages the `GameState`, determines legal moves, distributes stones across pits according to the rules of Kalaha, and evaluates game-over conditions.
- **`ai_player.py`**: Contains the artificial intelligence implementation. The AI uses the Minimax algorithm enhanced with Alpha-Beta pruning to evaluate future board states (up to a default depth of 6) and select the optimal move.

## How to Play

Run the main file with Python:

```bash
python3 main_play.py
```

### Gameplay Rules
- **Player 1 (You)** play on the bottom row and your goal is to collect stones in the rightmost store.
- **Player 2 (AI)** plays on the top row and collects stones in the leftmost store.
- During your turn, select one of your pits (numbered 1-6 from left to right) by entering its number. The stones in that pit will be sown counter-clockwise.

## Requirements

- Python 3.7 or higher. 
- No external dependencies are required (relies only on Python's standard library).
