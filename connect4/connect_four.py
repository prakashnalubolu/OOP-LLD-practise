from dataclasses import dataclass
from enum import Enum

class DiscColour(Enum):
    WHITE = "White"
    BLUE = "Blue"

class GameState(Enum):
    IN_PROGRESS = "in progress"
    WIN = "win"
    DRAW = "draw"

@dataclass(frozen=True)
class Player():
    id: int
    color: DiscColour

class Board():
    def __init__(self, row:int = 6, col: int = 7): #Has default value
        self.row = row
        self.col = col

        self.board = [[None]*self.col for _ in range(self.row)] #initialize a board[6x7]
        self.columns = [0]*self.col #Keeps track of the lowest position in the board for eahc column(0->6)

    def drop_a_disc(self, col: int, disc: DiscColour) -> int:
        if col < 0 or col >= self.col:
            return -1
        if self.columns[col] >= self.row:
            return -1

        r = self.columns[col]      # bottom-up: next free row
        self.board[r][col] = disc
        self.columns[col] += 1
        return r      

    def is_full(self):
        # If board is full return True
        for i in range(self.col):
            if self.columns[i] < self.row:
                return False   
        return True
    
    def has_disc(self, row, col)->bool:
        #return true if the block has disc else false
        return self.board[row][col] is not None
           

    def is_consecutive_4_discs(self, row:int, col:int):
        if not self.has_disc(row, col):
            return False 
        #when you drop a disc look for same color discs in vertial, horizantal and diagonal directions
        #positive and negative directions, if total count == 4 return true
        color = self.board[row][col]
        directions = [[1,0],[0,1],[1,1],[1,-1]]
        for dr, dc in directions:
            count = 1
            count += self._count_in_direction(row, col, dr, dc, color)
            count += self._count_in_direction(row, col, -dr, -dc, color)
            if count >= 4:
                return True
        return False
    
    def _count_in_direction(self, row: int, column: int, dr: int, dc: int, color: DiscColour) -> int:
        count = 0
        nr = row + dr
        nc = column + dc
        while 0 <= nr < self.row and 0 <= nc < self.col and self.board[nr][nc] == color:
            count += 1
            nr += dr
            nc += dc
        return count

class ConnectFour:
    def __init__(self, player1: Player, player2: Player, board: Board):
        self.player1 = player1
        self.player2 = player2
        self.board = board

        self.game_state = GameState.IN_PROGRESS
        self.curr_player = player1
        self.winner = None  # optional but useful

    def choose_a_column(self, player: Player, column: int):
        # validate game state
        if self.game_state != GameState.IN_PROGRESS:
            return "Game is already completed"
        # validate turn
        if player != self.curr_player:
            return "Not your turn"
        # drop disc
        row = self.board.drop_a_disc(column, player.color)
        if row == -1:
            return f"Cannot choose this {column} since it is full or invalid"
        # check win
        if self.board.is_consecutive_4_discs(row, column):
            self.game_state = GameState.WIN
            self.winner = player
            return f"{player} won"
        # check draw
        if self.board.is_full():
            self.game_state = GameState.DRAW
            return "Game is a draw"
        # switch turn
        self.curr_player = self.player2 if self.curr_player == self.player1 else self.player1
        return f"Move accepted. Now it's {self.curr_player}'s turn"
    
    def get_current_player(self):
        return self.curr_player
    
    def get_board(self):
        return self.board
    
    def get_winner(self):
        return self.winner
        
    def get_game_state(self):
        return self.game_state