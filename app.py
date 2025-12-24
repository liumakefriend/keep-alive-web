import streamlit as st
import urllib.parse
import requests

# ================= ⚙️ 配置区 =================
ACCESS_KEY = "brysj"  # 解锁密钥
# 建议使用稳定后端，或换成你自己的私有后端
DEFAULT_BACKEND = "https://url.atcloud.io/sub?" 
# ============================================

# 获取 URL 参数
user_key = st.query_params.get("key", "")

# 🎭 伪装逻辑
if user_key != ACCESS_KEY:
    st.set_page_config(page_title="登鹳雀楼", page_icon="📜")
    st.markdown("""
        <div style="text-align: center; margin-top: 150px; font-family: 'STKaiti', 'KaiTi', serif;">
            <h1 style="color: #333; font-size: 40px;">登鹳雀楼</h1>
            <p style="color: #666; font-size: 18px; margin-top: 10px;">王之涣 · 唐</p>
            <div style="font-size: 24px; line-height: 2; margin-top: 30px; color: #444;">
                白日依山尽，<br>黄河入海流。<br>
                欲穷千里目，<br>更上一层楼。
            </div>
        </div>
        <style> header {visibility: hidden;} footer {visibility: hidden;} .stApp {background-color: #fdfaf1;} </style>
    """, unsafe_allow_html=True)
    st.stop()

# ✅ 授权通过
st.set_page_config(page_title="内部订阅转换", page_icon="🚀")
st.title("🚀 内部订阅转换工具")

raw_links = st.text_area("粘贴原始链接 (vmess:// 每行一个)", height=250)

if st.button("🪄 生成 Clash 订阅", type="primary"):
    if not raw_links.strip():
        st.error("请输入链接！")
    else:
        # 构建转换参数
        params = {
            "target": "clash",
            "url": raw_links.strip(),
            "insert": "false",
            "emoji": "true",
            "list": "false",
            "udp": "true",
            "config": "https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/config/ACL4SSR_Online.ini"
        }
        final_sub = DEFAULT_BACKEND + urllib.parse.urlencode(params)
        
        st.success("转换链接已生成！")
        st.code(final_sub, language="text")
        st.info("💡 请复制上方代码填入 Clash 的 URL 下载框。")
        
# import streamlit as st
# import requests
# import time
# from github import Github
# from datetime import datetime
# import pytz

# # ================= 配置区 =================
# # 密码 (如果不需要密码，把这里设为 None)
# PASSWORD = "123"  

# # 监控目标
# TARGET_URLS = [
#     "https://watermelonus.g1-us-east.galaxycloud.app/",
#     "https://watermelon.g1-eu-west.galaxycloud.app/"
# ]
# # GitHub 配置
# REPO_NAME = "liumakefriend/abc"
# FILE_PATH = "wakeup_log.txt"
# BRANCH = "main"
# GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")

# # ================= 核心逻辑 =================

# def get_status_emoji(code):
#     if code == 200: return "🟢"
#     if code == 0: return "🔴"  # 连接失败
#     return "XR" # 其他错误码

# def check_website(url):
#     """
#     修复版检测函数：添加了 User-Agent 头部
#     """
#     headers = {
#         # 伪装成 Win10 上的 Chrome 浏览器，这是解决 status=0 的关键
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
#     }
#     try:
#         # timeout 设置为 15 秒，避免稍微慢一点就被判死刑
#         response = requests.get(url, headers=headers, timeout=15)
#         return response.status_code, response.elapsed.total_seconds()
#     except Exception as e:
#         return 0, 0.0

# def trigger_wakeup_action():
#     """触发 GitHub Action"""
#     try:
#         g = Github(GITHUB_TOKEN)
#         repo = g.get_repo(REPO_NAME)
        
#         # 尝试获取文件
#         try: contents = repo.get_contents(FILE_PATH, ref=BRANCH)
#         except: contents = None
        
