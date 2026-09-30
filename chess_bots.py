"""
chess_bots.py
==============
Provides inference and move selection using the 3 trained chess models:
  - NoviceBot (loads models/model_novice.json)
  - TacticianBot (loads models/model_tactician.json)
  - GrandmasterBot (loads models/model_grandmaster.json)

These bots can be played against via Python CLI, imported into any Python chess interface,
or served via API.
"""

import os
import json
import math
import random
import numpy as np
import chess

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')

PIECE_TYPES = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]

def encode_board_768(board: chess.Board):
    vec = np.zeros(768, dtype=np.float32)
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            p_idx = PIECE_TYPES.index(piece.piece_type)
            if piece.color == chess.BLACK:
                p_idx += 6
            vec[sq * 12 + p_idx] = 1.0
    return vec

def encode_aux_features(board: chess.Board):
    side = 1.0 if board.turn == chess.WHITE else -1.0
    castling = [
        1.0 if board.has_kingside_castling_rights(chess.WHITE) else 0.0,
        1.0 if board.has_queenside_castling_rights(chess.WHITE) else 0.0,
        1.0 if board.has_kingside_castling_rights(chess.BLACK) else 0.0,
        1.0 if board.has_queenside_castling_rights(chess.BLACK) else 0.0,
    ]
    center_sqs = [chess.D4, chess.E4, chess.D5, chess.E5]
    center_ctrl = sum(1.0 if board.piece_at(sq) is not None else 0.0 for sq in center_sqs) / 4.0
    
    mat = 0.0
    val_map = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
    for sq in chess.SQUARES:
        p = board.piece_at(sq)
        if p:
            v = val_map[p.piece_type]
            mat += v if p.color == chess.WHITE else -v
    mat_norm = np.tanh(mat / 10.0)
    mobility = len(list(board.legal_moves)) / 40.0
    return np.array([side] + castling + [center_ctrl, mat_norm, mobility], dtype=np.float32)

