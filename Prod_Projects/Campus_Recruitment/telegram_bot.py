"""
Hashira ATS - Telegram Delivery Integration
Direct HTTP-based Telegram Bot API client for instant notifications and document reports.
Includes automatic bot info discovery and chat-id auto detection.
"""
import os
import requests
from typing import List, Tuple, Optional, Dict
from models import CandidateResult

TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/{method}"

def get_bot_info(bot_token: str) -> Tuple[bool, Dict]:
    """Retrieve bot metadata from Telegram."""
    if not bot_token:
        return False, {"error": "Token is empty"}
    try:
        url = TELEGRAM_API_BASE.format(token=bot_token.strip(), method="getMe")
        res = requests.get(url, timeout=10)
        data = res.json()
        if data.get("ok"):
            return True, data.get("result", {})
        return False, {"error": data.get("description", "Unknown error")}
    except Exception as e:
        return False, {"error": str(e)}

def auto_detect_chat_id(bot_token: str) -> Tuple[bool, str, str]:
    """
    Check getUpdates to automatically find the Chat ID of anyone who messaged the bot.
    Returns: (success, chat_id, user_description)
    """
    if not bot_token:
        return False, "", "Bot token is missing."
    try:
        url = TELEGRAM_API_BASE.format(token=bot_token.strip(), method="getUpdates")
        res = requests.get(url, timeout=10)
        data = res.json()
        if not data.get("ok"):
            return False, "", f"Telegram API error: {data.get('description')}"
            
        updates = data.get("result", [])
        if not updates:
            # Get bot username to provide direct link
            ok, bot_info = get_bot_info(bot_token)
            username = bot_info.get("username", "your_bot")
            return False, "", f"No messages received yet. Please open https://t.me/{username} in Telegram and click 'START'."
            
        # Get latest message
        latest = updates[-1]
        msg = latest.get("message") or latest.get("channel_post") or latest.get("my_chat_member")
        if msg and "chat" in msg:
            chat = msg["chat"]
            cid = str(chat["id"])
            cname = chat.get("first_name") or chat.get("title") or chat.get("username") or "User"
            return True, cid, f"Found active chat with '{cname}' (ID: {cid})"
            
        return False, "", "Could not parse chat information from recent updates."
    except Exception as e:
        return False, "", f"Error checking updates: {str(e)}"

def test_telegram_connection(bot_token: str, chat_id: str) -> Tuple[bool, str]:
    """Verify bot token and chat ID reachability."""
    if not bot_token:
        return False, "Telegram Bot Token is missing."
    if not chat_id:
        return False, "Telegram Chat ID is missing."
    
    # 1. Test getMe
    ok, bot_info = get_bot_info(bot_token)
    if not ok:
        return False, f"Invalid Telegram Bot Token: {bot_info.get('error')}"
        
    bot_name = bot_info.get("first_name", "Bot")
    username = bot_info.get("username", "")

    # 2. Test ping message
    try:
        msg_url = TELEGRAM_API_BASE.format(token=bot_token.strip(), method="sendMessage")
        payload = {
            "chat_id": chat_id.strip(),
            "text": f"⚡ <b>Connected to Hashira ATS!</b>\nBot: @{username}\nReady to deliver live ATS candidate intelligence reports.",
            "parse_mode": "HTML"
        }
        res_msg = requests.post(msg_url, json=payload, timeout=10)
        res_data = res_msg.json()
        
        if not res_data.get("ok"):
            err_desc = res_data.get("description", "")
            if "chat not found" in err_desc.lower():
                return False, (
                    f"⚠️ Telegram returned 'chat not found' for Chat ID <code>{chat_id}</code>.<br>"
                    f"<b>Action Needed:</b> Open Telegram, go to <a href='https://t.me/{username}' target='_blank'>@{username}</a>, "
                    f"click <b>START</b> (or send any message), and click Test Connection again!"
                )
            return False, f"Telegram API error: {err_desc}"
            
        return True, f"✓ Successfully connected to Telegram bot @{username}! Test notification sent to chat."
    except Exception as e:
        return False, f"Connection error reaching Telegram API: {str(e)}"

