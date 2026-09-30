"""
build_apk.py
=============
Compiles and packages the Chess game and trained models into a production-ready,
signed Android APK (ChessMaster.apk) using the Android SDK build-tools.
"""

import os
import subprocess
import shutil

SDK_DIR = r"C:\Users\HP\AppData\Local\Android\Sdk"
BUILD_TOOLS = os.path.join(SDK_DIR, "build-tools", "36.0.0")
BUILD_TOOLS_LIB = os.path.join(BUILD_TOOLS, "lib")
ANDROID_JAR = os.path.join(SDK_DIR, "platforms", "android-36", "android.jar")

JAVA_HOME = r"C:\Program Files\BlueJ\jdk"
JAVA = os.path.join(JAVA_HOME, "bin", "java.exe")
JAVAC = os.path.join(JAVA_HOME, "bin", "javac.exe")
KEYTOOL = os.path.join(JAVA_HOME, "bin", "keytool.exe")

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

def build_apk():
    print("=" * 60)
    print("      BUILDING NATIVE ANDROID APK (ChessMaster.apk)")
    print("=" * 60)

    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    os.makedirs(BUILD_DIR, exist_ok=True)

    src_dir = os.path.join(BUILD_DIR, "src", "com", "chessmaster", "app")
    bin_dir = os.path.join(BUILD_DIR, "bin")
    res_dir = os.path.join(BUILD_DIR, "res")
    res_vals = os.path.join(res_dir, "values")
    assets_dir = os.path.join(BUILD_DIR, "assets")
    
    os.makedirs(src_dir, exist_ok=True)
    os.makedirs(bin_dir, exist_ok=True)
    os.makedirs(res_vals, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    # 1. AndroidManifest.xml
    manifest_path = os.path.join(BUILD_DIR, "AndroidManifest.xml")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write('''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.chessmaster.app"
    android:versionCode="1"
    android:versionName="1.0">

    <uses-sdk android:minSdkVersion="21" android:targetSdkVersion="36" />
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.VIBRATE" />

    <application
        android:label="Chess Master"
        android:hardwareAccelerated="true"
        android:theme="@android:style/Theme.NoTitleBar.Fullscreen">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|screenLayout|keyboardHidden"
            android:theme="@android:style/Theme.NoTitleBar.Fullscreen">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
''')

    # strings.xml
    with open(os.path.join(res_vals, "strings.xml"), "w", encoding="utf-8") as f:
        f.write('''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Chess Master</string>
</resources>
''')

    # 2. MainActivity.java
    java_file = os.path.join(src_dir, "MainActivity.java")
    with open(java_file, "w", encoding="utf-8") as f:
        f.write('''package com.chessmaster.app;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        try {
            getWindow().getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                | View.SYSTEM_UI_FLAG_FULLSCREEN
                | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            );
        } catch (Exception ignored) {}

        webView = new WebView(this);
        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowContentAccess(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);

        webView.setWebViewClient(new WebViewClient());
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
''')

    # 3. Copy game assets, models, and pieces
    print("[1/5] Bundling HTML, pieces, and trained models into assets...")
    shutil.copy(os.path.join(ROOT, "index.html"), os.path.join(assets_dir, "index.html"))
    shutil.copytree(os.path.join(ROOT, "pieces"), os.path.join(assets_dir, "pieces"))
    shutil.copytree(os.path.join(ROOT, "models"), os.path.join(assets_dir, "models"))

    # 4. Compile Java source with javac
    print("[2/5] Compiling Java source...")
    cmd_javac = [
        JAVAC,
        "-source", "1.8",
        "-target", "1.8",
        "-cp", ANDROID_JAR,
        "-d", bin_dir,
        java_file
    ]
    res = subprocess.run(cmd_javac, capture_output=True, text=True, env=CUSTOM_ENV)
    if res.returncode != 0:
        print("[!] javac error:", res.stderr)
        return False

    # 5. Convert .class to classes.dex using d8 (direct java invocation)
    print("[3/5] Converting bytecode with d8 to classes.dex...")
    classes = [os.path.join(bin_dir, "com", "chessmaster", "app", "MainActivity.class")]
    cmd_d8 = [
        JAVA, "-cp", D8_JAR,
        "com.android.tools.r8.D8",
        "--min-api", "21",
        "--lib", ANDROID_JAR,
        "--output", bin_dir
    ] + classes
    res = subprocess.run(cmd_d8, capture_output=True, text=True, env=CUSTOM_ENV)
    if res.returncode != 0:
        print("[!] d8 error:", res.stderr)
        return False

    # 6. Package resources & assets using aapt
    print("[4/5] Packaging APK package with aapt...")
    unsigned_apk = os.path.join(BUILD_DIR, "unsigned.apk")
    cmd_aapt = [
        AAPT, "package", "-f",
        "-M", manifest_path,
        "-S", res_dir,
        "-A", assets_dir,
        "-I", ANDROID_JAR,
        "-F", unsigned_apk,
        bin_dir
    ]
    res = subprocess.run(cmd_aapt, capture_output=True, text=True, env=CUSTOM_ENV)
    if res.returncode != 0:
        print("[!] aapt error:", res.stderr)
        return False

    # 7. Align APK with zipalign
    aligned_apk = os.path.join(BUILD_DIR, "aligned.apk")
    cmd_zipalign = [ZIPALIGN, "-f", "-p", "4", unsigned_apk, aligned_apk]
    res = subprocess.run(cmd_zipalign, capture_output=True, text=True, env=CUSTOM_ENV)
    if res.returncode != 0:
        print("[!] zipalign error:", res.stderr)
        return False

    # 8. Sign APK with a debug keystore using apksigner
    print("[5/5] Signing APK with apksigner...")
    keystore = os.path.join(BUILD_DIR, "debug.keystore")
    if not os.path.exists(keystore):
        cmd_keytool = [
            KEYTOOL, "-genkeypair", "-v",
            "-keystore", keystore,
            "-storepass", "android",
            "-alias", "androiddebugkey",
            "-keypass", "android",
            "-keyalg", "RSA",
            "-keysize", "2048",
            "-validity", "10000",
            "-dname", "CN=ChessMaster, OU=Chess, O=Chess, L=Local, S=State, C=US"
        ]
        subprocess.run(cmd_keytool, capture_output=True, text=True, env=CUSTOM_ENV)

    cmd_sign = [
        JAVA, "-jar", APKSIGNER_JAR, "sign",
        "--ks", keystore,
        "--ks-pass", "pass:android",
        "--key-pass", "pass:android",
        "--out", OUTPUT_APK,
        aligned_apk
    ]
    res = subprocess.run(cmd_sign, capture_output=True, text=True, env=CUSTOM_ENV)
    if res.returncode != 0:
        print("[!] apksigner error:", res.stderr)
        return False

    # Clean up temp
    shutil.rmtree(BUILD_DIR, ignore_errors=True)

    size_mb = os.path.getsize(OUTPUT_APK) / (1024 * 1024)
    print()
    print("=" * 60)
    print(f" [SUCCESS] Android Installer APK created successfully!")
    print(f" Output File: {OUTPUT_APK} ({size_mb:.2f} MB)")
    print(f" Ready to install on ANY Android phone!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    build_apk()
