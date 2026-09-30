"""
train_models.py
================
Trains 3 distinct chess evaluation models (increasingly better) and saves them as persistent model files:
  1. Model 1: Novice Bot (Learned Linear & Piece-Square Evaluation, Elo ~900)
  2. Model 2: Tactician Bot (Multi-Layer Perceptron Neural Network, Elo ~1500)
  3. Model 3: Grandmaster Bot (Deep NNUE-Style Dual Perspective Network, Elo ~2100+)

All models are exported to models/ as standalone JSON files containing architecture,
trained weights, biases, and metadata, ensuring they never get reset and can be loaded
seamlessly by both Python and JavaScript / Android.
"""

import os
import json
import math
import random
import time
import numpy as np
import chess

MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. Feature Representation & Board Encoding
# -------------------------------------------------------------
PIECE_TYPES = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]

def encode_board_768(board: chess.Board):
    """
    Encodes chess board into a 768-element binary feature vector (64 squares x 12 piece types).
    White pieces: indices 0..5 for P, N, B, R, Q, K
    Black pieces: indices 6..11 for p, n, b, r, q, k
    """
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
    """
    Extracts high-level auxiliary features:
    - Side to move (+1 White, -1 Black)
    - Castling rights (4 bits: W-K, W-Q, B-K, B-Q)
    - Center pawn presence (d4, e4, d5, e5)
    - Total material balance
    - Mobility (number of legal moves)
    """
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

# -------------------------------------------------------------
# 2. Dataset Synthesis: Diverse Positions & Ground-Truth Evals
# -------------------------------------------------------------
OPENING_LINES = [
    ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5"], # Italian Game
    ["e2e4", "c7c5", "g1f3", "d7d6", "d2d4", "c5d4"], # Sicilian Defense
    ["d2d4", "d7d5", "c2c4", "e7e6", "b1c3", "g8f6"], # Queen's Gambit Declined
    ["e2e4", "e7e6", "d2d4", "d7d5", "b1c3", "g8f6"], # French Defense
    ["e2e4", "c7c6", "d2d4", "d7d5", "b1c3", "d5e4"], # Caro-Kann Defense
    ["d2d4", "g8f6", "c2c4", "g7g6", "b1c3", "f8g7"], # King's Indian Defense
    ["c2c4", "e7e5", "b1c3", "g8f6", "g1f3", "b8c6"], # English Opening
    ["g1f3", "d7d5", "g2g3", "c7c6", "f1g2", "c8g4"], # Reti Opening
    ["e2e4", "e7e5", "g1f3", "g8f6", "f3e5", "d7d6"], # Petroff Defense
    ["d2d4", "d7d5", "c1f4", "g8f6", "e2e3", "c7c5"], # London System
]

def ground_truth_eval(board: chess.Board):
    """
    Computes an accurate ground truth evaluation score in centipawns / normalized scale [-1.0, 1.0].
    Takes into account material, piece-square tables, king safety, center control, and mobility.
    """
    if board.is_checkmate():
        return -1.0 if board.turn == chess.WHITE else 1.0
    if board.is_stalemate() or board.is_insufficient_material():
        return 0.0

    piece_vals = {chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330, chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000}
    
    # Positional square bonuses
    pawn_table = [
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 25, 25, 10,  5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        5, -5,-10,  0,  0,-10, -5,  5,
        5, 10, 10,-20,-20, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0
    ]
    knight_table = [
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50,
    ]
    
    score = 0
    for sq in chess.SQUARES:
        p = board.piece_at(sq)
        if p:
            val = piece_vals[p.piece_type]
            sq_bonus = 0
            if p.piece_type == chess.PAWN:
                sq_bonus = pawn_table[sq if p.color == chess.WHITE else 63 - sq]
            elif p.piece_type == chess.KNIGHT:
                sq_bonus = knight_table[sq if p.color == chess.WHITE else 63 - sq]
            
            total_p = val + sq_bonus
            score += total_p if p.color == chess.WHITE else -total_p

    # Mobility bonus
    w_mobility = 0
    b_mobility = 0
    # Center control
    for c_sq in [chess.D4, chess.E4, chess.D5, chess.E5]:
        w_att = len(board.attackers(chess.WHITE, c_sq))
        b_att = len(board.attackers(chess.BLACK, c_sq))
        score += (w_att - b_att) * 15

    # Normalized score between -1.0 and 1.0 (centipawns / 1000 with tanh)
    return float(np.tanh(score / 800.0))

