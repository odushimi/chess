from enum import Enum
from src.main.tools import color_fg_reset, color_fg, color_bg_reset
from abc import ABC, abstractmethod


class Color(Enum):
    WHITE = 'w'  # light
    BLACK = 'b'  # dark


class GameStatus(Enum):
    IN_PROGRESS = 'In Progress'
    STALEMATE = 'Stalemate'
    CHECKMATE = 'Checkmate'


# FILES: A - H
COLUMNS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
# Assuming: A=1, B=2, C=3, D=4, etc
EVEN_COLUMNS = [col for col in COLUMNS if COLUMNS.index(col) % 2 == 1]  # ['B', 'D', 'F', 'H']
ODD_COLUMNS = [col for col in COLUMNS if COLUMNS.index(col) % 2 == 0]  # ['A', 'C', 'E', 'G']

# RANKS: 1 - 8
ROWS = [1, 2, 3, 4, 5, 6, 7, 8]
EVEN_ROWS = [row for row in ROWS if row % 2 == 0]  # [2, 4, 6, 8]
ODD_ROWS = [row for row in ROWS if row % 2 == 1]  # [1, 3, 5, 7]


class Square:
    """ One box that represents a single square on the board """

    def __init__(self, col, row):

        if col not in COLUMNS:
            raise Exception('Col must be in list {}'.format(COLUMNS))

        if row not in ROWS:
            raise Exception('Row must be in list {}'.format(ROWS))

        self.col = col
        self.row = row
        self._piece = None  # Chess piece that occupies the square
        self.color = self._initialize_color(col, row)  # A square can either be dark (BLACK) or light (WHITE)

    @property
    def piece(self):
        return self._piece

    @piece.setter
    def piece(self, piece):
        self._piece = piece

    @staticmethod
    def _initialize_color(col, row):
        # odd - odd : dark
        if col in ODD_COLUMNS and row in ODD_ROWS:
            return Color.BLACK

        # odd - even : light
        elif col in ODD_COLUMNS and row in EVEN_ROWS:
            return Color.WHITE

        # even - even : dark
        elif col in EVEN_COLUMNS and row in EVEN_ROWS:
            return Color.BLACK

        # even - odd : light
        elif col in EVEN_COLUMNS and row in ODD_ROWS:
            return Color.WHITE

        else:
            raise Exception('Col {} and Row {} do not belong on the chess board')

    def __str__(self):
        bg = None
        if self.color == Color.WHITE:
            bg = 'white'
        elif self.color == Color.BLACK:
            bg = 'black'
        return color_bg_reset('{}{}[{}]'.format(self.col, self.row, self.piece if self.piece else '  '), bg)

    def __repr__(self):
        return self.__str__()


class Piece(ABC):
    short = ''

    def __init__(self, color, player=None, board_instance=None):
        self._player = player
        self._board = board_instance
        self._alive = True

        if isinstance(color, Color):
            self.color = color
        elif color.upper() in ['WHITE', 'BLACK']:
            self.color = getattr(Color, color.upper())

        self.moves = 0  # count for completed moves
        self.captured = []  # all pieces that it has captured

        super().__init__()

    @property
    def player(self):
        return self._player

    @player.setter
    def player(self, player):
        self._player = player

    @property
    def board(self):
        return self._board

    @board.setter
    def board(self, board_instance):
        self._board = board_instance

    @property
    def alive(self):
        return self._alive

    @alive.setter
    def alive(self, alive):
        self._alive = alive

    @abstractmethod
    def can_move(self, start: Square, end: Square):
        if not self.player:
            raise Exception('Illegal move: piece does not belong to any player')

        if not self.board:
            raise Exception('Illegal move: piece is not on the board')

    def __str__(self):
        return color_fg('{}{}'.format(self.short, self.color.value), 'red' if not self.alive else 'green')

    def __repr__(self):
        return self.__str__()


