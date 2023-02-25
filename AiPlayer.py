import random

pieceScores = {'K': 0, 'Q': 10, 'R': 5, 'B': 3, 'N': 3, 'p': 1}
checkMate = 2000
stalemate = 0
max_depth = 4

def getRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


def findBestMove(gs, validmoves):
    global nextMove
    nextMove = None
    random.shuffle(validmoves)
    findMoveAlphaBeta(gs, validmoves, max_depth, -checkMate, checkMate, 1 if gs.whiteToMove else -1)
    
    return nextMove  # this will return the next move after changing it in minimax move function


def findMoveMinMax(gs, validmoves, depth, whiteToMove):
    global nextMove
    # terminal state of recursion, if we reached to depth 0 then get score of this move
    if depth == 0:
        return getScore(gs.board)
    # check if this white turn, then maximize your score
    if whiteToMove:
        maxScore = -checkMate  # starting with really low score to be able to change it
        for move in validmoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()  # generate all possible moves depending in this move
            score = findMoveMinMax(gs, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == max_depth:  # if we explored the whole state space
                    nextMove = move 
            gs.undoMove()  # make sure to undo it
        return maxScore
    # this is the AI player's turn then we want to minimizing score
    else:
        minScore = checkMate  # starting min score with very high value
        for move in validmoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()  # generate all valid moves depends on this move
            score = findMoveMinMax(gs, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == max_depth:  # if we explored the whole state space
                    nextMove = move
            gs.undoMove()  # make sure to undo this move
        return minScore


def findMoveMinMaxAlphaBeta(gs, validmoves, depth, alpha, beta, whiteToMove):
    global nextMove
    # terminal state of recursion, if we reached to depth 0 then get score of this move
    if depth == 0:
        return getScore(gs.board)
    # check if this white turn, then maximize your score
    if whiteToMove:
        maxScore = -checkMate  # starting with really low score to be able to change it
        for move in validmoves:
            gs.makeMove(move)  # make each valid move
            nextMoves = gs.getValidMoves()  # generate all possible moves depending in this move
            score = findMoveMinMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, False)  # recursion but now, depth -1, False
            maxScore = max(maxScore, score)
            alpha = max(alpha, score)
            if depth == max_depth:
                nextMove = move
                if beta <= alpha:
                    break
            gs.undoMove()  # make sure to undo it
        return maxScore  # return max score

    # this is the AI player's turn then we want to minimizing score
    else:
        minScore = checkMate  # starting min score with very high value
        for move in validmoves:
            gs.makeMove(move)  # make each valid move
            nextMoves = gs.getValidMoves()  # generate all valid moves depends on this move
            score = findMoveMinMaxAlphaBeta(gs, nextMoves, depth - 1, beta, alpha, True)  # recursion
            minScore = min(minScore, score)
            beta = min(beta, score)
            if depth == max_depth:  # if we explored the whole state space
                nextMove = move  # then our next move is the current move
                if beta <= alpha:
                    break
            gs.undoMove()  # make sure to undo this move
        return minScore  # return min score


def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -checkMate
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = - findMoveNegaMax(gs, nextMoves, depth-1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == max_depth:
                nextMove = move
        gs.undoMove()
    return maxScore


def findMoveAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -checkMate
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = - findMoveAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == max_depth:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


# heuristic function that returns positive score if white wins, negative score if white wins
def scoreBoard(gs):
    # check if the king is checked
    if gs.checkMate:
        if gs.whiteToMove:
            return -checkMate  # really big negative score (black wins)
        else:
            return checkMate  # really big positive score (white wins)
    elif gs.staleMate:
        return stalemate
    score = 0
    for r in gs.board:
        for sq in r:
            if sq[0] == 'w':
                score += pieceScores[sq[1]]
            elif sq[0] == 'b':
                score -= pieceScores[sq[1]]
    return score

# heuristic function 1 to get score for the move
def getScore(board):
    score = 0
    for r in board:
        for square in r:
            if square[0] == 'w':  # if the white's turn this is maximizing score
                score += pieceScores[square[1]]
            elif square[0] == 'b':  # if the black's turn this is minimizing score
                score -= pieceScores[square[1]]
    return score
