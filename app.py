import streamlit as st
import base64
import json
import yaml
from urllib.parse import urlparse

# ================= ⚙️ 配置区 =================
ACCESS_KEY = "brysj"  # URL 密钥
# ============================================

def vmess_to_dict(vmess_url):
    """解析 VMess 链接为字典对象"""
    try:
        if not vmess_url.startswith("vmess://"):
            return None
        # 解密 Base64
        config_json = base64.b64decode(vmess_url[8:]).decode('utf-8')
        data = json.loads(config_json)
        
        # 映射为 Clash 格式
        proxy = {
            "name": data.get("ps", "Node"),
            "type": "vmess",
            "server": data.get("add"),
            "port": int(data.get("port")),
            "uuid": data.get("id"),
            "alterId": int(data.get("aid", 0)),
            "cipher": "auto",
            "tls": True if data.get("tls") == "tls" else False,
            "network": data.get("net", "tcp"),
        }
        
        if data.get("net") == "ws":
            proxy["ws-opts"] = {
                "path": data.get("path", "/"),
                "headers": {"Host": data.get("host", "")}
            }
        if data.get("tls") == "tls":
            proxy["servername"] = data.get("sni") or data.get("host")
            
        return proxy
    except Exception as e:
        return None

# --- 🎭 伪装逻辑 ---
user_key = st.query_params.get("key", "")
if user_key != ACCESS_KEY:
    st.set_page_config(page_title="登鹳雀楼", page_icon="📜")
    st.markdown("""
        <div style="text-align: center; margin-top: 150px; font-family: 'STKaiti', 'KaiTi', serif;">
            <h1 style="color: #333; font-size: 40px;">登鹳雀楼</h1>
            <p style="color: #666; font-size: 18px; margin-top: 10px;">王之涣 · 唐</p>
            <div style="font-size: 24px; line-height: 2; margin-top: 30px; color: #444;">
                白日依山尽，<br>黄河入海流。<br>欲穷千里目，<br>更上一层楼。
            </div>
        </div>
        <style> header {visibility: hidden;} footer {visibility: hidden;} .stApp {background-color: #fdfaf1;} </style>
    """, unsafe_allow_html=True)
    st.stop()

# --- ✅ 转换界面 ---
st.set_page_config(page_title="订阅本地转换", page_icon="⚡")
st.title("⚡ Clash YAML 本地生成器")
st.caption("所有转换均在本地完成，不会上传至任何第三方服务器")

raw_input = st.text_area("粘贴 V2RayN 链接 (vmess://)", height=200, placeholder="vmess://...")

if st.button("🪄 立即转换并生成 YAML", type="primary"):
    if not raw_input.strip():
        st.error("请输入链接！")
    else:
        links = raw_input.strip().split('\n')
        proxies_list = []
        
        for link in links:
            if link.strip():
                p = vmess_to_dict(link.strip())
                if p:
                    proxies_list.append(p)
        
        if not proxies_list:
            st.error("未识别到有效的 VMess 链接。")
        else:
            # 构建完整的 Clash 结构
            clash_config = {
                "port": 7890,
                "socks-port: 7891": 7891,
                "allow-lan": True,
                "mode": "Rule",
                "log-level": "info",
                "proxies": proxies_list,
                "proxy-groups": [
                    {
                        "name": "🚀 节点选择",
                        "type": "select",
                        "proxies": ["🛰️ 自动延迟"] + [p["name"] for p in proxies_list]
                    },
                    {
                        "name": "🛰️ 自动延迟",
                        "type": "url-test",
                        "url": "http://www.gstatic.com/generate_204",
                        "interval": 300,
                        "proxies": [p["name"] for p in proxies_list]
                    }
                ],
                "rules": [
                    "DOMAIN-SUFFIX,google.com,🚀 节点选择",
                    "GEOIP,CN,DIRECT",
                    "MATCH,🚀 节点选择"
                ]
            }
            
            # 转换为 YAML 字符串
            yaml_output = yaml.dump(clash_config, allow_unicode=True, default_flow_style=False, sort_keys=False)
            
            st.success(f"成功转换 {len(proxies_list)} 个节点！")
            
            # 预览与复制框
            st.subheader("📄 YAML 内容预览")
            st.code(yaml_output, language="yaml")
            
            # 下载按钮
            st.download_button(
                label="📥 下载 config.yaml",
                data=yaml_output,
                file_name="clash_config.yaml",
                mime="text/yaml"
            )