class Pawn(Piece):
    short = 'P'

    def can_move(self, start: Square, end: Square) -> bool:
        super().can_move(start, end)
        return self._pawn_can_move(start, end)

    def _pawn_can_move(self, start: Square, end: Square):
        forward_squares = self._get_pawn_forward_squares(start)
        diagonal_squares = self._get_pawn_diagonal_squares(start)

        if not end.piece:
            if self.moves == 0:
                # If it has not yet moved, the pawn has the option of moving two squares forward
                # provided both squares in front of the pawn are unoccupied.
                if end in forward_squares:
                    return True

            elif end == forward_squares[0]:
                # Pawns can move forward one square, if that square is unoccupied.
                return True

        # They can capture an enemy piece on either of the two spaces adjacent to the space in front of them
        # (i.e., the two squares diagonally in front of them) but cannot move to these spaces if they are vacant
        elif end in diagonal_squares and end.piece.color != self.color:
            return True

        return False

    def _get_pawn_forward_squares(self, current_square: Square):
        """ Returns a tuple of forward square for a pawn """
        forward_square_1 = None
        forward_square_2 = None
        try:
            if self.color == Color.WHITE:
                # Same column, row + 1, row + 2
                forward_square_1 = self.board.get_square(current_square.col, current_square.row + 1)
                forward_square_2 = self.board.get_square(current_square.col, current_square.row + 2)

            elif self.color == Color.BLACK:
                # Same column, row - 1, row - 2
                forward_square_1 = self.board.get_square(current_square.col, current_square.row - 1)
                forward_square_2 = self.board.get_square(current_square.col, current_square.row - 2)

        except Exception as exc:
            # Square does not exist
            pass

        return forward_square_1, forward_square_2

    def _get_pawn_diagonal_squares(self, current_square: Square):
        """ get diagonal squares """
        diagonal_square_1 = None
        diagonal_square_2 = None
        col_index = COLUMNS.index(current_square.col)
        try:

            if self.color == Color.WHITE:
                # Row above, square on left and right (i.e. -1, +1 Column)
                diagonal_square_1 = self.board.get_square(COLUMNS[col_index - 1], current_square.row + 1)
                diagonal_square_2 = self.board.get_square(COLUMNS[col_index + 1], current_square.row + 1)

            elif self.color == Color.BLACK:
                # Row below, square on left and right (i.e. -1, +1 Column )
                diagonal_square_1 = self.board.get_square(COLUMNS[col_index - 1], current_square.row - 1)
                diagonal_square_2 = self.board.get_square(COLUMNS[col_index + 1], current_square.row - 1)
        except Exception as exc:
            pass

        return diagonal_square_1, diagonal_square_2


class King(Piece):
    short = 'K'

    def can_move(self, start: Square, end: Square) -> bool:
        super().can_move(start, end)
        return self._king_can_move(start, end)

    def _king_can_move(self, start: Square, end: Square) -> bool:
        # King can move exactly one square horizontally, vertically, or diagonally.
        # At most once in every game, each king is allowed to make a special move, known as castling.

        neighbors = self._get_king_neighbor_squares(start)
        if (end.piece and end.piece.color != self.color or not end.piece) and end in neighbors:
            return True

        # TODO castling move
        return False

    def _get_king_neighbor_squares(self, current_square):
        neighbors = []
        col_index = COLUMNS.index(current_square.col)

        # On the same row at col - 1 and col + 1
        try:
            before = self.board.get_square(COLUMNS[col_index - 1], current_square.row)
            neighbors.append(before)
        except Exception as exc:
            pass

        try:
            after = self.board.get_square(COLUMNS[col_index + 1], current_square.row)
            neighbors.append(after)
        except Exception as exc:
            pass

        # same cold at row - 1 and row + 1
        try:
            above = self.board.get_square(current_square.col, current_square.row - 1)
            neighbors.append(above)
        except Exception as exc:
            pass

        try:
            below = self.board.get_square(current_square.col, current_square.row + 1)
            neighbors.append(below)
        except Exception as exc:
            pass

        # diagonally
        try:
            diagonal_1 = self.board.get_square(COLUMNS[col_index - 1], current_square.row - 1)
            neighbors.append(diagonal_1)
        except Exception as exc:
            pass
        try:
            diagonal_2 = self.board.get_square(COLUMNS[col_index - 1], current_square.row + 1)
            neighbors.append(diagonal_2)
        except Exception as exc:
            pass
        try:
            diagonal_3 = self.board.get_square(COLUMNS[col_index + 1], current_square.row + 1)
            neighbors.append(diagonal_3)
        except Exception as exc:
            pass

        try:
            diagonal_4 = self.board.get_square(COLUMNS[col_index + 1], current_square.row - 1)
            neighbors.append(diagonal_4)
        except Exception as exc:
            pass

        return neighbors


