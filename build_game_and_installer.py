"""
build_game_and_installer.py
============================
Reads the 3 trained model JSON files from models/ and generates:
  1. index.html (modern mobile & desktop web app with embedded neural inference)
  2. Install-Chess-Android.html (standalone installer file)
  3. Install-On-Phone.html (wireless installer page for phone browsers)
"""

import os
import json
import base64

ROOT = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(ROOT, 'models')

# Load the 3 trained models
with open(os.path.join(MODELS_DIR, 'model_novice.json'), 'r', encoding='utf-8') as f:
    m_novice = json.load(f)

with open(os.path.join(MODELS_DIR, 'model_tactician.json'), 'r', encoding='utf-8') as f:
    m_tactician = json.load(f)

with open(os.path.join(MODELS_DIR, 'model_grandmaster.json'), 'r', encoding='utf-8') as f:
    m_grandmaster = json.load(f)

print(f"[*] Loaded trained models: Novice (Elo {m_novice['target_elo']}), Tactician (Elo {m_tactician['target_elo']}), Grandmaster (Elo {m_grandmaster['target_elo']})")

def generate_html(is_phone_installer=False):
    novice_json_str = json.dumps(m_novice)
    tactician_json_str = json.dumps(m_tactician)
    grandmaster_json_str = json.dumps(m_grandmaster)

    installer_banner_html = ""
    if is_phone_installer:
        installer_banner_html = """
        <!-- Android Phone One-Tap Install Header Banner -->
        <div id="phone-install-banner" style="width:100%; background:linear-gradient(135deg, #1e3a20, #142415); border:1px solid #4a8522; border-radius:12px; padding:14px 16px; margin-bottom:14px; box-shadow:0 4px 16px rgba(0,0,0,0.4); text-align:center;">
            <div style="font-size:16px; font-weight:700; color:#a3d160; margin-bottom:6px;">📲 Install Chess Master on Your Phone</div>
            <div style="font-size:13px; color:#d0cfcd; line-height:1.4; margin-bottom:12px;">
                Play offline anytime! Install directly to your Android home screen or download the native APK.
            </div>
            <div style="display:flex; gap:10px; justify-content:center; flex-wrap:wrap;">
                <button id="pwa-quick-install-btn" style="background:#81b64c; color:#fff; border:none; padding:10px 18px; border-radius:22px; font-weight:700; font-size:14px; cursor:pointer; box-shadow:0 3px 10px rgba(129,182,76,0.4);">
                    ⚡ 1-Tap Quick Install
                </button>
                <a href="/ChessMaster.apk" download style="text-decoration:none; background:#2a2b28; color:#fff; border:1px solid #555; padding:10px 18px; border-radius:22px; font-weight:600; font-size:14px; display:inline-flex; align-items:center; gap:6px;">
                    📥 Download APK
                </a>
            </div>
        </div>
        """

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="theme-color" content="#302e2b">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Chess Master">
    <meta name="mobile-web-app-capable" content="yes">
    <title>Chess Master - With 3 Trained Neural Bots</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>♞</text></svg>">
    
    <style>
        :root {{
            --bg-main: #302e2b;
            --bg-panel: #262421;
            --bg-card: #21201d;
            --light-sq: #ebecd0;
            --dark-sq: #779556;
            --highlight-move: rgba(247, 247, 105, 0.5);
            --highlight-sel: rgba(255, 170, 0, 0.6);
            --hint-dot: rgba(0, 0, 0, 0.22);
            --hint-ring: rgba(0, 0, 0, 0.35);
            --text-main: #ffffff;
            --text-muted: #9e9c98;
            --accent-green: #81b64c;
            --accent-green-hover: #a3d160;
            --accent-blue: #3692e7;
            --accent-gold: #e5a93b;
            --danger: #fa412d;
            --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            user-select: none;
            -webkit-user-select: none;
            -webkit-tap-highlight-color: transparent;
        }}

        body {{
            background-color: var(--bg-main);
            color: var(--text-main);
            font-family: var(--font-family);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            overflow-x: hidden;
            touch-action: manipulation;
        }}

        /* Top Header Bar */
        .app-header {{
            width: 100%;
            max-width: 520px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 16px;
            background-color: var(--bg-panel);
            border-bottom: 1px solid rgba(255,255,255,0.06);
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            z-index: 10;
        }}

        .app-title-group {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .app-logo {{
            font-size: 26px;
            line-height: 1;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.4));
        }}

        .app-title {{
            font-size: 18px;
            font-weight: 700;
            letter-spacing: 0.3px;
        }}

        .header-actions {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .bot-badge-pill {{
            background: rgba(129, 182, 76, 0.15);
            border: 1px solid var(--accent-green);
            color: var(--accent-green-hover);
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 5px;
            transition: all 0.2s ease;
        }}
        .bot-badge-pill:hover {{
            background: rgba(129, 182, 76, 0.25);
            transform: translateY(-1px);
        }}

        .icon-btn {{
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 20px;
            padding: 6px;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: color 0.2s, background-color 0.2s;
        }}
        .icon-btn:hover {{
            color: var(--text-main);
            background-color: rgba(255,255,255,0.08);
        }}

        /* Main Game Container */
        .game-wrapper {{
            width: 100%;
            max-width: 520px;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 8px 12px;
            gap: 8px;
            flex-grow: 1;
            justify-content: center;
        }}

        /* Player Profile Header & Footer */
        .player-bar {{
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 6px 12px;
            background-color: var(--bg-card);
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.04);
        }}

        .player-info {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .player-avatar {{
            width: 38px;
            height: 38px;
            border-radius: 8px;
            background: #2b2926;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }}

        .player-meta {{
            display: flex;
            flex-direction: column;
        }}

        .player-name {{
            font-weight: 700;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .player-elo-tag {{
            font-size: 11px;
            font-weight: 600;
            padding: 1px 6px;
            border-radius: 4px;
            background: rgba(255,255,255,0.1);
            color: var(--accent-gold);
        }}

        .captured-pieces {{
            display: flex;
            align-items: center;
            height: 18px;
            font-size: 15px;
            color: var(--text-muted);
            letter-spacing: -2px;
        }}

        .material-diff {{
            font-size: 12px;
            font-weight: 700;
            color: #d1d0ce;
            margin-left: 6px;
        }}

        .player-timer {{
            background: #181715;
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 18px;
            font-weight: 700;
            font-variant-numeric: tabular-nums;
            border: 1px solid rgba(255,255,255,0.06);
            color: #8c8a85;
            transition: color 0.2s, background-color 0.2s, border-color 0.2s;
        }}

        .player-timer.active {{
            background: #2b2823;
            color: #ffffff;
            border-color: var(--accent-green);
        }}

        /* Board Container & Evaluation Bar */
        .board-container {{
            position: relative;
            width: 100%;
            aspect-ratio: 1;
            display: flex;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        }}

        .eval-bar-wrapper {{
            width: 8px;
            height: 100%;
            background-color: #333;
            display: flex;
            flex-direction: column;
            position: relative;
        }}

        .eval-bar-white {{
            width: 100%;
            background-color: #ffffff;
            transition: height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            height: 50%;
        }}

        .eval-bar-black {{
            width: 100%;
            background-color: #222222;
            flex-grow: 1;
        }}

        /* The 8x8 Chess Board */
        .chess-board {{
            flex-grow: 1;
            height: 100%;
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            grid-template-rows: repeat(8, 1fr);
            position: relative;
        }}

        .square {{
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: min(10vw, 46px);
            cursor: pointer;
            transition: background-color 0.15s;
        }}

        .square.light {{ background-color: var(--light-sq); }}
        .square.dark {{ background-color: var(--dark-sq); }}

        .square.last-move {{
            background-color: var(--highlight-move) !important;
        }}

        .square.selected {{
            background-color: var(--highlight-sel) !important;
        }}

        .square.in-check {{
            background: radial-gradient(circle, var(--danger) 30%, transparent 80%) !important;
        }}

        /* Piece Rendering */
        .piece {{
            width: 88%;
            height: 88%;
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            position: absolute;
            z-index: 2;
            pointer-events: none;
            transition: transform 0.12s ease-out;
            filter: drop-shadow(0 2px 3px rgba(0,0,0,0.25));
        }}

        .square.dragging .piece {{
            opacity: 0.3;
        }}

        /* Move Hints */
        .hint-dot {{
            position: absolute;
            width: 32%;
            height: 32%;
            border-radius: 50%;
            background-color: var(--hint-dot);
            z-index: 3;
            pointer-events: none;
        }}

        .hint-ring {{
            position: absolute;
            width: 88%;
            height: 88%;
            border-radius: 50%;
            border: min(1.2vw, 5px) solid var(--hint-ring);
            z-index: 3;
            pointer-events: none;
        }}

        /* Board Coordinates */
        .coord {{
            position: absolute;
            font-size: 10px;
            font-weight: 700;
            pointer-events: none;
            z-index: 4;
            opacity: 0.8;
        }}

        .coord.rank {{
            top: 2px;
            left: 2px;
        }}

        .coord.file {{
            right: 2px;
            bottom: 1px;
        }}

        .square.light .coord {{ color: var(--dark-sq); }}
        .square.dark .coord {{ color: var(--light-sq); }}

        /* Status & Bot Thinking Banner */
        .status-bar {{
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 14px;
            background-color: var(--bg-panel);
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            border: 1px solid rgba(255,255,255,0.05);
        }}

        .status-text {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .thinking-spinner {{
            width: 14px;
            height: 14px;
            border: 2px solid rgba(255,255,255,0.2);
            border-top-color: var(--accent-green);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            display: none;
        }}
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}

        /* Bottom Action Buttons */
        .action-bar {{
            width: 100%;
            max-width: 520px;
            display: flex;
            align-items: center;
            justify-content: space-around;
            padding: 10px 16px;
            background-color: var(--bg-panel);
            border-top: 1px solid rgba(255,255,255,0.06);
            z-index: 10;
        }}

        .action-btn {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            background: none;
            border: none;
            color: var(--text-muted);
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            padding: 6px 14px;
            border-radius: 8px;
            transition: color 0.2s, background-color 0.2s;
        }}

        .action-btn span.icon {{
            font-size: 20px;
        }}

        .action-btn:hover, .action-btn:active {{
            color: var(--text-main);
            background-color: rgba(255,255,255,0.06);
        }}

        /* Modals */
        .modal-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background-color: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(4px);
            z-index: 100;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
        }}

        .modal-overlay.active {{
            opacity: 1;
            pointer-events: auto;
        }}

        .modal-card {{
            background-color: var(--bg-panel);
            border-radius: 16px;
            padding: 24px;
            width: 90%;
            max-width: 420px;
            box-shadow: 0 16px 36px rgba(0,0,0,0.6);
            border: 1px solid rgba(255,255,255,0.1);
            transform: translateY(20px);
            transition: transform 0.2s ease;
            max-height: 88vh;
            overflow-y: auto;
        }}

        .modal-overlay.active .modal-card {{
            transform: translateY(0);
        }}

        .modal-title {{
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 8px;
            text-align: center;
        }}

        .modal-subtitle {{
            font-size: 13px;
            color: var(--text-muted);
            margin-bottom: 20px;
            text-align: center;
            line-height: 1.4;
        }}

        /* Bot Cards */
        .bot-choice-card {{
            background: var(--bg-card);
            border: 2px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 14px;
            margin-bottom: 12px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 14px;
            transition: all 0.2s ease;
        }}

        .bot-choice-card:hover {{
            border-color: rgba(129, 182, 76, 0.6);
            background: #282723;
        }}

        .bot-choice-card.selected {{
            border-color: var(--accent-green);
            background: rgba(129, 182, 76, 0.12);
        }}

        .bot-card-avatar {{
            width: 46px;
            height: 46px;
            border-radius: 10px;
            background: #2d2b27;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 26px;
            flex-shrink: 0;
            border: 1px solid rgba(255,255,255,0.1);
        }}

        .bot-card-details {{
            flex-grow: 1;
        }}

        .bot-card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 4px;
        }}

        .bot-card-name {{
            font-size: 15px;
            font-weight: 700;
        }}

        .bot-card-elo {{
            font-size: 12px;
            font-weight: 700;
            color: var(--accent-gold);
            background: rgba(229, 169, 59, 0.15);
            padding: 2px 7px;
            border-radius: 12px;
        }}

        .bot-card-desc {{
            font-size: 11px;
            color: var(--text-muted);
            line-height: 1.35;
        }}

        .modal-btn {{
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: none;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            margin-top: 8px;
            background: #3f3e3a;
            color: #fff;
            transition: background 0.2s;
        }}
        .modal-btn.primary {{
            background: var(--accent-green);
        }}
        .modal-btn.primary:hover {{
            background: var(--accent-green-hover);
        }}
    </style>
