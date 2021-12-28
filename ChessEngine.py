import pygame as p
import pygame.mixer
pygame.mixer.init()

captureSound = p.mixer.Sound("sounds/capture.wav")
checkSound = p.mixer.Sound("sounds/castling.wav")
checkMateSound = p.mixer.Sound("sounds/checkMate.wav")

class GameState:
    def __init__(self):
        # board is 8 * 8 dimensions 2d list
        # the first character represents the color which
        # is "b" or "w" the second character represents
        # the type of the piece "R" or "N" or "B" or "Q" or "K" or "p"
        # "--" represents blank space
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        # if white to move = True that means its white turn to play
        self.whiteToMove = True
        # to store log of moves
        self.moveLog = []
        # to store location of each king to check for checks and checkmate
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        # if the current player is in check, this variable will be true
        self.inCheck = False
        self.pins = []
        self.checks = []
        # boolean variable to determine whether checkmate or not
        self.checkMate = False
        # boolean variable to determine whether checkmate or not
        self.staleMate = False
        # will store row, col of an en passant square
        self.enPassantSq = ()

    # this function is making a move in our board, its taking an object of move class
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        # if the piece moved was king, then update its new location
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        # pawn promotion
        if move.isPawnPromoted:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
        # en passant
        if move.isEnPassant:
            self.board[move.startRow][move.endCol] = "--"
        # update en passant square
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enPassantSq = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enPassantSq = ()  # reset the en passant square

    # undo move function
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            # undo en passant move
            if move.isEnPassant:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enPassantSq = (move.endRow, move.endCol)
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enPassantSq = ()
            self.checkMate = False
            self.staleMate = False

    # get valid moves considering the king's checks
    def getValidMoves(self):
        tempEnPassantPossible = self.enPassantSq
        moves = []
        # calling that function will return list of all pins of the current king, list of squares that checks the king
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        # we have 3 different scenarios: (the king is checked by one piece - the king is checked by more than piece
        # or the king does not be checked)
        if self.inCheck:  # if the king is checked
            # checkSound.play()
            # if our king is checked by one piece only, we must block the check or move our king
            if len(self.checks) == 1:
                moves = self.getAllPossibleMoves()
                # to block this check we must put a piece into one of squares between enemy and our king
                check = self.checks[0]  # get the first check in checks list (which is the only one in this case)
                # here check will be something like that (row, col, direction[0], direction[1])
                checkRow = check[0]  # get its row
                checkCol = check[1]  # get its column
                # then we get it from our board to see its type
                pieceChecking = self.board[checkRow][checkCol]
                # list of squares that can we choose one from it to block this check
                validSquares = []
                # if the piece is knight, so we must capture the knight ot move the king, we cannot block it
                if pieceChecking[1] == 'N':
                    # valid squares that i can move to is where the knight is to kill it
                    validSquares = [(checkRow, checkCol)]
                # if the piece is not knight, so we can block it
                else:
                    # keep looping to find all valid squares to block the check
                    for i in range(1, 8):
                        # check[2] and check[3] is the check directions
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        # once i get a piece that causing check end the loop ( there is no valid squares )
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                # remove any moves that don't block check or moving the king
                for i in range(len(moves) - 1, -1, -1):
                    # if we didn't move the king, so that means we must block or capture the checking piece
                    move = moves[i]
                    if move.pieceMoved[1] != 'K':
                        # if this move does not exist in valid squares list, remove it
                        if (move.endRow, move.endCol) not in validSquares:
                            moves.remove(move)
            # if our king is checked by more than one piece, we must move the king
            else:
                self.getKingMoves(kingRow, kingCol, moves)
            # print("valid squares ", validSquares)
        # if the king is not in check so all of the moves is valid
        else:
            moves = self.getAllPossibleMoves()
        # check if there is no valid moves that's mean that is checkmate or stalemate
        if len(moves) == 0:
            if self.inCheck:  # if the king in check, checkmate becomes true
                self.checkMate = True
            else:
                self.staleMate = True
        self.enPassantSq = tempEnPassantPossible
        return moves

    # function helps us to check for pins and checks
    def checkForPinsAndChecks(self):
        pins = []  # list of all squares that contains a pins
        checks = []  # list of squares where enemy is applying check
        inCheck = False
        if self.whiteToMove:  # if it's white turn
            enemyColor = 'b'  # enemy color will be black
            allyColor = 'w'  # ally color will be white
            startRow = self.whiteKingLocation[0]  # white king's row
            startCol = self.whiteKingLocation[1]  # white king's col
        else:  # if it's black king's turn
            enemyColor = 'w'  # enemy color will be white
            allyColor = 'b'  # ally color will be black
            startRow = self.blackKingLocation[0]  # black king's row
            startCol = self.blackKingLocation[1]  # black ing's col
        # king directions, keep track of pins
        # up | left | down | right | upper-left | upper-right | lower-left | lower-right
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        # looping for each direction
        for j in range(len(directions)):
            d = directions[j]
            # tuple to store (row, col) for possible pin
            possiblePin = ()
            for i in range(1, 8):  # Maximum number of moves is 7 squares
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # make sure that square in the board boundaries
                    endPiece = self.board[endRow][endCol]  # get the end piece, Ex: "bQ"
                    # check if the color of end piece is ally color and not a king, this may be a pin
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():  # if there is no possible pin
                            # make that piece a possible pin
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:  # if there is more than an allied piece on the king's directions so no pin or check break
                            break
                    # if the end piece's color is enemy color
                    elif endPiece[0] == enemyColor:
                        # determine the type of this piece "R" "P" "K" "Q" "B" "N"
                        type = endPiece[1]
                        # 1) first situation that the piece is rook and horizontally or vertically away from the king
                        # 2) second situation that is diagonally away from the king and the piece is bishop
                        # 3) third situation is that there is only one square diagonally from the king and piece is pawn
                        # 4) fourth situation any direction and the piece is queen
                        # 5) fifth situation 1 square away and the piece is king
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and (
                                        (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            # if there is no piece blocking, so the king is in check and append it to checks list
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            # if there is a piece blocking add it to pins list
                            else:
                                pins.append(possiblePin)
                                break
                        # enemy piece not applying check
                        else:
                            break
                # if we ran out from the board boundaries break the loop
                else:
                    break
        # check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        # looping for ech directions  of knight moves
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:  # to make sure that we are in
                # the board boundaries
                endPiece = self.board[endRow][endCol]  # get the end piece, Ex:- "bQ"
                # if this an enemy piece and type is "N" that means the king is in check
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks

    # function that generating all possible moves
    def getAllPossibleMoves(self):
        moves = []
        # iterate over the whole board
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                # this stores the first character which is 'w' or 'b' or '-'
                color = self.board[row][col][0]
                # then we will check if the color 'w' and this is the white's
                # turn and if the color is 'b' and the
                # black's turn we will look at the piece
                if (color == 'w' and self.whiteToMove) or \
                        (color == 'b' and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    if piece == 'p':
                        self.getPawnMoves(row, col, moves)
                    elif piece == 'B':
                        self.getBishopMoves(row, col, moves)
                    elif piece == 'N':
                        self.getKnightMoves(row, col, moves)
                    elif piece == 'Q':
                        self.getQueenMoves(row, col, moves)
                    elif piece == 'R':
                        self.getRookMoves(row, col, moves)
                    elif piece == 'K':
                        self.getKingMoves(row, col, moves)
        return moves

    # get pawn moves function
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        # looping for each piece in pins list
        for i in range(len(self.pins) - 1, -1, -1):
            # if the current pawn is in pins
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        # check if its white turn
        if self.whiteToMove:
            # movement
            # if we go up so we're decreasing rows, if we find it empty we append it into moves list
            if self.board[r - 1][c] == "--":
                # check if this pawn is not a pin, or the direction where the piece wants to move, this is a valid move
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    # checks if i on row number 6, that's mean we can go up 2 steps rather than 1
                    if r == 6 and self.board[r - 2][c] == "--":
                        moves.append(Move((r, c), (r - 2, c), self.board))
            # capturing
            if c - 1 >= 0:  # to make sure that we are still there in the board boundaries (left)
                if self.board[r - 1][c - 1][0] == 'b':  # capturing black piece of the left diagonal of our pawn
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enPassantSq:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnPassant=True))

            if c + 1 <= 7:  # to make sure that we are still there in the board boundaries (right)
                if self.board[r - 1][c + 1][0] == 'b':  # capturing black piece of the right diagonal of our pawn
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enPassantSq:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnPassant=True))

        else:  # here is the black pawn moves
            # movement
            if self.board[r + 1][c] == "--":  # 1 square move
                # check if this pawn is not a pin, or the direction where the piece wants to move, this is a valid move
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    # checks if i on row number 1, that's mean we can go down 2 steps rather than 1
                    if r == 1 and self.board[r + 2][c] == "--":
                        moves.append(Move((r, c), (r + 2, c), self.board))
            # capturing
            if c - 1 >= 0:  # to make sure that we are still there in the board boundaries (left)
                if self.board[r + 1][c - 1][0] == 'w':  # capturing white piece of the left diagonal of our pawn
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enPassantSq:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnPassant=True))

            if c + 1 <= 7:  # to make sure that we are still there in the board boundaries (right)
                if self.board[r + 1][c + 1][0] == 'w':  # capturing white piece of the right diagonal of our pawn
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enPassantSq:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnPassant=True))

    # get rook moves function
    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                # to make sure that we don't delete queen moves
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        # up | down | left | right
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1))
        # if this is the white turn that's mean the enemy color is black and vise versa
        enemy = 'b' if self.whiteToMove else 'w'
        for d in directions:  # check for each direction (up | down | left | right)
            for i in range(1, 8):  # maximum number of moves for rook is 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # to make sure that we are in the board's boundaries
                    # if the piece is not a pin or in the same or opposite direction, this is a valid move
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]  # the piece which is at the end row and end column
                        if endPiece == "--":  # if the end piece is blank, this is a valid move
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemy:  # if the end piece is an enemy piece this is a valid move and break
                            # because we cannot jump over this piece
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # if the end piece is one of my pieces that means this is not a valid move
                            break
                else:  # if we try to skip the board boundaries we will break the loop also
                    break

    # get pawn bishop function
    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        # upper-left || upper-right || lower-left || lower-right
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        # if this is the white turn that's mean the enemy color is black and vise versa
        enemy = 'b' if self.whiteToMove else 'w'
        for d in directions:  # check for each direction (up | down | left | right)
            for i in range(1, 8):  # maximum number of moves for bishop is 7 squares
                endRow = r + d[0] * i  # to be able to calculate end row and end column each iteration
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # to make sure that we are in the board's boundaries
                    # check if this is not a pin or direction of pin is the same direction of this piece and also
                    # the opposite direction, this is able to move
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]  # the piece which is at the end row and end column
                        if endPiece == "--":  # if the end piece is blank, this is a valid move
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemy:  # if the end piece is an enemy piece this is a valid move and break
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break  # because we cannot jump over this piece
                        else:  # if the end piece is one of my pieces that means this is not a valid move
                            break
                else:  # if we try to skip the board boundaries we will break the loop also
                    break

    # get knight moves function
    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break

        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = 'w' if self.whiteToMove else 'b'
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    # get Queen moves function
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    # get kings moves function
    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = 'w' if self.whiteToMove else 'b'
        # king can move from 0 to 7 steps ( the whole board )
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            # to make sure that we are in the board boundaries
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # empty or enemy piece
                    # place king on end square and check for checks
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    # reset the king's location back
                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)


