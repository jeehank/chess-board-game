import base64

with open('Chess.jar', 'rb') as f:
    jar_data = f.read()

b64 = base64.b64encode(jar_data).decode('ascii')
lines = [b64[i:i+76] for i in range(0, len(b64), 76)]
payload = '\n'.join(lines)

sh_code = f'''#!/data/data/com.termux/files/usr/bin/bash
# Chess Game - Single File Installer for Android (Termux)
set -e

echo "========================================================"
echo "          CHESS GAME - ANDROID ONE-CLICK SETUP"
echo "========================================================"
echo ""

APP_DIR="$HOME/chess"
mkdir -p "$APP_DIR"

echo "[1/4] Extracting embedded Chess Game..."
sed -n '/^__PAYLOAD_START__$/,/^__PAYLOAD_END__$/p' "$0" | grep -v '^__' | base64 -d > "$APP_DIR/Chess.jar"

echo "[2/4] Checking and installing dependencies (Java & X11 GUI)..."
if ! command -v java >/dev/null 2>&1; then
    echo "[*] Installing OpenJDK 17..."
    pkg update -y
    pkg install -y openjdk-17
fi

if ! command -v termux-x11 >/dev/null 2>&1; then
    echo "[*] Installing Termux X11 graphics server..."
    pkg install -y x11-repo
    pkg install -y termux-x11 pulseaudio
fi

echo "[3/4] Creating launcher script..."
cat << 'EOF' > "$APP_DIR/launch.sh"
#!/data/data/com.termux/files/usr/bin/bash
export DISPLAY=:0
pulseaudio --start --exit-idle-time=-1 >/dev/null 2>&1 || true
am start --user 0 -n com.termux.x11/com.termux.x11.MainActivity >/dev/null 2>&1 || true
sleep 1
java -jar "$HOME/chess/Chess.jar"
EOF
chmod +x "$APP_DIR/launch.sh"

echo "[4/4] Setup complete!"
echo ""
echo "========================================================"
echo " Starting Chess Game..."
echo " (Make sure Termux:X11 app is installed from GitHub/F-Droid)"
echo "========================================================"
echo ""
bash "$APP_DIR/launch.sh"
exit 0

__PAYLOAD_START__
{payload}
__PAYLOAD_END__
'''

with open('Install-Chess-Android.sh', 'w', encoding='utf-8', newline='\n') as f:
    f.write(sh_code)

print('Install-Chess-Android.sh created successfully!')