def format_telegram_candidate_message(result: CandidateResult) -> str:
    """Format single candidate evaluation using Hashira's official report template."""
    req_pct = int((result.score_breakdown.required_skills / 30.0) * 100)
    tech_pct = int((result.score_breakdown.technical_skills / 20.0) * 100)
    sem_pct = int((result.score_breakdown.semantic_relevance / 15.0) * 100)
    exp_pct = int((result.score_breakdown.experience_match / 10.0) * 100)
    kw_pct = int((result.score_breakdown.keyword_coverage / 10.0) * 100)
    proj_pct = int((result.score_breakdown.projects_evidence / 10.0) * 100)
    ats_pct = int((result.score_breakdown.ats_readability / 5.0) * 100)

    matched_list = "\n".join([f"• {s}" for s in result.matched_skills[:8]]) or "• None detected"
    partial_list = "\n".join([f"• {s}" for s in result.partial_skills[:5]]) or "• None"
    missing_list = "\n".join([f"• {s}" for s in result.missing_skills[:8]]) or "• None"
    
    improvements_list = "\n".join([f"{i+1}. {imp}" for i, imp in enumerate(result.improvements[:4])]) or "1. Quantify engineering impact\n2. Align keywords with JD"
    roadmap_list = "\n".join([f"{item['day']}: {item['focus']}" for item in result.learning_roadmap[:4]]) or "1. Core Frameworks\n2. Production Deployment"

    msg = f"""🤖 <b>HASHIRA ATS — RESUME REPORT</b>
━━━━━━━━━━━━━━━━━━━━━━
👤 <b>CANDIDATE:</b> {result.candidate_name}
🎯 <b>TARGET ROLE:</b> {result.target_role}

📊 <b>OVERALL SCORE:</b> <b>{result.score} / 100</b>
🟢 <b>VERDICT:</b> {result.compatibility_band}

━━━━━━━━━━━━━━━━━━━━━━
📈 <b>SCORE BREAKDOWN</b>
• Required Skills: <b>{req_pct}%</b>
• Technical Skills: <b>{tech_pct}%</b>
• Semantic Match: <b>{sem_pct}%</b>
• Experience Alignment: <b>{exp_pct}%</b>
• Keyword Coverage: <b>{kw_pct}%</b>
• Project Evidence: <b>{proj_pct}%</b>
• ATS Readability: <b>{ats_pct}%</b>

━━━━━━━━━━━━━━━━━━━━━━
✅ <b>MATCHED SKILLS</b>
{matched_list}

⚠️ <b>PARTIAL MATCHES</b>
{partial_list}

❌ <b>MISSING SKILLS</b>
{missing_list}

━━━━━━━━━━━━━━━━━━━━━━
🔥 <b>TOP IMPROVEMENTS</b>
{improvements_list}

━━━━━━━━━━━━━━━━━━━━━━
📚 <b>LEARNING SPRINT</b>
{roadmap_list}

━━━━━━━━━━━━━━━━━━━━━━
🚀 <b>FINAL CONCLUSION</b>
{result.final_verdict}

— <i>Hashira ATS Resume Intelligence Engine</i>"""
    return msg

def format_telegram_batch_message(candidates: List[CandidateResult], target_role: str) -> str:
    """Format campus drive batch leaderboard summary."""
    sorted_candidates = sorted(candidates, key=lambda c: c.score, reverse=True)
    total_candidates = len(candidates)
    avg_score = round(sum(c.score for c in candidates) / total_candidates, 1) if total_candidates else 0
    above_80 = len([c for c in candidates if c.score >= 80])
    below_60 = len([c for c in candidates if c.score < 60])
    
    medals = ["🥇", "🥈", "🥉"]
    rankings_lines = []
    for i, c in enumerate(sorted_candidates[:10]):
        prefix = medals[i] if i < 3 else f"{i+1}."
        rankings_lines.append(f"{prefix} <b>{c.candidate_name}</b> — <b>{c.score}/100</b> ({c.compatibility_band})")
    
    rankings_str = "\n".join(rankings_lines)

    msg = f"""🏆 <b>HASHIRA CAMPUS DRIVE — BATCH REPORT</b>
━━━━━━━━━━━━━━━━━━━━━━
🎯 <b>ROLE:</b> {target_role}
👥 <b>TOTAL CANDIDATES ANALYZED:</b> {total_candidates}
📈 <b>AVERAGE SCORE:</b> {avg_score} / 100
🟢 <b>ABOVE 80 (Shortlist Ready):</b> {above_80}
🔴 <b>BELOW 60 (Needs Training):</b> {below_60}

━━━━━━━━━━━━━━━━━━━━━━
🏅 <b>TOP CANDIDATES LEADERBOARD</b>
{rankings_str}

━━━━━━━━━━━━━━━━━━━━━━
⚡ <i>Generated automatically by Hashira ATS</i>"""
    return msg

def send_telegram_message(text: str, bot_token: str, chat_id: str) -> Tuple[bool, str]:
    """Send text message to Telegram chat or channel."""
    if not bot_token or not chat_id:
        return False, "Telegram credentials not configured."
    
    url = TELEGRAM_API_BASE.format(token=bot_token.strip(), method="sendMessage")
    payload = {
        "chat_id": chat_id.strip(),
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        resp = requests.post(url, json=payload, timeout=15)
        data = resp.json()
        if data.get("ok"):
            return True, "Message delivered to Telegram successfully!"
        else:
            err_desc = data.get("description", resp.text)
            return False, f"Telegram API error: {err_desc}"
    except Exception as e:
        return False, f"Failed to send Telegram message: {str(e)}"

def send_telegram_file(file_path: str, caption: str, bot_token: str, chat_id: str) -> Tuple[bool, str]:
    """Send a document or markdown report to Telegram."""
    if not bot_token or not chat_id:
        return False, "Telegram credentials not configured."
    
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
        
    url = TELEGRAM_API_BASE.format(token=bot_token.strip(), method="sendDocument")
    try:
        with open(file_path, "rb") as doc_file:
            files = {"document": doc_file}
            data = {
                "chat_id": chat_id.strip(),
                "caption": caption[:1024],
                "parse_mode": "HTML"
            }
            resp = requests.post(url, data=data, files=files, timeout=25)
            res_data = resp.json()
            if res_data.get("ok"):
                return True, "Report document uploaded to Telegram successfully!"
            else:
                return False, f"Telegram upload error: {res_data.get('description', resp.text)}"
    except Exception as e:
        return False, f"Failed to upload document to Telegram: {str(e)}"