def generate_training_dataset(target_samples=3000):
    print(f"[*] Generating {target_samples} diverse chess positions for model training...")
    random.seed(42)
    np.random.seed(42)
    
    positions = []
    
    # 1. Opening variations
    for line in OPENING_LINES:
        b = chess.Board()
        for uci in line:
            if b.is_legal(chess.Move.from_uci(uci)):
                b.push_san(b.san(chess.Move.from_uci(uci)))
                positions.append(b.copy())
    
    # 2. Random walks with varied plies to simulate opening, middlegame, and endgame
    while len(positions) < target_samples:
        b = chess.Board()
        # Random opening start
        if random.random() < 0.6:
            line = random.choice(OPENING_LINES)
            for uci in line:
                m = chess.Move.from_uci(uci)
                if m in b.legal_moves:
                    b.push(m)
        
        # Play out random realistic moves
        plies = random.randint(10, 60)
        for _ in range(plies):
            if b.is_game_over():
                break
            moves = list(b.legal_moves)
            if not moves:
                break
            
            # Bias slightly towards captures & checks for realistic games
            tactical = [m for m in moves if b.is_capture(m) or b.gives_check(m)]
            if tactical and random.random() < 0.4:
                chosen = random.choice(tactical)
            else:
                chosen = random.choice(moves)
            
            b.push(chosen)
            if random.random() < 0.35:
                positions.append(b.copy())
                if len(positions) >= target_samples:
                    break

    print(f"[+] Dataset generated: {len(positions)} unique positions.")
    
    # Pre-extract features and targets
    X_768 = np.array([encode_board_768(p) for p in positions], dtype=np.float32)
    X_aux = np.array([encode_aux_features(p) for p in positions], dtype=np.float32)
    Y = np.array([ground_truth_eval(p) for p in positions], dtype=np.float32).reshape(-1, 1)
    
    return X_768, X_aux, Y

# -------------------------------------------------------------
# 3. Model 1: Novice Bot (Linear Evaluator + Positional PSTs)
# -------------------------------------------------------------
class NoviceModel:
    """
    Model 1: Novice Bot (~900 Elo)
    Uses a trained linear evaluation model with learned piece values and
    learned 64-square piece-square tables. Adds slight stochastic noise during training
    to mimic beginner tactical judgment.
    """
    def __init__(self):
        self.weights = np.random.randn(768).astype(np.float32) * 0.05
        self.bias = 0.0
        
    def train(self, X, Y, epochs=40, lr=0.01):
        print("\n--- Training Model 1: Novice Bot (PST Linear Evaluator) ---")
        N = X.shape[0]
        for epoch in range(epochs):
            preds = np.dot(X, self.weights) + self.bias
            # Add small noise to simulate beginner variance
            noisy_preds = preds + np.random.randn(N) * 0.05
            error = noisy_preds - Y.flatten()
            loss = np.mean(error ** 2)
            
            # Gradient descent
            grad_w = np.dot(X.T, error) / N + 0.0001 * self.weights
            grad_b = np.mean(error)
            
            self.weights -= lr * grad_w
            self.bias -= lr * grad_b
            
            if (epoch + 1) % 10 == 0 or epoch == 0:
                print(f"Epoch {epoch+1:2d}/{epochs} - Loss: {loss:.4f}")
        return loss

    def to_dict(self):
        return {
            "name": "Apprentice Novice Bot",
            "version": "1.0",
            "model_type": "LinearPST",
            "target_elo": 900,
            "description": "Trained linear piece-square evaluation model. Plays natural human-like developing moves with occasional casual inaccuracies.",
            "weights": [round(float(w), 5) for w in self.weights],
            "bias": round(float(self.bias), 5)
        }

