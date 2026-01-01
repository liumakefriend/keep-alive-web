#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import uuid
import base64
import tarfile
import subprocess
import threading
import time
import urllib.request
import platform
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

# ==================== 🛠️ 配置区域 ====================
USER_UUID = os.environ.get('UUID', '567e4508-3486-4528-a53f-361413867664')
WS_PATH = os.environ.get('WS_PATH', '/ws')
# 外部端口：云平台分配的端口（给 sing-box 用）
PUBLIC_PORT = int(os.environ.get('PORT', 8080))
# 内部端口：Python 伪装站监听的端口（Sing-box 回落到这里）
INTERNAL_PORT = 5000 
SING_BOX_VERSION = "1.8.0"
# ====================================================

# 定义一个多线程的 HTTP Server，防止卡顿
class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass

# ==================== 📦 Sing-box 核心逻辑 ====================
def get_platform_arch():
    return 'linux-amd64'

def install_sing_box():
    bin_path = "./sing-box"
    if os.path.exists(bin_path):
        return True
    
    arch = get_platform_arch()
    url = f"https://github.com/SagerNet/sing-box/releases/download/v{SING_BOX_VERSION}/sing-box-{SING_BOX_VERSION}-{arch}.tar.gz"
    print(f"⬇️ Downloading sing-box...")
    
    try:
        file_name = "sing-box.tar.gz"
        urllib.request.urlretrieve(url, file_name)
        with tarfile.open(file_name, "r:gz") as tar:
            for member in tar.getmembers():
                if member.name.endswith('/sing-box'):
                    member.name = 'sing-box'
                    tar.extract(member, ".")
                    break
        os.chmod(bin_path, 0o755)
        os.remove(file_name)
        print("✅ Sing-box installed.")
        return True
    except Exception as e:
        print(f"❌ Install failed: {e}")
        return False

def run_sing_box():
    install_sing_box()
    
    # 生成配置
    config = {
        "log": {"level": "info", "timestamp": True},
        "inbounds": [{
            "type": "vless",
            "tag": "vless-in",
            "listen": "::",
            "listen_port": PUBLIC_PORT, # 监听云平台的主端口
            "users": [{"uuid": USER_UUID, "flow": ""}],
            "transport": {
                "type": "ws",
                "path": WS_PATH,
                "early_data_header_name": "Sec-WebSocket-Protocol"
            },
            # 关键：非 VLESS 流量回落到本地 5000 端口
            "fallback": {
                "server": "127.0.0.1",
                "server_port": INTERNAL_PORT
            }
        }],
        "outbounds": [{"type": "direct", "tag": "direct"}]
    }
    
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
        
    print(f"🚀 Starting Sing-box on port {PUBLIC_PORT}...")
    subprocess.Popen(["./sing-box", "run", "-c", "config.json"])

# ==================== 🌐 原生 HTTP 处理逻辑 ====================

class CamouflageHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. 首页逻辑
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = f"""
            <html>
            <head><title>System Status</title></head>
            <body style="font-family: sans-serif; padding: 2rem; text-align: center;">
                <h1>✅ System Operational</h1>
                <p>Gateway ID: {USER_UUID}</p>
                <hr>
                <p style="color: gray">No dependency pure Python server.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
            
        # 2. 订阅链接逻辑
        elif self.path == '/sub':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            
            # 获取 Host 头部，如果拿不到就默认 localhost
            host = self.headers.get('Host', 'localhost')
            
            link = (
                f"vless://{USER_UUID}@{host}:{PUBLIC_PORT}"
                f"?encryption=none&security=none&type=ws&host={host}&path={WS_PATH}"
                f"#Zero-Dep-Node"
            )
            self.wfile.write(base64.b64encode(link.encode('utf-8')))
            
        # 3. 404 逻辑
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    # 禁止打印每条请求的日志，保持清爽
    def log_message(self, format, *args):
        return

# ==================== 🚀 启动 ====================
if __name__ == '__main__':
    # 1. 后台启动 Sing-box
    threading.Thread(target=run_sing_box, daemon=True).start()
    
    # 2. 启动 HTTP 服务器 (监听内部端口 5000)
    print(f"🟢 Python Server listening on 127.0.0.1:{INTERNAL_PORT}")
    server = ThreadingHTTPServer(('127.0.0.1', INTERNAL_PORT), CamouflageHandler)
    server.serve_forever()
