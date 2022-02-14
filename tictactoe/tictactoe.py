"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    
    X_count = 0
    O_count = 0
    #count number of x(s), o(s) in all rows of the board
    for row in board:
        X_count += row.count(X)
        O_count += row.count(O)

    if X_count <= O_count:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    #set of posible actions to be taken
    possible_actions = set()
    #loop through all rows
    for row_index, row in enumerate(board):
        #loop through all columns
        for column_index, col in enumerate(row):
            if col == None:
                possible_actions.add((row_index, column_index))
    
    return possible_actions    


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    
    player_move = player(board)
    #make a deep copy of the new state of the board
    new_board_state = copy.deepcopy(board)
    
    i, j = action

    if board[i][j] != None:
        raise Exception
    else:
        new_board_state[i][j] = player_move

    return new_board_state


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    for player in (X, O):
        #check row win else x(s) or o(s)
        for row in board:
            if row == [player] * 3:
                return player

        #check col win else x(s) or o(s)
        for i in range(3):
            column = [board[x][i] for x in range(3)]
            if column == [player] * 3:
                return player
        
        #check diagonal win
        if [board[i][i] for i in range(0, 3)] == [player] * 3:
            return player
        #check rest of arrays with the invert operator in any diagonal
        elif [board[i][~i] for i in range(0, 3)] == [player] * 3:
            return player
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    if winner(board) is not None or not actions(board):
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    win_player = winner(board)
    if win_player == X:
        return 1
    elif win_player == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
 
    def max_value(board):
        optimal_action = ()
        if terminal(board):
            return utility(board), optimal_action
        else:
            #all posible values
            values = -5
            for action in actions(board):
                minval = min_value(result(board, action))[0]
                if minval > values:
                    values = minval
                    optimal_action = action
            return values, optimal_action

    def min_value(board):
        optimal_action = ()
        if terminal(board):
            return utility(board), optimal_action
        else:
            values = 5
            for action in actions(board):
                maxval = max_value(result(board, action))[0]
                if maxval < values:
                    values = maxval
                    optimal_action = action
            return values, optimal_action

    current_player = player(board)

    if terminal(board):
        return None

    if current_player == X:
        return max_value(board)[1]

    else:
        return min_value(board)[1]