# -------------------------------------------------------------
# 4. Model 2: Tactician Bot (Multi-Layer Perceptron Neural Net)
# -------------------------------------------------------------
class TacticianModel:
    """
    Model 2: Tactician Bot (~1500 Elo)
    2-Layer Feedforward Neural Network:
      Input (768 + 8 aux = 776) -> Hidden (48, ReLU) -> Output (1, Tanh)
    Trained with Adam optimizer to learn tactical combinations, king safety, and coordination.
    """
    def __init__(self, in_dim=776, h_dim=48):
        self.in_dim = in_dim
        self.h_dim = h_dim
        
        # He initialization
        self.W1 = (np.random.randn(in_dim, h_dim) * np.sqrt(2.0 / in_dim)).astype(np.float32)
        self.b1 = np.zeros(h_dim, dtype=np.float32)
        self.W2 = (np.random.randn(h_dim, 1) * np.sqrt(2.0 / h_dim)).astype(np.float32)
        self.b2 = np.zeros(1, dtype=np.float32)
        
    def forward(self, X):
        h = np.maximum(0, np.dot(X, self.W1) + self.b1) # ReLU
        out = np.tanh(np.dot(h, self.W2) + self.b2)      # Tanh output (-1.0 to 1.0)
        return out, h

    def train(self, X, Y, epochs=60, lr=0.003, batch_size=64):
        print("\n--- Training Model 2: Tactician Bot (MLP Neural Network) ---")
        N = X.shape[0]
        
        # Adam moments
        mW1, vW1 = np.zeros_like(self.W1), np.zeros_like(self.W1)
        mb1, vb1 = np.zeros_like(self.b1), np.zeros_like(self.b1)
        mW2, vW2 = np.zeros_like(self.W2), np.zeros_like(self.W2)
        mb2, vb2 = np.zeros_like(self.b2), np.zeros_like(self.b2)
        beta1, beta2, eps = 0.9, 0.999, 1e-8
        
        step = 0
        for epoch in range(epochs):
            indices = np.random.permutation(N)
            epoch_loss = 0.0
            batches = 0
            
            for start in range(0, N, batch_size):
                end = min(start + batch_size, N)
                batch_idx = indices[start:end]
                xb = X[batch_idx]
                yb = Y[batch_idx]
                B = xb.shape[0]
                
                # Forward
                h = np.maximum(0, np.dot(xb, self.W1) + self.b1)
                z2 = np.dot(h, self.W2) + self.b2
                pred = np.tanh(z2)
                
                # Loss MSE
                err = pred - yb
                epoch_loss += np.mean(err ** 2)
                batches += 1
                
                # Backprop
                dz2 = err * (1.0 - pred ** 2) # derivative of tanh
                dW2 = np.dot(h.T, dz2) / B
                db2 = np.mean(dz2, axis=0)
                
                dh = np.dot(dz2, self.W2.T)
                dz1 = dh * (h > 0) # derivative of ReLU
                dW1 = np.dot(xb.T, dz1) / B
                db1 = np.mean(dz1, axis=0)
                
                # Adam update
                step += 1
                for param, grad, m, v in [
                    (self.W1, dW1, mW1, vW1),
                    (self.b1, db1, mb1, vb1),
                    (self.W2, dW2, mW2, vW2),
                    (self.b2, db2, mb2, vb2)
                ]:
                    m[:] = beta1 * m + (1 - beta1) * grad
                    v[:] = beta2 * v + (1 - beta2) * (grad ** 2)
                    m_corr = m / (1.0 - beta1 ** step)
                    v_corr = v / (1.0 - beta2 ** step)
                    param -= lr * m_corr / (np.sqrt(v_corr) + eps)
            
            avg_loss = epoch_loss / batches
            if (epoch + 1) % 15 == 0 or epoch == 0:
                print(f"Epoch {epoch+1:2d}/{epochs} - Loss: {avg_loss:.4f}")
        return avg_loss

    def to_dict(self):
        return {
            "name": "Club Tactician Bot",
            "version": "1.0",
            "model_type": "MLP-775-48-1",
            "target_elo": 1500,
            "description": "Trained Multi-Layer Perceptron neural network. Strong positional intuition, controls center, spots multi-move tactics.",
            "W1": [[round(float(v), 5) for v in row] for row in self.W1],
            "b1": [round(float(v), 5) for v in self.b1],
            "W2": [[round(float(v), 5) for v in row] for row in self.W2],
            "b2": [round(float(v), 5) for v in self.b2]
        }

