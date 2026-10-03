import os

html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="theme-color" content="#302e2b">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Chess">
    <meta name="mobile-web-app-capable" content="yes">
    <title>Chess Master - Mobile & Desktop</title>
    <!-- Favicon / Icon -->
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>♞</text></svg>">
    
    <style>
        :root {
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
            --danger: #fa412d;
            --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            user-select: none;
            -webkit-user-select: none;
            -webkit-tap-highlight-color: transparent;
        }

        body {
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
        }

        /* Top Header Bar */
        .app-header {
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
        }

        .app-title-group {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .app-logo {
            font-size: 26px;
            line-height: 1;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.4));
        }

        .app-title {
            font-size: 19px;
            font-weight: 700;
            letter-spacing: 0.3px;
        }

        .header-actions {
            display: flex;
            gap: 8px;
        }

        .install-btn {
            background: linear-gradient(135deg, #81b64c, #5f9730);
            color: white;
            border: none;
            border-radius: 20px;
            padding: 6px 14px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.25);
            transition: transform 0.15s, background 0.15s;
        }

        .install-btn:active {
            transform: scale(0.96);
        }

        .icon-btn {
            background: rgba(255,255,255,0.08);
            border: none;
            color: var(--text-main);
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            transition: background 0.15s;
        }

        .icon-btn:hover {
            background: rgba(255,255,255,0.15);
        }

        /* Main Game Layout */
        .game-wrapper {
            width: 100%;
            max-width: 520px;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 4px 8px;
            flex: 1;
            justify-content: center;
        }

        /* Player Bar */
        .player-bar {
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 6px 10px;
            background: var(--bg-panel);
            border-radius: 8px;
            margin: 4px 0;
            box-shadow: 0 1px 4px rgba(0,0,0,0.2);
        }

        .player-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .player-avatar {
            width: 36px;
            height: 36px;
            border-radius: 6px;
            background: #403e3b;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 700;
            color: var(--text-muted);
            border: 1px solid rgba(255,255,255,0.1);
        }

        .player-name {
            font-size: 14px;
            font-weight: 600;
        }

        .player-sub {
            font-size: 11px;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .captured-pieces {
            display: flex;
            align-items: center;
            min-height: 18px;
            font-size: 14px;
            letter-spacing: -2px;
        }

        .material-diff {
            font-size: 11px;
            font-weight: 700;
            color: #d1d5db;
            margin-left: 4px;
        }

        .player-timer {
            background: #1e1d1a;
            padding: 6px 12px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 17px;
            font-weight: 700;
            letter-spacing: 1px;
            color: #b5b5b5;
            border: 1px solid rgba(255,255,255,0.05);
            transition: all 0.2s;
        }

        .player-timer.active {
            background: #f1f1f1;
            color: #1a1a1a;
            box-shadow: 0 0 12px rgba(255,255,255,0.25);
        }

        /* Chess Board Arena */
        .board-arena {
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            margin: 4px 0;
            position: relative;
        }

        /* Evaluation Bar */
        .eval-bar-container {
            width: 10px;
            height: min(92vw, 460px);
            background: #333;
            border-radius: 4px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        }

        .eval-bar-black {
            width: 100%;
            background: #222;
            height: 50%;
            transition: height 0.4s ease-out;
        }

        .eval-bar-white {
            width: 100%;
            background: #f0f0f0;
            flex: 1;
        }

        /* The Board */
        .board-container {
            position: relative;
            width: min(92vw, 460px);
            height: min(92vw, 460px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
            border-radius: 6px;
            overflow: hidden;
        }

        .board-grid {
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            grid-template-rows: repeat(8, 1fr);
            width: 100%;
            height: 100%;
        }

        .square {
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: background-color 0.1s;
        }

        .square.light {
            background-color: var(--light-sq);
        }

        .square.dark {
            background-color: var(--dark-sq);
        }

        .square.selected {
            background-color: var(--highlight-sel) !important;
        }

        .square.last-move {
            background-color: var(--highlight-move) !important;
        }

        .square.in-check {
            background: radial-gradient(circle, #ff2a2a 0%, var(--dark-sq) 85%) !important;
        }

        .square.light.in-check {
            background: radial-gradient(circle, #ff2a2a 0%, var(--light-sq) 85%) !important;
        }

        /* Move Hint Indicators */
        .hint-dot {
            width: 32%;
            height: 32%;
            background-color: var(--hint-dot);
            border-radius: 50%;
            pointer-events: none;
            z-index: 2;
        }

        .hint-ring {
            position: absolute;
            width: 90%;
            height: 90%;
            border-radius: 50%;
            border: 6px solid var(--hint-ring);
            pointer-events: none;
            z-index: 2;
        }

        /* Coordinates */
        .coord {
            position: absolute;
            font-size: 10px;
            font-weight: 700;
            pointer-events: none;
            z-index: 1;
        }

        .coord.rank {
            top: 2px;
            left: 2px;
        }

        .coord.file {
            bottom: 1px;
            right: 2px;
        }

        .square.light .coord {
            color: var(--dark-sq);
        }

        .square.dark .coord {
            color: var(--light-sq);
        }

        /* Piece Graphic */
        .piece {
            width: 92%;
            height: 92%;
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            z-index: 3;
            pointer-events: none;
            transition: transform 0.15s ease-out;
            filter: drop-shadow(0 2px 3px rgba(0,0,0,0.35));
        }

        /* Bottom Controls */
        .controls-bar {
            width: 100%;
            max-width: 520px;
            display: flex;
            gap: 8px;
            padding: 10px 16px;
            background: var(--bg-panel);
            border-top: 1px solid rgba(255,255,255,0.06);
            justify-content: space-around;
        }

        .btn {
            flex: 1;
            padding: 10px 8px;
            border-radius: 8px;
            border: none;
            font-weight: 600;
            font-size: 13px;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 4px;
            color: white;
            background: rgba(255,255,255,0.08);
            transition: all 0.15s;
        }

        .btn:active {
            transform: scale(0.96);
            background: rgba(255,255,255,0.15);
        }

        .btn.primary {
            background: linear-gradient(135deg, #81b64c, #5f9730);
        }

        .btn-icon {
            font-size: 13px;
            font-weight: 700;
        }

        /* Modals & Overlays */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.75);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 100;
            padding: 20px;
            backdrop-filter: blur(4px);
        }

        .modal-overlay.active {
            display: flex;
        }

        .modal-card {
            background: var(--bg-panel);
            border-radius: 14px;
            padding: 24px;
            width: 100%;
            max-width: 360px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.6);
            border: 1px solid rgba(255,255,255,0.1);
            animation: popIn 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }

        @keyframes popIn {
            from { transform: scale(0.85); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }

        .modal-title {
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .modal-subtitle {
            font-size: 14px;
            color: var(--text-muted);
            margin-bottom: 20px;
            line-height: 1.4;
        }

        .modal-btn-group {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .modal-btn {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            border: none;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            background: rgba(255,255,255,0.1);
            color: white;
            transition: 0.15s;
        }

        .modal-btn.primary {
            background: var(--accent-green);
        }

        .modal-btn:active {
            transform: scale(0.98);
        }

        /* Promotion Picker */
        .promo-options {
            display: flex;
            justify-content: center;
            gap: 12px;
            margin: 16px 0;
        }

        .promo-choice {
            width: 60px;
            height: 60px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: 0.15s;
        }

        .promo-choice:hover, .promo-choice:active {
            background: var(--accent-green);
            transform: scale(1.1);
        }

        .promo-choice .piece {
            width: 48px;
            height: 48px;
        }

        /* Status Toast */
        .toast {
            position: fixed;
            top: 70px;
            left: 50%;
            transform: translateX(-50%) translateY(-20px);
            background: rgba(30, 29, 26, 0.95);
            color: white;
            padding: 8px 18px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            border: 1px solid rgba(255,255,255,0.1);
            opacity: 0;
            pointer-events: none;
            transition: all 0.25s ease-out;
            z-index: 50;
        }

        .toast.visible {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }
    </style>
</head>
<body>

    <!-- Header -->
    <header class="app-header">
        <div class="app-title-group">
            <span class="app-logo">♟️</span>
            <div>
                <h1 class="app-title">Chess Master</h1>
            </div>
        </div>
        <div class="header-actions">
            <button id="pwa-install-btn" class="install-btn" style="display:none;">
                <span>Install App</span>
            </button>
            <button id="mode-btn" class="icon-btn" title="Game Mode">Settings</button>
        </div>
    </header>

    <!-- Game Wrapper -->
    <main class="game-wrapper">

        <!-- Top Player (Black) -->
        <div class="player-bar">
            <div class="player-info">
                <div class="player-avatar" id="top-avatar">Bot</div>
                <div>
                    <div class="player-name" id="top-name">Computer (AI)</div>
                    <div class="player-sub">
                        <div class="captured-pieces" id="top-captured"></div>
                        <span class="material-diff" id="top-diff"></span>
                    </div>
                </div>
            </div>
            <div class="player-timer" id="top-timer">10:00</div>
        </div>

        <!-- Board Arena -->
        <div class="board-arena">
            <div class="eval-bar-container">
                <div class="eval-bar-black" id="eval-bar-black"></div>
                <div class="eval-bar-white"></div>
            </div>

            <div class="board-container">
                <div class="board-grid" id="chess-board"></div>
            </div>
        </div>

        <!-- Bottom Player (White) -->
        <div class="player-bar">
            <div class="player-info">
                <div class="player-avatar" id="bottom-avatar">You</div>
                <div>
                    <div class="player-name" id="bottom-name">You (White)</div>
                    <div class="player-sub">
                        <div class="captured-pieces" id="bottom-captured"></div>
                        <span class="material-diff" id="bottom-diff"></span>
                    </div>
                </div>
            </div>
            <div class="player-timer active" id="bottom-timer">10:00</div>
        </div>

    </main>

    <!-- Bottom Controls -->
    <footer class="controls-bar">
        <button class="btn primary" id="new-game-btn">
            <span class="btn-icon">+</span>
            <span>New Game</span>
        </button>
        <button class="btn" id="flip-board-btn">
            <span class="btn-icon">&#8693;</span>
            <span>Flip</span>
        </button>
        <button class="btn" id="undo-btn">
            <span class="btn-icon">&#8617;</span>
            <span>Undo</span>
        </button>
        <button class="btn" id="game-info-btn">
            <span class="btn-icon">AI</span>
            <span>Modes</span>
        </button>
    </footer>

    <!-- Promotion Modal -->
    <div class="modal-overlay" id="promo-modal">
        <div class="modal-card">
            <h2 class="modal-title">Pawn Promotion</h2>
            <p class="modal-subtitle">Choose which piece you want to promote your pawn to:</p>
            <div class="promo-options" id="promo-options"></div>
        </div>
    </div>

    <!-- Game Over Modal -->
    <div class="modal-overlay" id="game-over-modal">
        <div class="modal-card">
            <h2 class="modal-title" id="game-over-title">Game Over</h2>
            <p class="modal-subtitle" id="game-over-desc">Checkmate! White wins the game.</p>
            <div class="modal-btn-group">
                <button class="modal-btn primary" id="play-again-btn">Play Again</button>
                <button class="modal-btn" onclick="closeModal('game-over-modal')">Review Board</button>
            </div>
        </div>
    </div>

    <!-- Modes & Settings Modal -->
    <div class="modal-overlay" id="settings-modal">
        <div class="modal-card">
            <h2 class="modal-title">Game Options</h2>
            <p class="modal-subtitle">Select game mode and difficulty:</p>
            <div class="modal-btn-group">
                <button class="modal-btn primary" onclick="setMode('ai-easy')">vs Computer (Easy)</button>
                <button class="modal-btn primary" onclick="setMode('ai-medium')">vs Computer (Medium)</button>
                <button class="modal-btn primary" onclick="setMode('ai-hard')">vs Computer (Hard)</button>
                <button class="modal-btn" onclick="setMode('pass-and-play')">2 Players (Pass & Play)</button>
                <button class="modal-btn" onclick="setMode('pawns-only')">Pawns Only Battle</button>
                <button class="modal-btn" onclick="setMode('knights-only')">♞ Knights Only Rampage</button>
                <button class="modal-btn" style="background:#555;" onclick="closeModal('settings-modal')">Close</button>
            </div>
        </div>
    </div>

    <!-- Toast Notification -->
    <div class="toast" id="toast">White to move</div>

    <!-- Embedded Scripts -->
    <script>
        /* ============================================================
           1. PIECE SVGS (High-DPI Vector Art)
           ============================================================ */
        const PIECE_SVGS = {
            'wp': '<svg viewBox="0 0 45 45"><path d="m 22.5,9 c -2.21,0 -4,1.79 -4,4 0,0.89 0.29,1.71 0.78,2.38 C 17.33,16.5 16,18.59 16,21 c 0,2.03 0.94,3.84 2.41,5.03 C 15.41,27.09 11,31.58 11,39.5 l 23,0 c 0,-7.92 -4.41,-12.41 -7.41,-13.47 C 28.06,24.84 29,23.03 29,21 29,18.59 27.67,16.5 25.72,15.38 26.21,14.71 26.5,13.89 26.5,13 c 0,-2.21 -1.79,-4 -4,-4 z" fill="#fff" stroke="#000" stroke-width="1.5" stroke-linecap="round"/></svg>',
            'wn': '<svg viewBox="0 0 45 45"><path d="m 22,10 c 10.5,1 16.5,8 16,29 L 15,39 C 15,30 11.5,23.5 11,18 c -0.5,-5.5 4,-9 8,-9.5 0.5,0.5 1.5,1.5 2,2.5 z" fill="#fff" stroke="#000" stroke-width="1.5"/><path d="M 24,18 C 24,18 28,16 29,20 C 30,24 27,27 27,27" fill="none" stroke="#000" stroke-width="1.5"/><circle cx="27" cy="16" r="1.5" fill="#000"/></svg>',
            'wb': '<svg viewBox="0 0 45 45"><path d="M 9,36 C 12.39,35.03 19.11,36.43 22.5,34 C 25.89,36.43 32.61,35.03 36,36 C 36,36 37.65,36.54 39,38 C 38.32,38.97 37.35,38.99 36,38.5 C 32.61,37.53 25.89,38.96 22.5,37.5 C 19.11,38.96 12.39,37.53 9,38.5 C 7.646,38.99 6.677,38.97 6,38 C 7.354,36.54 9,36 9,36 z" fill="#fff" stroke="#000" stroke-width="1.5"/><path d="M 15,32 C 17.5,34.5 27.5,34.5 30,32 C 30.5,30.5 30,30 30,30 C 30,27.5 27.5,26 27.5,26 C 33,24.5 33.5,14.5 22.5,10.5 C 11.5,14.5 12,24.5 17.5,26 C 17.5,26 15,27.5 15,30 C 15,30 14.5,30.5 15,32 z" fill="#fff" stroke="#000" stroke-width="1.5"/><circle cx="22.5" cy="8" r="1.5" fill="#fff" stroke="#000" stroke-width="1.5"/></svg>',
            'wr': '<svg viewBox="0 0 45 45"><path d="m 9,39 27,0 0,-3 -27,0 z" fill="#fff" stroke="#000" stroke-width="1.5"/><path d="m 12,36 21,0 0,-4 -21,0 z" fill="#fff" stroke="#000" stroke-width="1.5"/><path d="m 14,32 17,0 -1,-18 -15,0 z" fill="#fff" stroke="#000" stroke-width="1.5"/><path d="m 9,14 27,0 0,-5 -4,0 0,2 -5,0 0,-2 -6,0 0,2 -5,0 0,-2 -7,0 z" fill="#fff" stroke="#000" stroke-width="1.5"/></svg>',
            'wq': '<svg viewBox="0 0 45 45"><path d="m 9,26 c 8.5,-1.5 21,-1.5 27,0 l 2,-12 -7,5 -4,-9 -4.5,9 -4.5,-9 -4,9 -7,-5 2,12 z" fill="#fff" stroke="#000" stroke-width="1.5"/><path d="m 9,26 c 0,2 1.5,2 2.5,4 1,1.5 1,1 0.5,3.5 -1.5,1 -1.5,2.5 -1.5,2.5 -1.5,1.5 0.5,2.5 0.5,2.5 6.5,1 16.5,1 23,0 0,0 1.5,-1 0.5,-2.5 0,0 0,-1.5 -1.5,-2.5 -0.5,-2.5 -0.5,-2 0.5,-3.5 1,-2 2.5,-2 2.5,-4-8.5,-1.5 -18.5,-1.5 -27,0 z" fill="#fff" stroke="#000" stroke-width="1.5"/><circle cx="6" cy="12" r="2" fill="#fff" stroke="#000"/><circle cx="14" cy="9" r="2" fill="#fff" stroke="#000"/><circle cx="22.5" cy="8" r="2" fill="#fff" stroke="#000"/><circle cx="31" cy="9" r="2" fill="#fff" stroke="#000"/><circle cx="39" cy="12" r="2" fill="#fff" stroke="#000"/></svg>',
            'wk': '<svg viewBox="0 0 45 45"><path d="M 22.5,11.63 L 22.5,6" stroke="#000" stroke-width="1.5"/><path d="M 20,8 L 25,8" stroke="#000" stroke-width="1.5"/><path d="M 22.5,25 C 22.5,25 27,17.5 25.5,14.5 C 24,11.5 21,11.5 19.5,14.5 C 18,17.5 22.5,25 22.5,25 Z" fill="#fff" stroke="#000" stroke-width="1.5"/><path d="M 11.5,37 C 17,40.5 28,40.5 33.5,37 C 33.5,37 36.5,28 36.5,24 C 36.5,20 33,18 33,18 C 30.5,19.5 27.5,19 22.5,19 C 17.5,19 14.5,19.5 12,18 C 12,18 8.5,20 8.5,24 C 8.5,28 11.5,37 11.5,37 Z" fill="#fff" stroke="#000" stroke-width="1.5"/><path d="M 11.5,30 C 17,27 28,27 33.5,30" fill="none" stroke="#000" stroke-width="1.5"/></svg>',
            'bp': '<svg viewBox="0 0 45 45"><path d="m 22.5,9 c -2.21,0 -4,1.79 -4,4 0,0.89 0.29,1.71 0.78,2.38 C 17.33,16.5 16,18.59 16,21 c 0,2.03 0.94,3.84 2.41,5.03 C 15.41,27.09 11,31.58 11,39.5 l 23,0 c 0,-7.92 -4.41,-12.41 -7.41,-13.47 C 28.06,24.84 29,23.03 29,21 29,18.59 27.67,16.5 25.72,15.38 26.21,14.71 26.5,13.89 26.5,13 c 0,-2.21 -1.79,-4 -4,-4 z" fill="#1e1e1e" stroke="#fff" stroke-width="1.5"/></svg>',
            'bn': '<svg viewBox="0 0 45 45"><path d="m 22,10 c 10.5,1 16.5,8 16,29 L 15,39 C 15,30 11.5,23.5 11,18 c -0.5,-5.5 4,-9 8,-9.5 0.5,0.5 1.5,1.5 2,2.5 z" fill="#1e1e1e" stroke="#fff" stroke-width="1.5"/><circle cx="27" cy="16" r="1.5" fill="#fff"/></svg>',
            'bb': '<svg viewBox="0 0 45 45"><path d="M 9,36 C 12.39,35.03 19.11,36.43 22.5,34 C 25.89,36.43 32.61,35.03 36,36 C 36,36 37.65,36.54 39,38 C 38.32,38.97 37.35,38.99 36,38.5 C 32.61,37.53 25.89,38.96 22.5,37.5 C 19.11,38.96 12.39,37.53 9,38.5 C 7.646,38.99 6.677,38.97 6,38 C 7.354,36.54 9,36 9,36 z" fill="#1e1e1e" stroke="#fff" stroke-width="1.5"/><path d="M 15,32 C 17.5,34.5 27.5,34.5 30,32 C 30.5,30.5 30,30 30,30 C 30,27.5 27.5,26 27.5,26 C 33,24.5 33.5,14.5 22.5,10.5 C 11.5,14.5 12,24.5 17.5,26 C 17.5,26 15,27.5 15,30 C 15,30 14.5,30.5 15,32 z" fill="#1e1e1e" stroke="#fff" stroke-width="1.5"/><circle cx="22.5" cy="8" r="1.5" fill="#1e1e1e" stroke="#fff" stroke-width="1.5"/></svg>',
            'br': '<svg viewBox="0 0 45 45"><path d="m 9,39 27,0 0,-3 -27,0 z" fill="#1e1e1e" stroke="#fff" stroke-width="1.5"/><path d="m 12,36 21,0 0,-4 -21,0 z" fill="#1e1e1e" stroke="#fff" stroke-width="1.5"/><path d="m 14,32 17,0 -1,-18 -15,0 z" fill="#1e1e1e" stroke="#fff" stroke-width="1.5"/><path d="m 9,14 27,0 0,-5 -4,0 0,2 -5,0 0,-2 -6,0 0,2 -5,0 0,-2 -7,0 z" fill="#1e1e1e" stroke="#fff" stroke-width="1.5"/></svg>',
            'bq': '<svg viewBox="0 0 45 45"><path d="m 9,26 c 8.5,-1.5 21,-1.5 27,0 l 2,-12 -7,5 -4,-9 -4.5,9 -4.5,-9 -4,9 -7,-5 2,12 z" fill="#1e1e1e" stroke="#fff" stroke-width="1.5"/><path d="m 9,26 c 0,2 1.5,2 2.5,4 1,1.5 1,1 0.5,3.5 -1.5,1 -1.5,2.5 -1.5,2.5 -1.5,1.5 0.5,2.5 0.5,2.5 6.5,1 16.5,1 23,0 0,0 1.5,-1 0.5,-2.5 0,0 0,-1.5 -1.5,-2.5 -0.5,-2.5 -0.5,-2 0.5,-3.5 1,-2 2.5,-2 2.5,-4-8.5,-1.5 -18.5,-1.5 -27,0 z" fill="#1e1e1e" stroke="#fff" stroke-width="1.5"/><circle cx="6" cy="12" r="2" fill="#1e1e1e" stroke="#fff"/><circle cx="14" cy="9" r="2" fill="#1e1e1e" stroke="#fff"/><circle cx="22.5" cy="8" r="2" fill="#1e1e1e" stroke="#fff"/><circle cx="31" cy="9" r="2" fill="#1e1e1e" stroke="#fff"/><circle cx="39" cy="12" r="2" fill="#1e1e1e" stroke="#fff"/></svg>',
            'bk': '<svg viewBox="0 0 45 45"><path d="M 22.5,11.63 L 22.5,6" stroke="#fff" stroke-width="1.5"/><path d="M 20,8 L 25,8" stroke="#fff" stroke-width="1.5"/><path d="M 22.5,25 C 22.5,25 27,17.5 25.5,14.5 C 24,11.5 21,11.5 19.5,14.5 C 18,17.5 22.5,25 22.5,25 Z" fill="#1e1e1e" stroke="#fff" stroke-width="1.5"/><path d="M 11.5,37 C 17,40.5 28,40.5 33.5,37 C 33.5,37 36.5,28 36.5,24 C 36.5,20 33,18 33,18 C 30.5,19.5 27.5,19 22.5,19 C 17.5,19 14.5,19.5 12,18 C 12,18 8.5,20 8.5,24 C 8.5,28 11.5,37 11.5,37 Z" fill="#1e1e1e" stroke="#fff" stroke-width="1.5"/><path d="M 11.5,30 C 17,27 28,27 33.5,30" fill="none" stroke="#fff" stroke-width="1.5"/></svg>'
        };

        /* ============================================================
           2. SOUND SYNTHESIZER (Identical to Java App's Sine Waves)
           ============================================================ */
        class ChessAudio {
            constructor() {
                this.ctx = null;
            }

            init() {
                if (!this.ctx) {
                    const AudioContext = window.AudioContext || window.webkitAudioContext;
                    if (AudioContext) this.ctx = new AudioContext();
                }
                if (this.ctx && this.ctx.state === 'suspended') {
                    this.ctx.resume();
                }
            }

            play(type) {
                try {
                    this.init();
                    if (!this.ctx) return;

                    const now = this.ctx.currentTime;
                    const osc = this.ctx.createOscillator();
                    const gain = this.ctx.createGain();
                    osc.connect(gain);
                    gain.connect(this.ctx.destination);

                    if (type === 'move') {
                        // 440 Hz exponential decay (40ms)
                        osc.frequency.setValueAtTime(440, now);
                        gain.gain.setValueAtTime(0.3, now);
                        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);
                        osc.start(now);
                        osc.stop(now + 0.05);
                    } else if (type === 'capture') {
                        // 250 Hz decay (75ms)
                        osc.frequency.setValueAtTime(250, now);
                        gain.gain.setValueAtTime(0.4, now);
                        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
                        osc.start(now);
                        osc.stop(now + 0.08);
                    } else if (type === 'illegal') {
                        // 140 Hz decay (110ms)
                        osc.frequency.setValueAtTime(140, now);
                        gain.gain.setValueAtTime(0.35, now);
                        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);
                        osc.start(now);
                        osc.stop(now + 0.12);
                    } else if (type === 'check') {
                        // Dual chime
                        osc.frequency.setValueAtTime(587.33, now);
                        osc.frequency.setValueAtTime(880, now + 0.08);
                        gain.gain.setValueAtTime(0.3, now);
                        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
                        osc.start(now);
                        osc.stop(now + 0.25);
                    }
                } catch(e) {}
            }
        }
        const audio = new ChessAudio();

        /* ============================================================
           3. CHESS ENGINE CORE (Full Rules: Castling, En Passant, Prom)
           ============================================================ */
        class ChessEngine {
            constructor() {
                this.reset();
            }

            reset(mode = 'standard') {
                this.board = Array(8).fill(null).map(() => Array(8).fill(null));
                this.turn = 'w'; // 'w' or 'b'
                this.castling = { wK: true, wQ: true, bK: true, bQ: true };
                this.epSquare = null; // [r, c]
                this.halfMoveClock = 0;
                this.fullMoveNumber = 1;
                this.history = [];
                this.captured = { w: [], b: [] };

                if (mode === 'pawns-only') {
                    for (let c = 0; c < 8; c++) {
                        this.board[1][c] = { color: 'b', type: 'p' };
                        this.board[6][c] = { color: 'w', type: 'p' };
                    }
                    this.board[0][4] = { color: 'b', type: 'k' };
                    this.board[7][4] = { color: 'w', type: 'k' };
                } else if (mode === 'knights-only') {
                    for (let c = 0; c < 8; c++) {
                        this.board[1][c] = { color: 'b', type: 'n' };
                        this.board[6][c] = { color: 'w', type: 'n' };
                    }
                    this.board[0][4] = { color: 'b', type: 'k' };
                    this.board[7][4] = { color: 'w', type: 'k' };
                } else {
                    const rowOrder = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'];
                    for (let c = 0; c < 8; c++) {
                        this.board[0][c] = { color: 'b', type: rowOrder[c] };
                        this.board[1][c] = { color: 'b', type: 'p' };
                        this.board[6][c] = { color: 'w', type: 'p' };
                        this.board[7][c] = { color: 'w', type: rowOrder[c] };
                    }
                }
            }

            cloneBoard() {
                return this.board.map(row => row.map(p => p ? { ...p } : null));
            }

            isSquareAttacked(r, c, byColor, board = this.board) {
                // Pawns
                const pForward = (byColor === 'w') ? -1 : 1;
                const pCapR = r - pForward;
                if (pCapR >= 0 && pCapR < 8) {
                    for (const dc of [-1, 1]) {
                        const pc = c + dc;
                        if (pc >= 0 && pc < 8) {
                            const p = board[pCapR][pc];
                            if (p && p.color === byColor && p.type === 'p') return true;
                        }
                    }
                }

                // Knights
                const knDeltas = [[-2,-1],[-2,1],[-1,-2],[-1,2],[1,-2],[1,2],[2,-1],[2,1]];
                for (const [dr, dc] of knDeltas) {
                    const nr = r + dr, nc = c + dc;
                    if (nr >= 0 && nr < 8 && nc >= 0 && nc < 8) {
                        const p = board[nr][nc];
                        if (p && p.color === byColor && p.type === 'n') return true;
                    }
                }

                // King
                for (let dr = -1; dr <= 1; dr++) {
                    for (let dc = -1; dc <= 1; dc++) {
                        if (dr === 0 && dc === 0) continue;
                        const nr = r + dr, nc = c + dc;
                        if (nr >= 0 && nr < 8 && nc >= 0 && nc < 8) {
                            const p = board[nr][nc];
                            if (p && p.color === byColor && p.type === 'k') return true;
                        }
                    }
                }

                // Straight rays (Rook / Queen)
                const straight = [[-1,0],[1,0],[0,-1],[0,1]];
                for (const [dr, dc] of straight) {
                    let nr = r + dr, nc = c + dc;
                    while (nr >= 0 && nr < 8 && nc >= 0 && nc < 8) {
                        const p = board[nr][nc];
                        if (p) {
                            if (p.color === byColor && (p.type === 'r' || p.type === 'q')) return true;
                            break;
                        }
                        nr += dr; nc += dc;
                    }
                }

                // Diagonal rays (Bishop / Queen)
                const diagonal = [[-1,-1],[-1,1],[1,-1],[1,1]];
                for (const [dr, dc] of diagonal) {
                    let nr = r + dr, nc = c + dc;
                    while (nr >= 0 && nr < 8 && nc >= 0 && nc < 8) {
                        const p = board[nr][nc];
                        if (p) {
                            if (p.color === byColor && (p.type === 'b' || p.type === 'q')) return true;
                            break;
                        }
                        nr += dr; nc += dc;
                    }
                }

                return false;
            }

            findKing(color, board = this.board) {
                for (let r = 0; r < 8; r++) {
                    for (let c = 0; c < 8; c++) {
                        const p = board[r][c];
                        if (p && p.color === color && p.type === 'k') return [r, c];
                    }
                }
                return null;
            }

            isInCheck(color, board = this.board) {
                const kingPos = this.findKing(color, board);
                if (!kingPos) return false;
                const opp = color === 'w' ? 'b' : 'w';
                return this.isSquareAttacked(kingPos[0], kingPos[1], opp, board);
            }

            getLegalMoves(r, c) {
                const piece = this.board[r][c];
                if (!piece || piece.color !== this.turn) return [];
                const pseudo = this.getPseudoMoves(r, c);
                const legal = [];

                for (const m of pseudo) {
                    // Test on simulated board
                    const sim = this.cloneBoard();
                    sim[m.toR][m.toC] = sim[m.fromR][m.fromC];
                    sim[m.fromR][m.fromC] = null;

                    // En passant capture simulation
                    if (m.isEp) {
                        sim[m.fromR][m.toC] = null;
                    }

                    if (!this.isInCheck(piece.color, sim)) {
                        legal.push(m);
                    }
                }

                return legal;
            }

            getPseudoMoves(r, c) {
                const piece = this.board[r][c];
                if (!piece) return [];
                const moves = [];
                const color = piece.color;
                const opp = color === 'w' ? 'b' : 'w';
                const forward = color === 'w' ? -1 : 1;

                if (piece.type === 'p') {
                    // Single forward
                    const oneR = r + forward;
                    if (oneR >= 0 && oneR < 8 && !this.board[oneR][c]) {
                        const isPromo = (oneR === 0 || oneR === 7);
                        moves.push({ fromR: r, fromC: c, toR: oneR, toC: c, isPromo });
                        // Double forward
                        const startR = color === 'w' ? 6 : 1;
                        const twoR = r + 2 * forward;
                        if (r === startR && !this.board[twoR][c]) {
                            moves.push({ fromR: r, fromC: c, toR: twoR, toC: c, isDouble: true });
                        }
                    }

                    // Captures
                    for (const dc of [-1, 1]) {
                        const nc = c + dc;
                        if (nc >= 0 && nc < 8 && oneR >= 0 && oneR < 8) {
                            const dest = this.board[oneR][nc];
                            if (dest && dest.color === opp) {
                                const isPromo = (oneR === 0 || oneR === 7);
                                moves.push({ fromR: r, fromC: c, toR: oneR, toC: nc, isPromo, isCapture: true });
                            } else if (this.epSquare && this.epSquare[0] === oneR && this.epSquare[1] === nc) {
                                moves.push({ fromR: r, fromC: c, toR: oneR, toC: nc, isEp: true, isCapture: true });
                            }
                        }
                    }
                } else if (piece.type === 'n') {
                    const deltas = [[-2,-1],[-2,1],[-1,-2],[-1,2],[1,-2],[1,2],[2,-1],[2,1]];
                    for (const [dr, dc] of deltas) {
                        const nr = r + dr, nc = c + dc;
                        if (nr >= 0 && nr < 8 && nc >= 0 && nc < 8) {
                            const dest = this.board[nr][nc];
                            if (!dest || dest.color === opp) {
                                moves.push({ fromR: r, fromC: c, toR: nr, toC: nc, isCapture: !!dest });
                            }
                        }
                    }
                } else if (piece.type === 'b') {
                    this.addRayMoves(r, c, [[-1,-1],[-1,1],[1,-1],[1,1]], moves);
                } else if (piece.type === 'r') {
                    this.addRayMoves(r, c, [[-1,0],[1,0],[0,-1],[0,1]], moves);
                } else if (piece.type === 'q') {
                    this.addRayMoves(r, c, [[-1,-1],[-1,1],[1,-1],[1,1],[-1,0],[1,0],[0,-1],[0,1]], moves);
                } else if (piece.type === 'k') {
                    for (let dr = -1; dr <= 1; dr++) {
                        for (let dc = -1; dc <= 1; dc++) {
                            if (dr === 0 && dc === 0) continue;
                            const nr = r + dr, nc = c + dc;
                            if (nr >= 0 && nr < 8 && nc >= 0 && nc < 8) {
                                const dest = this.board[nr][nc];
                                if (!dest || dest.color === opp) {
                                    moves.push({ fromR: r, fromC: c, toR: nr, toC: nc, isCapture: !!dest });
                                }
                            }
                        }
                    }

                    // Castling
                    if (!this.isInCheck(color)) {
                        if (color === 'w' && r === 7 && c === 4) {
                            if (this.castling.wK && !this.board[7][5] && !this.board[7][6] &&
                                !this.isSquareAttacked(7, 5, 'b') && !this.isSquareAttacked(7, 6, 'b')) {
                                moves.push({ fromR: 7, fromC: 4, toR: 7, toC: 6, isCastleK: true });
                            }
                            if (this.castling.wQ && !this.board[7][3] && !this.board[7][2] && !this.board[7][1] &&
                                !this.isSquareAttacked(7, 3, 'b') && !this.isSquareAttacked(7, 2, 'b')) {
                                moves.push({ fromR: 7, fromC: 4, toR: 7, toC: 2, isCastleQ: true });
                            }
                        } else if (color === 'b' && r === 0 && c === 4) {
                            if (this.castling.bK && !this.board[0][5] && !this.board[0][6] &&
                                !this.isSquareAttacked(0, 5, 'w') && !this.isSquareAttacked(0, 6, 'w')) {
                                moves.push({ fromR: 0, fromC: 4, toR: 0, toC: 6, isCastleK: true });
                            }
                            if (this.castling.bQ && !this.board[0][3] && !this.board[0][2] && !this.board[0][1] &&
                                !this.isSquareAttacked(0, 3, 'w') && !this.isSquareAttacked(0, 2, 'w')) {
                                moves.push({ fromR: 0, fromC: 4, toR: 0, toC: 2, isCastleQ: true });
                            }
                        }
                    }
                }

                return moves;
            }

            addRayMoves(r, c, dirs, moves) {
                const color = this.board[r][c].color;
                const opp = color === 'w' ? 'b' : 'w';
                for (const [dr, dc] of dirs) {
                    let nr = r + dr, nc = c + dc;
                    while (nr >= 0 && nr < 8 && nc >= 0 && nc < 8) {
                        const dest = this.board[nr][nc];
                        if (!dest) {
                            moves.push({ fromR: r, fromC: c, toR: nr, toC: nc, isCapture: false });
                        } else {
                            if (dest.color === opp) {
                                moves.push({ fromR: r, fromC: c, toR: nr, toC: nc, isCapture: true });
                            }
                            break;
                        }
                        nr += dr; nc += dc;
                    }
                }
            }

            getAllLegalMoves(color = this.turn) {
                const all = [];
                for (let r = 0; r < 8; r++) {
                    for (let c = 0; c < 8; c++) {
                        const p = this.board[r][c];
                        if (p && p.color === color) {
                            all.push(...this.getLegalMoves(r, c));
                        }
                    }
                }
                return all;
            }

            makeMove(m, promoChoice = 'q') {
                const p = this.board[m.fromR][m.fromC];
                let capturedPiece = this.board[m.toR][m.toC];

                // Save undo state
                this.history.push({
                    board: this.cloneBoard(),
                    turn: this.turn,
                    castling: { ...this.castling },
                    epSquare: this.epSquare ? [...this.epSquare] : null,
                    captured: { w: [...this.captured.w], b: [...this.captured.b] },
                    lastMove: m
                });

                // Move piece
                this.board[m.toR][m.toC] = p;
                this.board[m.fromR][m.fromC] = null;

                // En Passant capture
                if (m.isEp) {
                    capturedPiece = this.board[m.fromR][m.toC];
                    this.board[m.fromR][m.toC] = null;
                }

                // Add to captured
                if (capturedPiece) {
                    this.captured[this.turn].push(capturedPiece);
                }

                // Promotion
                if (m.isPromo) {
                    p.type = promoChoice;
                }

                // Castling move rooks
                if (m.isCastleK) {
                    const rank = p.color === 'w' ? 7 : 0;
                    this.board[rank][5] = this.board[rank][7];
                    this.board[rank][7] = null;
                } else if (m.isCastleQ) {
                    const rank = p.color === 'w' ? 7 : 0;
                    this.board[rank][3] = this.board[rank][0];
                    this.board[rank][0] = null;
                }

                // Update Castling rights
                if (p.type === 'k') {
                    if (p.color === 'w') { this.castling.wK = false; this.castling.wQ = false; }
                    else { this.castling.bK = false; this.castling.bQ = false; }
                } else if (p.type === 'r') {
                    if (m.fromR === 7 && m.fromC === 7) this.castling.wK = false;
                    if (m.fromR === 7 && m.fromC === 0) this.castling.wQ = false;
                    if (m.fromR === 0 && m.fromC === 7) this.castling.bK = false;
                    if (m.fromR === 0 && m.fromC === 0) this.castling.bQ = false;
                }

                // Update En Passant target
                if (m.isDouble) {
                    const forward = p.color === 'w' ? -1 : 1;
                    this.epSquare = [m.fromR + forward, m.fromC];
                } else {
                    this.epSquare = null;
                }

                // Switch turn
                this.turn = (this.turn === 'w') ? 'b' : 'w';

                return { captured: !!capturedPiece };
            }

            undo() {
                if (this.history.length === 0) return null;
                const state = this.history.pop();
                this.board = state.board;
                this.turn = state.turn;
                this.castling = state.castling;
                this.epSquare = state.epSquare;
                this.captured = state.captured;
                return state.lastMove;
            }

            evaluateMaterial() {
                const values = { p: 1, n: 3, b: 3, r: 5, q: 9, k: 0 };
                let score = 0;
                for (let r = 0; r < 8; r++) {
                    for (let c = 0; c < 8; c++) {
                        const p = this.board[r][c];
                        if (p) {
                            const val = values[p.type] || 0;
                            score += (p.color === 'w' ? val : -val);
                        }
                    }
                }
                return score;
            }
        }

        /* ============================================================
           4. MINIMAX AI ENGINE
           ============================================================ */
        class ChessAI {
            static pieceVal = { p: 100, n: 320, b: 330, r: 500, q: 900, k: 20000 };

            static evaluate(engine) {
                let score = 0;
                for (let r = 0; r < 8; r++) {
                    for (let c = 0; c < 8; c++) {
                        const p = engine.board[r][c];
                        if (p) {
                            let val = this.pieceVal[p.type] || 0;
                            // Small center bonus
                            if ((r === 3 || r === 4) && (c === 3 || c === 4)) val += 15;
                            score += (p.color === 'w' ? val : -val);
                        }
                    }
                }
                return score;
            }

            static getBestMove(engine, depth = 2) {
                const moves = engine.getAllLegalMoves('b');
                if (moves.length === 0) return null;

                // Shuffle for variety
                moves.sort(() => Math.random() - 0.5);

                let bestScore = Infinity;
                let bestMove = moves[0];

                for (const m of moves) {
                    engine.makeMove(m);
                    const score = this.minimax(engine, depth - 1, -Infinity, Infinity, true);
                    engine.undo();

                    if (score < bestScore) {
                        bestScore = score;
                        bestMove = m;
                    }
                }
                return bestMove;
            }

            static minimax(engine, depth, alpha, beta, isMaximizing) {
                if (depth === 0) return this.evaluate(engine);

                const color = isMaximizing ? 'w' : 'b';
                const moves = engine.getAllLegalMoves(color);
                if (moves.length === 0) {
                    if (engine.isInCheck(color)) return isMaximizing ? -99999 : 99999;
                    return 0; // Stalemate
                }

                if (isMaximizing) {
                    let maxEval = -Infinity;
                    for (const m of moves) {
                        engine.makeMove(m);
                        const ev = this.minimax(engine, depth - 1, alpha, beta, false);
                        engine.undo();
                        maxEval = Math.max(maxEval, ev);
                        alpha = Math.max(alpha, ev);
                        if (beta <= alpha) break;
                    }
                    return maxEval;
                } else {
                    let minEval = Infinity;
                    for (const m of moves) {
                        engine.makeMove(m);
                        const ev = this.minimax(engine, depth - 1, alpha, beta, true);
                        engine.undo();
                        minEval = Math.min(minEval, ev);
                        beta = Math.min(beta, ev);
                        if (beta <= alpha) break;
                    }
                    return minEval;
                }
            }
        }

        /* ============================================================
           5. UI & GAME CONTROLLER
           ============================================================ */
        const engine = new ChessEngine();
        let selectedSq = null;
        let legalMovesForSel = [];
        let lastMove = null;
        let isFlipped = false;
        let gameMode = 'ai-medium'; // 'ai-easy', 'ai-medium', 'ai-hard', 'pass-and-play', 'pawns-only', 'knights-only'
        let pendingPromoMove = null;

        // Timers
        let whiteSeconds = 600;
        let blackSeconds = 600;
        let timerInterval = null;

        function initUI() {
            renderBoard();
            updateStatus();
            startTimer();
            setupPWA();
        }

        function renderBoard() {
            const boardEl = document.getElementById('chess-board');
            boardEl.innerHTML = '';

            const inCheckWhite = engine.isInCheck('w');
            const inCheckBlack = engine.isInCheck('b');
            const whiteKing = engine.findKing('w');
            const blackKing = engine.findKing('b');

            for (let visualR = 0; visualR < 8; visualR++) {
                for (let visualC = 0; visualC < 8; visualC++) {
                    const r = isFlipped ? 7 - visualR : visualR;
                    const c = isFlipped ? 7 - visualC : visualC;
                    const isDark = (r + c) % 2 === 1;

                    const sq = document.createElement('div');
                    sq.className = `square ${isDark ? 'dark' : 'light'}`;
                    sq.dataset.r = r;
                    sq.dataset.c = c;

                    // Last move highlight
                    if (lastMove && ((lastMove.fromR === r && lastMove.fromC === c) || (lastMove.toR === r && lastMove.toC === c))) {
                        sq.classList.add('last-move');
                    }

                    // Selected square
                    if (selectedSq && selectedSq[0] === r && selectedSq[1] === c) {
                        sq.classList.add('selected');
                    }

                    // Check highlight
                    if ((inCheckWhite && whiteKing && whiteKing[0] === r && whiteKing[1] === c) ||
                        (inCheckBlack && blackKing && blackKing[0] === r && blackKing[1] === c)) {
                        sq.classList.add('in-check');
                    }

                    // Board Coordinates
                    if (visualC === 0) {
                        const rankSpan = document.createElement('span');
                        rankSpan.className = 'coord rank';
                        rankSpan.innerText = 8 - r;
                        sq.appendChild(rankSpan);
                    }
                    if (visualR === 7) {
                        const fileSpan = document.createElement('span');
                        fileSpan.className = 'coord file';
                        fileSpan.innerText = String.fromCharCode(97 + c);
                        sq.appendChild(fileSpan);
                    }

                    // Move hint dots / rings
                    const targetMove = legalMovesForSel.find(m => m.toR === r && m.toC === c);
                    if (targetMove) {
                        if (targetMove.isCapture) {
                            const ring = document.createElement('div');
                            ring.className = 'hint-ring';
                            sq.appendChild(ring);
                        } else {
                            const dot = document.createElement('div');
                            dot.className = 'hint-dot';
                            sq.appendChild(dot);
                        }
                    }

                    // Piece
                    const piece = engine.board[r][c];
                    if (piece) {
                        const pieceDiv = document.createElement('div');
                        pieceDiv.className = 'piece';
                        const key = piece.color + piece.type;
                        pieceDiv.innerHTML = PIECE_SVGS[key] || '';
                        sq.appendChild(pieceDiv);
                    }

                    sq.addEventListener('pointerdown', (e) => {
                        e.preventDefault();
                        handleSquareClick(r, c);
                    });

                    boardEl.appendChild(sq);
                }
            }

            updateCaptured();
            updateEvalBar();
        }

        function handleSquareClick(r, c) {
            const piece = engine.board[r][c];

            // If a piece is already selected
            if (selectedSq) {
                const move = legalMovesForSel.find(m => m.toR === r && m.toC === c);
                if (move) {
                    if (move.isPromo) {
                        pendingPromoMove = move;
                        showPromoDialog(engine.turn);
                        return;
                    }
                    executePlayerMove(move);
                    return;
                }
            }

            // Select new piece
            if (piece && piece.color === engine.turn) {
                selectedSq = [r, c];
                legalMovesForSel = engine.getLegalMoves(r, c);
                renderBoard();
            } else {
                if (selectedSq) {
                    selectedSq = null;
                    legalMovesForSel = [];
                    renderBoard();
                }
            }
        }

        function executePlayerMove(move, promoChoice = 'q') {
            const res = engine.makeMove(move, promoChoice);
            lastMove = move;
            selectedSq = null;
            legalMovesForSel = [];

            // Sound
            if (engine.isInCheck(engine.turn)) {
                audio.play('check');
            } else if (res.captured) {
                audio.play('capture');
            } else {
                audio.play('move');
            }

            renderBoard();
            checkGameEnd();

            // Trigger AI if applicable
            if (gameMode.startsWith('ai') && engine.turn === 'b') {
                setTimeout(makeAIMove, 300);
            }
        }

        function makeAIMove() {
            let depth = 2;
            if (gameMode === 'ai-easy') depth = 1;
            if (gameMode === 'ai-medium') depth = 2;
            if (gameMode === 'ai-hard') depth = 3;

            const move = ChessAI.getBestMove(engine, depth);
            if (move) {
                const res = engine.makeMove(move, 'q');
                lastMove = move;

                if (engine.isInCheck('w')) {
                    audio.play('check');
                } else if (res.captured) {
                    audio.play('capture');
                } else {
                    audio.play('move');
                }

                renderBoard();
                checkGameEnd();
            }
        }

        function checkGameEnd() {
            const moves = engine.getAllLegalMoves(engine.turn);
            if (moves.length === 0) {
                clearInterval(timerInterval);
                if (engine.isInCheck(engine.turn)) {
                    const winner = engine.turn === 'w' ? 'Black' : 'White';
                    showModal('game-over-modal', 'Checkmate!', `${winner} wins by checkmate!`);
                } else {
                    showModal('game-over-modal', 'Stalemate!', 'Game drawn by stalemate.');
                }
            }
        }

        function updateCaptured() {
            const topEl = document.getElementById('top-captured');
            const botEl = document.getElementById('bottom-captured');
            const sym = { p:'♟', n:'♞', b:'♝', r:'♜', q:'♛' };

            topEl.innerHTML = engine.captured.b.map(p => sym[p.type]).join(' ');
            botEl.innerHTML = engine.captured.w.map(p => sym[p.type]).join(' ');

            const score = engine.evaluateMaterial();
            document.getElementById('bottom-diff').innerText = score > 0 ? `+${score}` : '';
            document.getElementById('top-diff').innerText = score < 0 ? `+${-score}` : '';
        }

        function updateEvalBar() {
            const score = engine.evaluateMaterial();
            const pct = Math.max(5, Math.min(95, 50 - (score * 5)));
            document.getElementById('eval-bar-black').style.height = `${pct}%`;
        }

        function updateStatus() {
            const botTimer = document.getElementById('bottom-timer');
            const topTimer = document.getElementById('top-timer');
            if (engine.turn === 'w') {
                botTimer.classList.add('active');
                topTimer.classList.remove('active');
            } else {
                topTimer.classList.add('active');
                botTimer.classList.remove('active');
            }
        }

        function startTimer() {
            clearInterval(timerInterval);
            timerInterval = setInterval(() => {
                if (engine.turn === 'w') {
                    if (whiteSeconds > 0) whiteSeconds--;
                } else {
                    if (blackSeconds > 0) blackSeconds--;
                }
                formatTimers();
            }, 1000);
        }

        function formatTimers() {
            const fmt = (s) => {
                const m = Math.floor(s / 60);
                const sec = s % 60;
                return `${m}:${sec < 10 ? '0' : ''}${sec}`;
            };
            document.getElementById('bottom-timer').innerText = fmt(whiteSeconds);
            document.getElementById('top-timer').innerText = fmt(blackSeconds);
        }

        function showPromoDialog(color) {
            const modal = document.getElementById('promo-modal');
            const container = document.getElementById('promo-options');
            container.innerHTML = '';
            const types = ['q', 'r', 'b', 'n'];

            types.forEach(t => {
                const choice = document.createElement('div');
                choice.className = 'promo-choice';
                const p = document.createElement('div');
                p.className = 'piece';
                p.innerHTML = PIECE_SVGS[color + t] || '';
                choice.appendChild(p);

                choice.onclick = () => {
                    modal.classList.remove('active');
                    if (pendingPromoMove) {
                        executePlayerMove(pendingPromoMove, t);
                        pendingPromoMove = null;
                    }
                };
                container.appendChild(choice);
            });
            modal.classList.add('active');
        }

        function showModal(id, title, desc) {
            const modal = document.getElementById(id);
            if (title) document.getElementById('game-over-title').innerText = title;
            if (desc) document.getElementById('game-over-desc').innerText = desc;
            modal.classList.add('active');
        }

        function closeModal(id) {
            document.getElementById(id).classList.remove('active');
        }

        function setMode(mode) {
            gameMode = mode;
            closeModal('settings-modal');
            startNewGame();
        }

        function startNewGame() {
            engine.reset(gameMode.includes('pawns') ? 'pawns-only' : (gameMode.includes('knights') ? 'knights-only' : 'standard'));
            lastMove = null;
            selectedSq = null;
            legalMovesForSel = [];
            whiteSeconds = 600;
            blackSeconds = 600;

            const isAI = gameMode.startsWith('ai');
            document.getElementById('top-name').innerText = isAI ? `Computer (${gameMode.split('-')[1]})` : 'Player 2 (Black)';
            document.getElementById('top-avatar').innerText = isAI ? 'Bot' : 'P2';

            renderBoard();
            updateStatus();
            startTimer();
            showToast('New Game Started');
        }

        function showToast(msg) {
            const t = document.getElementById('toast');
            t.innerText = msg;
            t.classList.add('visible');
            setTimeout(() => t.classList.remove('visible'), 2000);
        }

        /* Controls */
        document.getElementById('new-game-btn').addEventListener('click', startNewGame);
        document.getElementById('play-again-btn').addEventListener('click', () => {
            closeModal('game-over-modal');
            startNewGame();
        });

        document.getElementById('flip-board-btn').addEventListener('click', () => {
            isFlipped = !isFlipped;
            renderBoard();
        });

        document.getElementById('undo-btn').addEventListener('click', () => {
            if (gameMode.startsWith('ai')) {
                engine.undo(); // Undo AI move
                engine.undo(); // Undo Player move
            } else {
                engine.undo();
            }
            lastMove = null;
            renderBoard();
            updateStatus();
            showToast('Move Undone');
        });

        document.getElementById('game-info-btn').addEventListener('click', () => {
            document.getElementById('settings-modal').classList.add('active');
        });

        document.getElementById('mode-btn').addEventListener('click', () => {
            document.getElementById('settings-modal').classList.add('active');
        });

        /* ============================================================
           6. ANDROID PWA INSTALLATION SYSTEM
           ============================================================ */
        let deferredPrompt = null;
        const installBtn = document.getElementById('pwa-install-btn');

        function setupPWA() {
            window.addEventListener('beforeinstallprompt', (e) => {
                e.preventDefault();
                deferredPrompt = e;
                installBtn.style.display = 'flex';
            });

            installBtn.addEventListener('click', async () => {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    const { outcome } = await deferredPrompt.userChoice;
                    if (outcome === 'accepted') {
                        installBtn.style.display = 'none';
                    }
                    deferredPrompt = null;
                } else {
                    alert('To install on Android:\\n\\n1. Tap the ⋮ (three dots) menu in your browser.\\n2. Tap "Install App" or "Add to Home screen".\\n3. Chess Master will install to your phone!');
                }
            });

            // Embedded Web App Manifest
            const manifest = {
                "name": "Chess Master",
                "short_name": "Chess",
                "start_url": ".",
                "display": "standalone",
                "background_color": "#302e2b",
                "theme_color": "#302e2b",
                "description": "Premium Chess Game for Android and Mobile",
                "icons": [
                    {
                        "src": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='20' fill='%23302e2b'/><text x='50%' y='68%' font-size='60' text-anchor='middle'>♞</text></svg>",
                        "sizes": "192x192 512x512",
                        "type": "image/svg+xml",
                        "purpose": "any maskable"
                    }
                ]
            };
            const stringManifest = JSON.stringify(manifest);
            const blob = new Blob([stringManifest], {type: 'application/json'});
            const manifestURL = URL.createObjectURL(blob);
            const manifestLink = document.createElement('link');
            manifestLink.rel = 'manifest';
            manifestLink.href = manifestURL;
            document.head.appendChild(manifestLink);
        }

        // Initialize on load
        window.addEventListener('DOMContentLoaded', initUI);
    </script>
</body>
</html>
'''

with open('Install-Chess-Android.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print('Install-Chess-Android.html created successfully!')
