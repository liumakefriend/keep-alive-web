import streamlit as _st
import requests as _rq
import time as _tm
from github import Github as _Gh
from datetime import datetime as _dt
import pytz as _pz
import base64 as _b64

_K = _b64.b64decode("YnJ5c2o=").decode()
# 原 监控地址列表 -> base64
_U_LIST = [
    _b64.b64decode("aHR0cHM6Ly93YXRlcm1lbG9udXMuZzEtdXMtZWFzdC5nYWxheHljbG91ZC5hcHAv").decode(),
    _b64.b64decode("aHR0cHM6Ly93YXRlcm1lbG9uLmcxLWV1LXdlc3QuZ2FsYXh5Y2xvdWQuYXBwLw==").decode()
]
# 原 REPO_NAME, FILE, BRANCH
_R = _b64.b64decode("bGl1bWFrZWZyaWVuZC9hYmM=").decode()
_F = "wakeup_log.txt"
_B = "main"

# --- 核心逻辑 ---
def _x1(_u):
    try:
        _r = _rq.get(_u, timeout=10);return _r.status_code
    except:return 0

def _x2():
    try:
        _t = _st.secrets.get("GITHUB_TOKEN", "")
        _g = _Gh(_t); _rp = _g.get_repo(_R)
        try: _c = _rp.get_contents(_F, ref=_B); _e = True
        except: _e = False; _c = None
        _tz = _pz.timezone('Asia/Shanghai'); _nw = _dt.now(_tz).strftime('%Y-%m-%d %H:%M:%S')
        _m = f"chore: wakeup {_nw}"; _nc = f"Log: {_nw}\nStatus: Down."
        if _e: _rp.update_file(_c.path, _m, _nc, _c.sha, branch=_B)
        else: _rp.create_file(_F, _m, _nc, branch=_B)
        return f"\u2705 Action Triggered ({_nw})"
    except Exception as e: return f"\u274C Err: {str(e)}"

def _p1():
    _st.set_page_config(page_title="404", page_icon="\U0001F6AB")
    _h1 = _b64.b64decode("PGgxIHN0eWxlPSd0ZXh0LWFsaWduOiBjZW50ZXI7IGNvbG9yOiBncmV5Oyc+NDA0IE5vdCBGb3VuZDwvaDE+").decode()
    _p = _b64.b64decode("PHAgc3R5bGU9J3RleHQtYWxpZ246IGNlbnRlcjsnPkludGVybmFsIFNlcnZlciBFcnJvci48L3A+").decode()
    _st.markdown(_h1, unsafe_allow_html=True); _st.markdown(_p, unsafe_allow_html=True); _st.divider()
    _st.caption("Apache/2.4.41 (Unix) OpenSSL/1.1.1g")

def _p2():
    _st.set_page_config(page_title="\u63A7\u5236\u53F0", page_icon="\U0001F6E1")
    _st.title("\U0001F6E1 Service Monitor")
    if "logs" not in _st.session_state: _st.session_state.logs = []
    if _st.button("\U0001F680 START MONITOR"):
        _st.toast("Service Started...")
        _ph1 = _st.empty(); _ph2 = _st.empty()
        while True:
            _ok = True; _cl = []
            for _u in _U_LIST:
                _c = _x1(_u); _n = _dt.now().strftime('%H:%M:%S')
                if _c == 200: _cl.append(f"[{_n}] \U0001F7E2 200 - {_u}")
                else: _cl.append(f"[{_n}] \U0001F534 {_c} - {_u}"); _ok = False
            if not _ok: _r = _x2(); _cl.append(f"   -> {_r}")
            _st.session_state.logs = _cl + _st.session_state.logs[:15]
            with _ph1.container():
                if _ok: _st.success(f"Last Check: {_dt.now().strftime('%H:%M:%S')} - OK")
                else: _st.error(f"Last Check: {_dt.now().strftime('%H:%M:%S')} - TRIGGERED")
            _ph2.text_area("Logs", value="\n".join(_st.session_state.logs), height=400)
            _tm.sleep(300)

# --- 入口 ---
_qp = _st.query_params
if _qp.get("key", "") == _K: _p2()
else: _p1()
    
# import streamlit as st
# import requests
# import time
# from github import Github
# from datetime import datetime
# import pytz

# # ================= 配置区 =================
# # 🔑 设置你的访问密钥 (出现在URL中)
# ACCESS_KEY = "brysj"  
# # 访问方式将变为: https://你的应用.streamlit.app/?key=my_secret_password

