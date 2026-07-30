import streamlit as st

LIGHT = {
    "bg": "#f0f2f6",
    "bg_secondary": "#e8ecf1",
    "bg_card": "#ffffff",
    "bg_gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    "text": "#1a1a2e",
    "text_secondary": "#6b7280",
    "text_muted": "#9ca3af",
    "primary": "#6366f1",
    "primary_hover": "#4f46e5",
    "primary_light": "#eef2ff",
    "accent": "#06b6d4",
    "accent_light": "#ecfeff",
    "success": "#10b981",
    "success_light": "#d1fae5",
    "warning": "#f59e0b",
    "warning_light": "#fef3c7",
    "danger": "#ef4444",
    "danger_light": "#fee2e2",
    "border": "#e2e8f0",
    "user_bubble_bg": "linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)",
    "user_text": "#ffffff",
    "assistant_bubble": "#ffffff",
    "assistant_text": "#1a1a2e",
    "shadow_sm": "0 1px 3px rgba(0,0,0,0.06)",
    "shadow_md": "0 4px 12px rgba(0,0,0,0.08)",
    "shadow_lg": "0 8px 24px rgba(0,0,0,0.12)",
    "skeleton": "#e2e8f0",
    "code_bg": "#1e293b",
    "code_text": "#e2e8f0",
    "hover_overlay": "rgba(99,102,241,0.04)",
    "scrollbar": "#cbd5e1",
    "scrollbar_hover": "#94a3b8",
    "sidebar_bg": "#ffffff",
    "mark_bg": "#fef08a",
    "mark_text": "#1a1a2e",
}

DARK = {
    "bg": "#0b1120",
    "bg_secondary": "#131c31",
    "bg_card": "#1a2338",
    "bg_gradient": "linear-gradient(135deg, #1e1b4b 0%, #312e81 100%)",
    "text": "#f1f5f9",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    "primary": "#818cf8",
    "primary_hover": "#6366f1",
    "primary_light": "#1e1b4b",
    "accent": "#22d3ee",
    "accent_light": "#083344",
    "success": "#34d399",
    "success_light": "#064e3b",
    "warning": "#fbbf24",
    "warning_light": "#451a03",
    "danger": "#f87171",
    "danger_light": "#450a0a",
    "border": "#1e293b",
    "user_bubble_bg": "linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)",
    "user_text": "#ffffff",
    "assistant_bubble": "#1a2338",
    "assistant_text": "#f1f5f9",
    "shadow_sm": "0 1px 3px rgba(0,0,0,0.3)",
    "shadow_md": "0 4px 12px rgba(0,0,0,0.4)",
    "shadow_lg": "0 8px 24px rgba(0,0,0,0.5)",
    "skeleton": "#1e293b",
    "code_bg": "#0f172a",
    "code_text": "#e2e8f0",
    "hover_overlay": "rgba(129,140,248,0.04)",
    "scrollbar": "#334155",
    "scrollbar_hover": "#475569",
    "sidebar_bg": "#131c31",
    "mark_bg": "#854d0e",
    "mark_text": "#fef08a",
}