# this class responsible for storing all information about a particular move
class Move:
    # here we declare our dictionaries to make the standard naming conventions of chess game
    # the first rank is the last row
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    # dictionary comprehension: change values to keys and keys to values
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    # dictionary comprehension: change values to keys and keys to values
    colsToFiles = {v: k for k, v in filesToCols.items()}

    # our move constructor will take our starting square and ending square and the board and optional parameter
    # which will determine whether the square is en passant or not
    def __init__(self, startSq, endSq, board, isEnPassant=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # handling pawn promotion
        self.isPawnPromoted = False
        if (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7):
            self.isPawnPromoted = True
        # handling en passant
        self.isEnPassant = isEnPassant
        if self.isEnPassant:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp" else "bp"
        self.moveId = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        # check if the other object is an instance from our move class
        if isinstance(other, Move):
            return self.moveId == other.moveId
        return False

    # this function is to get chess notation of the full move
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + \
               self.getRankFile(self.endRow, self.endCol)

    # this function is to get chess notation for a particular square
    def getRankFile(self, r, c):
        # in chess notation we say file first then rank like: "c4", "b8" and so on
        # if row = 0, col = 0 that's mean rank is 8 and the file is a which is "a8"
        return self.colsToFiles[c] + self.rowsToRanks[r]