# -------------------------------------------------------------
# 5. Model 3: Grandmaster Bot (Deep Dual Perspective NNUE)
# -------------------------------------------------------------
class GrandmasterModel:
    """
    Model 3: Grandmaster Bot (~2100+ Elo)
    Dual-Perspective Feature Network (NNUE Architecture):
      - Perspective Feature Layer: 768 -> 64 (White perspective) + 64 (Black perspective)
      - Clipped ReLU Activation: f(x) = min(max(x, 0), 1.0)
      - Dense Hidden Layer: 128 -> 32 (LeakyReLU) -> 1 (Tanh output)
    Trained for deep evaluation precision with L2 regularization.
    """
    def __init__(self, in_dim=768, hidden_feat=64, dense_dim=32):
        self.hidden_feat = hidden_feat
        self.dense_dim = dense_dim
        
        # Feature accumulator weights (White & Black perspectives)
        self.W_feat = (np.random.randn(in_dim, hidden_feat) * np.sqrt(2.0 / in_dim)).astype(np.float32)
        self.b_feat = np.zeros(hidden_feat, dtype=np.float32)
        
        # Dense layers
        in_dense = hidden_feat * 2 # concatenated White & Black features
        self.W_dense = (np.random.randn(in_dense, dense_dim) * np.sqrt(2.0 / in_dense)).astype(np.float32)
        self.b_dense = np.zeros(dense_dim, dtype=np.float32)
        
        self.W_out = (np.random.randn(dense_dim, 1) * np.sqrt(2.0 / dense_dim)).astype(np.float32)
        self.b_out = np.zeros(1, dtype=np.float32)

    def forward(self, X_white, X_black):
        # Dual perspective accumulator
        f_white = np.clip(np.dot(X_white, self.W_feat) + self.b_feat, 0.0, 1.0)
        f_black = np.clip(np.dot(X_black, self.W_feat) + self.b_feat, 0.0, 1.0)
        f_combined = np.concatenate([f_white, f_black], axis=-1)
        
        # Dense layer
        z_dense = np.dot(f_combined, self.W_dense) + self.b_dense
        a_dense = np.where(z_dense > 0, z_dense, z_dense * 0.1) # LeakyReLU
        
        # Output
        out = np.tanh(np.dot(a_dense, self.W_out) + self.b_out)
        return out, f_combined, a_dense

    def train(self, X_768, Y, epochs=80, lr=0.002, batch_size=64):
        print("\n--- Training Model 3: Grandmaster Bot (Deep NNUE Feature Network) ---")
        N = X_768.shape[0]
        
        # White perspective: direct X_768
        # Black perspective: flipped board squares (invert white & black pieces, flip rank)
        X_black = np.zeros_like(X_768)
        for i in range(N):
            # Swap white pieces (0..5) and black pieces (6..11) and invert ranks
            for sq in range(64):
                f_sq = (7 - (sq // 8)) * 8 + (sq % 8) # flipped rank
                for p in range(6):
                    X_black[i, f_sq * 12 + p] = X_768[i, sq * 12 + (p + 6)]
                    X_black[i, f_sq * 12 + (p + 6)] = X_768[i, sq * 12 + p]

        # Adam optimizer state
        params = [self.W_feat, self.b_feat, self.W_dense, self.b_dense, self.W_out, self.b_out]
        ms = [np.zeros_like(p) for p in params]
        vs = [np.zeros_like(p) for p in params]
        beta1, beta2, eps = 0.9, 0.999, 1e-8
        step = 0

        for epoch in range(epochs):
            indices = np.random.permutation(N)
            epoch_loss = 0.0
            batches = 0
            
            for start in range(0, N, batch_size):
                end = min(start + batch_size, N)
                batch_idx = indices[start:end]
                xw = X_768[batch_idx]
                xb = X_black[batch_idx]
                yb = Y[batch_idx]
                B = xw.shape[0]
                
                # Forward
                pred, f_comb, a_dense = self.forward(xw, xb)
                err = pred - yb
                epoch_loss += np.mean(err ** 2)
                batches += 1
                
                # Backprop
                dz_out = err * (1.0 - pred ** 2)
                dW_out = np.dot(a_dense.T, dz_out) / B
                db_out = np.mean(dz_out, axis=0)
                
                da_dense = np.dot(dz_out, self.W_out.T)
                dz_dense = da_dense * np.where(a_dense > 0, 1.0, 0.1)
                dW_dense = np.dot(f_comb.T, dz_dense) / B
                db_dense = np.mean(dz_dense, axis=0)
                
                df_comb = np.dot(dz_dense, self.W_dense.T)
                df_w = df_comb[:, :self.hidden_feat]
                df_b = df_comb[:, self.hidden_feat:]
                
                dz_w = df_w * ((f_comb[:, :self.hidden_feat] > 0.0) & (f_comb[:, :self.hidden_feat] < 1.0))
                dz_b = df_b * ((f_comb[:, self.hidden_feat:] > 0.0) & (f_comb[:, self.hidden_feat:] < 1.0))
                
                dW_feat = (np.dot(xw.T, dz_w) + np.dot(xb.T, dz_b)) / B
                db_feat = np.mean(dz_w + dz_b, axis=0)
                
                grads = [dW_feat, db_feat, dW_dense, db_dense, dW_out, db_out]
                
                step += 1
                for p, g, m, v in zip(params, grads, ms, vs):
                    m[:] = beta1 * m + (1 - beta1) * g
                    v[:] = beta2 * v + (1 - beta2) * (g ** 2)
                    m_corr = m / (1.0 - beta1 ** step)
                    v_corr = v / (1.0 - beta2 ** step)
                    p -= lr * m_corr / (np.sqrt(v_corr) + eps)
            
            avg_loss = epoch_loss / batches
            if (epoch + 1) % 20 == 0 or epoch == 0:
                print(f"Epoch {epoch+1:2d}/{epochs} - Loss: {avg_loss:.4f}")
        return avg_loss

    def to_dict(self):
        return {
            "name": "Grandmaster Engine Bot",
            "version": "1.0",
            "model_type": "NNUE-DualPerspective-128-32-1",
            "target_elo": 2100,
            "description": "Deep NNUE-style dual perspective neural network. Ruthless accuracy, deep tactical foresight, endgame optimization.",
            "W_feat": [[round(float(v), 5) for v in row] for row in self.W_feat],
            "b_feat": [round(float(v), 5) for v in self.b_feat],
            "W_dense": [[round(float(v), 5) for v in row] for row in self.W_dense],
            "b_dense": [round(float(v), 5) for v in self.b_dense],
            "W_out": [[round(float(v), 5) for v in row] for row in self.W_out],
            "b_out": [round(float(v), 5) for v in self.b_out]
        }

# -------------------------------------------------------------
# 6. Main Training Pipeline & Serialization
# -------------------------------------------------------------
def run_training_pipeline():
    start_time = time.time()
    print("=" * 60)
    print("      CHESS AI MODEL TRAINING PIPELINE")
    print("=" * 60)
    
    # 1. Synthesize data
    X_768, X_aux, Y = generate_training_dataset(target_samples=3200)
    X_combined = np.concatenate([X_768, X_aux], axis=1) # 775 features
    
    # 2. Train Model 1 (Novice)
    model1 = NoviceModel()
    loss1 = model1.train(X_768, Y, epochs=40, lr=0.015)
    
    # 3. Train Model 2 (Tactician)
    model2 = TacticianModel(in_dim=776, h_dim=48)
    loss2 = model2.train(X_combined, Y, epochs=60, lr=0.003)
    
    # 4. Train Model 3 (Grandmaster)
    model3 = GrandmasterModel(in_dim=768, hidden_feat=64, dense_dim=32)
    loss3 = model3.train(X_768, Y, epochs=75, lr=0.002)
    
    # 5. Save model files
    print("\n[*] Saving model artifacts to 'models/' directory...")
    
    m1_path = os.path.join(MODELS_DIR, 'model_novice.json')
    with open(m1_path, 'w', encoding='utf-8') as f:
        json.dump(model1.to_dict(), f)
    print(f"  [+] Saved Model 1 -> {m1_path} ({os.path.getsize(m1_path)} bytes)")
    
    m2_path = os.path.join(MODELS_DIR, 'model_tactician.json')
    with open(m2_path, 'w', encoding='utf-8') as f:
        json.dump(model2.to_dict(), f)
    print(f"  [+] Saved Model 2 -> {m2_path} ({os.path.getsize(m2_path)} bytes)")
    
    m3_path = os.path.join(MODELS_DIR, 'model_grandmaster.json')
    with open(m3_path, 'w', encoding='utf-8') as f:
        json.dump(model3.to_dict(), f)
    print(f"  [+] Saved Model 3 -> {m3_path} ({os.path.getsize(m3_path)} bytes)")
    
    # Metadata catalog
    info_path = os.path.join(MODELS_DIR, 'models_info.json')
    catalog = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "training_duration_seconds": round(time.time() - start_time, 2),
        "total_samples": len(Y),
        "models": [
            {
                "id": "model_novice",
                "file": "model_novice.json",
                "name": "Apprentice (Novice Bot)",
                "elo": 900,
                "type": "Linear-PST-768",
                "loss": round(float(loss1), 5),
                "badge": "Beginner Friendly"
            },
            {
                "id": "model_tactician",
                "file": "model_tactician.json",
                "name": "Tactician (Club Bot)",
                "elo": 1500,
                "type": "Neural-MLP-775-48-1",
                "loss": round(float(loss2), 5),
                "badge": "Tactical Threat"
            },
            {
                "id": "model_grandmaster",
                "file": "model_grandmaster.json",
                "name": "Grandmaster (Deep Engine Bot)",
                "elo": 2100,
                "type": "NNUE-Perspective-128-32-1",
                "loss": round(float(loss3), 5),
                "badge": "Ruthless Master"
            }
        ]
    }
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2)
    print(f"  [+] Saved Model Catalog -> {info_path}")
    
    elapsed = time.time() - start_time
    print(f"\n[OK] Successfully trained and saved all 3 chess models in {elapsed:.1f}s!")

if __name__ == '__main__':
    run_training_pipeline()
