"""
build_game_and_installer.py
============================
Reads the 3 trained model JSON files from models/ and generates:
  1. index.html (modern mobile & desktop web app with embedded neural inference)
  2. Install-Chess-Android.html (standalone installer file)
  3. Install-On-Phone.html (wireless installer page for phone browsers)
  4. chess-android/app/src/main/assets/index.html (native Android APK asset)
"""

import os
import json
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(ROOT, 'models')

# Load the 3 trained models
with open(os.path.join(MODELS_DIR, 'model_novice.json'), 'r', encoding='utf-8') as f:
    m_novice = json.load(f)

with open(os.path.join(MODELS_DIR, 'model_tactician.json'), 'r', encoding='utf-8') as f:
    m_tactician = json.load(f)

with open(os.path.join(MODELS_DIR, 'model_grandmaster.json'), 'r', encoding='utf-8') as f:
    m_grandmaster = json.load(f)

elo_n = m_novice.get('target_elo', 900)
elo_t = m_tactician.get('target_elo', 1500)
elo_g = m_grandmaster.get('target_elo', 2100)
print(f"[*] Loaded trained models: Novice (Elo {elo_n}), Tactician (Elo {elo_t}), Grandmaster (Elo {elo_g})")

def generate_html(is_phone_installer=False):
    novice_json_str = json.dumps(m_novice)
    tactician_json_str = json.dumps(m_tactician)
    grandmaster_json_str = json.dumps(m_grandmaster)

    installer_banner_html = ""
    if is_phone_installer:
        installer_banner_html = """
        <!-- Android Phone One-Tap Install Header Banner -->
        <div id="phone-install-banner" class="phone-install-banner">
            <div class="banner-title">Install Chess Master on Your Phone</div>
            <div class="banner-desc">
                Play offline anytime! Install directly to your Android home screen or download the native APK.
            </div>
            <div class="banner-buttons">
                <button type="button" id="pwa-quick-install-btn" class="banner-btn primary">
                    1-Tap Quick Install
                </button>
                <a href="/ChessMaster.apk" download class="banner-btn secondary">
                    Download APK
                </a>
            </div>
        </div>
        """

    template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="theme-color" content="#262421">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Chess Master">
    <meta name="mobile-web-app-capable" content="yes">
    <title>Chess Master - Trained Neural Bots & Classic Chess</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 45 45'><path d='M22 10c10.5 1 16.5 8 16 29L15 39C15 30 11.5 23.5 11 18c-0.5-5.5 4-9 8-9.5 0.5 0.5 1.5 1.5 2 2.5z' fill='%2381b64c'/></svg>">
    
    <style>
        :root {
            --bg-main: #302e2b;
            --bg-panel: #262421;
            --bg-card: #1e1d1a;
            --card-border: #3d3a34;
            --card-border-hover: #555047;
            --light-sq: #ebecd0;
            --dark-sq: #779556;
            --highlight-move: rgba(247, 247, 105, 0.45);
            --highlight-sel: rgba(255, 170, 0, 0.55);
            --hint-dot: rgba(0, 0, 0, 0.24);
            --hint-ring: rgba(0, 0, 0, 0.35);
            --text-main: #f5f5f5;
            --text-muted: #a09b91;
            --accent-green: #81b64c;
            --accent-green-hover: #96cc5a;
            --accent-blue: #457b9d;
            --accent-blue-hover: #5291b8;
            --accent-purple: #9b5de5;
            --accent-gold: #e9c46a;
            --danger: #e63946;
            --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
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
            justify-content: flex-start;
            overflow-x: hidden;
            touch-action: manipulation;
        }

        /* ── Views Switching ── */
        .view-screen {
            display: none;
            width: 100%;
            min-height: 100vh;
            flex-direction: column;
            align-items: center;
        }
        .view-screen.active {
            display: flex;
        }

        /* ═══════════════════════════════════════════════════════
           MAIN MENU VIEW STYLES
           ═══════════════════════════════════════════════════════ */
        .menu-container {
            width: 100%;
            max-width: 620px;
            padding: 24px 16px 40px 16px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .phone-install-banner {
            width: 100%;
            background: linear-gradient(135deg, #1e3a20, #142415);
            border: 1px solid #4a8522;
            border-radius: 12px;
            padding: 14px 16px;
            margin-bottom: 6px;
            text-align: center;
            box-shadow: 0 4px 16px rgba(0,0,0,0.4);
        }
        .banner-title {
            font-size: 15px;
            font-weight: 700;
            color: #a3d160;
            margin-bottom: 4px;
        }
        .banner-desc {
            font-size: 12px;
            color: #d0cfcd;
            line-height: 1.4;
            margin-bottom: 10px;
        }
        .banner-buttons {
            display: flex;
            gap: 8px;
            justify-content: center;
            flex-wrap: wrap;
        }
        .banner-btn {
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            border: none;
            display: inline-flex;
            align-items: center;
        }
        .banner-btn.primary {
            background: var(--accent-green);
            color: #fff;
        }
        .banner-btn.secondary {
            background: #2b2926;
            color: #f0f0f0;
            border: 1px solid #555;
        }

        .menu-header {
            text-align: center;
            padding: 8px 0 6px 0;
        }
        .menu-title {
            font-size: 32px;
            font-weight: 800;
            letter-spacing: 0.8px;
            color: #f5f5f5;
            margin-bottom: 4px;
        }
        .menu-subtitle {
            font-size: 13px;
            color: var(--text-muted);
            letter-spacing: 0.3px;
        }

        .menu-section {
            background-color: var(--bg-panel);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.25);
        }
        .section-title {
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.8px;
            color: var(--accent-gold);
            text-transform: uppercase;
        }

        /* Side Toggle */
        .side-selector {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding-bottom: 2px;
        }
        .side-label {
            font-size: 12px;
            color: var(--text-muted);
            margin-right: 4px;
        }
        .side-toggle-btn {
            background: #1e1d1a;
            border: 1px solid #504d48;
            color: var(--text-muted);
            border-radius: 6px;
            padding: 6px 14px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .side-toggle-btn.active {
            background: var(--accent-green);
            border-color: var(--accent-green-hover);
            color: #ffffff;
        }

        /* Bot Cards */
        .bot-grid {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .bot-card {
            display: flex;
            align-items: center;
            gap: 12px;
            background: var(--bg-card);
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 10px 14px;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .bot-card:hover {
            background: #282622;
            border-color: var(--card-border-hover);
            transform: translateY(-1px);
        }
        .bot-card-badge {
            width: 32px;
            height: 32px;
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.06);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 14px;
            flex-shrink: 0;
        }
        .bot-card.novice .bot-card-badge { color: var(--accent-green); }
        .bot-card.tactician .bot-card-badge { color: var(--accent-blue); }
        .bot-card.grandmaster .bot-card-badge { color: var(--accent-purple); }

        .bot-card-info {
            flex-grow: 1;
        }
        .bot-card-title {
            font-size: 14px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 2px;
        }
        .bot-card-meta {
            font-size: 11px;
            color: var(--text-muted);
        }
        .bot-card.novice .bot-card-meta { color: #9ecb70; }
        .bot-card.tactician .bot-card-meta { color: #6ba7cb; }
        .bot-card.grandmaster .bot-card-meta { color: #b784f0; }

        .bot-card-action {
            font-size: 12px;
            font-weight: 600;
            padding: 5px 14px;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.08);
            color: #e0deda;
        }

        /* 2-Player Pass & Play */
        .play-btn-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        .mode-btn {
            border: none;
            border-radius: 8px;
            padding: 12px 10px;
            cursor: pointer;
            text-align: center;
            display: flex;
            flex-direction: column;
            gap: 2px;
            transition: all 0.15s ease;
        }
        .mode-btn:hover {
            transform: translateY(-1px);
            filter: brightness(1.08);
        }
        .btn-casual {
            background: var(--accent-green);
            color: #ffffff;
        }
        .btn-blitz {
            background: var(--accent-blue);
            color: #ffffff;
        }
        .mode-btn-title {
            font-size: 13px;
            font-weight: 700;
        }
        .mode-btn-sub {
            font-size: 11px;
            opacity: 0.85;
        }

        /* Army Variants Grid */
        .variants-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }
        @media (max-width: 480px) {
            .variants-grid {
                grid-template-columns: 1fr;
            }
        }
        .variant-card {
            display: flex;
            align-items: center;
            gap: 10px;
            background: var(--bg-card);
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 9px 12px;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .variant-card:hover {
            background: #282622;
            border-color: var(--accent-green);
        }
        .variant-icon {
            width: 28px;
            height: 28px;
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.06);
            color: var(--accent-gold);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 13px;
            flex-shrink: 0;
        }
        .variant-info {
            flex-grow: 1;
        }
        .variant-title {
            font-size: 13px;
            font-weight: 700;
            color: #f5f5f5;
            margin-bottom: 1px;
        }
        .variant-desc {
            font-size: 11px;
            color: var(--text-muted);
        }

        .menu-footer {
            text-align: center;
            font-size: 11px;
            color: #78756e;
            padding: 8px 0;
        }

        /* ═══════════════════════════════════════════════════════
           GAME VIEW STYLES (Matching Java GameView)
           ═══════════════════════════════════════════════════════ */
        .game-header {
            width: 100%;
            max-width: 540px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 14px;
            background: var(--bg-panel);
            border-bottom: 1px solid var(--card-border);
            box-shadow: 0 2px 8px rgba(0,0,0,0.35);
            z-index: 10;
        }
        .header-btn {
            background: #302e2b;
            border: 1px solid #504d48;
            color: #e0deda;
            border-radius: 6px;
            padding: 6px 14px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .header-btn:hover {
            background: #3c3935;
            color: #ffffff;
            border-color: #66625b;
        }
        .game-header-center {
            text-align: center;
        }
        .game-status-title {
            font-size: 15px;
            font-weight: 700;
            color: #f5f5f5;
            margin-bottom: 1px;
        }
        .game-mode-subtitle {
            font-size: 11px;
            color: var(--text-muted);
        }

        .game-wrapper {
            width: 100%;
            max-width: 540px;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 8px 12px;
            gap: 8px;
            flex-grow: 1;
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
            border: 1px solid rgba(255,255,255,0.05);
        }
        .player-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .player-avatar {
            width: 32px;
            height: 32px;
            border-radius: 6px;
            background: #1e1d1a;
            border: 1px solid #3d3a34;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 700;
            color: var(--accent-green);
        }
        .player-meta {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        .player-name {
            font-size: 13px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .player-elo-tag {
            font-size: 10px;
            font-weight: 600;
            color: var(--accent-gold);
            background: rgba(233, 196, 106, 0.15);
            padding: 1px 5px;
            border-radius: 4px;
        }
        .captured-row {
            display: flex;
            align-items: center;
            gap: 4px;
            min-height: 14px;
        }
        .captured-pieces {
            display: flex;
            align-items: center;
            gap: 2px;
        }
        .cap-svg {
            width: 14px;
            height: 14px;
        }
        .material-diff {
            font-size: 10px;
            font-weight: 700;
            color: var(--text-muted);
        }
        .player-timer {
            font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
            font-size: 15px;
            font-weight: 700;
            padding: 4px 10px;
            background: #191816;
            border-radius: 6px;
            border: 1px solid #33312c;
            color: var(--text-muted);
        }
        .player-timer.active {
            color: #ffffff;
            border-color: var(--accent-green);
            background: #1e2618;
        }

        /* Board Container */
        .board-container {
            width: 100%;
            display: flex;
            align-items: stretch;
            gap: 8px;
            justify-content: center;
        }
        .eval-bar-wrapper {
            width: 8px;
            background: #191816;
            border-radius: 4px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            border: 1px solid #3d3a34;
        }
        .eval-bar-black {
            width: 100%;
            background: #222;
            flex-grow: 1;
        }
        .eval-bar-white {
            width: 100%;
            background: #fff;
            height: 50%;
            transition: height 0.3s ease;
        }
        .chess-board {
            width: 100%;
            max-width: 480px;
            aspect-ratio: 1 / 1;
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            grid-template-rows: repeat(8, 1fr);
            border-radius: 6px;
            overflow: hidden;
            box-shadow: 0 8px 24px rgba(0,0,0,0.55);
            position: relative;
        }
        .square {
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }
        .square.light { background-color: var(--light-sq); color: var(--dark-sq); }
        .square.dark { background-color: var(--dark-sq); color: var(--light-sq); }
        .square.selected { background-color: var(--highlight-sel) !important; }
        .square.last-move { background-color: var(--highlight-move) !important; }
        .square.in-check { background: radial-gradient(circle, #e63946 0%, transparent 80%) !important; }

        .coord {
            position: absolute;
            font-size: 10px;
            font-weight: 700;
            pointer-events: none;
            opacity: 0.8;
        }
        .coord.rank { top: 2px; left: 3px; }
        .coord.file { bottom: 2px; right: 3px; }

        .piece {
            width: 88%;
            height: 88%;
            display: flex;
            align-items: center;
            justify-content: center;
            pointer-events: none;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.25));
        }
        .piece svg {
            width: 100%;
            height: 100%;
        }

        .hint-dot {
            width: 26%;
            height: 26%;
            border-radius: 50%;
            background: var(--hint-dot);
            pointer-events: none;
        }
        .hint-ring {
            width: 84%;
            height: 84%;
            border-radius: 50%;
            border: 4px solid var(--hint-ring);
            pointer-events: none;
        }

        /* Status & Thinking Bar */
        .status-bar {
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 6px 12px;
            background: var(--bg-panel);
            border-radius: 6px;
            font-size: 12px;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .status-text {
            display: flex;
            align-items: center;
            gap: 6px;
            font-weight: 600;
            color: #f5f5f5;
        }
        .thinking-spinner {
            width: 10px;
            height: 10px;
            border: 2px solid var(--accent-green);
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 0.7s linear infinite;
            display: none;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .eval-score {
            font-size: 11px;
            font-weight: 700;
            color: var(--text-muted);
            font-family: ui-monospace, SFMono-Regular, monospace;
        }

        /* Action Bar */
        .action-bar {
            width: 100%;
            max-width: 540px;
            display: flex;
            justify-content: center;
            gap: 8px;
            padding: 8px 12px 16px 12px;
        }
        .action-btn {
            flex: 1;
            padding: 9px 8px;
            border-radius: 6px;
            background: var(--bg-panel);
            border: 1px solid var(--card-border);
            color: #d0cfcd;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            text-align: center;
            transition: all 0.15s ease;
        }
        .action-btn:hover {
            background: #302e2b;
            color: #ffffff;
            border-color: #555047;
        }

        /* Modals */
        .modal-overlay {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(0,0,0,0.72);
            z-index: 100;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
        }
        .modal-overlay.active {
            opacity: 1;
            pointer-events: auto;
        }
        .modal-card {
            background-color: var(--bg-panel);
            border-radius: 12px;
            padding: 22px;
            width: 90%;
            max-width: 420px;
            box-shadow: 0 16px 36px rgba(0,0,0,0.65);
            border: 1px solid rgba(255,255,255,0.1);
            text-align: center;
        }
        .modal-title {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 6px;
        }
        .modal-subtitle {
            font-size: 12px;
            color: var(--text-muted);
            margin-bottom: 16px;
            line-height: 1.4;
        }
        .promo-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            margin: 14px 0 6px 0;
        }
        .promo-btn {
            background: var(--bg-card);
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 10px 4px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .promo-btn:hover {
            background: #2b2926;
            border-color: var(--accent-green);
        }
        .promo-icon {
            width: 36px;
            height: 36px;
        }
        .promo-icon svg {
            width: 100%;
            height: 100%;
        }
        .promo-name {
            font-size: 11px;
            font-weight: 600;
            color: #f0f0f0;
        }
        .modal-btn-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: 12px;
        }
        .modal-btn {
            width: 100%;
            padding: 11px;
            border-radius: 6px;
            border: none;
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
            transition: background 0.15s;
        }
        .modal-btn.primary {
            background: var(--accent-green);
            color: #ffffff;
        }
        .modal-btn.primary:hover {
            background: var(--accent-green-hover);
        }
        .modal-btn.secondary {
            background: #302e2b;
            color: #d0cfcd;
            border: 1px solid #504d48;
        }
        .modal-btn.secondary:hover {
            background: #3b3935;
            color: #fff;
        }
    </style>
</head>
<body>

    <!-- ═══════════════════════════════════════════════════════
         1. MAIN MENU VIEW (Matching Java MenuView)
         ═══════════════════════════════════════════════════════ -->
    <div id="menu-view" class="view-screen active">
        <div class="menu-container">
            __INSTALLER_BANNER__
            
            <header class="menu-header">
                <h1 class="menu-title">CHESS MASTER</h1>
                <p class="menu-subtitle">Trained Neural Engines &amp; Classic Chess</p>
            </header>

            <!-- 1. Play vs Trained AI Bots -->
            <section class="menu-section">
                <div class="section-title">Play vs Trained AI Bots</div>
                
                <div class="side-selector">
                    <span class="side-label">Your Side:</span>
                    <button type="button" id="side-w-btn" class="side-toggle-btn active" onclick="setPlayerSide('w')">Play White (Move 1st)</button>
                    <button type="button" id="side-b-btn" class="side-toggle-btn" onclick="setPlayerSide('b')">Play Black (Bot 1st)</button>
                </div>

                <div class="bot-grid">
                    <div class="bot-card novice" onclick="startBotGame('novice')">
                        <div class="bot-card-badge">I</div>
                        <div class="bot-card-info">
                            <div class="bot-card-title">Apprentice Novice</div>
                            <div class="bot-card-meta">900 Elo &bull; Linear PST Model</div>
                        </div>
                        <div class="bot-card-action">Play</div>
                    </div>

                    <div class="bot-card tactician" onclick="startBotGame('tactician')">
                        <div class="bot-card-badge">II</div>
                        <div class="bot-card-info">
                            <div class="bot-card-title">Club Tactician</div>
                            <div class="bot-card-meta">1500 Elo &bull; Neural MLP Model</div>
                        </div>
                        <div class="bot-card-action">Play</div>
                    </div>

                    <div class="bot-card grandmaster" onclick="startBotGame('grandmaster')">
                        <div class="bot-card-badge">III</div>
                        <div class="bot-card-info">
                            <div class="bot-card-title">Grandmaster Engine</div>
                            <div class="bot-card-meta">2100+ Elo &bull; NNUE Dual Model</div>
                        </div>
                        <div class="bot-card-action">Play</div>
                    </div>
                </div>
            </section>

            <!-- 2. Classic Chess 2-Player -->
            <section class="menu-section">
                <div class="section-title">Play Classic Chess (2 Players)</div>
                <div class="play-btn-row">
                    <button type="button" class="mode-btn btn-casual" onclick="startPassAndPlay(false)">
                        <span class="mode-btn-title">Play Casual</span>
                        <span class="mode-btn-sub">Unlimited Time</span>
                    </button>
                    <button type="button" class="mode-btn btn-blitz" onclick="startPassAndPlay(true)">
                        <span class="mode-btn-title">Play 10 Min Blitz</span>
                        <span class="mode-btn-sub">Timed Match</span>
                    </button>
                </div>
            </section>

            <!-- 3. Army Variants -->
            <section class="menu-section">
                <div class="section-title">Select Army Variant</div>
                <div class="variants-grid">
                    <div class="variant-card" onclick="startArmyGame('classic')">
                        <div class="variant-icon">C</div>
                        <div class="variant-info">
                            <div class="variant-title">Classic Chess</div>
                            <div class="variant-desc">Standard FIDE setup</div>
                        </div>
                    </div>
                    <div class="variant-card" onclick="startArmyGame('pawns')">
                        <div class="variant-icon">P</div>
                        <div class="variant-info">
                            <div class="variant-title">Pawns Only</div>
                            <div class="variant-desc">1 King + 15 Pawns</div>
                        </div>
                    </div>
                    <div class="variant-card" onclick="startArmyGame('knights')">
                        <div class="variant-icon">K</div>
                        <div class="variant-info">
                            <div class="variant-title">Knights Only</div>
                            <div class="variant-desc">1 King + 15 Knights</div>
                        </div>
                    </div>
                    <div class="variant-card" onclick="startArmyGame('bishops')">
                        <div class="variant-icon">B</div>
                        <div class="variant-info">
                            <div class="variant-title">Bishops Only</div>
                            <div class="variant-desc">1 King + 15 Bishops</div>
                        </div>
                    </div>
                    <div class="variant-card" onclick="startArmyGame('rooks')">
                        <div class="variant-icon">R</div>
                        <div class="variant-info">
                            <div class="variant-title">Rooks Only</div>
                            <div class="variant-desc">1 King + 15 Rooks</div>
                        </div>
                    </div>
                    <div class="variant-card" onclick="startArmyGame('queens')">
                        <div class="variant-icon">Q</div>
                        <div class="variant-info">
                            <div class="variant-title">Queens Only</div>
                            <div class="variant-desc">1 King + 15 Queens</div>
                        </div>
                    </div>
                </div>
            </section>

            <footer class="menu-footer">
                Trained Neural Engines &bull; Dynamic Evaluation &bull; Cross-Platform Suite
            </footer>
        </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════
         2. GAME ARENA VIEW (Matching Java GameView)
         ═══════════════════════════════════════════════════════ -->
    <div id="game-view" class="view-screen">
        <!-- Top Header: Back, Status, Restart -->
        <header class="game-header">
            <button type="button" class="header-btn" onclick="showMenu()">Back</button>
            <div class="game-header-center">
                <div class="game-status-title" id="status-title">White's Turn</div>
                <div class="game-mode-subtitle" id="mode-subtitle">vs Club Tactician (1500 Elo)</div>
            </div>
            <button type="button" class="header-btn" onclick="restartCurrentGame()">Restart</button>
        </header>

        <!-- Main Arena Container -->
        <main class="game-wrapper">
            <!-- Top Player (Opponent) -->
            <div class="player-bar" id="top-player-bar">
                <div class="player-info">
                    <div class="player-avatar" id="top-avatar">II</div>
                    <div class="player-meta">
                        <div class="player-name">
                            <span id="top-name">Club Tactician</span>
                            <span class="player-elo-tag" id="top-elo">1500 Elo</span>
                        </div>
                        <div class="captured-row">
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
                    <div class="player-avatar" id="bottom-avatar">You</div>
                    <div class="player-meta">
                        <div class="player-name">
                            <span id="bottom-name">You (White)</span>
                        </div>
                        <div class="captured-row">
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
                <div class="eval-score" id="eval-score-text">+0.0</div>
            </div>
        </main>

        <!-- Bottom Actions -->
        <nav class="action-bar">
            <button type="button" class="action-btn" onclick="undoMove()">Undo</button>
            <button type="button" class="action-btn" onclick="flipBoard()">Flip Board</button>
            <button type="button" class="action-btn" onclick="restartCurrentGame()">Restart</button>
            <button type="button" class="action-btn" onclick="showMenu()">Menu</button>
        </nav>
    </div>

    <!-- ═══════════════════════════════════════════════════════
         3. MODALS
         ═══════════════════════════════════════════════════════ -->
    <!-- Pawn Promotion Modal -->
    <div class="modal-overlay" id="promo-modal">
        <div class="modal-card">
            <h2 class="modal-title">Pawn Promotion</h2>
            <p class="modal-subtitle">Choose which piece you want to promote your pawn to:</p>
            <div class="promo-grid">
                <button type="button" class="promo-btn" onclick="confirmPromotion('q')">
                    <div class="promo-icon" id="promo-icon-q"></div>
                    <span class="promo-name">Queen</span>
                </button>
                <button type="button" class="promo-btn" onclick="confirmPromotion('r')">
                    <div class="promo-icon" id="promo-icon-r"></div>
                    <span class="promo-name">Rook</span>
                </button>
                <button type="button" class="promo-btn" onclick="confirmPromotion('b')">
                    <div class="promo-icon" id="promo-icon-b"></div>
                    <span class="promo-name">Bishop</span>
                </button>
                <button type="button" class="promo-btn" onclick="confirmPromotion('n')">
                    <div class="promo-icon" id="promo-icon-n"></div>
                    <span class="promo-name">Knight</span>
                </button>
            </div>
        </div>
    </div>

    <!-- Game Over Modal -->
    <div class="modal-overlay" id="game-over-modal">
        <div class="modal-card">
            <h2 class="modal-title" id="game-over-title">Game Over</h2>
            <p class="modal-subtitle" id="game-over-desc">Checkmate! White wins the game.</p>
            <div class="modal-btn-group">
                <button type="button" class="modal-btn primary" onclick="restartCurrentGame()">Play Again</button>
                <button type="button" class="modal-btn secondary" onclick="showMenu()">Main Menu</button>
                <button type="button" class="modal-btn secondary" onclick="closeModal('game-over-modal')">Review Board</button>
            </div>
        </div>
    </div>

    <!-- ═══════════════════════════════════════════════════════
         4. JAVASCRIPT ENGINE & LOGIC
         ═══════════════════════════════════════════════════════ -->
    <script>
        /* ── Vector Piece Art (Zero Emojis) ── */
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

        /* ── Audio Synthesizer ── */
        class ChessAudio {
            constructor() { this.ctx = null; }
            init() {
                if (!this.ctx) {
                    const AC = window.AudioContext || window.webkitAudioContext;
                    if (AC) this.ctx = new AC();
                }
                if (this.ctx && this.ctx.state === 'suspended') this.ctx.resume();
            }
            play(type) {
                try {
                    this.init();
                    if (!this.ctx) return;
                    const osc = this.ctx.createOscillator();
                    const gain = this.ctx.createGain();
                    osc.connect(gain);
                    gain.connect(this.ctx.destination);
                    const now = this.ctx.currentTime;
                    if (type === 'move') {
                        osc.frequency.setValueAtTime(320, now);
                        osc.frequency.exponentialRampToValueAtTime(160, now + 0.08);
                        gain.gain.setValueAtTime(0.3, now);
                        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.08);
                        osc.start(now); osc.stop(now + 0.08);
                    } else if (type === 'capture') {
                        osc.frequency.setValueAtTime(450, now);
                        osc.frequency.exponentialRampToValueAtTime(200, now + 0.12);
                        gain.gain.setValueAtTime(0.4, now);
                        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.12);
                        osc.start(now); osc.stop(now + 0.12);
                    } else if (type === 'check') {
                        osc.frequency.setValueAtTime(600, now);
                        osc.frequency.exponentialRampToValueAtTime(800, now + 0.15);
                        gain.gain.setValueAtTime(0.4, now);
                        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.15);
                        osc.start(now); osc.stop(now + 0.15);
                    }
                } catch(e) {}
            }
        }
        const audio = new ChessAudio();

        /* ── Neural Engine Models & Inference ── */
        const MODEL_NOVICE = __NOVICE_JSON__;
        const MODEL_TACTICIAN = __TACTICIAN_JSON__;
        const MODEL_GRANDMASTER = __GRANDMASTER_JSON__;

        const BOTS = {
            'novice': {
                id: 'novice',
                name: 'Apprentice Novice',
                elo: 900,
                badge: 'I',
                desc: 'Linear PST (900 Elo)',
                model: MODEL_NOVICE,
                depth: 2
            },
            'tactician': {
                id: 'tactician',
                name: 'Club Tactician',
                elo: 1500,
                badge: 'II',
                desc: 'Neural MLP (1500 Elo)',
                model: MODEL_TACTICIAN,
                depth: 3
            },
            'grandmaster': {
                id: 'grandmaster',
                name: 'Grandmaster Engine',
                elo: 2100,
                badge: 'III',
                desc: 'NNUE Dual Perspective (2100+ Elo)',
                model: MODEL_GRANDMASTER,
                depth: 3
            }
        };

        class NeuralEngine {
            static pieceIndices = { p: 0, n: 1, b: 2, r: 3, q: 4, k: 5 };

            static encodeBoard768(engine) {
                const vec = new Float32Array(768);
                for (let r = 0; r < 8; r++) {
                    for (let c = 0; c < 8; c++) {
                        const p = engine.board[r][c];
                        if (p) {
                            const sq = r * 8 + c;
                            let idx = this.pieceIndices[p.type];
                            if (p.color === 'b') idx += 6;
                            vec[sq * 12 + idx] = 1.0;
                        }
                    }
                }
                return vec;
            }

            static encodeAux(engine) {
                const side = engine.turn === 'w' ? 1.0 : -1.0;
                const castling = [
                    engine.castling.w.k ? 1.0 : 0.0,
                    engine.castling.w.q ? 1.0 : 0.0,
                    engine.castling.b.k ? 1.0 : 0.0,
                    engine.castling.b.q ? 1.0 : 0.0
                ];
                let centerCtrl = 0;
                for (const [r, c] of [[3,3], [3,4], [4,3], [4,4]]) {
                    if (engine.board[r][c]) centerCtrl += 1;
                }
                centerCtrl /= 4.0;

                const valMap = { p: 1, n: 3, b: 3, r: 5, q: 9, k: 0 };
                let mat = 0;
                for (let r = 0; r < 8; r++) {
                    for (let c = 0; c < 8; c++) {
                        const p = engine.board[r][c];
                        if (p) {
                            const v = valMap[p.type] || 0;
                            mat += (p.color === 'w' ? v : -v);
                        }
                    }
                }
                const matNorm = Math.tanh(mat / 10.0);
                const mobility = engine.getAllLegalMoves(engine.turn).length / 40.0;
                return [side, castling[0], castling[1], castling[2], castling[3], centerCtrl, matNorm, mobility];
            }

            static evaluate(engine, botKey) {
                if (engine.isInCheck('w') && engine.getAllLegalMoves('w').length === 0) return -100.0;
                if (engine.isInCheck('b') && engine.getAllLegalMoves('b').length === 0) return 100.0;

                if (botKey === 'novice') {
                    const w = MODEL_NOVICE.weights;
                    const b = MODEL_NOVICE.bias;
                    const x = this.encodeBoard768(engine);
                    let score = b;
                    for (let i = 0; i < 768; i++) {
                        if (x[i] > 0) score += w[i];
                    }
                    return score;
                } else if (botKey === 'tactician') {
                    const x768 = this.encodeBoard768(engine);
                    const aux = this.encodeAux(engine);
                    const W1 = MODEL_TACTICIAN.W1;
                    const b1 = MODEL_TACTICIAN.b1;
                    const W2 = MODEL_TACTICIAN.W2;
                    const b2 = MODEL_TACTICIAN.b2;

                    const h = new Float32Array(48);
                    for (let j = 0; j < 48; j++) {
                        let sum = b1[j];
                        for (let i = 0; i < 768; i++) {
                            if (x768[i] > 0) sum += W1[i][j];
                        }
                        for (let a = 0; a < 8; a++) {
                            sum += aux[a] * W1[768 + a][j];
                        }
                        h[j] = sum > 0 ? sum : 0;
                    }
                    let out = b2[0];
                    for (let j = 0; j < 48; j++) {
                        out += h[j] * W2[j][0];
                    }
                    return Math.tanh(out) * 5.0;
                } else {
                    const xw = this.encodeBoard768(engine);
                    const xb = new Float32Array(768);
                    for (let sq = 0; sq < 64; sq++) {
                        const r = Math.floor(sq / 8);
                        const c = sq % 8;
                        const f_sq = (7 - r) * 8 + c;
                        for (let p = 0; p < 6; p++) {
                            xb[f_sq * 12 + p] = xw[sq * 12 + (p + 6)];
                            xb[f_sq * 12 + (p + 6)] = xw[sq * 12 + p];
                        }
                    }

                    const W_feat = MODEL_GRANDMASTER.W_feat;
                    const b_feat = MODEL_GRANDMASTER.b_feat;
                    const fw = new Float32Array(64);
                    const fb = new Float32Array(64);
                    for (let j = 0; j < 64; j++) {
                        let sw = b_feat[j];
                        let sb = b_feat[j];
                        for (let i = 0; i < 768; i++) {
                            if (xw[i] > 0) sw += W_feat[i][j];
                            if (xb[i] > 0) sb += W_feat[i][j];
                        }
                        fw[j] = Math.min(Math.max(sw, 0), 1.0);
                        fb[j] = Math.min(Math.max(sb, 0), 1.0);
                    }

                    const W_dense = MODEL_GRANDMASTER.W_dense;
                    const b_dense = MODEL_GRANDMASTER.b_dense;
                    const ad = new Float32Array(32);
                    for (let k = 0; k < 32; k++) {
                        let sum = b_dense[k];
                        for (let j = 0; j < 64; j++) {
                            sum += fw[j] * W_dense[j][k];
                            sum += fb[j] * W_dense[64 + j][k];
                        }
                        ad[k] = sum > 0 ? sum : sum * 0.1;
                    }

                    let out = MODEL_GRANDMASTER.b_out[0];
                    for (let k = 0; k < 32; k++) {
                        out += ad[k] * MODEL_GRANDMASTER.W_out[k][0];
                    }
                    return Math.tanh(out) * 6.0;
                }
            }

            static getBestMove(engine, botKey) {
                const bot = BOTS[botKey] || BOTS['tactician'];
                const moves = engine.getAllLegalMoves(engine.turn);
                if (moves.length === 0) return null;

                const pieceVals = { p: 1, n: 3, b: 3, r: 5, q: 9, k: 100 };
                moves.sort((a, b) => {
                    const capA = engine.board[a.toR][a.toC] ? (pieceVals[engine.board[a.toR][a.toC].type] || 1) : 0;
                    const capB = engine.board[b.toR][b.toC] ? (pieceVals[engine.board[b.toR][b.toC].type] || 1) : 0;
                    return capB - capA;
                });

                if (botKey === 'novice') {
                    moves.sort(() => Math.random() - 0.2);
                }

                const isWhite = (engine.turn === 'w');
                let bestScore = isWhite ? -Infinity : Infinity;
                let bestMove = moves[0];

                for (const m of moves) {
                    engine.makeMove(m);
                    const score = this.minimax(engine, bot.depth - 1, -Infinity, Infinity, !isWhite, botKey);
                    engine.undo();

                    if (isWhite) {
                        if (score > bestScore) {
                            bestScore = score;
                            bestMove = m;
                        }
                    } else {
                        if (score < bestScore) {
                            bestScore = score;
                            bestMove = m;
                        }
                    }
                }
                return bestMove;
            }

            static minimax(engine, depth, alpha, beta, isMaximizing, botKey) {
                if (depth === 0) return this.evaluate(engine, botKey);

                const color = isMaximizing ? 'w' : 'b';
                const moves = engine.getAllLegalMoves(color);
                if (moves.length === 0) {
                    if (engine.isInCheck(color)) return isMaximizing ? -9999 : 9999;
                    return 0;
                }

                if (isMaximizing) {
                    let maxEval = -Infinity;
                    for (const m of moves) {
                        engine.makeMove(m);
                        const ev = this.minimax(engine, depth - 1, alpha, beta, false, botKey);
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
                        const ev = this.minimax(engine, depth - 1, alpha, beta, true, botKey);
                        engine.undo();
                        minEval = Math.min(minEval, ev);
                        beta = Math.min(beta, ev);
                        if (beta <= alpha) break;
                    }
                    return minEval;
                }
            }
        }

        /* ── Full Chess Engine Core with Variant Support ── */
        class ChessEngine {
            constructor() {
                this.reset('classic');
            }
            reset(variant = 'classic') {
                this.board = Array(8).fill(null).map(() => Array(8).fill(null));
                this.turn = 'w';
                this.castling = { w: { k: true, q: true }, b: { k: true, q: true } };
                this.enPassant = null;
                this.halfMoves = 0;
                this.moveHistory = [];
                this.captured = { w: [], b: [] };
                this.currentVariant = variant;
                this.setupBoard(variant);
            }
            setupBoard(variant) {
                if (variant === 'classic' || !variant) {
                    const backRow = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'];
                    for (let c = 0; c < 8; c++) {
                        this.board[0][c] = { type: backRow[c], color: 'b' };
                        this.board[1][c] = { type: 'p', color: 'b' };
                        this.board[6][c] = { type: 'p', color: 'w' };
                        this.board[7][c] = { type: backRow[c], color: 'w' };
                    }
                    this.castling = { w: { k: true, q: true }, b: { k: true, q: true } };
                } else {
                    const pType = (variant === 'pawns') ? 'p' :
                                  (variant === 'knights') ? 'n' :
                                  (variant === 'bishops') ? 'b' :
                                  (variant === 'rooks') ? 'r' :
                                  (variant === 'queens') ? 'q' : 'p';
                    for (let r = 0; r < 2; r++) {
                        for (let c = 0; c < 8; c++) {
                            if (r === 0 && c === 4) {
                                this.board[r][c] = { type: 'k', color: 'b' };
                            } else {
                                this.board[r][c] = { type: pType, color: 'b' };
                            }
                        }
                    }
                    for (let r = 6; r < 8; r++) {
                        for (let c = 0; c < 8; c++) {
                            if (r === 7 && c === 4) {
                                this.board[r][c] = { type: 'k', color: 'w' };
                            } else {
                                this.board[r][c] = { type: pType, color: 'w' };
                            }
                        }
                    }
                    this.castling = { w: { k: false, q: false }, b: { k: false, q: false } };
                }
            }
            isInBounds(r, c) { return r >= 0 && r < 8 && c >= 0 && c < 8; }
            findKing(color) {
                for (let r = 0; r < 8; r++) {
                    for (let c = 0; c < 8; c++) {
                        const p = this.board[r][c];
                        if (p && p.type === 'k' && p.color === color) return [r, c];
                    }
                }
                return null;
            }
            isSquareAttacked(r, c, attackerColor) {
                for (let br = 0; br < 8; br++) {
                    for (let bc = 0; bc < 8; bc++) {
                        const p = this.board[br][bc];
                        if (p && p.color === attackerColor) {
                            if (this.canPieceAttack(p, br, bc, r, c)) return true;
                        }
                    }
                }
                return false;
            }
            canPieceAttack(p, fromR, fromC, toR, toC) {
                const dr = toR - fromR;
                const dc = toC - fromC;
                const absDr = Math.abs(dr);
                const absDc = Math.abs(dc);

                switch (p.type) {
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
                }
                return false;
            }
            isRayClear(fromR, fromC, toR, toC) {
                const stepR = Math.sign(toR - fromR);
                const stepC = Math.sign(toC - fromC);
                let currR = fromR + stepR;
                let currC = fromC + stepC;
                while (currR !== toR || currC !== toC) {
                    if (this.board[currR][currC] !== null) return false;
                    currR += stepR;
                    currC += stepC;
                }
                return true;
            }
            isInCheck(color) {
                const kPos = this.findKing(color);
                if (!kPos) return false;
                return this.isSquareAttacked(kPos[0], kPos[1], color === 'w' ? 'b' : 'w');
            }
            getLegalMoves(r, c) {
                const p = this.board[r][c];
                if (!p || p.color !== this.turn) return [];
                const pseudo = this.getPseudoMoves(r, c);
                const legal = [];
                for (const m of pseudo) {
                    this.makeMove(m);
                    if (!this.isInCheck(p.color)) {
                        legal.push(m);
                    }
                    this.undo();
                }
                return legal;
            }
            getPseudoMoves(r, c) {
                const p = this.board[r][c];
                if (!p) return [];
                const moves = [];
                const opp = p.color === 'w' ? 'b' : 'w';

                if (p.type === 'p') {
                    const dir = p.color === 'w' ? -1 : 1;
                    const canDouble = (p.color === 'w' && r >= 6) || (p.color === 'b' && r <= 1);

                    // 1 Step forward
                    const f1R = r + dir;
                    if (this.isInBounds(f1R, c) && this.board[f1R][c] === null) {
                        moves.push({ fromR: r, fromC: c, toR: f1R, toC: c });
                        // 2 Steps forward
                        const f2R = r + 2 * dir;
                        if (canDouble && this.isInBounds(f2R, c) && this.board[f2R][c] === null) {
                            moves.push({ fromR: r, fromC: c, toR: f2R, toC: c });
                        }
                    }

                    // Captures & En Passant
                    for (const dc of [-1, 1]) {
                        const toC = c + dc;
                        if (this.isInBounds(f1R, toC)) {
                            const target = this.board[f1R][toC];
                            if (target && target.color === opp) {
                                moves.push({ fromR: r, fromC: c, toR: f1R, toC: toC });
                            } else if (this.enPassant && this.enPassant[0] === f1R && this.enPassant[1] === toC) {
                                moves.push({ fromR: r, fromC: c, toR: f1R, toC: toC, isEnPassant: true });
                            }
                        }
                    }
                } else if (p.type === 'n') {
                    const offsets = [[-2,-1],[-2,1],[-1,-2],[-1,2],[1,-2],[1,2],[2,-1],[2,1]];
                    for (const [dr, dc] of offsets) {
                        const tr = r + dr, tc = c + dc;
                        if (this.isInBounds(tr, tc)) {
                            const t = this.board[tr][tc];
                            if (!t || t.color === opp) moves.push({ fromR: r, fromC: c, toR: tr, toC: tc });
                        }
                    }
                } else if (p.type === 'b' || p.type === 'r' || p.type === 'q') {
                    const dirs = [];
                    if (p.type === 'b' || p.type === 'q') dirs.push([-1,-1],[-1,1],[1,-1],[1,1]);
                    if (p.type === 'r' || p.type === 'q') dirs.push([-1,0],[1,0],[0,-1],[0,1]);

                    for (const [dr, dc] of dirs) {
                        let tr = r + dr, tc = c + dc;
                        while (this.isInBounds(tr, tc)) {
                            const t = this.board[tr][tc];
                            if (!t) {
                                moves.push({ fromR: r, fromC: c, toR: tr, toC: tc });
                            } else {
                                if (t.color === opp) moves.push({ fromR: r, fromC: c, toR: tr, toC: tc });
                                break;
                            }
                            tr += dr; tc += dc;
                        }
                    }
                } else if (p.type === 'k') {
                    for (let dr = -1; dr <= 1; dr++) {
                        for (let dc = -1; dc <= 1; dc++) {
                            if (dr === 0 && dc === 0) continue;
                            const tr = r + dr, tc = c + dc;
                            if (this.isInBounds(tr, tc)) {
                                const t = this.board[tr][tc];
                                if (!t || t.color === opp) moves.push({ fromR: r, fromC: c, toR: tr, toC: tc });
                            }
                        }
                    }

                    // Castling (Classic only)
                    if (this.currentVariant === 'classic' && !this.isInCheck(p.color)) {
                        const cRights = this.castling[p.color];
                        const row = p.color === 'w' ? 7 : 0;
                        if (r === row && c === 4) {
                            if (cRights.k && !this.board[row][5] && !this.board[row][6] &&
                                !this.isSquareAttacked(row, 5, opp) && !this.isSquareAttacked(row, 6, opp)) {
                                moves.push({ fromR: r, fromC: c, toR: row, toC: 6, isCastle: 'k' });
                            }
                            if (cRights.q && !this.board[row][3] && !this.board[row][2] && !this.board[row][1] &&
                                !this.isSquareAttacked(row, 3, opp) && !this.isSquareAttacked(row, 2, opp)) {
                                moves.push({ fromR: r, fromC: c, toR: row, toC: 2, isCastle: 'q' });
                            }
                        }
                    }
                }
                return moves;
            }
            getAllLegalMoves(color) {
                const all = [];
                for (let r = 0; r < 8; r++) {
                    for (let c = 0; c < 8; c++) {
                        if (this.board[r][c] && this.board[r][c].color === color) {
                            all.push(...this.getLegalMoves(r, c));
                        }
                    }
                }
                return all;
            }
            makeMove(m, promoType = 'q') {
                const p = this.board[m.fromR][m.fromC];
                const captured = this.board[m.toR][m.toC];
                const state = {
                    move: m,
                    captured: captured,
                    pType: p.type,
                    castling: { w: { ...this.castling.w }, b: { ...this.castling.b } },
                    enPassant: this.enPassant,
                    halfMoves: this.halfMoves
                };

                if (captured) {
                    this.captured[p.color].push(captured);
                }

                this.board[m.toR][m.toC] = p;
                this.board[m.fromR][m.fromC] = null;

                if (m.isEnPassant) {
                    const capR = m.fromR;
                    const capC = m.toC;
                    state.enPassantCap = this.board[capR][capC];
                    state.enPassantCapPos = [capR, capC];
                    this.captured[p.color].push(this.board[capR][capC]);
                    this.board[capR][capC] = null;
                }

                if (m.isCastle === 'k') {
                    const rook = this.board[m.fromR][7];
                    this.board[m.fromR][5] = rook;
                    this.board[m.fromR][7] = null;
                } else if (m.isCastle === 'q') {
                    const rook = this.board[m.fromR][0];
                    this.board[m.fromR][3] = rook;
                    this.board[m.fromR][0] = null;
                }

                if (p.type === 'p' && (m.toR === 0 || m.toR === 7)) {
                    p.type = promoType;
                    m.promoted = promoType;
                }

                if (p.type === 'p' && Math.abs(m.toR - m.fromR) === 2) {
                    this.enPassant = [(m.fromR + m.toR) / 2, m.fromC];
                } else {
                    this.enPassant = null;
                }

                if (p.type === 'k') {
                    this.castling[p.color].k = false;
                    this.castling[p.color].q = false;
                }
                if (p.type === 'r') {
                    if (m.fromR === 7 && m.fromC === 0) this.castling.w.q = false;
                    if (m.fromR === 7 && m.fromC === 7) this.castling.w.k = false;
                    if (m.fromR === 0 && m.fromC === 0) this.castling.b.q = false;
                    if (m.fromR === 0 && m.fromC === 7) this.castling.b.k = false;
                }

                this.moveHistory.push(state);
                this.turn = (this.turn === 'w' ? 'b' : 'w');
                return { captured };
            }
            undo() {
                if (this.moveHistory.length === 0) return null;
                const state = this.moveHistory.pop();
                const m = state.move;
                const p = this.board[m.toR][m.toC];
                p.type = state.pType;

                this.board[m.fromR][m.fromC] = p;
                this.board[m.toR][m.toC] = state.captured;

                if (state.captured) {
                    this.captured[p.color].pop();
                }

                if (m.isEnPassant && state.enPassantCapPos) {
                    this.board[m.toR][m.toC] = null;
                    this.board[state.enPassantCapPos[0]][state.enPassantCapPos[1]] = state.enPassantCap;
                }

                if (m.isCastle === 'k') {
                    const rook = this.board[m.fromR][5];
                    this.board[m.fromR][7] = rook;
                    this.board[m.fromR][5] = null;
                } else if (m.isCastle === 'q') {
                    const rook = this.board[m.fromR][3];
                    this.board[m.fromR][0] = rook;
                    this.board[m.fromR][3] = null;
                }

                this.castling = state.castling;
                this.enPassant = state.enPassant;
                this.halfMoves = state.halfMoves;
                this.turn = (this.turn === 'w' ? 'b' : 'w');
                return m;
            }
        }

        /* ── UI Controller & Game Loop ── */
        const engine = new ChessEngine();
        let currentGameMode = 'bot'; // 'bot', 'pass-and-play', 'variant'
        let currentVariant = 'classic';
        let selectedPlayerSide = 'w'; // 'w' or 'b'
        let activeBotKey = localStorage.getItem('chess_selected_bot') || 'tactician';
        if (!BOTS[activeBotKey]) activeBotKey = 'tactician';

        let isTimedMode = false;
        let isFlipped = false;
        let selectedSq = null;
        let legalMovesForSel = [];
        let lastMove = null;
        let pendingPromoMove = null;
        let isBotThinking = false;

        let whiteSeconds = 600;
        let blackSeconds = 600;
        let timerInterval = null;

        function showMenu() {
            clearInterval(timerInterval);
            document.getElementById('game-view').classList.remove('active');
            document.getElementById('menu-view').classList.add('active');
        }

        function showGame() {
            document.getElementById('menu-view').classList.remove('active');
            document.getElementById('game-view').classList.add('active');
        }

        function setPlayerSide(side) {
            selectedPlayerSide = side;
            document.getElementById('side-w-btn').classList.toggle('active', side === 'w');
            document.getElementById('side-b-btn').classList.toggle('active', side === 'b');
        }

        function startBotGame(botKey) {
            currentGameMode = 'bot';
            currentVariant = 'classic';
            activeBotKey = botKey;
            localStorage.setItem('chess_selected_bot', botKey);
            isTimedMode = false;

            // If playing Black, board is flipped and bot is White
            isFlipped = (selectedPlayerSide === 'b');
            setupMatchView();
            showGame();

            // If player chose Black, bot moves first as White!
            if (selectedPlayerSide === 'b') {
                isBotThinking = true;
                showThinking(true);
                setTimeout(makeAIMove, 350);
            }
        }

        function startPassAndPlay(isTimed) {
            currentGameMode = 'pass-and-play';
            currentVariant = 'classic';
            isTimedMode = isTimed;
            isFlipped = false;
            setupMatchView();
            showGame();
        }

        function startArmyGame(variantKey) {
            currentGameMode = 'variant';
            currentVariant = variantKey;
            isTimedMode = false;
            isFlipped = false;
            setupMatchView();
            showGame();
        }

        function setupMatchView() {
            engine.reset(currentVariant);
            lastMove = null;
            selectedSq = null;
            legalMovesForSel = [];
            isBotThinking = false;
            showThinking(false);

            whiteSeconds = 600;
            blackSeconds = 600;
            clearInterval(timerInterval);

            // Update Header & Player Bars
            const bot = BOTS[activeBotKey];
            const topAvatar = document.getElementById('top-avatar');
            const topName = document.getElementById('top-name');
            const topElo = document.getElementById('top-elo');
            const bottomAvatar = document.getElementById('bottom-avatar');
            const bottomName = document.getElementById('bottom-name');
            const modeSubtitle = document.getElementById('mode-subtitle');

            if (currentGameMode === 'bot') {
                const playerIsWhite = (selectedPlayerSide === 'w');
                modeSubtitle.innerText = `vs ${bot.name} (${bot.elo} Elo)`;
                if (playerIsWhite) {
                    topAvatar.innerText = bot.badge;
                    topName.innerText = bot.name;
                    topElo.style.display = 'inline';
                    topElo.innerText = `${bot.elo} Elo`;
                    bottomAvatar.innerText = 'You';
                    bottomName.innerText = 'You (White)';
                } else {
                    topAvatar.innerText = bot.badge;
                    topName.innerText = bot.name + ' (White)';
                    topElo.style.display = 'inline';
                    topElo.innerText = `${bot.elo} Elo`;
                    bottomAvatar.innerText = 'You';
                    bottomName.innerText = 'You (Black)';
                }
            } else if (currentGameMode === 'pass-and-play') {
                modeSubtitle.innerText = isTimedMode ? '2 Players • 10 Min Blitz' : '2 Players • Casual';
                topAvatar.innerText = 'P2';
                topName.innerText = 'Player 2 (Black)';
                topElo.style.display = 'none';
                bottomAvatar.innerText = 'P1';
                bottomName.innerText = 'Player 1 (White)';
            } else {
                const varTitles = {
                    'classic': 'Classic Chess',
                    'pawns': 'Pawns Only Variant',
                    'knights': 'Knights Only Variant',
                    'bishops': 'Bishops Only Variant',
                    'rooks': 'Rooks Only Variant',
                    'queens': 'Queens Only Variant'
                };
                modeSubtitle.innerText = varTitles[currentVariant] || 'Army Variant';
                topAvatar.innerText = 'B';
                topName.innerText = 'Black Army';
                topElo.style.display = 'none';
                bottomAvatar.innerText = 'W';
                bottomName.innerText = 'White Army';
            }

            // Timers
            const topTimer = document.getElementById('top-timer');
            const bottomTimer = document.getElementById('bottom-timer');
            if (isTimedMode) {
                topTimer.style.display = 'block';
                bottomTimer.style.display = 'block';
                updateTimerDisplays();
                timerInterval = setInterval(tickTimer, 1000);
            } else {
                topTimer.style.display = 'none';
                bottomTimer.style.display = 'none';
            }

            renderBoard();
            updateStatus();
        }

        function restartCurrentGame() {
            closeModal('game-over-modal');
            setupMatchView();
            if (currentGameMode === 'bot' && selectedPlayerSide === 'b') {
                isBotThinking = true;
                showThinking(true);
                setTimeout(makeAIMove, 350);
            }
        }

        function flipBoard() {
            isFlipped = !isFlipped;
            renderBoard();
        }

        function undoMove() {
            if (isBotThinking) return;
            if (currentGameMode === 'bot') {
                // In bot mode, undo bot move + player move
                engine.undo();
                engine.undo();
            } else {
                engine.undo();
            }
            lastMove = engine.moveHistory.length ? engine.moveHistory[engine.moveHistory.length - 1].move : null;
            selectedSq = null;
            legalMovesForSel = [];
            renderBoard();
            updateStatus();
        }

        function tickTimer() {
            if (engine.turn === 'w') {
                whiteSeconds = Math.max(0, whiteSeconds - 1);
            } else {
                blackSeconds = Math.max(0, blackSeconds - 1);
            }
            updateTimerDisplays();

            if (whiteSeconds <= 0 || blackSeconds <= 0) {
                clearInterval(timerInterval);
                const winner = whiteSeconds <= 0 ? 'Black' : 'White';
                showModal('game-over-modal', 'Time Out!', `${winner} wins on time.`);
            }
        }

        function updateTimerDisplays() {
            const fmt = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
            document.getElementById('bottom-timer').innerText = isFlipped ? fmt(blackSeconds) : fmt(whiteSeconds);
            document.getElementById('top-timer').innerText = isFlipped ? fmt(whiteSeconds) : fmt(blackSeconds);
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

                    // Coordinates
                    if (visualC === 0) {
                        const rankSpan = document.createElement('span');
                        rankSpan.className = 'coord rank';
                        rankSpan.innerText = isFlipped ? (r + 1) : (8 - r);
                        sq.appendChild(rankSpan);
                    }
                    if (visualR === 7) {
                        const fileSpan = document.createElement('span');
                        fileSpan.className = 'coord file';
                        fileSpan.innerText = String.fromCharCode(97 + c);
                        sq.appendChild(fileSpan);
                    }

                    // Piece Rendering via Vector SVG
                    const p = engine.board[r][c];
                    if (p) {
                        const pEl = document.createElement('div');
                        pEl.className = 'piece';
                        pEl.innerHTML = PIECE_SVGS[p.color + p.type] || '';
                        sq.appendChild(pEl);
                    }

                    // Legal Move Hints
                    const isLegalTarget = legalMovesForSel.find(m => m.toR === r && m.toC === c);
                    if (isLegalTarget) {
                        const hint = document.createElement('div');
                        hint.className = p ? 'hint-ring' : 'hint-dot';
                        sq.appendChild(hint);
                    }

                    sq.addEventListener('pointerdown', (e) => onSquareClick(r, c, e));
                    boardEl.appendChild(sq);
                }
            }
            updateCapturedDisplay();
            updateEvaluationBar();
        }

        function onSquareClick(r, c, e) {
            if (isBotThinking) return;
            audio.init();

            // In Bot mode, prevent human from moving bot's pieces
            if (currentGameMode === 'bot') {
                const botColor = (selectedPlayerSide === 'w') ? 'b' : 'w';
                if (engine.turn === botColor) return;
            }

            const p = engine.board[r][c];

            if (selectedSq) {
                const move = legalMovesForSel.find(m => m.toR === r && m.toC === c);
                if (move) {
                    const selP = engine.board[selectedSq[0]][selectedSq[1]];
                    if (selP.type === 'p' && (r === 0 || r === 7)) {
                        pendingPromoMove = move;
                        openPromoModal(selP.color);
                        return;
                    }
                    executeMove(move);
                    selectedSq = null;
                    legalMovesForSel = [];
                    return;
                }
            }

            if (p && p.color === engine.turn) {
                selectedSq = [r, c];
                legalMovesForSel = engine.getLegalMoves(r, c);
            } else {
                selectedSq = null;
                legalMovesForSel = [];
            }
            renderBoard();
        }

        function openPromoModal(color) {
            document.getElementById('promo-icon-q').innerHTML = PIECE_SVGS[color + 'q'];
            document.getElementById('promo-icon-r').innerHTML = PIECE_SVGS[color + 'r'];
            document.getElementById('promo-icon-b').innerHTML = PIECE_SVGS[color + 'b'];
            document.getElementById('promo-icon-n').innerHTML = PIECE_SVGS[color + 'n'];
            document.getElementById('promo-modal').classList.add('active');
        }

        function confirmPromotion(pieceType) {
            closeModal('promo-modal');
            if (pendingPromoMove) {
                executeMove(pendingPromoMove, pieceType);
                pendingPromoMove = null;
                selectedSq = null;
                legalMovesForSel = [];
            }
        }

        function executeMove(m, promoType = 'q') {
            const res = engine.makeMove(m, promoType);
            lastMove = m;

            if (engine.isInCheck(engine.turn)) {
                audio.play('check');
            } else if (res.captured) {
                audio.play('capture');
            } else {
                audio.play('move');
            }

            renderBoard();
            updateStatus();

            if (checkGameEnd()) return;

            // Trigger Bot Move if applicable
            if (currentGameMode === 'bot') {
                const botColor = (selectedPlayerSide === 'w') ? 'b' : 'w';
                if (engine.turn === botColor) {
                    isBotThinking = true;
                    showThinking(true);
                    setTimeout(makeAIMove, 250);
                }
            }
        }

        function makeAIMove() {
            const bestMove = NeuralEngine.getBestMove(engine, activeBotKey);
            isBotThinking = false;
            showThinking(false);

            if (bestMove) {
                const res = engine.makeMove(bestMove, 'q');
                lastMove = bestMove;

                if (engine.isInCheck(engine.turn)) {
                    audio.play('check');
                } else if (res.captured) {
                    audio.play('capture');
                } else {
                    audio.play('move');
                }

                renderBoard();
                updateStatus();
                checkGameEnd();
            }
        }

        function showThinking(thinking) {
            const spinner = document.getElementById('status-spinner');
            const bot = BOTS[activeBotKey];
            if (thinking) {
                spinner.style.display = 'inline-block';
                document.getElementById('status-msg').innerText = `${bot.name} is thinking...`;
            } else {
                spinner.style.display = 'none';
            }
        }

        function checkGameEnd() {
            const moves = engine.getAllLegalMoves(engine.turn);
            if (moves.length === 0) {
                clearInterval(timerInterval);
                if (engine.isInCheck(engine.turn)) {
                    const winner = engine.turn === 'w' ? 'Black' : 'White';
                    showModal('game-over-modal', 'Checkmate!', `${winner} wins the game!`);
                } else {
                    showModal('game-over-modal', 'Stalemate!', 'The game is drawn by stalemate.');
                }
                return true;
            }
            return false;
        }

        function showModal(id, title, desc) {
            document.getElementById('game-over-title').innerText = title;
            document.getElementById('game-over-desc').innerText = desc;
            document.getElementById(id).classList.add('active');
        }

        function closeModal(id) {
            document.getElementById(id).classList.remove('active');
        }

        function updateStatus() {
            if (isBotThinking) return;
            const turnStr = (engine.turn === 'w') ? "White's Turn" : "Black's Turn";
            const check = engine.isInCheck(engine.turn) ? " — IN CHECK!" : "";
            document.getElementById('status-title').innerText = `${turnStr}${check}`;
            document.getElementById('status-msg').innerText = `${turnStr}${check}`;

            // Timer active state
            if (isTimedMode) {
                const isWhiteTurn = (engine.turn === 'w');
                const isBottomTurn = isFlipped ? !isWhiteTurn : isWhiteTurn;
                document.getElementById('bottom-timer').classList.toggle('active', isBottomTurn);
                document.getElementById('top-timer').classList.toggle('active', !isBottomTurn);
            }
        }

        function updateEvaluationBar() {
            const evalScore = NeuralEngine.evaluate(engine, activeBotKey);
            const whitePct = Math.min(Math.max(50 + (evalScore * 10), 5), 95);
            document.getElementById('eval-bar-white').style.height = `${whitePct}%`;
            const sign = evalScore > 0 ? '+' : '';
            document.getElementById('eval-score-text').innerText = `${sign}${evalScore.toFixed(1)}`;
        }

        function updateCapturedDisplay() {
            const renderCaps = (list, containerId) => {
                const el = document.getElementById(containerId);
                el.innerHTML = '';
                for (const p of list) {
                    const span = document.createElement('span');
                    span.className = 'cap-svg';
                    span.innerHTML = PIECE_SVGS[p.color + p.type] || '';
                    el.appendChild(span);
                }
            };
            renderCaps(engine.captured.b, 'top-captured');
            renderCaps(engine.captured.w, 'bottom-captured');
        }

        function setupPWA() {
            let deferredPrompt;
            window.addEventListener('beforeinstallprompt', (e) => {
                e.preventDefault();
                deferredPrompt = e;
                const quickBtn = document.getElementById('pwa-quick-install-btn');
                if (quickBtn) {
                    quickBtn.addEventListener('click', () => {
                        deferredPrompt.prompt();
                        deferredPrompt.userChoice.then(() => { deferredPrompt = null; });
                    });
                }
            });

            const manifest = {
                "name": "Chess Master",
                "short_name": "Chess",
                "start_url": ".",
                "display": "standalone",
                "background_color": "#262421",
                "theme_color": "#262421",
                "icons": [
                    {
                        "src": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='20' fill='%23262421'/><path d='M50 20c15 1 24 12 23 42L40 62C40 50 35 40 34 32c-1-8 6-13 12-14z' fill='%2381b64c'/></svg>",
                        "sizes": "192x192 512x512",
                        "type": "image/svg+xml"
                    }
                ]
            };
            const blob = new Blob([JSON.stringify(manifest)], { type: 'application/json' });
            const link = document.createElement('link');
            link.rel = 'manifest';
            link.href = URL.createObjectURL(blob);
            document.head.appendChild(link);
        }

        window.addEventListener('DOMContentLoaded', () => {
            setupPWA();
        });
    </script>
</body>
</html>"""

    html = template.replace("__INSTALLER_BANNER__", installer_banner_html)
    html = html.replace("__NOVICE_JSON__", novice_json_str)
    html = html.replace("__TACTICIAN_JSON__", tactician_json_str)
    html = html.replace("__GRANDMASTER_JSON__", grandmaster_json_str)
    return html

# 1. Generate index.html
index_html = generate_html(is_phone_installer=False)
with open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(index_html)
print(f"[+] Successfully generated index.html ({len(index_html)} bytes)")

# 2. Generate Install-Chess-Android.html
android_html = generate_html(is_phone_installer=True)
with open(os.path.join(ROOT, 'Install-Chess-Android.html'), 'w', encoding='utf-8') as f:
    f.write(android_html)
print(f"[+] Successfully generated Install-Chess-Android.html ({len(android_html)} bytes)")

# 3. Generate Install-On-Phone.html (served over Wi-Fi)
with open(os.path.join(ROOT, 'Install-On-Phone.html'), 'w', encoding='utf-8') as f:
    f.write(android_html)
print(f"[+] Successfully generated Install-On-Phone.html ({len(android_html)} bytes)")

# 4. Synchronize Android APK assets
android_assets_dir = os.path.join(ROOT, 'chess-android', 'app', 'src', 'main', 'assets')
if os.path.exists(android_assets_dir):
    shutil.copy(os.path.join(ROOT, 'index.html'), os.path.join(android_assets_dir, 'index.html'))
    print(f"[+] Successfully updated {os.path.join(android_assets_dir, 'index.html')}")

if __name__ == '__main__':
    print("[*] Build completed successfully!")