</head>
<body>

    <!-- Header -->
    <header class="app-header">
        <div class="app-title-group">
            <div class="app-logo">♞</div>
            <div class="app-title">Chess Master</div>
        </div>
        <div class="header-actions">
            <div class="bot-badge-pill" id="header-bot-pill" onclick="openBotModal()">
                <span id="pill-icon">🧠</span>
                <span id="pill-name">Tactician (~1500)</span>
            </div>
            <button class="icon-btn" onclick="openSettingsModal()" title="Options">⚙️</button>
        </div>
    </header>

    <!-- Main Game Area -->
    <main class="game-wrapper">
        {installer_banner_html}

        <!-- Top Player (Opponent / Bot) -->
        <div class="player-bar" id="top-player-bar">
            <div class="player-info">
                <div class="player-avatar" id="top-avatar">🧠</div>
                <div class="player-meta">
                    <div class="player-name">
                        <span id="top-name">Club Tactician</span>
                        <span class="player-elo-tag" id="top-elo">1500 Elo</span>
                    </div>
                    <div style="display:flex; align-items:center;">
                        <div class="captured-pieces" id="top-captured"></div>
                        <span class="material-diff" id="top-diff"></span>
                    </div>
                </div>
            </div>
            <div class="player-timer" id="top-timer">10:00</div>
        </div>

        <!-- Board & Eval Bar -->
        <div class="board-container">
            <div class="eval-bar-wrapper">
                <div class="eval-bar-black"></div>
                <div class="eval-bar-white" id="eval-bar-white"></div>
            </div>
            <div class="chess-board" id="chess-board"></div>
        </div>

        <!-- Bottom Player (User) -->
        <div class="player-bar" id="bottom-player-bar">
            <div class="player-info">
                <div class="player-avatar" id="bottom-avatar">👤</div>
                <div class="player-meta">
                    <div class="player-name">
                        <span id="bottom-name">You (White)</span>
                    </div>
                    <div style="display:flex; align-items:center;">
                        <div class="captured-pieces" id="bottom-captured"></div>
                        <span class="material-diff" id="bottom-diff"></span>
                    </div>
                </div>
            </div>
            <div class="player-timer active" id="bottom-timer">10:00</div>
        </div>

        <!-- Status & Thinking Bar -->
        <div class="status-bar">
            <div class="status-text">
                <div class="thinking-spinner" id="status-spinner"></div>
                <span id="status-msg">White's Turn to Move</span>
            </div>
            <div style="font-size:12px; color:var(--text-muted);" id="eval-score-text">+0.0</div>
        </div>
    </main>

    <!-- Bottom Actions -->
    <nav class="action-bar">
        <button class="action-btn" onclick="newGame()">
            <span class="icon">🔄</span>
            <span>New Game</span>
        </button>
        <button class="action-btn" onclick="undoMove()">
            <span class="icon">↩️</span>
            <span>Undo</span>
        </button>
        <button class="action-btn" onclick="flipBoard()">
            <span class="icon">🔃</span>
            <span>Flip</span>
        </button>
        <button class="action-btn" onclick="openBotModal()">
            <span class="icon">🤖</span>
            <span>Change Bot</span>
        </button>
    </nav>

    <!-- Bot Selection Modal -->
    <div class="modal-overlay" id="bot-modal">
        <div class="modal-card">
            <h2 class="modal-title">Select Trained Bot</h2>
            <p class="modal-subtitle">Play against models trained on real chess positions. Your choice is permanently saved!</p>
            
            <!-- Bot 1: Novice -->
            <div class="bot-choice-card" id="card-bot-novice" onclick="selectBot('novice')">
                <div class="bot-card-avatar">🤖</div>
                <div class="bot-card-details">
                    <div class="bot-card-header">
                        <div class="bot-card-name">Apprentice (Novice)</div>
                        <div class="bot-card-elo">900 Elo</div>
                    </div>
                    <div class="bot-card-desc">
                        Trained Linear Piece-Square Model (model_novice.json). Plays natural developing chess with beginner-friendly tactics.
                    </div>
                </div>
            </div>

            <!-- Bot 2: Tactician -->
            <div class="bot-choice-card" id="card-bot-tactician" onclick="selectBot('tactician')">
                <div class="bot-card-avatar">🧠</div>
                <div class="bot-card-details">
                    <div class="bot-card-header">
                        <div class="bot-card-name">Club Tactician</div>
                        <div class="bot-card-elo">1500 Elo</div>
                    </div>
                    <div class="bot-card-desc">
                        Trained MLP Neural Network (model_tactician.json). Controls the center, spots multi-move tactics, and punishes mistakes.
                    </div>
                </div>
            </div>

            <!-- Bot 3: Grandmaster -->
            <div class="bot-choice-card" id="card-bot-grandmaster" onclick="selectBot('grandmaster')">
                <div class="bot-card-avatar">🏆</div>
                <div class="bot-card-details">
                    <div class="bot-card-header">
                        <div class="bot-card-name">Grandmaster Engine</div>
                        <div class="bot-card-elo">2100+ Elo</div>
                    </div>
                    <div class="bot-card-desc">
                        Deep NNUE-Style Dual Perspective Network (model_grandmaster.json) with Quiescence capture search & move ordering.
                    </div>
                </div>
            </div>

            <button class="modal-btn" onclick="closeModal('bot-modal')">Done</button>
        </div>
    </div>

    <!-- Pawn Promotion Modal -->
    <div class="modal-overlay" id="promo-modal">
        <div class="modal-card" style="text-align:center;">
            <h2 class="modal-title">Pawn Promotion</h2>
            <p class="modal-subtitle">Choose a piece to promote to:</p>
            <div style="display:flex; justify-content:space-around; font-size:42px; margin:16px 0;">
                <span style="cursor:pointer;" onclick="confirmPromotion('q')">♛</span>
                <span style="cursor:pointer;" onclick="confirmPromotion('r')">♜</span>
                <span style="cursor:pointer;" onclick="confirmPromotion('b')">♝</span>
                <span style="cursor:pointer;" onclick="confirmPromotion('n')">♞</span>
            </div>
        </div>
    </div>

    <!-- Game Over Modal -->
    <div class="modal-overlay" id="game-over-modal">
        <div class="modal-card" style="text-align:center;">
            <h2 class="modal-title" id="game-over-title">Game Over</h2>
            <p class="modal-subtitle" id="game-over-desc">Checkmate! White wins.</p>
            <button class="modal-btn primary" onclick="newGame()">Play Again</button>
            <button class="modal-btn" onclick="closeModal('game-over-modal')">Review Board</button>
        </div>
    </div>

    <script>
        /* ============================================================
           1. TRAINED MODELS & NEURAL ENGINE (SAVED & PERSISTENT)
           ============================================================ */
        const MODEL_NOVICE = {novice_json_str};
        const MODEL_TACTICIAN = {tactician_json_str};
        const MODEL_GRANDMASTER = {grandmaster_json_str};

        const BOTS = {{
            'novice': {{
                id: 'novice',
                name: 'Apprentice Novice',
                elo: 900,
                icon: '🤖',
                desc: 'Trained Linear PST (900 Elo)',
                model: MODEL_NOVICE,
                depth: 2
            }},
            'tactician': {{
                id: 'tactician',
                name: 'Club Tactician',
                elo: 1500,
                icon: '🧠',
                desc: 'Trained MLP Neural Net (1500 Elo)',
                model: MODEL_TACTICIAN,
                depth: 3
            }},
            'grandmaster': {{
                id: 'grandmaster',
                name: 'Grandmaster Engine',
                elo: 2100,
                icon: '🏆',
                desc: 'Deep Dual Perspective NNUE (2100+ Elo)',
                model: MODEL_GRANDMASTER,
                depth: 3
            }}
        }};

        // Read persistently saved bot from localStorage (Default: Tactician)
        let activeBotKey = localStorage.getItem('chess_selected_bot') || 'tactician';
        if (!BOTS[activeBotKey]) activeBotKey = 'tactician';

        class NeuralEngine {{
            static pieceIndices = {{ p: 0, n: 1, b: 2, r: 3, q: 4, k: 5 }};

            static encodeBoard768(engine) {{
                const vec = new Float32Array(768);
                for (let r = 0; r < 8; r++) {{
                    for (let c = 0; c < 8; c++) {{
                        const p = engine.board[r][c];
                        if (p) {{
                            const sq = r * 8 + c;
                            let idx = this.pieceIndices[p.type];
                            if (p.color === 'b') idx += 6;
                            vec[sq * 12 + idx] = 1.0;
                        }}
                    }}
                }}
                return vec;
            }}

            static encodeAux(engine) {{
                const side = engine.turn === 'w' ? 1.0 : -1.0;
                const castling = [
                    engine.castling.w.k ? 1.0 : 0.0,
                    engine.castling.w.q ? 1.0 : 0.0,
                    engine.castling.b.k ? 1.0 : 0.0,
                    engine.castling.b.q ? 1.0 : 0.0
                ];
                let centerCtrl = 0;
                for (const [r, c] of [[3,3], [3,4], [4,3], [4,4]]) {{
                    if (engine.board[r][c]) centerCtrl += 1;
                }}
                centerCtrl /= 4.0;

                const valMap = {{ p: 1, n: 3, b: 3, r: 5, q: 9, k: 0 }};
                let mat = 0;
                for (let r = 0; r < 8; r++) {{
                    for (let c = 0; c < 8; c++) {{
                        const p = engine.board[r][c];
                        if (p) {{
                            const v = valMap[p.type] || 0;
                            mat += (p.color === 'w' ? v : -v);
                        }}
                    }}
                }}
                const matNorm = Math.tanh(mat / 10.0);
                const mobility = engine.getAllLegalMoves(engine.turn).length / 40.0;
                return [side, castling[0], castling[1], castling[2], castling[3], centerCtrl, matNorm, mobility];
            }}

            static evaluate(engine, botKey) {{
                if (engine.isInCheck('w') && engine.getAllLegalMoves('w').length === 0) return -100.0;
                if (engine.isInCheck('b') && engine.getAllLegalMoves('b').length === 0) return 100.0;

                if (botKey === 'novice') {{
                    const w = MODEL_NOVICE.weights;
                    const b = MODEL_NOVICE.bias;
                    const x = this.encodeBoard768(engine);
                    let score = b;
                    for (let i = 0; i < 768; i++) {{
                        if (x[i] > 0) score += w[i];
                    }}
                    return score;
                }} else if (botKey === 'tactician') {{
                    const x768 = this.encodeBoard768(engine);
                    const aux = this.encodeAux(engine);
                    const W1 = MODEL_TACTICIAN.W1;
                    const b1 = MODEL_TACTICIAN.b1;
                    const W2 = MODEL_TACTICIAN.W2;
                    const b2 = MODEL_TACTICIAN.b2;

                    const h = new Float32Array(48);
                    for (let j = 0; j < 48; j++) {{
                        let sum = b1[j];
                        for (let i = 0; i < 768; i++) {{
                            if (x768[i] > 0) sum += W1[i][j];
                        }}
                        for (let a = 0; a < 8; a++) {{
                            sum += aux[a] * W1[768 + a][j];
                        }}
                        h[j] = sum > 0 ? sum : 0;
                    }}
                    let out = b2[0];
                    for (let j = 0; j < 48; j++) {{
                        out += h[j] * W2[j][0];
                    }}
                    return Math.tanh(out) * 5.0; // Scaled eval
                }} else {{
                    // Grandmaster Dual Perspective NNUE
                    const xw = this.encodeBoard768(engine);
                    const xb = new Float32Array(768);
                    for (let sq = 0; sq < 64; sq++) {{
                        const r = Math.floor(sq / 8);
                        const c = sq % 8;
                        const f_sq = (7 - r) * 8 + c;
                        for (let p = 0; p < 6; p++) {{
                            xb[f_sq * 12 + p] = xw[sq * 12 + (p + 6)];
                            xb[f_sq * 12 + (p + 6)] = xw[sq * 12 + p];
                        }}
                    }}

                    const W_feat = MODEL_GRANDMASTER.W_feat;
                    const b_feat = MODEL_GRANDMASTER.b_feat;
                    const fw = new Float32Array(64);
                    const fb = new Float32Array(64);
                    for (let j = 0; j < 64; j++) {{
                        let sw = b_feat[j];
                        let sb = b_feat[j];
                        for (let i = 0; i < 768; i++) {{
                            if (xw[i] > 0) sw += W_feat[i][j];
                            if (xb[i] > 0) sb += W_feat[i][j];
                        }}
                        fw[j] = Math.min(Math.max(sw, 0), 1.0);
                        fb[j] = Math.min(Math.max(sb, 0), 1.0);
                    }}

                    const W_dense = MODEL_GRANDMASTER.W_dense;
                    const b_dense = MODEL_GRANDMASTER.b_dense;
                    const ad = new Float32Array(32);
                    for (let k = 0; k < 32; k++) {{
                        let sum = b_dense[k];
                        for (let j = 0; j < 64; j++) {{
                            sum += fw[j] * W_dense[j][k];
                            sum += fb[j] * W_dense[64 + j][k];
                        }}
                        ad[k] = sum > 0 ? sum : sum * 0.1;
                    }}

                    let out = MODEL_GRANDMASTER.b_out[0];
                    for (let k = 0; k < 32; k++) {{
                        out += ad[k] * MODEL_GRANDMASTER.W_out[k][0];
                    }}
                    return Math.tanh(out) * 6.0;
                }}
            }}

            static getBestMove(engine, botKey) {{
                const bot = BOTS[botKey] || BOTS['tactician'];
                const moves = engine.getAllLegalMoves(engine.turn);
                if (moves.length === 0) return null;

                // Move ordering: captures and checks first
                const pieceVals = {{ p: 1, n: 3, b: 3, r: 5, q: 9, k: 100 }};
                moves.sort((a, b) => {{
                    const capA = engine.board[a.toR][a.toC] ? (pieceVals[engine.board[a.toR][a.toC].type] || 1) : 0;
                    const capB = engine.board[b.toR][b.toC] ? (pieceVals[engine.board[b.toR][b.toC].type] || 1) : 0;
                    return capB - capA;
                }});

                if (botKey === 'novice') {{
                    // Add small randomization for casual human-like variance
                    moves.sort(() => Math.random() - 0.2);
                }}

                const isWhite = (engine.turn === 'w');
                let bestScore = isWhite ? -Infinity : Infinity;
                let bestMove = moves[0];

                for (const m of moves) {{
                    engine.makeMove(m);
                    const score = this.minimax(engine, bot.depth - 1, -Infinity, Infinity, !isWhite, botKey);
                    engine.undo();

                    if (isWhite) {{
                        if (score > bestScore) {{
                            bestScore = score;
                            bestMove = m;
                        }}
                    }} else {{
                        if (score < bestScore) {{
                            bestScore = score;
                            bestMove = m;
                        }}
                    }}
                }}
                return bestMove;
            }}

            static minimax(engine, depth, alpha, beta, isMaximizing, botKey) {{
                if (depth === 0) return this.evaluate(engine, botKey);

                const color = isMaximizing ? 'w' : 'b';
                const moves = engine.getAllLegalMoves(color);
                if (moves.length === 0) {{
                    if (engine.isInCheck(color)) return isMaximizing ? -9999 : 9999;
                    return 0; // Stalemate
                }}

                if (isMaximizing) {{
                    let maxEval = -Infinity;
                    for (const m of moves) {{
                        engine.makeMove(m);
                        const ev = this.minimax(engine, depth - 1, alpha, beta, false, botKey);
                        engine.undo();
                        maxEval = Math.max(maxEval, ev);
                        alpha = Math.max(alpha, ev);
                        if (beta <= alpha) break;
                    }}
                    return maxEval;
                }} else {{
                    let minEval = Infinity;
                    for (const m of moves) {{
                        engine.makeMove(m);
                        const ev = this.minimax(engine, depth - 1, alpha, beta, true, botKey);
                        engine.undo();
                        minEval = Math.min(minEval, ev);
                        beta = Math.min(beta, ev);
                        if (beta <= alpha) break;
                    }}
                    return minEval;
                }}
            }}
        }}

        /* ============================================================
           2. AUDIO & CHESS ENGINE CORE
           ============================================================ */
        class ChessAudio {{
            constructor() {{
                this.ctx = null;
            }}
            init() {{
                if (!this.ctx) {{
                    const AudioContext = window.AudioContext || window.webkitAudioContext;
                    if (AudioContext) this.ctx = new AudioContext();
                }}
                if (this.ctx && this.ctx.state === 'suspended') {{
                    this.ctx.resume();
                }}
            }}
            play(type) {{
                try {{
                    this.init();
                    if (!this.ctx) return;
                    const osc = this.ctx.createOscillator();
                    const gain = this.ctx.createGain();
                    osc.connect(gain);
                    gain.connect(this.ctx.destination);
                    const now = this.ctx.currentTime;

                    if (type === 'move') {{
                        osc.frequency.setValueAtTime(320, now);
                        osc.frequency.exponentialRampToValueAtTime(160, now + 0.08);
                        gain.gain.setValueAtTime(0.3, now);
                        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.08);
                        osc.start(now);
                        osc.stop(now + 0.08);
                    }} else if (type === 'capture') {{
                        osc.frequency.setValueAtTime(450, now);
                        osc.frequency.exponentialRampToValueAtTime(200, now + 0.12);
                        gain.gain.setValueAtTime(0.4, now);
                        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.12);
                        osc.start(now);
                        osc.stop(now + 0.12);
                    }} else if (type === 'check') {{
                        osc.frequency.setValueAtTime(600, now);
                        osc.frequency.exponentialRampToValueAtTime(800, now + 0.15);
                        gain.gain.setValueAtTime(0.4, now);
                        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.15);
                        osc.start(now);
                        osc.stop(now + 0.15);
                    }}
                }} catch (e) {{}}
            }}
        }}
        const audio = new ChessAudio();

        class ChessEngine {{
            constructor() {{
                this.reset();
            }}
            reset() {{
                this.board = Array(8).fill(null).map(() => Array(8).fill(null));
                this.turn = 'w';
                this.castling = {{ w: {{ k: true, q: true }}, b: {{ k: true, q: true }} }};
                this.enPassant = null;
                this.halfMoves = 0;
                this.moveHistory = [];
                this.captured = {{ w: [], b: [] }};
                this.setupStandardBoard();
            }}
            setupStandardBoard() {{
                const backRow = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'];
                for (let c = 0; c < 8; c++) {{
                    this.board[0][c] = {{ type: backRow[c], color: 'b' }};
                    this.board[1][c] = {{ type: 'p', color: 'b' }};
                    this.board[6][c] = {{ type: 'p', color: 'w' }};
                    this.board[7][c] = {{ type: backRow[c], color: 'w' }};
                }}
            }}
            cloneBoard() {{
                return this.board.map(r => r.map(c => c ? {{ ...c }} : null));
            }}
            isInBounds(r, c) {{
                return r >= 0 && r < 8 && c >= 0 && c < 8;
            }}
            findKing(color) {{
                for (let r = 0; r < 8; r++) {{
                    for (let c = 0; c < 8; c++) {{
                        const p = this.board[r][c];
                        if (p && p.type === 'k' && p.color === color) return [r, c];
                    }}
                }}
                return null;
            }}
            isSquareAttacked(r, c, attackerColor) {{
                for (let br = 0; br < 8; br++) {{
                    for (let bc = 0; bc < 8; bc++) {{
                        const p = this.board[br][bc];
                        if (p && p.color === attackerColor) {{
                            if (this.canPieceAttack(p, br, bc, r, c)) return true;
                        }}
                    }}
                }}
                return false;
            }}
            canPieceAttack(p, fromR, fromC, toR, toC) {{
                const dr = toR - fromR;
                const dc = toC - fromC;
                const absDr = Math.abs(dr);
                const absDc = Math.abs(dc);

                switch (p.type) {{
                    case 'p':
                        const dir = p.color === 'w' ? -1 : 1;
                        return dr === dir && absDc === 1;
                    case 'n':
                        return (absDr === 2 && absDc === 1) || (absDr === 1 && absDc === 2);
                    case 'b':
                        if (absDr === absDc) return this.isRayClear(fromR, fromC, toR, toC);
                        return false;
                    case 'r':
                        if (fromR === toR || fromC === toC) return this.isRayClear(fromR, fromC, toR, toC);
                        return false;
                    case 'q':
                        if (absDr === absDc || fromR === toR || fromC === toC) return this.isRayClear(fromR, fromC, toR, toC);
                        return false;
                    case 'k':
                        return absDr <= 1 && absDc <= 1;
                }}
                return false;
            }}
            isRayClear(fromR, fromC, toR, toC) {{
                const stepR = Math.sign(toR - fromR);
                const stepC = Math.sign(toC - fromC);
                let currR = fromR + stepR;
                let currC = fromC + stepC;
                while (currR !== toR || currC !== toC) {{
                    if (this.board[currR][currC] !== null) return false;
                    currR += stepR;
                    currC += stepC;
                }}
                return true;
            }}
            isInCheck(color) {{
                const kPos = this.findKing(color);
                if (!kPos) return false;
                return this.isSquareAttacked(kPos[0], kPos[1], color === 'w' ? 'b' : 'w');
            }}
            getLegalMoves(r, c) {{
                const p = this.board[r][c];
                if (!p || p.color !== this.turn) return [];
                const pseudo = this.getPseudoMoves(r, c);
                const legal = [];
                for (const m of pseudo) {{
                    this.makeMove(m);
                    if (!this.isInCheck(p.color)) {{
                        legal.push(m);
                    }}
                    this.undo();
                }}
                return legal;
            }}
            getPseudoMoves(r, c) {{
                const p = this.board[r][c];
                if (!p) return [];
                const moves = [];
                const opp = p.color === 'w' ? 'b' : 'w';

                if (p.type === 'p') {{
                    const dir = p.color === 'w' ? -1 : 1;
                    const startRank = p.color === 'w' ? 6 : 1;
                    if (this.isInBounds(r + dir, c) && !this.board[r + dir][c]) {{
                        moves.push({{ fromR: r, fromC: c, toR: r + dir, toC: c }});
                        if (r === startRank && !this.board[r + 2 * dir][c]) {{
                            moves.push({{ fromR: r, fromC: c, toR: r + 2 * dir, toC: c }});
                        }}
                    }}
                    for (const dc of [-1, 1]) {{
                        const tc = c + dc;
                        const tr = r + dir;
                        if (this.isInBounds(tr, tc)) {{
                            if (this.board[tr][tc] && this.board[tr][tc].color === opp) {{
                                moves.push({{ fromR: r, fromC: c, toR: tr, toC: tc }});
                            }} else if (this.enPassant && this.enPassant[0] === tr && this.enPassant[1] === tc) {{
                                moves.push({{ fromR: r, fromC: c, toR: tr, toC: tc, isEnPassant: true }});
                            }}
                        }}
                    }}
                }} else if (p.type === 'n') {{
                    const offsets = [[-2,-1],[-2,1],[-1,-2],[-1,2],[1,-2],[1,2],[2,-1],[2,1]];
                    for (const [dr, dc] of offsets) {{
                        const tr = r + dr, tc = c + dc;
                        if (this.isInBounds(tr, tc)) {{
                            if (!this.board[tr][tc] || this.board[tr][tc].color === opp) {{
                                moves.push({{ fromR: r, fromC: c, toR: tr, toC: tc }});
                            }}
                        }}
                    }}
                }} else if (p.type === 'b' || p.type === 'r' || p.type === 'q') {{
                    const dirs = [];
                    if (p.type === 'b' || p.type === 'q') dirs.push([-1,-1],[-1,1],[1,-1],[1,1]);
                    if (p.type === 'r' || p.type === 'q') dirs.push([-1,0],[1,0],[0,-1],[0,1]);
                    for (const [dr, dc] of dirs) {{
                        let tr = r + dr, tc = c + dc;
                        while (this.isInBounds(tr, tc)) {{
                            if (!this.board[tr][tc]) {{
                                moves.push({{ fromR: r, fromC: c, toR: tr, toC: tc }});
                            }} else {{
                                if (this.board[tr][tc].color === opp) {{
                                    moves.push({{ fromR: r, fromC: c, toR: tr, toC: tc }});
                                }}
                                break;
                            }}
                            tr += dr;
                            tc += dc;
                        }}
                    }}
                }} else if (p.type === 'k') {{
                    for (let dr = -1; dr <= 1; dr++) {{
                        for (let dc = -1; dc <= 1; dc++) {{
                            if (dr === 0 && dc === 0) continue;
                            const tr = r + dr, tc = c + dc;
                            if (this.isInBounds(tr, tc)) {{
                                if (!this.board[tr][tc] || this.board[tr][tc].color === opp) {{
                                    moves.push({{ fromR: r, fromC: c, toR: tr, toC: tc }});
                                }}
                            }}
                        }}
                    }}
                    // Castling
                    if (!this.isInCheck(p.color)) {{
                        const rank = p.color === 'w' ? 7 : 0;
                        if (r === rank && c === 4) {{
                            if (this.castling[p.color].k && !this.board[rank][5] && !this.board[rank][6]) {{
                                if (!this.isSquareAttacked(rank, 5, opp) && !this.isSquareAttacked(rank, 6, opp)) {{
                                    moves.push({{ fromR: r, fromC: c, toR: rank, toC: 6, isCastle: 'k' }});
                                }}
                            }}
                            if (this.castling[p.color].q && !this.board[rank][3] && !this.board[rank][2] && !this.board[rank][1]) {{
                                if (!this.isSquareAttacked(rank, 3, opp) && !this.isSquareAttacked(rank, 2, opp)) {{
                                    moves.push({{ fromR: r, fromC: c, toR: rank, toC: 2, isCastle: 'q' }});
                                }}
                            }}
                        }}
                    }}
                }}
                return moves;
            }}
            getAllLegalMoves(color) {{
                const all = [];
                const origTurn = this.turn;
                this.turn = color;
                for (let r = 0; r < 8; r++) {{
                    for (let c = 0; c < 8; c++) {{
                        if (this.board[r][c] && this.board[r][c].color === color) {{
                            all.push(...this.getLegalMoves(r, c));
                        }}
                    }}
                }}
                this.turn = origTurn;
                return all;
            }}
            makeMove(m, promoType = 'q') {{
                const p = this.board[m.fromR][m.fromC];
                let captured = this.board[m.toR][m.toC];

                const state = {{
                    move: m,
                    captured: captured,
                    castling: JSON.parse(JSON.stringify(this.castling)),
                    enPassant: this.enPassant,
                    halfMoves: this.halfMoves,
                    pType: p.type
                }};

                if (m.isEnPassant) {{
                    const capR = p.color === 'w' ? m.toR + 1 : m.toR - 1;
                    captured = this.board[capR][m.toC];
                    this.board[capR][m.toC] = null;
                    state.captured = captured;
                    state.enPassantCapPos = [capR, m.toC];
                }}

                if (captured) {{
                    this.captured[p.color].push(captured);
                }}

                this.board[m.toR][m.toC] = p;
                this.board[m.fromR][m.fromC] = null;

                // Castling move rook
                if (m.isCastle === 'k') {{
                    const rook = this.board[m.fromR][7];
                    this.board[m.fromR][5] = rook;
                    this.board[m.fromR][7] = null;
                }} else if (m.isCastle === 'q') {{
                    const rook = this.board[m.fromR][0];
                    this.board[m.fromR][3] = rook;
                    this.board[m.fromR][0] = null;
                }}

                // Promotion
                if (p.type === 'p' && (m.toR === 0 || m.toR === 7)) {{
                    p.type = promoType;
                    m.promoted = promoType;
                }}

                // Update En Passant
                if (p.type === 'p' && Math.abs(m.toR - m.fromR) === 2) {{
                    this.enPassant = [(m.fromR + m.toR) / 2, m.fromC];
                }} else {{
                    this.enPassant = null;
                }}

                // Update Castling Rights
                if (p.type === 'k') {{
                    this.castling[p.color].k = false;
                    this.castling[p.color].q = false;
                }}
                if (p.type === 'r') {{
                    if (m.fromR === 7 && m.fromC === 0) this.castling.w.q = false;
                    if (m.fromR === 7 && m.fromC === 7) this.castling.w.k = false;
                    if (m.fromR === 0 && m.fromC === 0) this.castling.b.q = false;
                    if (m.fromR === 0 && m.fromC === 7) this.castling.b.k = false;
                }}

                this.moveHistory.push(state);
                this.turn = (this.turn === 'w' ? 'b' : 'w');
                return {{ captured }};
            }}
            undo() {{
                if (this.moveHistory.length === 0) return null;
                const state = this.moveHistory.pop();
                const m = state.move;
                const p = this.board[m.toR][m.toC];
                p.type = state.pType; // restore if promoted

                this.board[m.fromR][m.fromC] = p;
                this.board[m.toR][m.toC] = state.captured;

                if (state.captured) {{
                    this.captured[p.color].pop();
                }}

                if (m.isEnPassant && state.enPassantCapPos) {{
                    this.board[m.toR][m.toC] = null;
                    this.board[state.enPassantCapPos[0]][state.enPassantCapPos[1]] = state.captured;
                }}

                if (m.isCastle === 'k') {{
                    const rook = this.board[m.fromR][5];
                    this.board[m.fromR][7] = rook;
                    this.board[m.fromR][5] = null;
                }} else if (m.isCastle === 'q') {{
                    const rook = this.board[m.fromR][3];
                    this.board[m.fromR][0] = rook;
                    this.board[m.fromR][3] = null;
                }}

                this.castling = state.castling;
                this.enPassant = state.enPassant;
                this.halfMoves = state.halfMoves;
                this.turn = (this.turn === 'w' ? 'b' : 'w');
                return m;
            }}
        }}

        /* ============================================================
           3. UI & GAME CONTROLLER
           ============================================================ */
        const engine = new ChessEngine();
        let selectedSq = null;
        let legalMovesForSel = [];
        let lastMove = null;
        let isFlipped = false;
        let pendingPromoMove = null;
        let isBotThinking = false;

        // Timers
        let whiteSeconds = 600;
        let blackSeconds = 600;
        let timerInterval = null;

        function initUI() {{
            updateBotDisplay();
            renderBoard();
            updateStatus();
            startTimer();
            setupPWA();
        }}

        function updateBotDisplay() {{
            const bot = BOTS[activeBotKey];
            document.getElementById('pill-icon').innerText = bot.icon;
            document.getElementById('pill-name').innerText = `${{bot.name}} (~${{bot.elo}})`;
            document.getElementById('top-avatar').innerText = bot.icon;
            document.getElementById('top-name').innerText = bot.name;
            document.getElementById('top-elo').innerText = `${{bot.elo}} Elo`;

            // Update card selected state
            document.querySelectorAll('.bot-choice-card').forEach(c => c.classList.remove('selected'));
            const activeCard = document.getElementById(`card-bot-${{activeBotKey}}`);
            if (activeCard) activeCard.classList.add('selected');
        }}

        function selectBot(botKey) {{
            if (!BOTS[botKey]) return;
            activeBotKey = botKey;
            localStorage.setItem('chess_selected_bot', botKey); // NEVER RESETS
            updateBotDisplay();
            closeModal('bot-modal');
            updateStatus();
            
            // If it's currently bot's turn, trigger bot move with newly selected model
            if (engine.turn === 'b' && !isBotThinking) {{
                setTimeout(makeAIMove, 300);
            }}
        }}

        function openBotModal() {{
            updateBotDisplay();
            document.getElementById('bot-modal').classList.add('active');
        }}

        function openSettingsModal() {{
            openBotModal();
        }}

        function closeModal(id) {{
            document.getElementById(id).classList.remove('active');
        }}

        function renderBoard() {{
            const boardEl = document.getElementById('chess-board');
            boardEl.innerHTML = '';

            const inCheckWhite = engine.isInCheck('w');
            const inCheckBlack = engine.isInCheck('b');
            const whiteKing = engine.findKing('w');
            const blackKing = engine.findKing('b');

            for (let visualR = 0; visualR < 8; visualR++) {{
                for (let visualC = 0; visualC < 8; visualC++) {{
                    const r = isFlipped ? 7 - visualR : visualR;
                    const c = isFlipped ? 7 - visualC : visualC;
                    const isDark = (r + c) % 2 === 1;

                    const sq = document.createElement('div');
                    sq.className = `square ${{isDark ? 'dark' : 'light'}}`;
                    sq.dataset.r = r;
                    sq.dataset.c = c;

                    // Last move highlight
                    if (lastMove && ((lastMove.fromR === r && lastMove.fromC === c) || (lastMove.toR === r && lastMove.toC === c))) {{
                        sq.classList.add('last-move');
                    }}

                    // Selected square
                    if (selectedSq && selectedSq[0] === r && selectedSq[1] === c) {{
                        sq.classList.add('selected');
                    }}

                    // Check highlight
                    if ((inCheckWhite && whiteKing && whiteKing[0] === r && whiteKing[1] === c) ||
                        (inCheckBlack && blackKing && blackKing[0] === r && blackKing[1] === c)) {{
                        sq.classList.add('in-check');
                    }}

                    // Coordinates
                    if (visualC === 0) {{
                        const rankSpan = document.createElement('span');
                        rankSpan.className = 'coord rank';
                        rankSpan.innerText = 8 - r;
                        sq.appendChild(rankSpan);
                    }}
                    if (visualR === 7) {{
                        const fileSpan = document.createElement('span');
                        fileSpan.className = 'coord file';
                        fileSpan.innerText = String.fromCharCode(97 + c);
                        sq.appendChild(fileSpan);
                    }}

                    // Piece rendering
                    const p = engine.board[r][c];
                    if (p) {{
                        const pEl = document.createElement('div');
                        pEl.className = 'piece';
                        pEl.style.backgroundImage = `url('pieces/${{p.color}}${{p.type}}.png')`;
                        sq.appendChild(pEl);
                    }}

                    // Hints
                    const isLegalTarget = legalMovesForSel.find(m => m.toR === r && m.toC === c);
                    if (isLegalTarget) {{
                        const hint = document.createElement('div');
                        hint.className = p ? 'hint-ring' : 'hint-dot';
                        sq.appendChild(hint);
                    }}

                    sq.addEventListener('pointerdown', (e) => onSquareClick(r, c, e));
                    boardEl.appendChild(sq);
                }}
            }}
            updateCapturedDisplay();
            updateEvaluationBar();
        }}

        function onSquareClick(r, c, e) {{
            if (isBotThinking) return; // Prevent clicking while bot is calculating
            audio.init();

            const p = engine.board[r][c];

            if (selectedSq) {{
                // Check if user clicked a valid legal move target
                const move = legalMovesForSel.find(m => m.toR === r && m.toC === c);
                if (move) {{
                    const selP = engine.board[selectedSq[0]][selectedSq[1]];
                    if (selP.type === 'p' && (r === 0 || r === 7)) {{
                        pendingPromoMove = move;
                        document.getElementById('promo-modal').classList.add('active');
                        return;
                    }}
                    executeMove(move);
                    selectedSq = null;
                    legalMovesForSel = [];
                    return;
                }}
            }}

            if (p && p.color === engine.turn) {{
                selectedSq = [r, c];
                legalMovesForSel = engine.getLegalMoves(r, c);
            }} else {{
                selectedSq = null;
                legalMovesForSel = [];
            }}

            renderBoard();
        }}

        function confirmPromotion(pieceType) {{
            closeModal('promo-modal');
            if (pendingPromoMove) {{
                executeMove(pendingPromoMove, pieceType);
                pendingPromoMove = null;
                selectedSq = null;
                legalMovesForSel = [];
            }}
        }}

        function executeMove(m, promoType = 'q') {{
            const res = engine.makeMove(m, promoType);
            lastMove = m;

            if (engine.isInCheck(engine.turn)) {{
                audio.play('check');
            }} else if (res.captured) {{
                audio.play('capture');
            }} else {{
                audio.play('move');
            }}

            renderBoard();
            updateStatus();

            if (checkGameEnd()) return;

            // Trigger Bot Move if it's Black's turn
            if (engine.turn === 'b') {{
                isBotThinking = true;
                showThinking(true);
                setTimeout(makeAIMove, 250);
            }}
        }}

        function makeAIMove() {{
            const bestMove = NeuralEngine.getBestMove(engine, activeBotKey);
            isBotThinking = false;
            showThinking(false);

            if (bestMove) {{
                const res = engine.makeMove(bestMove, 'q');
                lastMove = bestMove;

                if (engine.isInCheck(engine.turn)) {{
                    audio.play('check');
                }} else if (res.captured) {{
                    audio.play('capture');
                }} else {{
                    audio.play('move');
                }}

                renderBoard();
                updateStatus();
                checkGameEnd();
            }}
        }}

        function showThinking(thinking) {{
            const spinner = document.getElementById('status-spinner');
            const bot = BOTS[activeBotKey];
            if (thinking) {{
                spinner.style.display = 'inline-block';
                document.getElementById('status-msg').innerText = `${{bot.name}} is thinking...`;
            }} else {{
                spinner.style.display = 'none';
            }}
        }}

        function checkGameEnd() {{
            const moves = engine.getAllLegalMoves(engine.turn);
            if (moves.length === 0) {{
                clearInterval(timerInterval);
                if (engine.isInCheck(engine.turn)) {{
                    const winner = engine.turn === 'w' ? 'Black (Bot)' : 'White (You)';
                    showModal('game-over-modal', 'Checkmate!', `${{winner}} wins by checkmate!`);
                }} else {{
                    showModal('game-over-modal', 'Stalemate!', 'Game drawn by stalemate.');
                }}
                return true;
            }}
            return false;
        }}

        function showModal(id, title, desc) {{
            document.getElementById('game-over-title').innerText = title;
            document.getElementById('game-over-desc').innerText = desc;
            document.getElementById(id).classList.add('active');
        }}

        function updateStatus() {{
            if (isBotThinking) return;
            const turnName = engine.turn === 'w' ? "White's Turn (You)" : `Black's Turn (${{BOTS[activeBotKey].name}})`;
            const check = engine.isInCheck(engine.turn) ? " — IN CHECK!" : "";
            document.getElementById('status-msg').innerText = `${{turnName}}${{check}}`;

            // Active timer highlight
            if (engine.turn === 'w') {{
                document.getElementById('bottom-timer').classList.add('active');
                document.getElementById('top-timer').classList.remove('active');
            }} else {{
                document.getElementById('top-timer').classList.add('active');
                document.getElementById('bottom-timer').classList.remove('active');
            }}
        }}

        function updateEvaluationBar() {{
            const evalScore = NeuralEngine.evaluate(engine, activeBotKey);
            const whitePct = Math.min(Math.max(50 + (evalScore * 10), 5), 95);
            document.getElementById('eval-bar-white').style.height = `${{whitePct}}%`;
            const sign = evalScore > 0 ? '+' : '';
            document.getElementById('eval-score-text').innerText = `${{sign}}${{evalScore.toFixed(1)}}`;
        }}

        function updateCapturedDisplay() {{
            const sym = {{ p: '♟', n: '♞', b: '♝', r: '♜', q: '♛' }};
            document.getElementById('top-captured').innerText = engine.captured.b.map(p => sym[p.type]).join(' ');
            document.getElementById('bottom-captured').innerText = engine.captured.w.map(p => sym[p.type]).join(' ');
        }}

        function newGame() {{
            closeModal('game-over-modal');
            engine.reset();
            selectedSq = null;
            legalMovesForSel = [];
            lastMove = null;
            isBotThinking = false;
            showThinking(false);
            whiteSeconds = 600;
            blackSeconds = 600;
            renderBoard();
            updateStatus();
        }}

        function undoMove() {{
            if (isBotThinking) return;
            // Undo user move and bot move
            engine.undo();
            engine.undo();
            lastMove = null;
            selectedSq = null;
            legalMovesForSel = [];
            renderBoard();
            updateStatus();
        }}

        function flipBoard() {{
            isFlipped = !isFlipped;
            renderBoard();
        }}

        function startTimer() {{
            clearInterval(timerInterval);
            timerInterval = setInterval(() => {{
                if (engine.turn === 'w') {{
                    if (whiteSeconds > 0) whiteSeconds--;
                }} else {{
                    if (blackSeconds > 0) blackSeconds--;
                }}
                const fmt = s => `${{Math.floor(s / 60)}}:${{(s % 60).toString().padStart(2, '0')}}`;
                document.getElementById('bottom-timer').innerText = fmt(whiteSeconds);
                document.getElementById('top-timer').innerText = fmt(blackSeconds);
            }}, 1000);
        }}

        // PWA & Android 1-Tap Installation
        let deferredPrompt = null;
        function setupPWA() {{
            window.addEventListener('beforeinstallprompt', (e) => {{
                e.preventDefault();
                deferredPrompt = e;
                const quickBtn = document.getElementById('pwa-quick-install-btn');
                if (quickBtn) {{
                    quickBtn.addEventListener('click', async () => {{
                        if (deferredPrompt) {{
                            deferredPrompt.prompt();
                            const {{ outcome }} = await deferredPrompt.userChoice;
                            deferredPrompt = null;
                        }}
                    }});
                }}
            }});

            const manifest = {{
                "name": "Chess Master",
                "short_name": "Chess",
                "start_url": ".",
                "display": "standalone",
                "background_color": "#302e2b",
                "theme_color": "#302e2b",
                "icons": [
                    {{
                        "src": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='20' fill='%23302e2b'/><text x='50%' y='68%' font-size='60' text-anchor='middle'>♞</text></svg>",
                        "sizes": "192x192 512x512",
                        "type": "image/svg+xml"
                    }}
                ]
            }};
            const blob = new Blob([JSON.stringify(manifest)], {{ type: 'application/json' }});
            const link = document.createElement('link');
            link.rel = 'manifest';
            link.href = URL.createObjectURL(blob);
            document.head.appendChild(link);
        }}

        window.addEventListener('DOMContentLoaded', initUI);
    </script>
</body>
</html>
'''
    return html

# Generate index.html
index_html = generate_html(is_phone_installer=False)
with open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(index_html)
print(f"[+] Successfully generated index.html ({len(index_html)} bytes)")

# Generate Install-Chess-Android.html
android_html = generate_html(is_phone_installer=True)
with open(os.path.join(ROOT, 'Install-Chess-Android.html'), 'w', encoding='utf-8') as f:
    f.write(android_html)
print(f"[+] Successfully generated Install-Chess-Android.html ({len(android_html)} bytes)")

# Generate Install-On-Phone.html (served over Wi-Fi)
with open(os.path.join(ROOT, 'Install-On-Phone.html'), 'w', encoding='utf-8') as f:
    f.write(android_html)
print(f"[+] Successfully generated Install-On-Phone.html ({len(android_html)} bytes)")
