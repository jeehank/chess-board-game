"""
build_apk.py
=============
Compiles and packages the Chess game and trained models into a production-ready,
signed Android APK (ChessMaster.apk) using the Android SDK build-tools.

Fixed: Ensures classes.dex is the ONLY code artifact in the APK (no stray .class files),
targets SDK 34 for maximum device compatibility, and uses proper aapt packaging.
"""

import os
import subprocess
import shutil

SDK_DIR = r"C:\Users\HP\AppData\Local\Android\Sdk"
BUILD_TOOLS = os.path.join(SDK_DIR, "build-tools", "36.0.0")
BUILD_TOOLS_LIB = os.path.join(BUILD_TOOLS, "lib")
ANDROID_JAR = os.path.join(SDK_DIR, "platforms", "android-34", "android.jar")

JAVA_HOME = r"C:\Program Files\BlueJ\jdk"
JAVA = os.path.join(JAVA_HOME, "bin", "java.exe")
JAVAC = os.path.join(JAVA_HOME, "bin", "javac.exe")
KEYTOOL = os.path.join(JAVA_HOME, "bin", "keytool.exe")

AAPT2 = os.path.join(BUILD_TOOLS, "aapt2.exe")
AAPT = os.path.join(BUILD_TOOLS, "aapt.exe")
ZIPALIGN = os.path.join(BUILD_TOOLS, "zipalign.exe")
D8_JAR = os.path.join(BUILD_TOOLS_LIB, "d8.jar")
APKSIGNER_JAR = os.path.join(BUILD_TOOLS_LIB, "apksigner.jar")

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(ROOT, "build_apk_tmp")
OUTPUT_APK = os.path.join(ROOT, "ChessMaster.apk")

CUSTOM_ENV = os.environ.copy()
CUSTOM_ENV["JAVA_HOME"] = JAVA_HOME
CUSTOM_ENV["PATH"] = os.path.join(JAVA_HOME, "bin") + os.pathsep + CUSTOM_ENV.get("PATH", "")


def run(cmd, label=""):
    """Run a subprocess, print errors and return success boolean."""
    res = subprocess.run(cmd, capture_output=True, text=True, env=CUSTOM_ENV)
    if res.returncode != 0:
        print(f"[!] {label} FAILED (exit {res.returncode})")
        if res.stdout.strip():
            print("    stdout:", res.stdout.strip()[:500])
        if res.stderr.strip():
            print("    stderr:", res.stderr.strip()[:500])
        return False
    return True


def build_apk():
    print("=" * 60)
    print("      BUILDING ANDROID APK (ChessMaster.apk)")
    print("=" * 60)

    # Clean previous build
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)

    # Directory layout
    java_dir = os.path.join(BUILD_DIR, "java_src", "com", "chessmaster", "app")
    classes_dir = os.path.join(BUILD_DIR, "classes")
    dex_dir = os.path.join(BUILD_DIR, "dex")
    res_dir = os.path.join(BUILD_DIR, "res", "values")
    assets_dir = os.path.join(BUILD_DIR, "assets")

    for d in [java_dir, classes_dir, dex_dir, res_dir, assets_dir]:
        os.makedirs(d, exist_ok=True)

    # ── 1. AndroidManifest.xml ──
    manifest = os.path.join(BUILD_DIR, "AndroidManifest.xml")
    with open(manifest, "w", encoding="utf-8") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.chessmaster.app"
    android:versionCode="1"
    android:versionName="1.0">

    <uses-sdk android:minSdkVersion="21" android:targetSdkVersion="34" />
    <uses-permission android:name="android.permission.INTERNET" />

    <application
        android:label="Chess Master"
        android:hardwareAccelerated="true"
        android:theme="@android:style/Theme.NoTitleBar.Fullscreen">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|keyboardHidden"
            android:screenOrientation="portrait">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
