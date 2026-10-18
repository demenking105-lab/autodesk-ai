"""
AutoDesk AI - Modern Streamlit Web Dashboard
Interactive Automated Incident Triage, Log Diagnostics & System Health Visualizer
"""

import os
import streamlit as st
import pandas as pd
from core.system_scanner import SystemScanner
from core.log_parser import LogParser
from core.triage_engine import TriageEngine
from core.ai_resolver import AIResolver

# Page setup
st.set_page_config(
    page_title="AutoDesk AI - IT Support & Incident Resolver",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1e3a8a;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    .p1-badge {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        border: 1px solid #f87171;
        display: inline-block;
    }
    .p2-badge {
        background-color: #ffedd5;
        color: #9a3412;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        border: 1px solid #fb923c;
        display: inline-block;
    }
    .p3-badge {
        background-color: #fef9c3;
        color: #854d0e;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        border: 1px solid #facc15;
        display: inline-block;
    }
    .p4-badge {
        background-color: #dcfce7;
        color: #166534;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        border: 1px solid #4ade80;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title">🛠️ AutoDesk AI: Incident Triage & Resolution Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Intelligent Log Diagnostics, SRE Metric Monitoring, and Auto-Remediation | Created by <b>Syed Saqeeb Ali</b></div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.header("⚙️ Configuration")
api_key = st.sidebar.text_input("Google Gemini API Key (Optional)", type="password", help="Leave blank to use the built-in offline heuristic diagnostic engine.")
if api_key:
    os.environ["GEMINI_API_KEY"] = api_key
    st.sidebar.success("Cloud AI Engine: Gemini 2.5 Active")
else:
    st.sidebar.info("Engine: Built-in Offline Heuristic Knowledge Base")

st.sidebar.markdown("---")
st.sidebar.subheader("📌 Project Links")
st.sidebar.markdown("- [GitHub Repo](https://github.com/demenking105-lab)")
st.sidebar.markdown("- [Presidency University AIML](https://presidencyuniversity.in)")

# Tabs
tab1, tab2, tab3 = st.tabs(["🔍 Incident Log Diagnostic", "🩺 Live System Health & Vitals", "📖 About Architecture"])

# TAB 1: INCIDENT DIAGNOSTIC
with tab1:
    col_input, col_preset = st.columns([2, 1])
    
    with col_preset:
        st.subheader("📁 Load Sample Incident")
        sample_choice = st.selectbox(
            "Select sample log file:",
            [
                "None (Write Custom / Upload)",
                "memory_leak.log (OOM Critical)",
                "database_timeout.log (PostgreSQL Timeout)",
                "python_crash.log (Unhandled Exception)",
                "network_dns_fail.log (DNS / Socket Error)"
            ]
        )
        uploaded_file = st.file_uploader("Or upload your log (.txt, .log):", type=["txt", "log"])

    log_content = ""
    sample_dir = os.path.join(os.path.dirname(__file__), "sample_logs")
    
    if uploaded_file is not None:
        log_content = uploaded_file.read().decode("utf-8", errors="ignore")
    elif "memory_leak.log" in sample_choice:
        with open(os.path.join(sample_dir, "memory_leak.log"), "r") as f:
            log_content = f.read()
    elif "database_timeout.log" in sample_choice:
        with open(os.path.join(sample_dir, "database_timeout.log"), "r") as f:
            log_content = f.read()
    elif "python_crash.log" in sample_choice:
        with open(os.path.join(sample_dir, "python_crash.log"), "r") as f:
            log_content = f.read()
    elif "network_dns_fail.log" in sample_choice:
        log_content = "[2026-10-18 12:40:02] [ERROR] DNS lookup failed for 'api.cloud-gateway.internal'\nTimeoutError: [Errno 110] Connection timed out: 8.8.8.8:53 unreachable"

    with col_input:
        st.subheader("📝 Incident Log / Stack Trace")
        user_log = st.text_area("Paste error log or stack trace below:", value=log_content, height=220)
        diagnose_btn = st.button("🚀 Analyze & Auto-Triage Incident", type="primary")

    if diagnose_btn and user_log.strip():
        with st.spinner("Parsing error signatures and running diagnostic heuristics..."):
            parsed = LogParser.parse_log_text(user_log)
            scanner = SystemScanner()
            vitals = scanner.get_hardware_vitals()
            triage = TriageEngine.evaluate_priority(parsed, vitals)
            resolver = AIResolver(api_key=api_key)
            diagnosis = resolver.diagnose_issue(user_log, parsed, triage, vitals)

        st.markdown("---")
        st.subheader("🎯 Triage & Diagnostic Findings")
        
        # Severity row
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            badge_class = f"{triage['priority'].lower()}-badge"
            st.markdown(f'<div class="{badge_class}">Tier {triage["priority"]} - {triage["severity_name"]}</div>', unsafe_allow_html=True)
            st.caption(triage["description"])
        with c2:
            st.metric("Assigned Engineering Team", triage["assigned_team"])
        with c3:
            st.metric("Resolution SLA Target", triage["sla_display"])
        with c4:
            st.metric("Diagnostic Engine", diagnosis["ai_source"].split()[0] + " " + diagnosis["ai_source"].split()[1])

        # Diagnostic Details
        col_root, col_remedy = st.columns(2)
        with col_root:
            st.markdown("#### 🧠 Root Cause Analysis")
            st.info(diagnosis["root_cause"])
            
            st.markdown("#### 🛡️ Prevention Recommendations")
            for prev in diagnosis["prevention"]:
                st.markdown(f"- {prev}")

        with col_remedy:
            st.markdown("#### 📋 Immediate Remediation Checklist")
            for i, step in enumerate(diagnosis["remediation_steps"], 1):
                st.markdown(f"**{i}.** {step}")

            st.markdown("#### ⚡ Executable Fix Script")
            st.code(diagnosis["fix_commands"], language="bash")

# TAB 2: SYSTEM VITALS
with tab2:
    st.subheader("🩺 Live Hardware Health & Telemetry")
    scanner = SystemScanner()
    data = scanner.scan_full_system()
    vitals = data["vitals"]

    v1, v2, v3, v4 = st.columns(4)
    v1.metric("CPU Utilization", f"{vitals['cpu']['percent']}%", f"{vitals['cpu']['cores']} Cores")
    v2.metric("RAM Used", f"{vitals['memory']['used_gb']} GB", f"{vitals['memory']['percent']}% Used")
    v3.metric("Disk Free", f"{vitals['disk']['free_gb']} GB", f"{vitals['disk']['percent']}% Used")
    
    net = data["network"]
    net_val = f"{net['latency_ms']} ms" if net['online'] else "Offline"
    v4.metric("Network Ping", net_val, net["status"])

    if vitals["warnings"]:
        for w in vitals["warnings"]:
            st.warning(w)

    st.markdown("---")
    st.subheader("📊 Top Active Processes (Memory & CPU Allocation)")
    if data["top_processes"]:
        df = pd.DataFrame(data["top_processes"])
        df.columns = ["PID", "Process Name", "CPU %", "Memory %"]
        st.dataframe(df, use_container_width=True)

# TAB 3: ABOUT
with tab3:
    st.subheader("💡 Architecture & Design Overview")
    st.markdown("""
    **AutoDesk AI** combines rule-based pattern matching with Large Language Model diagnostics to automate Tier-1 and Tier-2 IT support triage.
    
    ### Key Highlights:
    - **Dual-Engine Architecture:** Operates seamlessly offline via deterministic heuristics and online via **Google Gemini 2.5 Flash**.
    - **Real-Time Telemetry:** Integrates directly with OS-level primitives using `psutil` to cross-examine host vitals with application error dumps.
    - **Incident ITIL Prioritization:** Automated P1 (Critical Outage) to P4 (Low Impact) scoring with SLA target tracking.
    - **Interactive Interfaces:** Ships with both a **Rich Terminal CLI** and a responsive **Streamlit Web Dashboard**.
    """)
