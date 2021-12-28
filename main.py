# importing pygame, fonts, sounds and chess engine
import pygame as p
import ChessEngine, AiPlayer
import pygame.mixer
import pygame.font
pygame.mixer.init()
pygame.font.init()

# declare constants of our game
WIDTH = HEIGHT = 512  # width, height of our screen
DIMENSION = 8  # chess board is 8 x 8 dimensions
SQ_SIZE = HEIGHT // DIMENSION  # square size is 512 // 8 = 64 px
MAX_FPS = 60  # for animations (optional)
IMAGES = {}  # image dictionary to store images of chess pieces
WHITE = (255, 255, 255)
YELLOW = (233, 230, 223)
ORANGE = (255, 217, 102)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
WINNER_FONT = p.font.SysFont('calibri', 60)

# import sounds
startSound = p.mixer.Sound("sounds/start.wav")
captureSound = p.mixer.Sound("sounds/capture.wav")
moveSound = p.mixer.Sound("sounds/move.wav")
# soundTrack = p.mixer.Sound("sounds/soundTrack.mp3")
checkSound = p.mixer.Sound("sounds/castling.wav")
checkMateSound = p.mixer.Sound("sounds/checkMate.wav")
youWin = p.mixer.Sound("sounds/youWin.mp3")
AIWin = p.mixer.Sound("sounds/AiWins.mp3")
staleMateSound = p.mixer.Sound("sounds/staleMate.wav")

# load images function
def loadImages():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.image.load("images/" + piece + ".png")

# main function
def main():
    p.init()  # initializing pygame components
    # soundTrack.play()
    startSound.play()  # play the start sound
    clock = p.time.Clock()  # tak a clock object to control execution of our program
    screen = p.display.set_mode((WIDTH, HEIGHT))  # creating display
    p.display.set_caption("Intelligent Chess Player")
    screen.fill(WHITE)  # initialize screen color by white
    gs = ChessEngine.GameState()  # taking a game state object
    validMoves = gs.getValidMoves()  # get all valid moves at the beginning of the game which are 20
    moveMade = False  # boolean variable to check whether the move is made or not
    gameOver = False  # boolean variable to check whether there are valid moves or not
    loadImages()  # calling load images function before loop ( initial state )
    running = True  # variable for our game loop
    animate = True
    sqSelected = ()  # tuple to store row, col of the selected piece
    playerClicks = []  # list of tuples to store player clicks which are : selected piece and ending place
    playerOne = True  # if the white it's true, if it's AI it's false
    playerTwo = False  # if the AI turn, this is true, if this white turn this will be false
    while running:
        # human turn will be true if this is white turn and playerOne=true
        # or this black turn and playerTwo=false
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        # loop to get all events of pygame
        for event in p.event.get():
            # check if we clicked on 'X' icon break the loop
            if event.type == p.QUIT:
                running = False
            # MOUSE EVENTS HANDLING
            elif event.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    # if we pressed at any point, store the mouse position(0:height, 0:width)
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    # check if the selected piece is already selected, reset it
                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    # if we clicked in two places, make a move object
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        # check if this move is valid move, then make this move
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                # reset the selected square and player clicks for the next move
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            # KEYBOARD EVENTS HANDLING
            elif event.type == p.KEYDOWN:
                # if we pressed z, undo last move
                if event.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    gameOver = False
                    animate = False

                # if we pressed escape, break the loop and close the game
                elif event.key == p.K_ESCAPE:
                    running = False
                # if we pressed r, reset the game
                elif event.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False
                    animate = False

        # AI Move
        if not gameOver and not humanTurn:
            AIMove = AiPlayer.findBestMove(gs, validMoves)
            if AIMove is None:
                AIMove = AiPlayer.getRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        # if we made a move, then generating all valid moves
        # again after making this move (we changing game state)
        if moveMade:
            moveSound.play()
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
        # after that keep drawing the current game state
        drawGameState(screen, gs, validMoves, sqSelected)
        if gs.checkMate:
            gameOver = True
            # checkMateSound.play()
            if gs.whiteToMove:
                drawText(screen, "AI Player wins by CheckMate!")
            else:
                drawText(screen, "Congrats You Win by CheckMate!")
        elif gs.staleMate:
            gameOver = True
            # staleMateSound.play()
            drawText(screen, "StaleMate")

        clock.tick(MAX_FPS)
        p.display.update()

# function for highlighting the square and its valid moves
def highlightSquares(screen, gs, validMoves, sqSelected):
    # check if there is a square selected
    if sqSelected != ():
        # get the row and column of it to be able to highlight it
        r, c = sqSelected
        # check what color of the piece selected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            # highlighting selected square
            # creating a square surface and its size is 64 x 64
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(ORANGE)
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            # highlighting valid moves
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    s.fill(p.Color('green'))
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))
                if gs.inCheck:
                    if gs.whiteToMove:
                        s.fill(p.Color('red'))
                        screen.blit(s, (gs.whiteKingLocation[1] * SQ_SIZE, gs.whiteKingLocation[0] * SQ_SIZE))
                    else:
                        s.fill(p.Color('red'))
                        screen.blit(s, (gs.blackKingLocation[1] * SQ_SIZE, gs.blackKingLocation[0] * SQ_SIZE))

# drawing game state function which takes screen, game state, valid moves, sq selected tp draw it
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)

# drawing board
def drawBoard(screen):
    global colors
    colors = [WHITE, YELLOW]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            # to keep switching between colors
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

# draw pieces of chess game which take the current board representation, snd the screen to draw on it
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            # check if the piece not empty, then put it on the screen
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawText(screen, text):
    font = p.font.SysFont("calibri", 32, True)
    textObject = font.render(text, True, BLACK)
    textLoc = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLoc)

def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    frames = 5
    framesCount = (abs(dR) + abs(dC)) * frames
    for frame in range(framesCount + 1):
        r, c = (move.startRow + dR * frame / framesCount, move.startCol + dC * frame / framesCount)
        drawBoard(screen)
        drawPieces(screen, board)
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()