def build_css(t: dict) -> str:
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

        * {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }}

        .stApp {{
            background: {t['bg']};
            color: {t['text']};
        }}

        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: {t['scrollbar']}; border-radius: 3px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: {t['scrollbar_hover']}; }}
        * {{ scrollbar-width: thin; scrollbar-color: {t['scrollbar']} transparent; }}

        section[data-testid="stSidebar"] {{
            background: {t['sidebar_bg']};
            border-right: 1px solid {t['border']};
        }}

        /* ── Chat Messages ── */
        .stChatMessage {{
            padding: 0.4rem 0 !important;
            animation: msgSlideIn 0.35s ease-out;
        }}
        @keyframes msgSlideIn {{
            from {{ opacity: 0; transform: translateY(12px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .stChatMessage [data-testid="chatMessageContent"] {{
            background: {t['assistant_bubble']} !important;
            color: {t['assistant_text']} !important;
            border-radius: 18px !important;
            padding: 1rem 1.25rem !important;
            box-shadow: {t['shadow_sm']};
            max-width: 82%;
            line-height: 1.7;
            font-size: 0.9375rem;
            border: 1px solid {t['border']};
            transition: box-shadow 0.2s, transform 0.2s;
        }}
        .stChatMessage [data-testid="chatMessageContent"]:hover {{
            box-shadow: {t['shadow_md']};
        }}

        .stChatMessage[data-testid="user-message"] [data-testid="chatMessageContent"] {{
            background: {t['user_bubble_bg']} !important;
            color: {t['user_text']} !important;
            border: none;
            box-shadow: 0 4px 15px rgba(99,102,241,0.35);
        }}
        .stChatMessage[data-testid="user-message"] [data-testid="chatMessageContent"]:hover {{
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(99,102,241,0.4);
        }}

        .stChatMessage [data-testid="chatMessageContent"] p {{ margin: 0 0 0.5rem 0; }}
        .stChatMessage [data-testid="chatMessageContent"] p:last-child {{ margin-bottom: 0; }}
        .stChatMessage [data-testid="chatMessageContent"] h1,
        .stChatMessage [data-testid="chatMessageContent"] h2,
        .stChatMessage [data-testid="chatMessageContent"] h3 {{
            margin: 0.75rem 0 0.5rem;
            font-weight: 600;
        }}
        .stChatMessage [data-testid="chatMessageContent"] h1 {{ font-size: 1.25rem; }}
        .stChatMessage [data-testid="chatMessageContent"] h2 {{ font-size: 1.1rem; }}
        .stChatMessage [data-testid="chatMessageContent"] h3 {{ font-size: 1rem; }}
        .stChatMessage [data-testid="chatMessageContent"] code {{
            background: {t['code_bg']};
            color: {t['code_text']};
            padding: 0.2rem 0.45rem;
            border-radius: 6px;
            font-size: 0.85em;
            font-family: 'JetBrains Mono', monospace;
        }}
        .stChatMessage [data-testid="chatMessageContent"] pre {{
            background: {t['code_bg']};
            border-radius: 12px;
            padding: 1.25rem;
            overflow-x: auto;
            border: 1px solid {t['border']};
            margin: 0.75rem 0;
        }}
        .stChatMessage [data-testid="chatMessageContent"] pre code {{
            background: none; padding: 0; border-radius: 0; font-size: 0.85rem;
        }}
        .stChatMessage [data-testid="chatMessageContent"] blockquote {{
            border-left: 4px solid {t['primary']};
            padding: 0.25rem 0 0.25rem 1rem;
            color: {t['text_secondary']};
            margin: 0.75rem 0;
            background: {t['primary_light']};
            border-radius: 0 8px 8px 0;
        }}
        .stChatMessage [data-testid="chatMessageContent"] table {{
            border-collapse: collapse; width: 100%; margin: 0.75rem 0; font-size: 0.875rem;
            border-radius: 8px; overflow: hidden;
        }}
        .stChatMessage [data-testid="chatMessageContent"] th,
        .stChatMessage [data-testid="chatMessageContent"] td {{
            border: 1px solid {t['border']}; padding: 0.5rem 0.75rem; text-align: left;
        }}
        .stChatMessage [data-testid="chatMessageContent"] th {{
            background: {t['bg_secondary']}; font-weight: 600;
        }}
        .stChatMessage [data-testid="chatMessageContent"] tr:nth-child(even) {{ background: {t['bg_secondary']}44; }}

        /* ── Search Highlight ── */
        mark.search-match {{
            background: {t['mark_bg']};
            color: {t['mark_text']};
            padding: 0.1rem 0.25rem;
            border-radius: 4px;
        }}

        /* ── Token Badge ── */
        .chat-token-badge {{
            display: inline-block;
            font-size: 0.6rem;
            font-weight: 600;
            background: {t['bg_secondary']};
            color: {t['text_muted']};
            padding: 0.1rem 0.4rem;
            border-radius: 8px;
            font-family: 'JetBrains Mono', monospace;
        }}

        /* ── Token Summary ── */
        .token-summary {{
            font-size: 0.75rem;
            color: {t['text_muted']};
            padding: 0.4rem 0.75rem;
            background: {t['bg_card']};
            border: 1px solid {t['border']};
            border-radius: 10px;
            margin: 0.5rem 0;
        }}

        /* ── Welcome ── */
        .welcome-container {{
            display: flex; flex-direction: column; align-items: center;
            justify-content: center; min-height: 60vh; text-align: center;
            padding: 2rem; animation: fadeIn 0.6s ease-out;
        }}
        @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
        @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-10px); }} }}
        @keyframes glow {{
            0%, 100% {{ filter: drop-shadow(0 4px 20px rgba(99,102,241,0.3)); }}
            50% {{ filter: drop-shadow(0 4px 40px rgba(99,102,241,0.6)); }}
        }}
        .welcome-icon {{
            font-size: 5rem; margin-bottom: 1.25rem;
            animation: float 3s ease-in-out infinite, glow 3s ease-in-out infinite;
        }}
        .welcome-title {{
            font-size: 2.25rem; font-weight: 800;
            background: {t['bg_gradient']};
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text; margin-bottom: 0.75rem; letter-spacing: -0.02em;
        }}
        .welcome-subtitle {{ font-size: 1rem; color: {t['text_secondary']}; max-width: 480px; line-height: 1.7; }}
        .welcome-features {{ display: flex; gap: 1rem; margin-top: 1.5rem; flex-wrap: wrap; justify-content: center; }}
        .welcome-feature {{
            background: {t['bg_card']}; border: 1px solid {t['border']};
            border-radius: 16px; padding: 1rem 1.25rem; min-width: 110px;
            box-shadow: {t['shadow_sm']}; transition: all 0.25s; cursor: default;
        }}
        .welcome-feature:hover {{
            box-shadow: {t['shadow_md']}; transform: translateY(-4px);
            border-color: {t['primary']}44;
        }}
        .welcome-feature-icon {{ font-size: 1.5rem; margin-bottom: 0.35rem; }}
        .welcome-feature-label {{ font-size: 0.8rem; font-weight: 600; color: {t['text']}; }}
        .welcome-feature-desc {{ font-size: 0.65rem; color: {t['text_muted']}; margin-top: 0.15rem; }}

        /* ── Chat Footer ── */
        .chat-footer {{ opacity: 0.6; transition: opacity 0.2s; }}
        .stChatMessage:hover .chat-footer {{ opacity: 1; }}
        .chat-timestamp {{ font-size: 0.65rem; color: {t['text_muted']}; }}

        /* ── Controls ── */
        .controls-bar {{
            display: flex; gap: 0.5rem; padding: 0.75rem 0 0.25rem;
            flex-wrap: wrap; border-top: 1px solid {t['border']}; margin-top: 1rem;
        }}
        .controls-bar .stButton button {{
            border-radius: 10px; font-size: 0.8rem; padding: 0.3rem 0.75rem;
            background: {t['bg_card']}; color: {t['text_secondary']};
            border: 1px solid {t['border']}; transition: all 0.2s;
            box-shadow: {t['shadow_sm']};
        }}
        .controls-bar .stButton button:hover {{
            background: {t['primary']}; color: white; border-color: {t['primary']};
            box-shadow: 0 4px 12px rgba(99,102,241,0.3);
        }}

        /* ── Status ── */
        .status-processing {{
            display: flex; align-items: center; gap: 0.75rem;
            padding: 0.75rem 1rem; background: {t['primary_light']};
            border: 1px solid {t['primary']}33; border-radius: 12px;
            margin: 0.75rem 0; font-size: 0.875rem; color: {t['primary']};
        }}
        .status-dot {{
            width: 10px; height: 10px; border-radius: 50%;
            background: {t['primary']}; animation: dotPulse 1.2s ease-in-out infinite;
        }}
        @keyframes dotPulse {{
            0%, 100% {{ transform: scale(1); opacity: 1; }}
            50% {{ transform: scale(1.4); opacity: 0.6; }}
        }}

        .stop-btn .stButton button {{
            background: {t['danger']} !important; color: white !important;
            border: none !important; border-radius: 10px; font-weight: 500;
            box-shadow: 0 4px 12px rgba(239,68,68,0.3);
        }}
        .stop-btn .stButton button:hover {{
            background: #dc2626 !important;
            box-shadow: 0 6px 16px rgba(239,68,68,0.4);
        }}

        /* ── Sidebar ── */
        .sidebar-card {{
            background: {t['bg_card']}; border: 1px solid {t['border']};
            border-radius: 14px; padding: 0.85rem; margin: 0.6rem 0;
            box-shadow: {t['shadow_sm']}; transition: all 0.2s;
        }}
        .sidebar-card:hover {{ box-shadow: {t['shadow_md']}; }}
        .sidebar-section-title {{
            font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
            letter-spacing: 0.08em; color: {t['text_muted']}; margin-bottom: 0.6rem;
        }}
        .sidebar-agent {{
            padding: 0.5rem 0.6rem; margin: 0.25rem 0;
            background: {t['bg_secondary']}; border-radius: 10px;
            border-left: 3px solid {t['primary']}; transition: background 0.15s;
        }}
        .sidebar-agent:hover {{ background: {t['hover_overlay']}; }}
        .sidebar-agent-role {{ font-weight: 600; font-size: 0.8rem; color: {t['text']}; }}
        .sidebar-agent-goal {{ font-size: 0.7rem; color: {t['text_secondary']}; margin-top: 0.1rem; }}

        .stat-row {{ display: flex; justify-content: space-between; padding: 0.2rem 0; font-size: 0.8rem; }}
        .stat-label {{ color: {t['text_secondary']}; }}
        .stat-value {{ color: {t['text']}; font-weight: 600; }}

        section[data-testid="stSidebar"] .stButton button {{
            background: {t['bg_card']}; color: {t['text']};
            border: 1px solid {t['border']}; border-radius: 10px;
            transition: all 0.15s; font-size: 0.8rem;
        }}
        section[data-testid="stSidebar"] .stButton button:hover {{
            background: {t['primary']}; color: white; border-color: {t['primary']};
        }}

        /* ── Input ── */
        .stChatInputContainer {{
            border: 2px solid {t['border']} !important;
            border-radius: 18px !important; background: {t['bg_card']} !important;
            transition: all 0.2s !important; box-shadow: {t['shadow_sm']};
            padding: 0.25rem 0.25rem 0.25rem 0.75rem !important;
        }}
        .stChatInputContainer:focus-within {{
            border-color: {t['primary']} !important;
            box-shadow: 0 0 0 4px {t['primary']}22 !important;
        }}

        .stSelectbox div[data-baseweb="select"] {{ border-radius: 10px !important; border-color: {t['border']} !important; }}
        div[data-testid="stAlert"] {{ border-radius: 12px; }}
        div[data-testid="stToast"] {{ border-radius: 12px; box-shadow: {t['shadow_lg']}; }}

        /* ── Search ── */
        .stTextInput input {{ border-radius: 10px !important; }}

        @media (max-width: 768px) {{
            .stChatMessage [data-testid="chatMessageContent"] {{ max-width: 95%; }}
            .welcome-title {{ font-size: 1.5rem; }}
            .welcome-icon {{ font-size: 3.5rem; }}
            .welcome-features {{ gap: 0.5rem; }}
            .welcome-feature {{ min-width: 80px; padding: 0.75rem; }}
        }}
    </style>
    """


def apply_theme(theme_name: str) -> dict:
    palette = LIGHT if theme_name == "light" else DARK
    css = build_css(palette)
    st.markdown(css, unsafe_allow_html=True)
    return palette
