#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VLESS WebSocket 代理服务器 - 教育学习版本
仅供技术学习和研究使用

功能：
1. 首页显示古诗（伪装）
2. 生成V2Ray订阅链接
3. 基本的VLESS WebSocket代理实现

注意：这是简化的教育版本，生产环境请使用Xray-core等专业工具
"""

from flask import Flask, request, Response, make_response
import base64
import json
import uuid
import struct
import socket
import threading
import hashlib
import os

app = Flask(__name__)

# ==================== 配置部分 ====================

def get_server_address():
    """自动获取服务器地址"""
    try:
        # 尝试获取外网IP
        import urllib.request
        external_ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
        return external_ip
    except:
        try:
            # 如果获取外网IP失败，尝试获取局域网IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            # 如果都失败，返回localhost
            return "127.0.0.1"

# 自动生成配置
SERVER_CONFIG = {
    "address": None,  # 将在运行时自动填充
    "port": 5000,  # Flask默认端口
    "uuid": str(uuid.uuid4()),  # 自动生成UUID
    "path": "/ws",  # WebSocket路径
    "tls": "none"  # 本地测试用none，生产环境用tls
}

# 存储活动的WebSocket连接
active_connections = {}

# ==================== 首页路由 ====================
@app.route('/')
def index():
    """首页 - 显示古诗作为伪装"""
    html = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>诗词鉴赏</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'KaiTi', 'STKaiti', serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                background: rgba(255, 255, 255, 0.98);
                padding: 60px 80px;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                text-align: center;
                max-width: 700px;
                backdrop-filter: blur(10px);
            }
            h1 {
                color: #2c3e50;
                font-size: 2.8em;
                margin-bottom: 40px;
                font-weight: normal;
                letter-spacing: 8px;
            }
            .poem {
                font-size: 1.6em;
                line-height: 2.2;
                color: #34495e;
                margin: 40px 0;
                letter-spacing: 2px;
            }
            .poem-line {
                margin: 15px 0;
                opacity: 0;
                animation: fadeIn 0.8s ease-in forwards;
            }
            .poem-line:nth-child(1) { animation-delay: 0.2s; }
            .poem-line:nth-child(2) { animation-delay: 0.4s; }
            .poem-line:nth-child(3) { animation-delay: 0.6s; }
            .poem-line:nth-child(4) { animation-delay: 0.8s; }
            .author {
                color: #7f8c8d;
                font-size: 0.9em;
                margin-top: 30px;
                font-style: italic;
            }
            .decoration {
                color: #e74c3c;
                font-size: 3em;
                margin: 20px 0;
                opacity: 0.6;
            }
            @keyframes fadeIn {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            .footer {
                margin-top: 50px;
                padding-top: 30px;
                border-top: 1px solid #ecf0f1;
                color: #95a5a6;
                font-size: 0.85em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>诗词鉴赏</h1>
            <div class="decoration">❀</div>
            <div class="poem">
                <div class="poem-line">床前明月光，</div>
                <div class="poem-line">疑是地上霜。</div>
                <div class="poem-line">举头望明月，</div>
                <div class="poem-line">低头思故乡。</div>
            </div>
            <div class="author">—— 唐·李白《静夜思》</div>
            <div class="decoration">❀</div>
            <div class="footer">
                中华诗词文化传承 · 品味千年经典
            </div>
        </div>
    </body>
    </html>
    """
    return html

# ==================== 订阅路由 ====================
@app.route('/subscription')
@app.route('/sub')
def subscription():
    """生成V2Ray订阅链接"""
    # 构建VLESS链接
    vless_link = (
        f"vless://{SERVER_CONFIG['uuid']}@{SERVER_CONFIG['address']}:{SERVER_CONFIG['port']}"
        f"?encryption=none"
        f"&security={SERVER_CONFIG['tls']}"
        f"&type=ws"
        f"&host={SERVER_CONFIG['address']}"
        f"&path={SERVER_CONFIG['path']}"
        f"#学习节点-VLESS"
    )
    
    # Base64编码
    subscription_content = base64.b64encode(vless_link.encode()).decode()
    
    return Response(
        subscription_content,
        mimetype='text/plain',
        headers={
            'Content-Disposition': 'attachment; filename=subscription.txt',
            'Subscription-Userinfo': 'upload=0; download=0; total=10737418240; expire=0',
            'Profile-Update-Interval': '24'
        }
    )

