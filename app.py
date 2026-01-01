#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import uuid
import base64
import tarfile
import subprocess
import threading
import time
import platform
import urllib.request
import shutil
from flask import Flask, Response, request

# ==================== 🛠️ 用户配置区域 ====================
# 如果环境变量中有 UUID 则使用，否则生成一个新的（建议固定 UUID）
USER_UUID = os.environ.get('UUID', '567e4508-3486-4528-a53f-361413867664')

# 伪装路径 (WebSocket Path)
WS_PATH = os.environ.get('WS_PATH', '/ws')

# 端口配置
# PORT 是云平台分配的外部端口 (Sing-box 监听这个)
# LOCAL_PORT 是 Python Flask 监听的内部端口 (Sing-box 转发给这个)
PUBLIC_PORT = int(os.environ.get('PORT', 8080))
INTERNAL_PORT = 5000 

# Sing-box 版本
SING_BOX_VERSION = "1.8.0"
# ========================================================

app = Flask(__name__)

# ==================== 📦 Sing-box 管理逻辑 ====================

def get_platform_arch():
    """检测系统架构以下载对应的 Binary"""
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system != 'linux':
        print(f"⚠️ 警告: 此脚本主要为 Linux 服务器设计，检测到系统为 {system}，可能无法自动运行核心。")
    
    # 简单的架构映射
    if 'aarch64' in machine or 'arm64' in machine:
        return 'linux-arm64'
    elif 'x86_64' in machine or 'amd64' in machine:
        return 'linux-amd64'
    else:
        return 'linux-amd64' # 默认尝试 amd64

def install_sing_box():
    """检查并下载 Sing-box"""
    bin_path = "./sing-box"
    if os.path.exists(bin_path):
        print("✅ Sing-box 核心已存在")
        return True

    arch = get_platform_arch()
    url = f"https://github.com/SagerNet/sing-box/releases/download/v{SING_BOX_VERSION}/sing-box-{SING_BOX_VERSION}-{arch}.tar.gz"
    
    print(f"⬇️ 正在下载 Sing-box ({arch})...")
    try:
        file_name = "sing-box.tar.gz"
        urllib.request.urlretrieve(url, file_name)
        
        print("📦 正在解压...")
        with tarfile.open(file_name, "r:gz") as tar:
            # 查找二进制文件并解压
            for member in tar.getmembers():
                if member.name.endswith('/sing-box'):
                    member.name = 'sing-box' # 重命名到当前目录
                    tar.extract(member, ".")
                    break
        
        # 赋予执行权限
        os.chmod(bin_path, 0o755)
        # 清理压缩包
        os.remove(file_name)
        print("✅ Sing-box 安装完成")
        return True
    except Exception as e:
        print(f"❌ 下载或安装失败: {e}")
        return False

def generate_config():
    """生成 config.json"""
    config = {
        "log": {"level": "info", "timestamp": True},
        "inbounds": [
            {
                "type": "vless",
                "tag": "vless-in",
                "listen": "::", 
                "listen_port": PUBLIC_PORT,  # 监听云平台分配的端口
                "users": [{"uuid": USER_UUID, "flow": ""}],
                "transport": {
                    "type": "ws",
                    "path": WS_PATH,
                    "early_data_header_name": "Sec-WebSocket-Protocol"
                },
                # !!! 核心魔法：回落机制 !!!
                # 任何非 VLESS 流量都被转发到本地 5000 端口 (Flask)
                "fallback": {
                    "server": "127.0.0.1",
                    "server_port": INTERNAL_PORT
                }
            }
        ],
        "outbounds": [{"type": "direct", "tag": "direct"}]
    }
    
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
    print("✅ 配置文件 config.json 已生成")

def run_sing_box():
    """在后台运行 Sing-box"""
    if not os.path.exists("./sing-box"):
        print("❌ 找不到 sing-box 文件，跳过启动")
        return

    generate_config()
    
    print(f"🚀 启动 Sing-box 核心 (监听端口: {PUBLIC_PORT} -> 回落: {INTERNAL_PORT})...")
    # 使用 subprocess 在后台运行
    subprocess.Popen(["./sing-box", "run", "-c", "config.json"])

# ==================== 🌐 Flask 伪装网站 ====================

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>云计算学习笔记</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { border-bottom: 2px solid #eaecef; padding-bottom: 0.3em; }
            code { background-color: #f6f8fa; padding: 0.2em 0.4em; border-radius: 3px; font-family: monospace; }
            .note { border-left: 4px solid #0366d6; padding-left: 15px; color: #586069; margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>分布式系统原理</h1>
        <p>分布式系统（Distributed System）是建立在网络之上的软件系统。</p>
        <div class="note">
            <p>关键特性：</p>
            <ul>
                <li>内聚性：每个节点高度自治</li>
                <li>透明性：用户感知不到系统的分布特性</li>
            </ul>
        </div>
        <p>最近在研究 <code>Raft</code> 一致性算法和 <code>Paxos</code> 协议的区别...</p>
        <hr>
        <p style="font-size:0.8em; color:#999">Powered by Flask & Docker</p>
    </body>
    </html>
    """

@app.route('/sub')
def subscription():
    """生成订阅链接"""
    host = request.host.split(':')[0]
    
    # 尝试获取如果是部署在 Render/Heroku 等平台的 HTTPS 域名
    # 如果通过 sing-box 转发，request.host 可能是 127.0.0.1，需要手动指定或自动探测
    # 这里做一个简单的容错：如果 HOST 是 localhost，尝试用 render 环境变量
    if "127.0.0.1" in host or "localhost" in host:
        host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', host)

    vless_link = (
        f"vless://{USER_UUID}@{host}:{PUBLIC_PORT}"
        f"?encryption=none&security=none&type=ws&host={host}&path={WS_PATH}"
        f"#Learn-VLESS-{host}"
    )
    
    return Response(
        base64.b64encode(vless_link.encode()).decode(),
        mimetype='text/plain'
    )

# ==================== 🏁 主程序入口 ====================

if __name__ == '__main__':
    print(">>> 初始化全能代理服务...")
    
    # 1. 尝试安装 Sing-box (如果是 Linux 环境)
    # 为了防止构建 Docker 时卡死，这里做一个简单的检查
    # 实际部署时，脚本运行时会自动下载
    install_sing_box()
    
    # 2. 启动 Sing-box (它会占用 PUBLIC_PORT)
    # 我们使用 daemon 线程或者直接 subprocess
    # 注意：在某些云环境（如 Cloud Run），必须有一个前台进程监听 PORT。
    # 这里我们的策略是：Sing-box 监听 PORT，Flask 监听 5000。
    # 只要 Python 脚本不退出，subprocess 就一直运行。
    run_sing_box()
    
    # 3. 启动 Flask (监听 INTERNAL_PORT，等待 Sing-box 的回落流量)
    print(f">>> 启动 Flask 伪装服务 (监听内部端口: {INTERNAL_PORT})...")
    # 注意：use_reloader=False 防止 Flask 重启导致 sing-box 启动两次
    app.run(host='127.0.0.1', port=INTERNAL_PORT, use_reloader=False)