# # 监控配置
# TARGET_URLS = [
#     "https://watermelonus.g1-us-east.galaxycloud.app/",
#     "https://watermelon.g1-eu-west.galaxycloud.app/
# ]
# REPO_NAME = "liumakefriend/abc"
# FILE_PATH = "wakeup_log.txt"
# BRANCH = "main"
# # 建议放到 st.secrets，这里为了方便直接演示
# GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "你的_GITHUB_TOKEN_填在这里")
# # =========================================

# # --- 功能函数 (保持不变) ---
# def check_website(url):
#     try:
#         response = requests.get(url, timeout=10)
#         return response.status_code
#     except:
#         return 0

# def push_to_wakeup():
#     try:
#         g = Github(GITHUB_TOKEN)
#         repo = g.get_repo(REPO_NAME)
#         try:
#             contents = repo.get_contents(FILE_PATH, ref=BRANCH)
#             file_exists = True
#         except:
#             file_exists = False
#             contents = None
            
#         beijing_tz = pytz.timezone('Asia/Shanghai')
#         current_time = datetime.now(beijing_tz).strftime('%Y-%m-%d %H:%M:%S')
#         commit_message = f"chore: wakeup trigger at {current_time}"
#         new_content = f"Wakeup trigger log: {current_time}\nStatus: Service Down."

#         if file_exists:
#             repo.update_file(contents.path, commit_message, new_content, contents.sha, branch=BRANCH)
#         else:
#             repo.create_file(FILE_PATH, commit_message, new_content, branch=BRANCH)
#         return f"✅ 已触发 GitHub Action ({current_time})"
#     except Exception as e:
#         return f"❌ 提交失败: {str(e)}"

# # --- 🎭 伪装逻辑核心 ---

# def show_fake_page():
#     """显示伪装页面 - 这里伪装成一个简单的服务器维护公告"""
#     st.set_page_config(page_title="404 Not Found", page_icon="🚫")
#     st.markdown("<h1 style='text-align: center; color: grey;'>404 Not Found</h1>", unsafe_allow_html=True)
#     st.markdown("<p style='text-align: center;'>The requested resource is not available on this server.</p>", unsafe_allow_html=True)
#     st.divider()
#     # 甚至可以加一个假的无关紧要的功能，让人以为这就是全部
#     st.caption("Server ID: nginx/1.18.0 (Ubuntu)")

# def show_real_app():
#     """显示真正的监控应用"""
#     st.set_page_config(page_title="监控控制台", page_icon="🛡️")
#     st.title("🛡️ 内部服务保活系统")
    
#     # 获取参数
#     if "logs" not in st.session_state:
#         st.session_state.logs = []
    
#     start_btn = st.button("🚀 启动循环监控 (每5分钟)")
    
#     status_placeholder = st.empty()
#     log_placeholder = st.empty()

#     if start_btn:
#         st.toast("监控进程已在后台启动...")
#         while True:
#             all_ok = True
#             current_batch_log = []
            
#             for url in TARGET_URLS:
#                 code = check_website(url)
#                 now = datetime.now().strftime('%H:%M:%S')
#                 if code == 200:
#                     current_batch_log.append(f"[{now}] 🟢 200 OK - {url}")
#                 else:
#                     current_batch_log.append(f"[{now}] 🔴 {code} Error - {url}")
#                     all_ok = False
            
#             if not all_ok:
#                 res = push_to_wakeup()
#                 current_batch_log.append(f"   ↳ {res}")
            
#             # 更新日志状态
#             # 将新日志插到最前面
#             st.session_state.logs = current_batch_log + st.session_state.logs[:15]
            
#             with status_placeholder.container():
#                 if all_ok:
#                     st.success(f"最后检测: {datetime.now().strftime('%H:%M:%S')} - 服务正常")
#                 else:
#                     st.error(f"最后检测: {datetime.now().strftime('%H:%M:%S')} - 触发唤醒")

#             log_text = "\n".join(st.session_state.logs)
#             log_placeholder.text_area("实时日志", value=log_text, height=400)
            
#             time.sleep(300)
#             # 注意：Streamlit的机制里，while循环中rerun会导致状态重置，
#             # 在这种简单脚本中，直接sleep不rerun，依靠placeholder更新UI是更稳定的做法。

# # --- 🔐 入口判断 ---

# # 获取 URL 参数
# query_params = st.query_params
# # 检查是否存在 key 且值正确
# user_key = query_params.get("key", "")

# if user_key == ACCESS_KEY:
#     show_real_app()
# else:
#     show_fake_page()