class TrainedNoviceBot:
    """
    Bot 1: Novice / Apprentice (~900 Elo)
    Loaded from models/model_novice.json
    Searches depth 2 with learned piece-square evaluation.
    """
    def __init__(self, model_file=None):
        if model_file is None:
            model_file = os.path.join(MODELS_DIR, 'model_novice.json')
        with open(model_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.name = data.get("name", "Apprentice Novice Bot")
        self.elo = data.get("target_elo", 900)
        self.weights = np.array(data["weights"], dtype=np.float32)
        self.bias = float(data["bias"])

    def evaluate(self, board: chess.Board):
        if board.is_checkmate():
            return -1000.0 if board.turn == chess.WHITE else 1000.0
        if board.is_stalemate() or board.is_insufficient_material():
            return 0.0
        x = encode_board_768(board)
        return float(np.dot(x, self.weights) + self.bias)

    def select_move(self, board: chess.Board, depth=2):
        moves = list(board.legal_moves)
        if not moves:
            return None
        # Add slight randomness for beginner variety
        random.shuffle(moves)
        
        is_white = (board.turn == chess.WHITE)
        best_val = -float('inf') if is_white else float('inf')
        best_move = moves[0]

        for m in moves:
            board.push(m)
            val = self._minimax(board, depth - 1, not is_white)
            board.pop()

            if is_white:
                if val > best_val:
                    best_val = val
                    best_move = m
            else:
                if val < best_val:
                    best_val = val
                    best_move = m

        return best_move

    def _minimax(self, board: chess.Board, depth: int, is_white: bool):
        if depth == 0 or board.is_game_over():
            return self.evaluate(board)
        moves = list(board.legal_moves)
        if not moves:
            return self.evaluate(board)

        if is_white:
            max_v = -float('inf')
            for m in moves:
                board.push(m)
                v = self._minimax(board, depth - 1, False)
                board.pop()
                max_v = max(max_v, v)
            return max_v
        else:
            min_v = float('inf')
            for m in moves:
                board.push(m)
                v = self._minimax(board, depth - 1, True)
                board.pop()
                min_v = min(min_v, v)
            return min_v


class TrainedTacticianBot:
    """
    Bot 2: Club Tactician (~1500 Elo)
    Loaded from models/model_tactician.json
    Evaluates positions using the trained 2-layer MLP neural network.
    Alpha-beta pruning depth 3.
    """
    def __init__(self, model_file=None):
        if model_file is None:
            model_file = os.path.join(MODELS_DIR, 'model_tactician.json')
        with open(model_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.name = data.get("name", "Club Tactician Bot")
        self.elo = data.get("target_elo", 1500)
        self.W1 = np.array(data["W1"], dtype=np.float32)
        self.b1 = np.array(data["b1"], dtype=np.float32)
        self.W2 = np.array(data["W2"], dtype=np.float32)
        self.b2 = np.array(data["b2"], dtype=np.float32)

    def evaluate(self, board: chess.Board):
        if board.is_checkmate():
            return -10.0 if board.turn == chess.WHITE else 10.0
        if board.is_stalemate() or board.is_insufficient_material():
            return 0.0
        x_768 = encode_board_768(board)
        x_aux = encode_aux_features(board)
        x = np.concatenate([x_768, x_aux])
        
        # Neural forward pass
        h = np.maximum(0, np.dot(x, self.W1) + self.b1)
        val = np.tanh(np.dot(h, self.W2) + self.b2)
        return float(val[0])

    def select_move(self, board: chess.Board, depth=3):
        moves = list(board.legal_moves)
        if not moves:
            return None
        
        # Move ordering: prioritize captures and checks
        moves.sort(key=lambda m: (board.is_capture(m), board.gives_check(m)), reverse=True)
        
        is_white = (board.turn == chess.WHITE)
        alpha = -float('inf')
        beta = float('inf')
        best_val = -float('inf') if is_white else float('inf')
        best_move = moves[0]

        for m in moves:
            board.push(m)
            val = self._alphabeta(board, depth - 1, alpha, beta, not is_white)
            board.pop()

            if is_white:
                if val > best_val:
                    best_val = val
                    best_move = m
                alpha = max(alpha, val)
            else:
                if val < best_val:
                    best_val = val
                    best_move = m
                beta = min(beta, val)

            if beta <= alpha:
                break

        return best_move

    def _alphabeta(self, board: chess.Board, depth: int, alpha: float, beta: float, is_white: bool):
        if depth == 0 or board.is_game_over():
            return self.evaluate(board)
        moves = list(board.legal_moves)
        if not moves:
            return self.evaluate(board)

        # Move ordering
        moves.sort(key=lambda m: (board.is_capture(m), board.gives_check(m)), reverse=True)

        if is_white:
            max_v = -float('inf')
            for m in moves:
                board.push(m)
                v = self._alphabeta(board, depth - 1, alpha, beta, False)
                board.pop()
                max_v = max(max_v, v)
                alpha = max(alpha, v)
                if beta <= alpha:
                    break
            return max_v
        else:
            min_v = float('inf')
            for m in moves:
                board.push(m)
                v = self._alphabeta(board, depth - 1, alpha, beta, True)
                board.pop()
                min_v = min(min_v, v)
                beta = min(beta, v)
                if beta <= alpha:
                    break
            return min_v


class TrainedGrandmasterBot:
    """
    Bot 3: Grandmaster Engine (~2100+ Elo)
    Loaded from models/model_grandmaster.json
    Deep NNUE-style dual perspective neural network evaluation + Quiescence capture search.
    """
    def __init__(self, model_file=None):
        if model_file is None:
            model_file = os.path.join(MODELS_DIR, 'model_grandmaster.json')
        with open(model_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.name = data.get("name", "Grandmaster Engine Bot")
        self.elo = data.get("target_elo", 2100)
        self.W_feat = np.array(data["W_feat"], dtype=np.float32)
        self.b_feat = np.array(data["b_feat"], dtype=np.float32)
        self.W_dense = np.array(data["W_dense"], dtype=np.float32)
        self.b_dense = np.array(data["b_dense"], dtype=np.float32)
        self.W_out = np.array(data["W_out"], dtype=np.float32)
        self.b_out = np.array(data["b_out"], dtype=np.float32)

    def evaluate(self, board: chess.Board):
        if board.is_checkmate():
            return -10.0 if board.turn == chess.WHITE else 10.0
        if board.is_stalemate() or board.is_insufficient_material():
            return 0.0

        xw = encode_board_768(board)
        # Flip rank for black perspective
        xb = np.zeros_like(xw)
        for sq in range(64):
            f_sq = (7 - (sq // 8)) * 8 + (sq % 8)
            for p in range(6):
                xb[f_sq * 12 + p] = xw[sq * 12 + (p + 6)]
                xb[f_sq * 12 + (p + 6)] = xw[sq * 12 + p]

        # Dual perspective accumulator
        fw = np.clip(np.dot(xw, self.W_feat) + self.b_feat, 0.0, 1.0)
        fb = np.clip(np.dot(xb, self.W_feat) + self.b_feat, 0.0, 1.0)
        f_comb = np.concatenate([fw, fb])
        
        # Dense combination
        zd = np.dot(f_comb, self.W_dense) + self.b_dense
        ad = np.where(zd > 0, zd, zd * 0.1) # LeakyReLU
        
        # Output neuron
        out = np.tanh(np.dot(ad, self.W_out) + self.b_out)
        return float(out[0])

    def select_move(self, board: chess.Board, depth=3):
        moves = list(board.legal_moves)
        if not moves:
            return None
        
        # MVV-LVA move ordering (Most Valuable Victim - Least Valuable Attacker)
        piece_vals = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 100}
        def move_score(m):
            score = 0
            if board.is_capture(m):
                victim = board.piece_at(m.to_square)
                aggressor = board.piece_at(m.from_square)
                vic_val = piece_vals.get(victim.piece_type, 1) if victim else 1
                agg_val = piece_vals.get(aggressor.piece_type, 1) if aggressor else 1
                score += 1000 + (vic_val * 10 - agg_val)
            if board.gives_check(m):
                score += 500
            return score

        moves.sort(key=move_score, reverse=True)
        
        is_white = (board.turn == chess.WHITE)
        alpha = -float('inf')
        beta = float('inf')
        best_val = -float('inf') if is_white else float('inf')
        best_move = moves[0]

        for m in moves:
            board.push(m)
            val = self._alphabeta(board, depth - 1, alpha, beta, not is_white)
            board.pop()

            if is_white:
                if val > best_val:
                    best_val = val
                    best_move = m
                alpha = max(alpha, val)
            else:
                if val < best_val:
                    best_val = val
                    best_move = m
                beta = min(beta, val)

            if beta <= alpha:
                break

        return best_move

    def _alphabeta(self, board: chess.Board, depth: int, alpha: float, beta: float, is_white: bool):
        if depth == 0:
            return self._quiescence(board, alpha, beta, is_white, q_depth=2)
        if board.is_game_over():
            return self.evaluate(board)

        moves = list(board.legal_moves)
        if not moves:
            return self.evaluate(board)

        # Move ordering
        moves.sort(key=lambda m: (board.is_capture(m), board.gives_check(m)), reverse=True)

        if is_white:
            max_v = -float('inf')
            for m in moves:
                board.push(m)
                v = self._alphabeta(board, depth - 1, alpha, beta, False)
                board.pop()
                max_v = max(max_v, v)
                alpha = max(alpha, v)
                if beta <= alpha:
                    break
            return max_v
        else:
            min_v = float('inf')
            for m in moves:
                board.push(m)
                v = self._alphabeta(board, depth - 1, alpha, beta, True)
                board.pop()
                min_v = min(min_v, v)
                beta = min(beta, v)
                if beta <= alpha:
                    break
            return min_v

    def _quiescence(self, board: chess.Board, alpha: float, beta: float, is_white: bool, q_depth: int):
        stand_pat = self.evaluate(board)
        if q_depth == 0 or board.is_game_over():
            return stand_pat

        if is_white:
            if stand_pat >= beta:
                return beta
            alpha = max(alpha, stand_pat)
            capture_moves = [m for m in board.legal_moves if board.is_capture(m)]
            for m in capture_moves:
                board.push(m)
                score = self._quiescence(board, alpha, beta, False, q_depth - 1)
                board.pop()
                if score >= beta:
                    return beta
                alpha = max(alpha, score)
            return alpha
        else:
            if stand_pat <= alpha:
                return alpha
            beta = min(beta, stand_pat)
            capture_moves = [m for m in board.legal_moves if board.is_capture(m)]
            for m in capture_moves:
                board.push(m)
                score = self._quiescence(board, alpha, beta, True, q_depth - 1)
                board.pop()
                if score <= alpha:
                    return alpha
                beta = min(beta, score)
            return beta

def get_bot(bot_id: str):
    """
    Factory function to retrieve bot instance by ID:
      - 'novice' or '1'
      - 'tactician' or '2'
      - 'grandmaster' or '3'
    """
    if bot_id in ['novice', '1', 'easy']:
        return TrainedNoviceBot()
    elif bot_id in ['tactician', '2', 'medium']:
        return TrainedTacticianBot()
    elif bot_id in ['grandmaster', '3', 'hard']:
        return TrainedGrandmasterBot()
    else:
        raise ValueError(f"Unknown bot ID: {bot_id}")

if __name__ == '__main__':
    print("[*] Testing all 3 trained chess bots...")
    b = chess.Board()
    print("Starting Board FEN:", b.fen())
    
    bot1 = get_bot('novice')
    m1 = bot1.select_move(b, depth=2)
    print(f"Bot 1 ({bot1.name} ~{bot1.elo} Elo) chooses: {b.san(m1)}")
    
    bot2 = get_bot('tactician')
    m2 = bot2.select_move(b, depth=3)
    print(f"Bot 2 ({bot2.name} ~{bot2.elo} Elo) chooses: {b.san(m2)}")
    
    bot3 = get_bot('grandmaster')
    m3 = bot3.select_move(b, depth=3)
    print(f"Bot 3 ({bot3.name} ~{bot3.elo} Elo) chooses: {b.san(m3)}")
    print("[+] All 3 bots successfully loaded from persistent JSON files and executed move inference!")
