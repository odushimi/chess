import unittest
from src.main import chess
import random
import string


class SquareTest(unittest.TestCase):

    def setUp(self) -> None:
        self.rand_col = random.choice(chess.COLUMNS)
        self.rand_row = random.choice(chess.ROWS)
        self.square = chess.Square(self.rand_col, self.rand_row)
        # print('Square at {}{}: {}'.format(self.rand_col, self.rand_row, self.square))

    def test_initialization(self):

        for i in range(0, 10000):
            rand_col = random.choice(list(string.ascii_uppercase) + list(string.ascii_lowercase))
            rand_row = random.randint(0, 1000)
            if rand_col not in chess.COLUMNS or rand_row not in chess.ROWS:
                self.assertRaises(Exception, chess.Square)
            else:
                square = chess.Square(rand_col, rand_row)
                print('Randomly Generated Square: {}'.format(square))
                self.assertIn(square.col, chess.COLUMNS)
                self.assertIn(square.row, chess.ROWS)

                # odd col - odd row black
                if chess.COLUMNS.index(square.col) % 2 == 0 and square.row % 2 == 1:
                    self.assertEqual(square.color, chess.Color.BLACK)
                # odd col - even row white
                elif chess.COLUMNS.index(square.col) % 2 == 0 and square.row % 2 == 0:
                    self.assertEqual(square.color, chess.Color.WHITE)
                # even col - odd row white
                elif chess.COLUMNS.index(square.col) % 2 == 1 and square.row % 2 == 1:
                    self.assertEqual(square.color, chess.Color.WHITE)
                # even col - even row black
                elif chess.COLUMNS.index(square.col) % 2 == 1 and square.row % 2 == 0:
                    self.assertEqual(square.color, chess.Color.BLACK)


class TestPiece(unittest.TestCase):
    def setUp(self) -> None:
        self.black_pawn = chess.Pawn('black')
        self.white_pawn = chess.Pawn('WHITE')

        self.king = chess.King('white')
        self.queen = chess.Queen('white')
        self.rook = chess.Rook('white')
        self.knight = chess.Knight('white')
        self.bishop = chess.Bishop('white')

        self.board = chess.Board()
        self.player = chess.Player('white', board_instance=self.board)

    def test_initialization(self):
        print('Black Pawn: {}'.format(self.black_pawn))
        print('White Pawn: {}'.format(self.white_pawn))
        print(self.board)
        self.assertEqual(self.black_pawn.color, chess.Color.BLACK)
        self.assertEqual(self.white_pawn.color, chess.Color.WHITE)

    def test_pawn_can_move_white(self):
        square = self.board.get_square('C', 2)
        square.piece = self.white_pawn
        self.white_pawn.board = self.board
        self.white_pawn.player = self.player
        square_allowed_movements = [self.board.get_square('C', 3), self.board.get_square('C', 4)]
        self.assertFalse(self.white_pawn.can_move(self.board.get_square('C', 2), self.board.get_square('C', 5),))
        self.assertFalse(self.white_pawn.can_move(self.board.get_square('C', 2), self.board.get_square('B', 2),))
        self.assertFalse(self.white_pawn.can_move(self.board.get_square('C', 2), self.board.get_square('D', 2),))
        self.assertFalse(self.white_pawn.can_move(self.board.get_square('C', 2), self.board.get_square('C', 1),))

        allowed_movements = []
        for row, row_squares in self.board.squares.items():
            for s in row_squares:
                if self.white_pawn.can_move(square, s):
                    allowed_movements.append(s)
                    self.assertIn(s, square_allowed_movements)

        black_pawn_1 = chess.Pawn('black')
        black_pawn_2 = chess.Pawn('black')
        square_1 = self.board.get_square('B', 3)
        square_2 = self.board.get_square('D', 3)
        square_allowed_movements.extend([square_1, square_2])
        square_1.piece = black_pawn_1
        square_2.piece = black_pawn_2

        allowed_movements = []
        for row, row_squares in self.board.squares.items():
            for s in row_squares:
                if self.white_pawn.can_move(square, s):
                    allowed_movements.append(s)
                    self.assertIn(s, square_allowed_movements)

        self.assertEqual(len(allowed_movements), len(square_allowed_movements))

    def test_pawn_can_move_black(self):
        square = self.board.get_square('E', 6)
        square.piece = self.black_pawn
        self.black_pawn.board = self.board
        self.black_pawn.player = self.player
        square_allowed_movements = [self.board.get_square('E', 5), self.board.get_square('E', 4)]

        self.assertFalse(self.black_pawn.can_move(self.board.get_square('E', 5), self.board.get_square('E', 6),))
        self.assertFalse(self.black_pawn.can_move(self.board.get_square('E', 5), self.board.get_square('F', 6),))
        self.assertFalse(self.black_pawn.can_move(self.board.get_square('E', 5), self.board.get_square('E', 6),))
        self.assertFalse(self.black_pawn.can_move(self.board.get_square('E', 5), self.board.get_square('E', 1),))

        allowed_movements = []
        for row, row_squares in self.board.squares.items():
            for s in row_squares:
                if self.black_pawn.can_move(square, s):
                    allowed_movements.append(s)
                    self.assertIn(s, square_allowed_movements)
        self.assertEqual(len(allowed_movements), len(square_allowed_movements))
        # Diagonal occupied
        white_pawn_1 = chess.Pawn('white')
        white_pawn_2 = chess.Pawn('white')
        square_1 = self.board.get_square('D', 5)
        square_2 = self.board.get_square('F', 5)
        square_allowed_movements.extend([square_1, square_2])
        square_1.piece = white_pawn_1
        square_2.piece = white_pawn_2

        allowed_movements = []
        for row, row_squares in self.board.squares.items():
            for s in row_squares:
                if self.black_pawn.can_move(square, s):
                    allowed_movements.append(s)
                    self.assertIn(s, square_allowed_movements)

        self.assertEqual(len(allowed_movements), len(square_allowed_movements))

    def test_king_can_move(self):
        square = self.board.get_square('E', 1)
        square.piece = self.king
        self.king.board = self.board
        self.king.player = self.player

        square_allowed_movements = [
            self.board.get_square('E', 2),
            self.board.get_square('F', 2),
            self.board.get_square('D', 2),
            self.board.get_square('D', 1),
            self.board.get_square('F', 1)
        ]
        allowed_movements = []
        for row, row_squares in self.board.squares.items():
            for s in row_squares:
                if self.king.can_move(square, s):
                    allowed_movements.append(s)
                    self.assertIn(s, square_allowed_movements)

        print(allowed_movements)

    def test_rook_can_move(self):
        square = self.board.get_square('D', 5)
        square.piece = self.rook
        self.rook.board = self.board
        self.rook.player = self.player

        self.assertEqual(len(self.rook._get_rook_legal_movements(square)), 14)

    def test_knight_can_move(self):
        square = self.board.get_square('D', 5)
        square.piece = self.knight
        self.knight.board = self.board
        self.knight.player = self.player

        print(self.board)
        print(self.knight._get_knight_legal_moves(square))


class BoardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.board = chess.Board()
        # print(self.board)

    def test_initialization(self):
        print(self.board)
        self.assertIsNotNone(self.board)

    def test_get_square(self):
        for i in range(0, 10000):
            rand_col = random.choice(list(string.ascii_uppercase) + list(string.ascii_lowercase))
            rand_row = random.randint(0, 100)

            if rand_col not in chess.COLUMNS or rand_row not in chess.ROWS:
                self.assertRaises(Exception, self.board.get_square)
            else:
                square = self.board.get_square(rand_col, rand_row)
                self.assertEqual(square.col, rand_col)
                self.assertEqual(square.row, rand_row)
                self.assertIsNone(square.piece)

    def test_get_squares_at_row(self):
        for i in range(0, 10000):
            rand_row = random.randint(0, 100)

            if rand_row not in chess.ROWS:
                self.assertRaises(Exception, self.board.get_squares_at_row)
            else:
                squares = self.board.get_squares_at_row(rand_row)
                row_print = ''
                for square in squares:
                    row_print = '{}{}'.format(row_print, square)
                # print('Squares at Row {}: {}'.format(rand_row, row_print))

                for col_index, square in enumerate(squares):
                    self.assertEqual(square.row, rand_row)
                    self.assertEqual(square.col, chess.COLUMNS[col_index])

    def test_get_squares_at_col(self):
        for i in range(0, 10000):
            rand_col = random.choice(list(string.ascii_uppercase) + list(string.ascii_lowercase))

            if rand_col not in chess.COLUMNS:
                self.assertRaises(Exception, self.board.get_squares_at_col)
            else:
                squares = self.board.get_squares_at_col(rand_col)
                col_print = ''
                for square in squares:
                    col_print = '{}\n{}'.format(col_print, square)

                # print('Squares at Col {}: {}'.format(rand_col, col_print))
                for row_index, square in enumerate(squares):
                    self.assertEqual(square.col, rand_col)
                    self.assertEqual(square.row, row_index + 1)


class TestPlayer(unittest.TestCase):
    def setUp(self) -> None:
        self.player = chess.Player(color='white')
        self.player_2 = chess.Player(chess.Color.WHITE)

    def test_initialization(self):
        print('Player: {}'.format(self.player))
        self.assertEqual(self.player.color.name, 'WHITE')
        self.assertEqual(self.player_2.color, chess.Color.WHITE)
        self.assertEqual(self.player.name, 'White')


class TestGame(unittest.TestCase):
    def setUp(self) -> None:
        self.game = chess.Game()

    def test_initialization(self):
        print('Game: {}'.format(self.game))
        self.assertEqual(self.game.round, 1)
        self.assertEqual(self.game.player_1.color, chess.Color.WHITE)
        self.assertEqual(self.game.player_1.name, 'White')
        self.assertEqual(self.game.player_2.color, chess.Color.BLACK)
        self.assertEqual(self.game.player_2.name, 'Black')


class TestMove(unittest.TestCase):
    def setUp(self) -> None:
        self.board = chess.Board()
        self.player = chess.Player('white')
        self.piece = chess.Pawn('white')
        self.piece.player = self.player
        self.piece.board = self.board
        self.player.board = self.board
        self.start = self.board.get_square('A', 1)
        self.start.piece = self.piece
        self.end = self.board.get_square('A', 2)
        self.move = chess.Move(self.player, self.piece, self.start, self.end)

    def test_initialization(self):
        self.assertEqual(self.move.start, self.player.board.get_square('A', 1))
        self.assertEqual(self.move.end, self.player.board.get_square('A', 2))

    def test_move(self):
        # check if pawn is promoted when it reaches rank 8
        start = self.board.get_square('B', 7)

        end = self.board.get_square('B', 8)
        start.piece = chess.Pawn('white', self.player, self.board)

        new_move = chess.Move(self.player, start.piece, start, end)
        new_move.make()
        self.assertTrue(isinstance(self.player.board.get_square('B', 8).piece, chess.Queen))


if __name__ == '__main__':
    unittest.main()