class Queen(Piece):
    short = 'Q'

    def can_move(self, start: Square, end: Square) -> bool:
        super().can_move(start, end)
        return self._queen_can_move(start, end)

    def _queen_can_move(self, start: Square, end: Square) -> bool:
        # Queen can move any number of vacant squares diagonally, horizontally, or vertically.
        return False


class Bishop(Piece):
    short = 'B'

    def can_move(self, start: Square, end: Square) -> bool:
        super().can_move(start, end)
        return self._bishop_can_move(start, end)

    def _bishop_can_move(self, start: Square, end: Square) -> bool:
        # Bishop can move any number of vacant squares in any diagonal direction.
        return False


class Knight(Piece):
    short = 'N'

    def can_move(self, start: Square, end: Square) -> bool:
        super().can_move(start, end)
        return self._knight_can_move(start, end)

    def _knight_can_move(self, start: Square, end: Square) -> bool:
        # Knight can move one square along any rank or file and then at an angle.
        if end in self._get_knight_legal_moves(start):
            return True
        return False

    def _get_knight_legal_moves(self, current_square):
        moves = []
        col_index = COLUMNS.index(current_square.col)

        # Left above 1
        try:
            if col_index - 1 < 0:
                raise Exception('Col Index Error')

            move_1 = self.board.get_square(COLUMNS[col_index - 1], current_square.row + 2)
            moves.append(move_1)
        except Exception as exc:
            pass

        # Left above 2
        try:
            if col_index - 2 < 0:
                raise Exception('Col Index Error')
            move_2 = self.board.get_square(COLUMNS[col_index - 2], current_square.row + 1)
            moves.append(move_2)
        except Exception as exc:
            pass

        # Left below 1
        try:
            if col_index - 1 < 0:
                raise Exception('Col Index Error')
            move_3 = self.board.get_square(COLUMNS[col_index - 1], current_square.row - 2)
            moves.append(move_3)
        except Exception as exc:
            pass

        # Left below 2
        try:
            if col_index - 2 < 0:
                raise Exception('Col Index Error')
            move_4 = self.board.get_square(COLUMNS[col_index - 2], current_square.row - 1)
            moves.append(move_4)
        except Exception as exc:
            pass

        # Right above 1
        try:
            move_5 = self.board.get_square(COLUMNS[col_index + 1], current_square.row + 2)
            moves.append(move_5)
        except Exception as exc:
            pass
        try:
            move_6 = self.board.get_square(COLUMNS[col_index + 2], current_square.row + 1)
            moves.append(move_6)
        except Exception as exc:
            pass

        # Right below 1
        try:
            move_7 = self.board.get_square(COLUMNS[col_index + 2], current_square.row - 1)
            moves.append(move_7)
        except Exception as exc:
            pass

        try:
            move_8 = self.board.get_square(COLUMNS[col_index + 1], current_square.row - 2)
            moves.append(move_8)
        except Exception as exc:
            pass

        return moves


class Rook(Piece):
    short = 'R'

    def can_move(self, start: Square, end: Square) -> bool:
        super().can_move(start, end)
        return self._rook_can_move(start, end)

    def _rook_can_move(self, start: Square, end: Square) -> bool:
        # A rook can move any number of squares along a rank or file, but cannot leap over other pieces.
        # Along with the king, a rook is involved during the king's castling move.

        if end in self._get_rook_legal_movements(start):
            # TODO Rook cannot skip occupied cell
            return True
        return False

    def _get_rook_legal_movements(self, current_square):
        col = current_square.col
        row = current_square.row
        # all squares on the same row + squares on same column
        same_col = self.board.get_squares_at_col(col)
        same_row = self.board.get_squares_at_row(row)

        movements = list(set(same_col + same_row))
        movements.remove(current_square)
        return movements