#         # 构造提交
#         tz = pytz.timezone('Asia/Shanghai')
#         now_str = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
#         msg = f"chore: wakeup trigger at {now_str}"
#         content = f"Wakeup Log: {now_str}\nStatus: Down detected."

#         if contents:
#             repo.update_file(contents.path, msg, content, contents.sha, branch=BRANCH)
#         else:
#             repo.create_file(FILE_PATH, msg, content, branch=BRANCH)
#         return True, f"✅ 已推送代码触发重启 ({now_str})"
#     except Exception as e:
#         return False, f"❌ 触发失败: {str(e)}"

# # ================= 界面逻辑 (仿 UptimeRobot) =================

# st.set_page_config(page_title="Service Monitor", page_icon="📈", layout="wide")

# # 登录逻辑
# if "auth" not in st.session_state: st.session_state.auth = False
# if PASSWORD and not st.session_state.auth:
#     c1, c2, c3 = st.columns([1,2,1])
#     with c2:
#         st.title("🔒 Login")
#         pwd = st.text_input("Password", type="password")
#         if st.button("Unlock"):
#             if pwd == PASSWORD: st.session_state.auth = True; st.rerun()
#             else: st.error("Wrong Password")
#     st.stop()

# # 主界面
# st.title("📈 Service Monitor Dashboard")

# # 侧边栏控制
# with st.sidebar:
#     st.header("控制台")
#     run_btn = st.button("🚀 立即开始监控", type="primary")
#     st.info("点击按钮后，系统将每 5 分钟自动刷新一次。")
#     logs_expander = st.expander("📜 详细运行日志", expanded=True)

# if "logs" not in st.session_state: st.session_state.logs = []
# if "history" not in st.session_state: st.session_state.history = {} # 记录历史状态

# # 样式 CSS
# st.markdown("""
# <style>
#     .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 5px; }
#     div[data-testid="stColumn"] { text-align: center; }
# </style>
# """, unsafe_allow_html=True)

# if run_btn:
#     st.toast("正在后台运行监控循环...")
    
#     status_placeholder = st.empty()
    
#     while True:
#         results = []
#         any_failure = False
#         check_time = datetime.now().strftime('%H:%M:%S')
        
#         # 1. 批量检测
#         for url in TARGET_URLS:
#             code, latency = check_website(url)
#             # 简化 URL 显示
#             short_name = url.split("//")[1].split(".")[0]
            
#             is_up = (code == 200)
#             if not is_up: any_failure = True
            
#             results.append({
#                 "name": short_name,
#                 "url": url,
#                 "code": code,
#                 "latency": f"{latency:.2f}s",
#                 "status": "UP" if is_up else "DOWN"
#             })

#         # 2. 绘制仪表盘 (每次循环重新绘制)
#         with status_placeholder.container():
#             st.markdown(f"### 🕒 Last Check: {check_time}")
            
#             # 使用列布局显示卡片
#             cols = st.columns(len(results))
#             for i, res in enumerate(results):
#                 with cols[i]:
#                     color = "normal" if res['status'] == "UP" else "inverse"
#                     st.metric(
#                         label=res['name'], 
#                         value=res['status'], 
#                         delta=f"Code: {res['code']} | {res['latency']}",
#                         delta_color=color
#                     )

#             # 3. 决策与行动
#             if any_failure:
#                 st.error("⚠️ 检测到服务异常，正在执行唤醒动作...")
#                 success, msg = trigger_wakeup_action()
#                 action_log = msg
#             else:
#                 st.success("✅ 所有服务正常，无需操作。")
#                 action_log = "无需操作"

#         # 4. 更新日志
#         log_entry = f"[{check_time}] " + " | ".join([f"{r['name']}:{r['code']}" for r in results]) + f" -> {action_log}"
#         st.session_state.logs.insert(0, log_entry)
        
#         # 显示在侧边栏
#         with logs_expander:
#             st.code("\n".join(st.session_state.logs[:20]), language="text")

#         time.sleep(300)
