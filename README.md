# ChessAI
"ChessAI" is an intelligent chess player based on searching algorithms specifically `alpha-beta-pruning` algorithm. It's a kind of brute-force algorithm as at any node(move) on the tree(game space), it calculates the next move by simply trying every possible move and return the move with the heighst score.
you can read full explanation of `alpha-beta pruning` algorithm in this blog:
https://www.javatpoint.com/ai-alpha-beta-pruning

### Modules:
ChessAI consists of 3 modules:
1. Main module
2. ChessEngine module
3. AIPlayer module

### Main module:
The `main` module reponsible for creating the user-interface of the game board in addition to animation, sounds, and the actual game loop. It uses the `ChessEngine` module and `AIPlayer` module.

### ChessEngine module:
It's the actual engine of the chess game. It implements all chess' pieces moves like `pawn moves`, `king moves`, etc.
#### GameState class:
The primary class of `ChessEngine` module is the `GameState` class which responsible for all functions of the chess game. including all pieces moves function implementations, calculating all valid moves at each gamestate, and making and undoing a move.
#### Move class:
the secondary class of `ChessEngine` is the `Move` class, it's responsible for storing all information about a particular move like the previous square that a piece was at, and the sqaure that a piece is currently at. e.g. if I moved the left-most white pawn from its default sqaure "a2" one step further, it will be on this square "a3". So, we creating an instance of `Move` class to store all of these information.

### AIPlayer module:
The actual magic of `thinking` is done here!. As I said there is nothing magical of this intgelligent chess player, it just examines all valid moves at each step and choose the best move that returns the lowest score for his opponent aka maximizing its own score. It implements the `minimax` algorithm which is a brute-force alogithm but without ``pruning`` and that's mean that it examines all the nodes of the gamestate tree. In other words, it examines all of the moves it can make without regarding if this move is maximizing or minimizing the score.
you can read full explanation of `minimax` algorithm in this blog:
https://www.javatpoint.com/mini-max-algorithm-in-ai

### Used packages:
`pygame`: for implementing the UI and the actual gameloop.

Example usage:
```python
import pygame as p
p.init()

# This is an example usage of making a gameloop with quit mechanism
running = True
while running:
  for event in p.event.get():
    if event.type == p.QUIT:
      running = False
```
here is the link of its official documentation:
https://www.pygame.org/docs/