class Board:
    """ Single board: 64 squares, 32 blacks and 32 whites"""

    def __init__(self):
        self._squares = self.initialize()

    @property
    def squares(self):
        return self._squares

    @squares.setter
    def squares(self, squares):
        self._squares = squares

    @staticmethod
    def initialize():
        """ Create squares on the board"""

        # Create a dict to hold the squares
        squares = {}
        for row in ROWS:
            squares_on_row = []
            for col in COLUMNS:
                square = Square(col, row)
                squares_on_row.append(square)
            squares[row] = squares_on_row
        return squares

    def get_square(self, col, row):
        """ Return square on col and row """
        if col not in COLUMNS or row not in ROWS:
            raise Exception('Square at {}{} does not exist'.format(col, row))
        return self.get_squares_at_row(row)[COLUMNS.index(col)]

    def get_piece(self, col, row):
        """ Return piece at col and row """
        return self.get_square(col, row).piece

    def get_squares_at_row(self, row):
        if row not in ROWS:
            raise Exception('Row {} does not exist'.format(row))
        return self.squares[row]

    def get_squares_at_col(self, col):
        if col not in COLUMNS:
            raise Exception('Col {} does not exist'.format(col))
        col_index = COLUMNS.index(col)
        return [square[col_index] for _, square in self.squares.items() if square[col_index].col == col]

    def __str__(self):
        print_board = ''
        for row, row_squares in self.squares.items():
            print_row = ''
            for square in row_squares:
                print_row = '{}{}'.format(print_row, square)

            print_board = '{}\n{}'.format(print_row, print_board)
        return print_board

    def __repr__(self):
        return self.__str__()


class Player:
    """ Each individual player will have own board. """

    def __init__(self, color, name=None, board_instance=None, ):
        self._name = name
        self._board = board_instance

        if isinstance(color, Color):
            self.color = color
        elif color.upper() in ['WHITE', 'BLACK']:
            self.color = getattr(Color, color.upper())
        else:
            raise Exception('Color {} is not valid'.format(color))

        if name:
            self._name = name
        else:
            self._name = self.color.name.capitalize()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def board(self):
        return self._board

    @board.setter
    def board(self, board_instance):
        self._board = board_instance

    def move(self):
        # Make a move
        pass

    def setup(self, board_instance: Board):
        """ Assign player side on the board """
        self.board = board_instance

        if self.color == Color.WHITE:
            # Place piece on row 1 and 2
            first_row = 1
            second_row = 2
        elif self.color == Color.BLACK:
            # Place piece on row 7 and 8
            first_row = 8
            second_row = 7
        else:
            raise Exception('Unknown Color {} while placing pieces'.format(self.color))

        # Place pieces on the first row for each player
        row_1 = board_instance.get_squares_at_row(first_row)
        row_1[0].piece = Rook(self.color, self, self.board)
        row_1[1].piece = Knight(self.color, self, self.board)
        row_1[2].piece = Bishop(self.color, self, self.board)
        row_1[3].piece = Queen(self.color, self, self.board)
        row_1[4].piece = King(self.color, self, self.board)
        row_1[5].piece = Bishop(self.color, self, self.board)
        row_1[6].piece = Knight(self.color, self, self.board)
        row_1[7].piece = Rook(self.color, self, self.board)

        row_2 = board_instance.get_squares_at_row(second_row)
        for square in row_2:
            # Fill row 2 with 8 pawns
            square.piece = Pawn(self.color, self, self.board)

    def has_no_legal_move(self):
        return False

    def __str__(self):
        return '{} {}'.format(self.name, self.color.value)

    def __repr__(self):
        return self.__str__()