# ==================== WebSocket处理 ====================
@app.route('/ws', methods=['GET'])
def websocket_handler():
    """
    VLESS WebSocket处理端点
    这是一个简化的实现，用于教育目的
    """
    # 检查是否是WebSocket升级请求
    if request.headers.get('Upgrade', '').lower() != 'websocket':
        return "Bad Request - WebSocket upgrade required", 400
    
    # 获取WebSocket密钥
    ws_key = request.headers.get('Sec-WebSocket-Key')
    if not ws_key:
        return "Bad Request - Missing Sec-WebSocket-Key", 400
    
    # 计算接受密钥
    magic_string = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    accept_key = base64.b64encode(
        hashlib.sha1((ws_key + magic_string).encode()).digest()
    ).decode()
    
    # 构建WebSocket握手响应
    response_headers = [
        ('Upgrade', 'websocket'),
        ('Connection', 'Upgrade'),
        ('Sec-WebSocket-Accept', accept_key),
    ]
    
    # 注意：这里返回101状态码表示协议切换
    # 但Flask不太适合处理WebSocket，这只是演示
    # 实际生产环境应该使用专门的WebSocket库或Xray-core
    
    return Response(
        "WebSocket connection established (simplified demo)",
        status=101,
        headers=response_headers
    )

# ==================== 配置信息路由 ====================
@app.route('/config')
@app.route('/info')
def show_config():
    """显示配置信息"""
    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>配置信息</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                background: #0d1117;
                color: #c9d1d9;
                padding: 40px;
                line-height: 1.6;
            }}
            .container {{
                max-width: 900px;
                margin: 0 auto;
                background: #161b22;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
                border: 1px solid #30363d;
            }}
            h1 {{
                color: #58a6ff;
                border-bottom: 2px solid #58a6ff;
                padding-bottom: 15px;
                margin-bottom: 30px;
                font-size: 2em;
            }}
            h2 {{
                color: #79c0ff;
                margin-top: 30px;
                margin-bottom: 15px;
                font-size: 1.4em;
            }}
            pre {{
                background: #0d1117;
                padding: 20px;
                border-radius: 8px;
                overflow-x: auto;
                border-left: 4px solid #1f6feb;
                color: #79c0ff;
                font-size: 0.95em;
            }}
            .warning {{
                background: linear-gradient(135deg, #f85149 0%, #da3633 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                margin: 25px 0;
                border-left: 5px solid #ff6b6b;
                font-weight: bold;
            }}
            .info {{
                background: linear-gradient(135deg, #388bfd 0%, #1f6feb 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                margin: 25px 0;
                border-left: 5px solid #58a6ff;
            }}
            ul {{
                list-style: none;
                padding-left: 0;
            }}
            li {{
                padding: 10px 0;
                border-bottom: 1px solid #21262d;
            }}
            li:last-child {{
                border-bottom: none;
            }}
            a {{
                color: #58a6ff;
                text-decoration: none;
                transition: color 0.3s;
            }}
            a:hover {{
                color: #79c0ff;
                text-decoration: underline;
            }}
            .code {{
                background: #0d1117;
                padding: 3px 8px;
                border-radius: 4px;
                color: #ff7b72;
                font-family: monospace;
            }}
            .badge {{
                display: inline-block;
                padding: 4px 10px;
                border-radius: 12px;
                font-size: 0.85em;
                font-weight: bold;
                margin-left: 10px;
            }}
            .badge-warning {{
                background: #da3633;
                color: white;
            }}
            .badge-info {{
                background: #1f6feb;
                color: white;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>� 服务器配置信息 <span class="badge badge-warning">教育版</span></h1>
            
            <div class="warning">
                ⚠️ 警告：这是教育学习项目，仅用于理解VLESS协议原理！<br>
                生产环境请使用专业工具如 Xray-core 或 V2Ray-core
            </div>
            
            <h2>📋 当前配置</h2>
            <pre>{json.dumps(SERVER_CONFIG, indent=2, ensure_ascii=False)}</pre>
            
            <div class="info">
                💡 提示：服务器地址和UUID在启动时自动生成<br>
                如需自定义，请修改 app.py 中的 SERVER_CONFIG
            </div>
            
            <h2>🔗 可用端点</h2>
            <ul>
                <li>🏠 首页（伪装）: <a href="/">http://127.0.0.1:5000/</a></li>
                <li>📡 订阅地址: <a href="/subscription">http://127.0.0.1:5000/subscription</a></li>
                <li>⚙️ 配置信息: <a href="/config">http://127.0.0.1:5000/config</a></li>
                <li>🔌 WebSocket端点: <span class="code">/ws</span> (需要WebSocket客户端)</li>
            </ul>
            
            <h2>📖 使用步骤</h2>
            <ul>
                <li><strong>步骤 1:</strong> 修改 <span class="code">SERVER_CONFIG</span> 中的配置</li>
                <li><strong>步骤 2:</strong> 运行 <span class="code">python app.py</span></li>
                <li><strong>步骤 3:</strong> 在V2RayN中添加订阅地址</li>
                <li><strong>步骤 4:</strong> 更新订阅并测试连接</li>
            </ul>
            
            <h2>⚡ 重要说明</h2>
            <ul>
                <li>这个应用包含了<strong>订阅生成</strong>和<strong>简化的WebSocket处理</strong></li>
                <li>WebSocket实现是<strong>简化版</strong>，仅用于理解协议流程</li>
                <li>完整的VLESS协议实现非常复杂，建议使用 <strong>Xray-core</strong></li>
                <li>本地测试可以使用 <span class="code">tls: "none"</span></li>
                <li>生产环境<strong>必须</strong>使用TLS加密</li>
            </ul>
            
            <h2>🚀 下一步</h2>
            <ul>
                <li>学习VLESS协议规范</li>
                <li>了解WebSocket协议</li>
                <li>研究Xray-core源码</li>
                <li>配置TLS证书（Let's Encrypt）</li>
                <li>部署到实际VPS环境</li>
            </ul>
        </div>
    </body>
    </html>
    """
    return html

# ==================== 健康检查 ====================
@app.route('/health')
@app.route('/ping')
def health_check():
    """健康检查端点"""
    return {
        "status": "ok",
        "service": "VLESS Learning Server",
        "version": "1.0.0-edu"
    }

# ==================== 主程序入口 ====================
if __name__ == '__main__':
    # 从环境变量获取端口（云平台通常会设置PORT环境变量）
    port = int(os.environ.get('PORT', 5000))
    SERVER_CONFIG['port'] = port
    
    # 自动检测服务器地址
    if SERVER_CONFIG["address"] is None:
        detected_address = get_server_address()
        SERVER_CONFIG["address"] = detected_address
        print("\n🔍 自动检测服务器地址...")
        print(f"✅ 检测到地址: {detected_address}")
    
    # 检测是否在Databricks环境
    is_databricks = os.environ.get('DATABRICKS_RUNTIME_VERSION') is not None
    
    if is_databricks:
        print("\n" + "=" * 70)
        print("  🎓 检测到 Databricks 环境")
        print("=" * 70)
        print("\n  ⚠️  Databricks 平台说明:")
        print("  • Databricks 主要用于数据处理，不是标准的Web托管平台")
        print("  • Web应用需要通过 Databricks 的代理访问")
        print("  • 建议使用标准VPS（如AWS EC2、阿里云等）部署Web服务")
        print("\n  📍 如果要在 Databricks 中测试，请使用:")
        print("  • Databricks Notebook 的代理URL")
        print("  • 或使用 ngrok 等隧道工具暴露服务")
        print("=" * 70 + "\n")
    
    print("\n" + "=" * 70)
    print("  🎓 VLESS WebSocket 代理服务器 - 教育学习版")
    print("=" * 70)
    print(f"\n  📍 首页（伪装）:    http://{SERVER_CONFIG['address']}:{SERVER_CONFIG['port']}/")
    print(f"  📍 配置信息:        http://{SERVER_CONFIG['address']}:{SERVER_CONFIG['port']}/config")
    print(f"  📍 订阅地址:        http://{SERVER_CONFIG['address']}:{SERVER_CONFIG['port']}/subscription")
    print(f"  📍 健康检查:        http://{SERVER_CONFIG['address']}:{SERVER_CONFIG['port']}/health")
    print(f"\n  🔑 UUID: {SERVER_CONFIG['uuid']}")
    print(f"  🌐 地址: {SERVER_CONFIG['address']}")
    print(f"  🔌 端口: {SERVER_CONFIG['port']}")
    print(f"  📡 路径: {SERVER_CONFIG['path']}")
    print("\n" + "=" * 70)
    print("  ⚠️  注意事项:")
    print("  • 这是教育学习项目，仅用于理解技术原理")
    print("  • 服务器地址和UUID已自动生成")
    print("  • 生产环境请使用 Xray-core 等专业工具")
    print("  • 请遵守当地法律法规")
    print("=" * 70 + "\n")
    
    # 检测是否在云平台环境
    is_cloud = os.environ.get('PORT') is not None or is_databricks
    
    try:
        # 启动Flask应用
        # 在Databricks环境中，需要特殊配置
        print(f"🚀 正在启动服务器，监听 0.0.0.0:{port}...")
        
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,  # 关闭调试模式
            threaded=True,
            use_reloader=False,  # 关闭自动重载
            # Databricks 可能需要这些额外配置
            processes=1
        )
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("\n💡 建议:")
        print("  1. 检查端口是否被占用")
        print("  2. 确认防火墙设置")
        print("  3. 如果在 Databricks，考虑使用标准VPS平台")
        print("  4. 推荐平台: AWS EC2, Google Cloud, 阿里云, 腾讯云等")
