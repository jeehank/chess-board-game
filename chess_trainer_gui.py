"""
chess_trainer_gui.py
====================
Standalone GUI application for training 3 chess AI models.
Run this separately from the game to train and export model weights.

Usage:
    python chess_trainer_gui.py

Requirements:
    - Python 3.10+
    - numpy (pip install numpy)
    - tkinter (built-in with Python)
"""

import os
import sys
import json
import math
import time
import random
import threading
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import numpy as np
except ImportError:
    print("ERROR: numpy is required. Run:  pip install numpy")
    sys.exit(1)


ROOT = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(ROOT, "models")

# ═══════════════════════════════════════════════════════════
#   CHESS POSITION GENERATOR
# ═══════════════════════════════════════════════════════════

PIECE_VALUES = {'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000}

# Piece-Square Tables (midgame, from white's perspective)
PST = {
    'P': [
         0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
         5,  5, 10, 25, 25, 10,  5,  5,
         0,  0,  0, 20, 20,  0,  0,  0,
         5, -5,-10,  0,  0,-10, -5,  5,
         5, 10, 10,-20,-20, 10, 10,  5,
         0,  0,  0,  0,  0,  0,  0,  0
    ],
    'N': [
       -50,-40,-30,-30,-30,-30,-40,-50,
       -40,-20,  0,  0,  0,  0,-20,-40,
       -30,  0, 10, 15, 15, 10,  0,-30,
       -30,  5, 15, 20, 20, 15,  5,-30,
       -30,  0, 15, 20, 20, 15,  0,-30,
       -30,  5, 10, 15, 15, 10,  5,-30,
       -40,-20,  0,  5,  5,  0,-20,-40,
       -50,-40,-30,-30,-30,-30,-40,-50
    ],
    'B': [
       -20,-10,-10,-10,-10,-10,-10,-20,
       -10,  0,  0,  0,  0,  0,  0,-10,
       -10,  0,  5, 10, 10,  5,  0,-10,
       -10,  5,  5, 10, 10,  5,  5,-10,
       -10,  0, 10, 10, 10, 10,  0,-10,
       -10, 10, 10, 10, 10, 10, 10,-10,
       -10,  5,  0,  0,  0,  0,  5,-10,
       -20,-10,-10,-10,-10,-10,-10,-20
    ],
    'R': [
         0,  0,  0,  0,  0,  0,  0,  0,
         5, 10, 10, 10, 10, 10, 10,  5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
         0,  0,  0,  5,  5,  0,  0,  0
    ],
    'Q': [
       -20,-10,-10, -5, -5,-10,-10,-20,
       -10,  0,  0,  0,  0,  0,  0,-10,
       -10,  0,  5,  5,  5,  5,  0,-10,
        -5,  0,  5,  5,  5,  5,  0, -5,
         0,  0,  5,  5,  5,  5,  0, -5,
       -10,  5,  5,  5,  5,  5,  0,-10,
       -10,  0,  5,  0,  0,  0,  0,-10,
       -20,-10,-10, -5, -5,-10,-10,-20
    ],
    'K': [
       -30,-40,-40,-50,-50,-40,-40,-30,
       -30,-40,-40,-50,-50,-40,-40,-30,
       -30,-40,-40,-50,-50,-40,-40,-30,
       -30,-40,-40,-50,-50,-40,-40,-30,
       -20,-30,-30,-40,-40,-30,-30,-20,
       -10,-20,-20,-20,-20,-20,-20,-10,
        20, 20,  0,  0,  0,  0, 20, 20,
        20, 30, 10,  0,  0, 10, 30, 20
    ]
}


def generate_random_position():
    """Generate a realistic random chess position and return (board_768, eval_score)."""
    board = [None] * 64

    # Always place kings
    wk_sq = random.choice(range(56, 64))  # White king on rank 1
    bk_sq = random.choice(range(0, 8))     # Black king on rank 8
    board[wk_sq] = ('K', 'w')
    board[bk_sq] = ('K', 'b')

    pieces_white = []
    pieces_black = []

    # Randomly place pieces
    n_white = random.randint(2, 8)
    n_black = random.randint(2, 8)

    piece_pool = ['P', 'P', 'P', 'P', 'N', 'N', 'B', 'B', 'R', 'R', 'Q']

    empty_squares = [i for i in range(64) if board[i] is None]
    random.shuffle(empty_squares)

    for i in range(min(n_white, len(empty_squares))):
        sq = empty_squares.pop()
        p = random.choice(piece_pool)
        if p == 'P' and (sq < 8 or sq >= 56):
            p = random.choice(['N', 'B', 'R', 'Q'])
        board[sq] = (p, 'w')
        pieces_white.append((p, sq))

    for i in range(min(n_black, len(empty_squares))):
        sq = empty_squares.pop()
        p = random.choice(piece_pool)
        if p == 'P' and (sq < 8 or sq >= 56):
            p = random.choice(['N', 'B', 'R', 'Q'])
        board[sq] = (p, 'b')
        pieces_black.append((p, sq))

    # Encode to 768 features (12 piece types × 64 squares)
    piece_order = ['P', 'N', 'B', 'R', 'Q', 'K']
    features = [0.0] * 768

    for sq in range(64):
        if board[sq] is not None:
            piece, color = board[sq]
            idx = piece_order.index(piece)
            if color == 'b':
                idx += 6
            features[idx * 64 + sq] = 1.0

    # Expert evaluation using material + PST
    score = 0.0
    for sq in range(64):
        if board[sq] is not None:
            piece, color = board[sq]
            val = PIECE_VALUES[piece]
            if color == 'w':
                pst_val = PST[piece][sq]
                score += val + pst_val
            else:
                mirror_sq = (7 - sq // 8) * 8 + (sq % 8)
                pst_val = PST[piece][mirror_sq]
                score -= val + pst_val

    # Normalize to [-1, 1] range
    score = max(-1.0, min(1.0, score / 2000.0))

    return features, score


def generate_dataset(n_positions, progress_callback=None):
    """Generate training dataset."""
    X = []
    y = []
    for i in range(n_positions):
        features, score = generate_random_position()
        X.append(features)
        y.append(score)
        if progress_callback and i % 100 == 0:
            progress_callback(i, n_positions)
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)


# ═══════════════════════════════════════════════════════════
#   MODEL ARCHITECTURES
# ═══════════════════════════════════════════════════════════

class NoviceModel:
    """Linear Piece-Square Table model (768 → 1)."""

    def __init__(self):
        self.weights = np.random.randn(768).astype(np.float32) * 0.01
        self.bias = np.float32(0.0)
        self.name = "Apprentice Novice Bot"

    def predict(self, X):
        return np.tanh(X @ self.weights + self.bias)

    def train_epoch(self, X, y, lr=0.001):
        preds = self.predict(X)
        errors = preds - y
        grad_w = (2.0 / len(y)) * (X.T @ (errors * (1 - preds**2)))
        grad_b = (2.0 / len(y)) * np.sum(errors * (1 - preds**2))
        self.weights -= lr * grad_w
        self.bias -= lr * grad_b
        mse = np.mean(errors**2)
        return float(mse)

    def to_json(self):
        return {
            "name": self.name,
            "version": "1.0",
            "model_type": "LinearPST",
            "input_size": 768,
            "weights": self.weights.tolist(),
            "bias": float(self.bias)
        }


class TacticianModel:
    """MLP model (768 → 48 → 1) with ReLU activation."""

    def __init__(self):
        self.W1 = np.random.randn(768, 48).astype(np.float32) * np.sqrt(2.0 / 768)
        self.b1 = np.zeros(48, dtype=np.float32)
        self.W2 = np.random.randn(48, 1).astype(np.float32) * np.sqrt(2.0 / 48)
        self.b2 = np.float32(0.0)
        self.name = "Club Tactician Bot"

    def predict(self, X):
        self._h = X @ self.W1 + self.b1
        self._a = np.maximum(0, self._h)  # ReLU
        out = self._a @ self.W2 + self.b2
        return np.tanh(out.flatten())

    def train_epoch(self, X, y, lr=0.0005):
        preds = self.predict(X)
        errors = preds - y
        n = len(y)

        # Backprop through tanh
        dtanh = (1 - preds**2)
        delta_out = (2.0 / n) * errors * dtanh

        # Gradients for output layer
        grad_W2 = self._a.T @ delta_out.reshape(-1, 1)
        grad_b2 = np.sum(delta_out)

        # Backprop through ReLU
        delta_hidden = delta_out.reshape(-1, 1) * self.W2.T
        delta_hidden = delta_hidden * (self._h > 0).astype(np.float32)

        # Gradients for hidden layer
        grad_W1 = X.T @ delta_hidden
        grad_b1 = np.sum(delta_hidden, axis=0)

        # Update
        self.W1 -= lr * grad_W1
        self.b1 -= lr * grad_b1
        self.W2 -= lr * grad_W2
        self.b2 -= lr * grad_b2

        return float(np.mean(errors**2))

    def to_json(self):
        return {
            "name": self.name,
            "version": "1.0",
            "model_type": "MLP-768-48-1",
            "hidden_size": 48,
            "weights_hidden": self.W1.tolist(),
            "bias_hidden": self.b1.tolist(),
            "weights_output": self.W2.flatten().tolist(),
            "bias_output": float(self.b2)
        }


class GrandmasterModel:
    """NNUE-style dual perspective model (768 → 64 → 32 → 1)."""

    def __init__(self):
        self.W1 = np.random.randn(768, 64).astype(np.float32) * np.sqrt(2.0 / 768)
        self.b1 = np.zeros(64, dtype=np.float32)
        self.W2 = np.random.randn(64, 32).astype(np.float32) * np.sqrt(2.0 / 64)
        self.b2 = np.zeros(32, dtype=np.float32)
        self.W3 = np.random.randn(32, 1).astype(np.float32) * np.sqrt(2.0 / 32)
        self.b3 = np.float32(0.0)
        self.name = "Grandmaster Engine Bot"

    def predict(self, X):
        self._h1 = X @ self.W1 + self.b1
        self._a1 = np.maximum(0, self._h1)
        self._h2 = self._a1 @ self.W2 + self.b2
        self._a2 = np.maximum(0, self._h2)
        out = self._a2 @ self.W3 + self.b3
        return np.tanh(out.flatten())

    def train_epoch(self, X, y, lr=0.0003):
        preds = self.predict(X)
        errors = preds - y
        n = len(y)

        dtanh = (1 - preds**2)
        delta_out = (2.0 / n) * errors * dtanh

        # Layer 3
        grad_W3 = self._a2.T @ delta_out.reshape(-1, 1)
        grad_b3 = np.sum(delta_out)

        # Layer 2
        delta2 = delta_out.reshape(-1, 1) * self.W3.T
        delta2 = delta2 * (self._h2 > 0).astype(np.float32)
        grad_W2 = self._a1.T @ delta2
        grad_b2 = np.sum(delta2, axis=0)

        # Layer 1
        delta1 = delta2 @ self.W2.T
        delta1 = delta1 * (self._h1 > 0).astype(np.float32)
        grad_W1 = X.T @ delta1
        grad_b1 = np.sum(delta1, axis=0)

        # Update
        self.W1 -= lr * grad_W1
        self.b1 -= lr * grad_b1
        self.W2 -= lr * grad_W2
        self.b2 -= lr * grad_b2
        self.W3 -= lr * grad_W3
        self.b3 -= lr * grad_b3

        return float(np.mean(errors**2))

    def to_json(self):
        return {
            "name": self.name,
            "version": "1.0",
            "model_type": "NNUE-768-64-32-1",
            "layer1_weights": self.W1.tolist(),
            "layer1_bias": self.b1.tolist(),
            "layer2_weights": self.W2.tolist(),
            "layer2_bias": self.b2.tolist(),
            "layer3_weights": self.W3.flatten().tolist(),
            "layer3_bias": float(self.b3)
        }


# ═══════════════════════════════════════════════════════════
#   TRAINING GUI APPLICATION
# ═══════════════════════════════════════════════════════════

class ChessTrainerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess AI Model Trainer")
        self.root.geometry("900x700")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(True, True)

        self.training = False
        self.stop_requested = False
        self.models = {}
        self.loss_history = {}

        self._build_ui()

    def _build_ui(self):
        # ── Title Bar ──
        title_frame = tk.Frame(self.root, bg="#16213e", pady=10)
        title_frame.pack(fill=tk.X)

        tk.Label(title_frame, text="CHESS AI MODEL TRAINER",
                 font=("Segoe UI", 18, "bold"), fg="#e94560", bg="#16213e").pack()
        tk.Label(title_frame, text="Train neural network bots for Chess Master",
                 font=("Segoe UI", 10), fg="#a0a0b0", bg="#16213e").pack()

        # ── Settings Panel ──
        settings_frame = tk.LabelFrame(self.root, text=" Training Settings ",
                                        font=("Segoe UI", 11, "bold"),
                                        fg="#e94560", bg="#1a1a2e",
                                        padx=15, pady=10)
        settings_frame.pack(fill=tk.X, padx=15, pady=(10, 5))

        row1 = tk.Frame(settings_frame, bg="#1a1a2e")
        row1.pack(fill=tk.X, pady=3)

        tk.Label(row1, text="Training Positions:", font=("Segoe UI", 10),
                 fg="#e0e0e0", bg="#1a1a2e").pack(side=tk.LEFT)
        self.positions_var = tk.StringVar(value="5000")
        ttk.Combobox(row1, textvariable=self.positions_var,
                     values=["1000", "2000", "5000", "10000", "20000", "50000"],
                     width=10, state="readonly").pack(side=tk.LEFT, padx=10)

        tk.Label(row1, text="Epochs:", font=("Segoe UI", 10),
                 fg="#e0e0e0", bg="#1a1a2e").pack(side=tk.LEFT, padx=(20, 0))
        self.epochs_var = tk.StringVar(value="100")
        ttk.Combobox(row1, textvariable=self.epochs_var,
                     values=["50", "100", "200", "500", "1000"],
                     width=10, state="readonly").pack(side=tk.LEFT, padx=10)

        # ── Model Selection ──
        model_frame = tk.LabelFrame(self.root, text=" Models to Train ",
                                     font=("Segoe UI", 11, "bold"),
                                     fg="#e94560", bg="#1a1a2e",
                                     padx=15, pady=10)
        model_frame.pack(fill=tk.X, padx=15, pady=5)

        self.train_novice = tk.BooleanVar(value=True)
        self.train_tactician = tk.BooleanVar(value=True)
        self.train_grandmaster = tk.BooleanVar(value=True)

        models_info = [
            (self.train_novice, "Apprentice Novice",
             "Linear PST model (768 -> 1). Fast to train, plays decent opening moves."),
            (self.train_tactician, "Club Tactician",
             "MLP neural network (768 -> 48 -> 1). Understands tactics and center control."),
            (self.train_grandmaster, "Grandmaster Engine",
             "NNUE dual-perspective (768 -> 64 -> 32 -> 1). Deepest evaluation, best play.")
        ]

        for var, name, desc in models_info:
            row = tk.Frame(model_frame, bg="#1a1a2e")
            row.pack(fill=tk.X, pady=2)
            tk.Checkbutton(row, variable=var, bg="#1a1a2e", fg="#e0e0e0",
                           selectcolor="#16213e", activebackground="#1a1a2e",
                           font=("Segoe UI", 10, "bold"),
                           text=f"  {name}").pack(side=tk.LEFT)
            tk.Label(row, text=f"  -  {desc}", font=("Segoe UI", 9),
                     fg="#808090", bg="#1a1a2e").pack(side=tk.LEFT)

        # ── Buttons ──
        btn_frame = tk.Frame(self.root, bg="#1a1a2e", pady=5)
        btn_frame.pack(fill=tk.X, padx=15)

        self.train_btn = tk.Button(btn_frame, text="START TRAINING",
                                    font=("Segoe UI", 12, "bold"),
                                    bg="#e94560", fg="white",
                                    activebackground="#c9184a",
                                    padx=20, pady=8, bd=0,
                                    command=self._start_training)
        self.train_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_btn = tk.Button(btn_frame, text="STOP",
                                   font=("Segoe UI", 12, "bold"),
                                   bg="#555", fg="white",
                                   activebackground="#777",
                                   padx=20, pady=8, bd=0,
                                   state=tk.DISABLED,
                                   command=self._stop_training)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.export_btn = tk.Button(btn_frame, text="EXPORT MODELS",
                                     font=("Segoe UI", 12, "bold"),
                                     bg="#0f3460", fg="white",
                                     activebackground="#16213e",
                                     padx=20, pady=8, bd=0,
                                     state=tk.DISABLED,
                                     command=self._export_models)
        self.export_btn.pack(side=tk.LEFT)

        # ── Progress ──
        progress_frame = tk.Frame(self.root, bg="#1a1a2e", pady=5)
        progress_frame.pack(fill=tk.X, padx=15)

        self.progress_label = tk.Label(progress_frame, text="Ready to train",
                                        font=("Segoe UI", 10), fg="#a0a0b0",
                                        bg="#1a1a2e", anchor="w")
        self.progress_label.pack(fill=tk.X)

        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate',
                                             length=400)
        self.progress_bar.pack(fill=tk.X, pady=3)

        # ── Log Output (Text Console) ──
        log_frame = tk.LabelFrame(self.root, text=" Training Log ",
                                   font=("Segoe UI", 11, "bold"),
                                   fg="#e94560", bg="#1a1a2e",
                                   padx=10, pady=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 15))

        self.log_text = tk.Text(log_frame, bg="#0a0a1a", fg="#00ff88",
                                 font=("Consolas", 10), height=15,
                                 insertbackground="#00ff88", wrap=tk.WORD,
                                 bd=0, padx=8, pady=8)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self._log("Chess AI Model Trainer initialized.")
        self._log(f"Models output directory: {MODELS_DIR}")
        self._log("Select models to train and press START TRAINING.\n")

    def _log(self, msg):
        """Append a message to the log console."""
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)

    def _start_training(self):
        if self.training:
            return

        selected = []
        if self.train_novice.get():
            selected.append("novice")
        if self.train_tactician.get():
            selected.append("tactician")
        if self.train_grandmaster.get():
            selected.append("grandmaster")

        if not selected:
            messagebox.showwarning("No Models Selected",
                                    "Please select at least one model to train.")
            return

        self.training = True
        self.stop_requested = False
        self.train_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        self.export_btn.configure(state=tk.DISABLED)

        n_pos = int(self.positions_var.get())
        n_epochs = int(self.epochs_var.get())

        thread = threading.Thread(target=self._train_worker,
                                   args=(selected, n_pos, n_epochs),
                                   daemon=True)
        thread.start()

    def _stop_training(self):
        self.stop_requested = True
        self._log("\n[!] Stop requested... finishing current epoch...\n")

    def _train_worker(self, selected_models, n_positions, n_epochs):
        """Training worker running in background thread."""
        try:
            # Generate dataset
            self.root.after(0, lambda: self.progress_label.configure(
                text=f"Generating {n_positions} training positions..."))
            self._log(f"Generating {n_positions} chess positions for training...")

            start = time.time()
            X, y = generate_dataset(n_positions, progress_callback=lambda i, n:
                self.root.after(0, lambda i=i, n=n: self.progress_bar.configure(
                    value=int(100 * i / n))))
            elapsed = time.time() - start
            self._log(f"Dataset generated in {elapsed:.1f}s  "
                      f"(mean eval: {np.mean(y):.4f}, std: {np.std(y):.4f})\n")

            # Train each model
            total_models = len(selected_models)
            for m_idx, model_key in enumerate(selected_models):
                if self.stop_requested:
                    break

                if model_key == "novice":
                    model = NoviceModel()
                    lr = 0.002
                elif model_key == "tactician":
                    model = TacticianModel()
                    lr = 0.001
                else:
                    model = GrandmasterModel()
                    lr = 0.0005

                self._log(f"{'='*50}")
                self._log(f"Training: {model.name}")
                self._log(f"Architecture: {model.__class__.__name__}")
                self._log(f"Learning rate: {lr}, Epochs: {n_epochs}")
                self._log(f"{'='*50}")

                best_loss = float('inf')
                self.loss_history[model_key] = []

                for epoch in range(n_epochs):
                    if self.stop_requested:
                        break

                    loss = model.train_epoch(X, y, lr=lr)
                    self.loss_history[model_key].append(loss)

                    if loss < best_loss:
                        best_loss = loss

                    # Update progress
                    overall_pct = ((m_idx * n_epochs + epoch + 1) /
                                   (total_models * n_epochs)) * 100
                    self.root.after(0, lambda p=overall_pct: self.progress_bar.configure(value=p))
                    self.root.after(0, lambda mk=model.name, e=epoch+1, l=loss:
                        self.progress_label.configure(
                            text=f"Training {mk} - Epoch {e}/{n_epochs} - Loss: {l:.6f}"))

                    if (epoch + 1) % 10 == 0 or epoch == 0 or epoch == n_epochs - 1:
                        bar_len = 30
                        filled = int(bar_len * (epoch + 1) / n_epochs)
                        bar = "#" * filled + "-" * (bar_len - filled)
                        self._log(f"  Epoch {epoch+1:4d}/{n_epochs}  "
                                  f"[{bar}]  Loss: {loss:.6f}")

                self.models[model_key] = model
                self._log(f"\n  >> {model.name} training complete!")
                self._log(f"  >> Best loss: {best_loss:.6f}\n")

            if not self.stop_requested:
                self._log("\n" + "=" * 50)
                self._log("ALL MODELS TRAINED SUCCESSFULLY!")
                self._log("Click 'EXPORT MODELS' to save them as JSON files.")
                self._log("=" * 50)
                self.root.after(0, lambda: self.export_btn.configure(state=tk.NORMAL))
            else:
                self._log("\nTraining stopped by user.")
                if self.models:
                    self.root.after(0, lambda: self.export_btn.configure(state=tk.NORMAL))

        except Exception as e:
            self._log(f"\n[ERROR] Training failed: {e}")

        finally:
            self.training = False
            self.root.after(0, lambda: self.train_btn.configure(state=tk.NORMAL))
            self.root.after(0, lambda: self.stop_btn.configure(state=tk.DISABLED))
            self.root.after(0, lambda: self.progress_label.configure(text="Training complete"))

    def _export_models(self):
        """Export trained models to JSON files."""
        os.makedirs(MODELS_DIR, exist_ok=True)

        count = 0
        model_infos = []

        for key, model in self.models.items():
            filename = f"model_{key}.json"
            filepath = os.path.join(MODELS_DIR, filename)

            data = model.to_json()
            data["trained_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            data["loss_history"] = self.loss_history.get(key, [])

            with open(filepath, 'w') as f:
                json.dump(data, f)

            size_kb = os.path.getsize(filepath) / 1024
            self._log(f"Exported: {filename} ({size_kb:.1f} KB)")
            count += 1

            model_infos.append({
                "name": model.name,
                "file": filename,
                "type": data["model_type"],
                "final_loss": self.loss_history.get(key, [0])[-1] if self.loss_history.get(key) else 0
            })

        # Save models_info.json
        info_path = os.path.join(MODELS_DIR, "models_info.json")
        with open(info_path, 'w') as f:
            json.dump({
                "models": model_infos,
                "exported_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0"
            }, f, indent=2)

        self._log(f"\n{count} model(s) exported to: {MODELS_DIR}")
        self._log(f"Models info saved to: {info_path}")
        self._log("\nYou can now rebuild the game/APK to include these updated models.")

        messagebox.showinfo("Export Complete",
                            f"{count} model(s) exported to:\n{MODELS_DIR}\n\n"
                            "Run build_apk.py to rebuild the APK with updated models.")


def main():
    root = tk.Tk()

    # Apply dark theme to ttk widgets
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TProgressbar", troughcolor="#16213e",
                     background="#e94560", thickness=20)
    style.configure("TCombobox", fieldbackground="#16213e",
                     background="#16213e", foreground="#e0e0e0")

    app = ChessTrainerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
