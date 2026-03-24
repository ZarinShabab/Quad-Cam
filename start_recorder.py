#!/usr/bin/env python3
"""
QUADCAM Recorder — Server
==========================
• Serves the recorder app at  http://localhost:8765/
• Handles POST /save  — receives video blobs and saves them into
  a dated folder:  Recordings/Recording_YYYY-MM-DD_HH-MM-SS/

Usage:
  Windows  : Double-click  START_RECORDER.bat
  Mac/Linux: python3 start_recorder.py
"""

import http.server
import socketserver
import threading
import webbrowser
import os
import sys
import time
import json
import urllib.parse

PORT      = 8765
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = "quad-camera-recorder.html"

# All recordings will be saved under:  <script folder>/Recordings/
RECORDINGS_ROOT = os.path.join(DIRECTORY, "Recordings")


# ─────────────────────────────────────────────────────────────────
class QuadCamHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, fmt, *args):
        pass  # suppress default request noise

    # ── POST /save  ──────────────────────────────────────────────
    def do_POST(self):
        if self.path != '/save':
            self.send_error(404)
            return

        folder   = self.headers.get('X-Folder',   'Recording_unknown')
        filename = self.headers.get('X-Filename',  'camera.webm')
        length   = int(self.headers.get('Content-Length', 0))

        # Sanitise path components (prevent directory traversal)
        folder   = os.path.basename(folder)
        filename = os.path.basename(filename)

        # Create:  Recordings/Recording_YYYY-MM-DD_HH-MM-SS/
        save_dir = os.path.join(RECORDINGS_ROOT, folder)
        os.makedirs(save_dir, exist_ok=True)

        filepath = os.path.join(save_dir, filename)

        try:
            data = self.rfile.read(length)
            with open(filepath, 'wb') as f:
                f.write(data)

            size_mb = len(data) / (1024 * 1024)
            print(f"  ✓  Saved  {filename}  ({size_mb:.1f} MB)")
            print(f"     → {filepath}")

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'ok': True,
                'path': filepath,
                'size': len(data)
            }).encode())

        except Exception as e:
            print(f"  ✗  Error saving {filename}: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': str(e)}).encode())

    # ── OPTIONS (CORS preflight) ──────────────────────────────────
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin',  '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Folder, X-Filename')
        self.end_headers()

    # ── GET — serve static files ─────────────────────────────────
    def do_GET(self):
        # Add CORS header for completeness
        super().do_GET()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()


# ─────────────────────────────────────────────────────────────────
def main():
    url = f"http://localhost:{PORT}/{HTML_FILE}"

    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║          QUADCAM RECORDER  —  Local Server           ║")
    print("╠══════════════════════════════════════════════════════╣")
    print(f"║  App     : {url:<42} ║")
    print(f"║  Saves   : {RECORDINGS_ROOT:<42} ║")
    print("╠══════════════════════════════════════════════════════╣")
    print("║  ► Connect USB cameras BEFORE launching              ║")
    print("║  ► Click ALLOW when browser asks for camera access   ║")
    print("║  ► Videos save automatically to a dated folder       ║")
    print("║  ► Press Ctrl+C here to stop the server              ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    # Check HTML exists
    if not os.path.exists(os.path.join(DIRECTORY, HTML_FILE)):
        print(f"  ERROR: '{HTML_FILE}' not found.")
        print(f"  Make sure start_recorder.py and {HTML_FILE} are in the same folder.")
        input("\n  Press Enter to exit...")
        sys.exit(1)

    # Create Recordings root folder upfront
    os.makedirs(RECORDINGS_ROOT, exist_ok=True)
    print(f"  Recordings folder ready: {RECORDINGS_ROOT}")
    print()

    # Bind server
    try:
        socketserver.TCPServer.allow_reuse_address = True
        server = socketserver.TCPServer(("", PORT), QuadCamHandler)
    except OSError:
        print(f"  ERROR: Port {PORT} is already in use.")
        print(f"  If a server is already running, just open:  {url}")
        input("\n  Press Enter to exit...")
        sys.exit(1)

    def open_browser():
        time.sleep(1.3)
        print(f"  Opening browser → {url}\n")
        webbrowser.open(url)

    threading.Thread(target=open_browser, daemon=True).start()
    print(f"  Server running on port {PORT}  (waiting for recordings…)\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped. All recordings have been saved.")
        print(f"  Find your videos in:  {RECORDINGS_ROOT}")
        server.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    main()
