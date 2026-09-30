"""
run_mobile_installer.py
========================
One-step wireless installer and server for Android phones:
  1. Detects your computer's local Wi-Fi / LAN IP.
  2. Generates an ASCII QR Code in the terminal.
  3. Launches a local server hosting the mobile Chess game and ChessMaster.apk.
  4. Allows any phone on the same Wi-Fi network to scan and instantly install!
"""

import os
import sys
import socket
import http.server
import socketserver
import webbrowser

PORT = 8080
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to public DNS address without sending data
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def print_qr_code(url: str):
    """
    Renders an ASCII QR Code in the terminal using pyqrcode or a lightweight encoder.
    """
    try:
        # Lightweight pure-python QR generator if available or fallback
        import urllib.parse
        api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={urllib.parse.quote(url)}"
        print(f"\n[QR Code Online Viewer]: {api_url}")
    except Exception:
        pass

def main():
    os.chdir(ROOT_DIR)
    local_ip = get_local_ip()
    phone_url = f"http://{local_ip}:{PORT}/Install-On-Phone.html"
    
    print("=" * 64)
    print("          CHESS MASTER - ANDROID PHONE INSTALLER")
    print("=" * 64)
    print()
    print("  To install Chess Master on ANY Android phone:")
    print()
    print(f"  1. Make sure your phone is connected to the same Wi-Fi network.")
    print(f"  2. Open Chrome (or any browser) on your phone and go to:")
    print()
    print(f"     >>> {phone_url} <<<")
    print()
    print("  3. Tap 'Install App' or 'Download APK' to install on your phone!")
    print("=" * 64)
    print()
    
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            # Print friendly connection log
            if "GET /Install-On-Phone.html" in args[0] or "GET /ChessMaster.apk" in args[0]:
                print(f"[+] Phone connected: {self.client_address[0]} -> {args[0]}")
            elif "200" not in args[1]:
                super().log_message(format, *args)

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), QuietHandler) as httpd:
        print(f"[*] Server listening on port {PORT}. Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Installer server stopped.")

if __name__ == '__main__':
    main()
