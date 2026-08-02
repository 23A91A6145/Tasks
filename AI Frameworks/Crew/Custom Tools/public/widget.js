/* TenantDesk AI widget — self-contained, no build step.
 * Usage (from the workspace Settings → Public widget page):
 *   <script src="http://localhost:3000/widget.js"
 *           data-widget-src="/api/v1/public/acme-support/chat"
 *           data-token="<widget-token>"></script>
 *   (or data-widget-src="…" can be replaced with data-slug="acme-support")
 *
 * The script renders a floating chat bubble on the host page and talks to the
 * backend public chat endpoint using the widget token. Host pages served from a
 * different origin than the backend must be listed in the backend's
 * BACKEND_CORS_ORIGINS setting.
 */
(function () {
  "use strict";

  var script = document.currentScript;
  if (!script) return;

  var WIDGET_SRC = script.getAttribute("data-widget-src")
    || (script.getAttribute("data-slug")
        ? "/api/v1/public/" + script.getAttribute("data-slug") + "/chat"
        : "/api/v1/public/chat");
  var TOKEN = script.getAttribute("data-token") || "";
  var API_BASE = script.getAttribute("data-base") || "";
  var BRAND = script.getAttribute("data-brand") || "Support Assistant";
  var PRIMARY = script.getAttribute("data-primary") || "#6366f1";

  var endpoint = (API_BASE ? API_BASE.replace(/\/$/, "") : "") + WIDGET_SRC;

  var css = document.createElement("style");
  css.textContent =
    ".td-widget-btn{position:fixed;right:20px;bottom:20px;width:56px;height:56px;border-radius:50%;" +
    "background:" + PRIMARY + ";color:#fff;border:none;cursor:pointer;box-shadow:0 6px 20px rgba(0,0,0,.25);" +
    "font-size:24px;z-index:99999;transition:transform .15s}.td-widget-btn:hover{transform:scale(1.06)}" +
    ".td-widget-panel{position:fixed;right:20px;bottom:88px;width:340px;max-width:calc(100vw - 40px);" +
    "height:440px;background:#fff;border-radius:14px;box-shadow:0 10px 40px rgba(0,0,0,.2);" +
    "display:none;flex-direction:column;overflow:hidden;z-index:99999;font-family:-apple-system,Segoe UI,Roboto,sans-serif}" +
    ".td-widget-panel.open{display:flex}" +
    ".td-widget-header{background:" + PRIMARY + ";color:#fff;padding:12px 16px;font-weight:600;font-size:14px}" +
    ".td-widget-body{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:8px;background:#f7f8fa}" +
    ".td-msg{max-width:82%;padding:9px 12px;border-radius:14px;font-size:13px;line-height:1.45;white-space:pre-wrap}" +
    ".td-msg.bot{background:#fff;border:1px solid #e5e7eb;align-self:flex-start;border-bottom-left-radius:4px}" +
    ".td-msg.user{background:" + PRIMARY + ";color:#fff;align-self:flex-end;border-bottom-right-radius:4px}" +
    ".td-msg.err{background:#fee2e2;color:#b91c1c;align-self:center}" +
    ".td-src{font-size:11px;color:#6b7280;margin-top:4px}" +
    ".td-widget-input{display:flex;gap:8px;padding:10px;border-top:1px solid #e5e7eb;background:#fff}" +
    ".td-widget-input input{flex:1;border:1px solid #d1d5db;border-radius:8px;padding:8px 10px;font-size:13px;outline:none}" +
    ".td-widget-input button{background:" + PRIMARY + ";color:#fff;border:none;border-radius:8px;padding:8px 14px;" +
    "font-size:13px;cursor:pointer}";
  document.head.appendChild(css);

  var btn = document.createElement("button");
  btn.className = "td-widget-btn";
  btn.setAttribute("aria-label", "Open " + BRAND);
  btn.textContent = "✕";
  btn.style.display = "none";
  btn.style.fontSize = "0";
  btn.style.backgroundImage =
    "url('data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 24 24%22 fill=%22none%22 stroke=%22white%22 stroke-width=%222%22><path d=%22M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z%22/></svg>')";
  btn.style.backgroundRepeat = "no-repeat";
  btn.style.backgroundPosition = "center";
  btn.style.backgroundSize = "24px";

  var panel = document.createElement("div");
  panel.className = "td-widget-panel";
  panel.innerHTML =
    '<div class="td-widget-header">' + BRAND + "</div>" +
    '<div class="td-widget-body"><div class="td-msg bot">Hi! Ask me anything about this product.</div></div>' +
    '<form class="td-widget-input"><input type="text" placeholder="Type your question…" autocomplete="off" />' +
    '<button type="submit">Send</button></form>';
  document.body.appendChild(btn);
  document.body.appendChild(panel);

  var body = panel.querySelector(".td-widget-body");
  var input = panel.querySelector("input");
  var form = panel.querySelector("form");

  function addMsg(text, cls) {
    var el = document.createElement("div");
    el.className = "td-msg " + cls;
    el.textContent = text;
    body.appendChild(el);
    body.scrollTop = body.scrollHeight;
    return el;
  }

  btn.addEventListener("click", function () {
    var open = panel.classList.toggle("open");
    btn.style.backgroundImage =
      "url('data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 24 24%22 fill=%22none%22 stroke=%22white%22 stroke-width=%222%22>" +
      (open
        ? '<path d=%22M18 6L6 18M6 6l12 12%22/></svg>'
        : '<path d=%22M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z%22/></svg>') +
      "')";
    if (open) input.focus();
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var text = input.value.trim();
    if (!text) return;
    input.value = "";
    addMsg(text, "user");

    fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Widget-Token": TOKEN,
      },
      body: JSON.stringify({ message: text }),
    })
      .then(function (res) {
        return res.json().then(function (data) {
          if (!res.ok) {
            addMsg(data.detail || "The assistant is currently unavailable.", "err");
            return;
          }
          var reply = data.answer || "No answer available.";
          var sources = data.sources && data.sources.length ? " Sources: " + data.sources.length : "";
          addMsg(reply + sources, "bot");
        });
      })
      .catch(function () {
        addMsg("Network error — could not reach the assistant.", "err");
      });
  });

  setTimeout(function () {
    btn.style.display = "block";
  }, 300);
})();