class Move:
    def __init__(self, player: Player, piece: Piece, start, end):
        self.player = player
        self.piece = piece
        self._captured = None

        if isinstance(start, Square):
            self.start = start
        elif isinstance(start, str) and len(start) == 2:
            # Something like A1, H7
            col = '{}'.format(start[0]).upper()
            row = int(start[1])

            self.start = self.player.board.get_square(col, row)

        else:
            raise Exception('Illegal move: Start square {} not recognized'.format(start))

        if isinstance(end, Square):
            self.end = end
        elif isinstance(end, str) and len(end) == 2:
            # Something like A1, H7
            col = '{}'.format(end[0]).upper()
            row = int(end[1])

            self.end = self.player.board.get_square(col, row)

        else:
            raise Exception('Illegal move: End square {} not recognized'.format(end))

        if self.player.color != self.piece.color:
            raise Exception('Illegal move: Player can only move their own pieces')

        if not self.piece.can_move(self.start, self.end):
            raise Exception('Illegal move: {} cannot be moved from {} to {}'.format(piece, start, end))

    @property
    def captured(self):
        return self._captured

    @captured.setter
    def captured(self, captured):
        self._captured = captured

    def make(self):
        # Capture piece at destination
        self.captured = self.end.piece if self.end.piece else None
        self.piece.captured.append(self.captured)
        self.piece.moves += 1
        self.start.piece = None
        self.end.piece = self.piece

        # Promote pawn  if it move to the last row
        # When a pawn advances to the eighth rank, as a part of the move it
        # is promoted and must be exchanged for the player's choice of queen,
        # rook, bishop, or knight of the same color.
        # Let's promote it to Queen here
        if isinstance(self.piece, Pawn):
            if self.piece.color.WHITE and self.end.row == 8 or self.piece.color.BLACK and self.end.row == 1:
                # remove piece from the board and replace it with a Queen piece
                self.end.piece = Queen(self.piece.color, self.player, self.player.board)

    def __str__(self):
        return '{}:{}->{}'.format(self.piece, self.start, self.end)

    def __repr__(self):
        return self.__str__()


class Game:
    def __init__(self, player_1_name='White', player_2_name='Black'):
        self.round = 1  # current round
        self.board = Board()
        self.player_1 = Player(color='white', board_instance=self.board, name=player_1_name)
        self.player_2 = Player(color='black', board_instance=self.board, name=player_2_name)
        self.setup()
        self.winner = None
        self.status = GameStatus.IN_PROGRESS
        self.moves = []  # all moves made during this game
        self._over = False

    @property
    def over(self):
        return self._over

    @over.setter
    def over(self, over):
        self._over = over

    def setup(self):
        self.player_1.setup(self.board)
        self.player_2.setup(self.board)

    def make_move(self, player: Player, piece: Piece, start: Square, end: Square):
        if self.status == GameStatus.CHECKMATE:
            raise Exception('Game is already over')

        new_move = Move(player, piece, start, end)
        new_move.make()
        self.moves.append(new_move)

        # Checkmate when King is captured
        if isinstance(new_move.captured, King):
            self.status = GameStatus.CHECKMATE
            self.over = True

            if new_move.captured.color == Color.BLACK:
                self.winner = self.player_1
            elif new_move.captured.color == Color.WHITE:
                self.winner = self.player_2

        elif player.has_no_legal_move():
            self.status = GameStatus.STALEMATE
            self.over = True

    def play_round(self, _start_1, _start_2, _end_1, _end_2):

        if not isinstance(_start_1, Square):
            _start_1 = self.board.get_square(_start_1[0], int(_start_1[1]))

        if not isinstance(_start_2, Square):
            _start_2 = self.board.get_square(_start_2[0], int(_start_2[1]))

        if not isinstance(_end_1, Square):
            _end_1 = self.board.get_square(_end_1[0], int(_end_1[1]))

        if not isinstance(_end_2, Square):
            _end_2 = self.board.get_square(_end_2[0], int(_end_2[1]))

        self.make_move(player=self.player_1, piece=_start_1.piece, start=_start_1, end=_end_1)
        self.make_move(player=self.player_2, piece=_start_2.piece, start=_start_2, end=_end_2)
        self.round += 1
        print(self)

    def __str__(self):
        return '{} vs {}: Round {}, Winner: {}\n{}'.format(
            self.player_1.name, self.player_2.name, self.round, self.winner, self.board)

    def __repr__(self):
        return self.__str__()


if __name__ == "__main__":

    new_game = Game()
    while not new_game.over:
        try:
            print(new_game)
            move_1 = input('White: Enter your move. Ex: D2->D4 \n')
            move_2 = input('Black: Enter your move. Ex: C7->C5 \n')

            start_1 = move_1.split('->')[0]
            start_2 = move_2.split('->')[0]
            end_1 = move_1.split('->')[1]
            end_2 = move_2.split('->')[1]

            new_game.play_round(start_1, start_2, end_1, end_2)
        except Exception as exc:
            print(color_fg_reset('Error: {}\n'.format(exc), 'red'))

