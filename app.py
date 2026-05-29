
from flask import Flask, render_template, request, jsonify
import chess
import math
import torch
import torch.nn as nn

app = Flask(__name__)

board = chess.Board()

difficulty_levels = {
    "beginner": 1,
    "easy": 2,
    "medium": 3,
    "hard": 4,
    "expert": 5
}

current_difficulty = "medium"

piece_values = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

class ChessEvaluator(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(64, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 1)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

model = ChessEvaluator()

def board_to_tensor(board):
    tensor = torch.zeros(64)
    piece_map = board.piece_map()

    for square, piece in piece_map.items():
        value = piece_values.get(piece.piece_type, 0)
        tensor[square] = value if piece.color else -value

    return tensor

def evaluate_board(board):
    if board.is_checkmate():
        return -99999 if board.turn else 99999

    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0

    for piece_type in piece_values:
        score += len(board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
        score -= len(board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]

    board_tensor = board_to_tensor(board)

    with torch.no_grad():
        ai_score = model(board_tensor).item()

    return score + ai_score

def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if maximizing_player:
        max_eval = -math.inf

        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()

            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)

            if beta <= alpha:
                break

        return max_eval

    else:
        min_eval = math.inf

        for move in board.legal_moves:
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()

            min_eval = min(min_eval, eval)
            beta = min(beta, eval)

            if beta <= alpha:
                break

        return min_eval

def find_best_move(board, depth):
    best_move = None
    best_value = -math.inf

    for move in board.legal_moves:
        board.push(move)
        board_value = minimax(board, depth - 1, -math.inf, math.inf, False)
        board.pop()

        if board_value > best_value:
            best_value = board_value
            best_move = move

    return best_move

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/set_difficulty", methods=["POST"])
def set_difficulty():
    global current_difficulty

    data = request.json
    current_difficulty = data.get("difficulty", "medium")

    return jsonify({"message": "Difficulty updated"})

@app.route("/move", methods=["POST"])
def make_move():
    global board

    data = request.json
    user_move = data["move"]

    try:
        move = chess.Move.from_uci(user_move)

        if move not in board.legal_moves:
            return jsonify({"error": "Illegal move"})

        board.push(move)

        if board.is_game_over():
            return jsonify({
                "status": "game_over",
                "result": board.result()
            })

        depth = difficulty_levels[current_difficulty]

        ai_move = find_best_move(board, depth)

        board.push(ai_move)

        return jsonify({
            "ai_move": str(ai_move),
            "fen": board.fen()
        })

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/reset")
def reset():
    global board
    board = chess.Board()

    return jsonify({"message": "Board reset"})

if __name__ == "__main__":
    app.run(debug=True, port=5002)