""")

    # ── 2. res/values/strings.xml ──
    with open(os.path.join(res_dir, "strings.xml"), "w", encoding="utf-8") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Chess Master</string>
</resources>
""")

    # ── 3. MainActivity.java ──
    java_file = os.path.join(java_dir, "MainActivity.java")
    with open(java_file, "w", encoding="utf-8") as f:
        f.write("""package com.chessmaster.app;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebChromeClient;

public class MainActivity extends Activity {
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().setFlags(
            WindowManager.LayoutParams.FLAG_FULLSCREEN,
            WindowManager.LayoutParams.FLAG_FULLSCREEN
        );

        webView = new WebView(this);
        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowContentAccess(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        s.setUseWideViewPort(true);
        s.setLoadWithOverviewMode(true);

        webView.setWebViewClient(new WebViewClient());
        webView.setWebChromeClient(new WebChromeClient());
        webView.loadUrl("file:///android_asset/index.html");
        setContentView(webView);
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
""")

    # ── 4. Copy game assets ──
    print("[1/6] Bundling game HTML, pieces, and trained model files...")
    shutil.copy(os.path.join(ROOT, "index.html"), os.path.join(assets_dir, "index.html"))
    shutil.copytree(os.path.join(ROOT, "pieces"), os.path.join(assets_dir, "pieces"))
    shutil.copytree(os.path.join(ROOT, "models"), os.path.join(assets_dir, "models"))

    # ── 5. Compile Java → .class ──
    print("[2/6] Compiling Java source with javac...")
    if not run([JAVAC, "-source", "1.8", "-target", "1.8",
                "-cp", ANDROID_JAR, "-d", classes_dir, java_file], "javac"):
        return False

    # ── 6. Convert .class → classes.dex ──
    print("[3/6] Converting to Dalvik bytecode (classes.dex)...")
    class_file = os.path.join(classes_dir, "com", "chessmaster", "app", "MainActivity.class")
    if not run([JAVA, "-cp", D8_JAR, "com.android.tools.r8.D8",
                "--min-api", "21", "--lib", ANDROID_JAR,
                "--output", dex_dir, class_file], "d8"):
        return False

    # ── 7. aapt package: create unsigned APK with resources + assets + dex ──
    # IMPORTANT: We pass dex_dir (which has ONLY classes.dex) as the raw-files dir,
    # NOT the classes_dir (which has raw .class files that break installation).
    print("[4/6] Packaging APK with aapt...")
    unsigned_apk = os.path.join(BUILD_DIR, "unsigned.apk")
    if not run([AAPT, "package", "-f",
                "-M", manifest,
                "-S", os.path.join(BUILD_DIR, "res"),
                "-A", assets_dir,
                "-I", ANDROID_JAR,
                "-F", unsigned_apk,
                dex_dir], "aapt"):
        return False

    # ── 8. zipalign ──
    print("[5/6] Aligning APK...")
    aligned_apk = os.path.join(BUILD_DIR, "aligned.apk")
    if not run([ZIPALIGN, "-f", "-p", "4", unsigned_apk, aligned_apk], "zipalign"):
        return False

    # ── 9. Generate debug keystore & sign ──
    print("[6/6] Signing APK...")
    keystore = os.path.join(BUILD_DIR, "debug.keystore")
    run([KEYTOOL, "-genkeypair", "-v",
         "-keystore", keystore, "-storepass", "android",
         "-alias", "androiddebugkey", "-keypass", "android",
         "-keyalg", "RSA", "-keysize", "2048", "-validity", "10000",
         "-dname", "CN=ChessMaster,OU=Dev,O=Dev,L=X,S=X,C=US"], "keytool")

    if not run([JAVA, "-jar", APKSIGNER_JAR, "sign",
                "--ks", keystore, "--ks-pass", "pass:android",
                "--key-pass", "pass:android",
                "--out", OUTPUT_APK, aligned_apk], "apksigner"):
        return False

    # Verify
    res = subprocess.run([JAVA, "-jar", APKSIGNER_JAR, "verify", "-v", OUTPUT_APK],
                         capture_output=True, text=True, env=CUSTOM_ENV)
    print("    Verify:", res.stdout.strip().split('\n')[0])

    # Cleanup
    shutil.rmtree(BUILD_DIR, ignore_errors=True)

    size_mb = os.path.getsize(OUTPUT_APK) / (1024 * 1024)
    print()
    print("=" * 60)
    print(f"  ✅ ChessMaster.apk built successfully! ({size_mb:.2f} MB)")
    print(f"  📁 {OUTPUT_APK}")
    print(f"  📱 Transfer to your phone → tap → Install → Play!")
    print("=" * 60)
    return True


if __name__ == '__main__':
    build_apk()
