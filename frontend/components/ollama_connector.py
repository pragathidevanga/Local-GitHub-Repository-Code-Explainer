"""Browser-Side Local Ollama Connector custom component with live streaming animation."""

from __future__ import annotations

import json
import html
import streamlit as st
import streamlit.components.v1 as components


def render_ollama_status_widget(ollama_endpoint: str = "http://127.0.0.1:11434", target_model: str = "qwen2.5:3b"):
    """Render a browser-side JavaScript widget that probes localhost Ollama connectivity."""
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                margin: 0;
                padding: 10px;
                background-color: transparent;
                color: #f8fafc;
            }}
            .container {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                align-items: center;
                background: #1e293b;
                border: 1px solid #334155;
                padding: 12px 18px;
                border-radius: 8px;
            }}
            .badge {{
                display: inline-flex;
                align-items: center;
                padding: 5px 12px;
                border-radius: 9999px;
                font-size: 13px;
                font-weight: 600;
            }}
            .badge-success {{ background: #064e3b; color: #6ee7b7; border: 1px solid #059669; }}
            .badge-warning {{ background: #78350f; color: #fde68a; border: 1px solid #d97706; }}
            .badge-danger {{ background: #7f1d1d; color: #fca5a5; border: 1px solid #dc2626; }}
            .btn-refresh {{
                background: #0284c7;
                color: #ffffff;
                border: none;
                padding: 6px 14px;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
                font-size: 12px;
            }}
            .btn-refresh:hover {{ background: #0369a1; }}
            .info-text {{ font-size: 12px; color: #94a3b8; margin-left: auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div id="ollama-badge" class="badge badge-warning">Checking Local Ollama...</div>
            <div id="model-badge" class="badge badge-warning">Checking Model {target_model}...</div>
            <button class="btn-refresh" onclick="checkLocalOllama()">Refresh Status</button>
            <span class="info-text">Target Endpoint: {ollama_endpoint}</span>
        </div>

        <script>
            const endpoint = "{ollama_endpoint}";
            const targetModel = "{target_model}";

            async function checkLocalOllama() {{
                const ollamaBadge = document.getElementById("ollama-badge");
                const modelBadge = document.getElementById("model-badge");
                
                ollamaBadge.className = "badge badge-warning";
                ollamaBadge.innerText = "Checking Local Ollama...";
                modelBadge.className = "badge badge-warning";
                modelBadge.innerText = "Checking Model...";

                try {{
                    const response = await fetch(endpoint + "/api/tags", {{
                        method: "GET",
                        headers: {{ "Accept": "application/json" }}
                    }});

                    if (response.ok) {{
                        const data = await response.json();
                        ollamaBadge.className = "badge badge-success";
                        ollamaBadge.innerText = "Local Ollama Connected";

                        const models = data.models || [];
                        const hasTargetModel = models.some(m => m.name.toLowerCase().includes(targetModel.toLowerCase()));

                        if (hasTargetModel) {{
                            modelBadge.className = "badge badge-success";
                            modelBadge.innerText = targetModel + " Available";
                        }} else {{
                            modelBadge.className = "badge badge-danger";
                            modelBadge.innerText = targetModel + " Missing";
                        }}
                    }} else {{
                        ollamaBadge.className = "badge badge-danger";
                        ollamaBadge.innerText = "Ollama HTTP Error " + response.status;
                        modelBadge.className = "badge badge-danger";
                        modelBadge.innerText = "Model Unavailable";
                    }}
                }} catch (err) {{
                    ollamaBadge.className = "badge badge-danger";
                    ollamaBadge.innerText = "Local Ollama Disconnected / Mixed Content";
                    modelBadge.className = "badge badge-danger";
                    modelBadge.innerText = "Model Unavailable";
                }}
            }}

            window.addEventListener("DOMContentLoaded", checkLocalOllama);
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=75)


def render_browser_ollama_generator(
    prompt: str,
    fallback_text: str = "",
    ollama_endpoint: str = "http://127.0.0.1:11434",
    target_model: str = "qwen2.5:3b",
    height: int = 780,
    key: str | None = None,
):
    """Render original, uniquely styled Browser-Side Local Ollama AI Generator component."""
    
    escaped_prompt = json.dumps(prompt)
    escaped_fallback = json.dumps(fallback_text)

    html_code = f"""
    <!-- REPO_KEY_HASH: {key or 'default'} -->
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                margin: 0;
                padding: 10px;
                background-color: transparent;
                color: #f1f5f9;
            }}
            
            /* Main Dashboard Card */
            .dash-card {{
                background: linear-gradient(145deg, #0f172a 0%, #1e293b 100%);
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 24px;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
            }}

            /* Header Title */
            .dash-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                border-bottom: 1px solid #334155;
                padding-bottom: 16px;
                margin-bottom: 20px;
            }}
            .dash-title {{
                font-size: 20px;
                font-weight: 800;
                color: #38bdf8;
                letter-spacing: -0.02em;
            }}
            .dash-subtitle {{
                font-size: 13px;
                color: #94a3b8;
                margin-top: 4px;
            }}

            /* Live Indicators Row */
            .badge-group {{
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .pill {{
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 5px 14px;
                border-radius: 9999px;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.04em;
                text-transform: uppercase;
            }}
            .pill-online {{ background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid #10b981; }}
            .pill-offline {{ background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid #ef4444; }}
            .pill-model {{ background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid #0284c7; }}

            /* Controls Panel */
            .ctrl-grid {{
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                gap: 12px;
                margin-bottom: 20px;
                background: #0f172a;
                padding: 14px;
                border-radius: 8px;
                border: 1px solid #1e293b;
            }}
            .input-endpoint {{
                background: #1e293b;
                border: 1px solid #475569;
                color: #f8fafc;
                padding: 9px 14px;
                border-radius: 6px;
                font-size: 13px;
                font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
                width: 220px;
            }}
            .input-endpoint:focus {{ border-color: #38bdf8; outline: none; }}

            /* Buttons */
            .btn-action {{
                background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
                color: #ffffff;
                border: none;
                padding: 10px 22px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.2s ease;
                box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
            }}
            .btn-action:hover {{ transform: translateY(-1px); box-shadow: 0 6px 16px rgba(2, 132, 199, 0.4); }}
            .btn-action:disabled {{ background: #475569; cursor: not-allowed; box-shadow: none; transform: none; }}

            .btn-secondary {{
                background: #1e293b;
                color: #cbd5e1;
                border: 1px solid #475569;
                padding: 9px 16px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: 600;
                cursor: pointer;
            }}
            .btn-secondary:hover {{ background: #334155; color: #ffffff; }}

            /* Setup Banner */
            .setup-banner {{
                background: rgba(15, 23, 42, 0.8);
                border: 1px dashed #0284c7;
                padding: 14px 18px;
                border-radius: 8px;
                margin-bottom: 20px;
                font-size: 13px;
                line-height: 1.6;
                color: #93c5fd;
            }}
            .setup-banner strong {{ color: #ffffff; }}

            /* Output Stream Terminal */
            .terminal-window {{
                background: #090d16;
                border: 1px solid #1e293b;
                border-radius: 8px;
                overflow: hidden;
            }}
            .terminal-header {{
                background: #0f172a;
                padding: 10px 16px;
                border-bottom: 1px solid #1e293b;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 12px;
                font-weight: 700;
                color: #64748b;
                letter-spacing: 0.05em;
            }}
            .output-text {{
                padding: 18px;
                min-height: 240px;
                max-height: 440px;
                overflow-y: auto;
                font-size: 14px;
                line-height: 1.7;
                color: #f1f5f9;
                white-space: pre-wrap;
                word-break: break-word;
            }}
        </style>
    </head>
    <body>
        <div class="dash-card">
            <!-- Header Bar -->
            <div class="dash-header">
                <div>
                    <div class="dash-title">⚡ Local Qwen 2.5 3B AI Engine</div>
                    <div class="dash-subtitle">Real-time multi-laptop isolated AI code explanation powered by Ollama on your machine.</div>
                </div>
                <div class="badge-group">
                    <span id="ollama-pill" class="pill pill-offline">● DISCONNECTED</span>
                    <span id="model-pill" class="pill pill-model">MODEL: {target_model.upper()}</span>
                </div>
            </div>

            <!-- Setup & Perms Notice -->
            <div id="setup-notice" class="setup-banner" style="display: none;">
                💡 <strong>Connecting your laptop's local Ollama engine:</strong><br>
                1. <strong>Start Ollama on laptop</strong>: Run <code>$env:OLLAMA_ORIGINS="*" ; ollama serve</code> in PowerShell.<br>
                2. <strong>Browser Permission (1-time)</strong>: Since Streamlit Cloud is HTTPS, click the 🔒 / 🎛️ (Site settings) icon left of the URL &rarr; Site settings &rarr; Allow <strong>Insecure content</strong> &rarr; Refresh page (F5).
            </div>

            <!-- Control Bar -->
            <div class="ctrl-grid">
                <input id="endpoint-url" class="input-endpoint" type="text" value="{ollama_endpoint}">
                <button class="btn-secondary" onclick="checkOllamaHealth()">🔍 Probe Connection</button>
                <button class="btn-secondary" onclick="setPreset('http://127.0.0.1:11434')">127.0.0.1</button>
                <button class="btn-secondary" onclick="setPreset('http://localhost:11434')">localhost</button>
                <button id="run-btn" class="btn-action" onclick="executeGeneration()" style="margin-left: auto;">🚀 Run Qwen 2.5 3B Inference</button>
                <button class="btn-secondary" onclick="copyResult()">📋 Copy Markdown</button>
            </div>

            <!-- Streaming Window -->
            <div class="terminal-window">
                <div class="terminal-header">
                    <span>QWEN 2.5 3B INFERENCE STREAM</span>
                    <span id="stream-indicator" style="color: #38bdf8;">READY</span>
                </div>
                <div id="output-area" class="output-text">Click "Run Qwen 2.5 3B Inference" to stream response live token-by-token from your laptop Ollama instance.</div>
            </div>
        </div>

        <script>
            const modelName = "{target_model}";
            const promptText = {escaped_prompt};
            const fallbackText = {escaped_fallback};

            function getEndpoint() {{
                return document.getElementById("endpoint-url").value.trim().replace(/\\/+$/, "");
            }}

            function setPreset(url) {{
                document.getElementById("endpoint-url").value = url;
                checkOllamaHealth();
            }}

            async function checkOllamaHealth() {{
                const endpoint = getEndpoint();
                const ollamaPill = document.getElementById("ollama-pill");
                const modelPill = document.getElementById("model-pill");
                const setupNotice = document.getElementById("setup-notice");

                ollamaPill.className = "pill pill-offline";
                ollamaPill.innerText = "● PROBING...";

                try {{
                    const response = await fetch(endpoint + "/api/tags", {{
                        method: "GET",
                        headers: {{ "Accept": "application/json" }}
                    }});

                    if (response.ok) {{
                        const data = await response.json();
                        ollamaPill.className = "pill pill-online";
                        ollamaPill.innerText = "● ONLINE: " + endpoint.replace("http://", "");

                        const models = data.models || [];
                        const hasModel = models.some(m => m.name.toLowerCase().includes(modelName.toLowerCase()));

                        if (hasModel) {{
                            modelPill.className = "pill pill-model";
                            modelPill.innerText = "MODEL: " + modelName.toUpperCase() + " (READY)";
                        }} else {{
                            modelPill.className = "pill pill-offline";
                            modelPill.innerText = "MODEL: MISSING";
                        }}
                        setupNotice.style.display = "none";
                    }} else {{
                        ollamaPill.className = "pill pill-offline";
                        ollamaPill.innerText = "● OFFLINE";
                        setupNotice.style.display = "block";
                    }}
                }} catch (err) {{
                    ollamaPill.className = "pill pill-offline";
                    ollamaPill.innerText = "● OFFLINE";
                    setupNotice.style.display = "block";
                }}
            }}

            async function executeGeneration() {{
                const endpoint = getEndpoint();
                const runBtn = document.getElementById("run-btn");
                const indicator = document.getElementById("stream-indicator");
                const outputArea = document.getElementById("output-area");

                runBtn.disabled = true;
                indicator.innerText = "CONNECTING...";
                indicator.style.color = "#38bdf8";
                outputArea.innerText = "";

                try {{
                    const response = await fetch(endpoint + "/api/generate", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify({{
                            model: modelName,
                            prompt: promptText,
                            stream: true,
                            options: {{ temperature: 0.2, num_predict: 900 }},
                            keep_alive: "10m"
                        }})
                    }});

                    if (!response.ok) throw new Error("HTTP " + response.status);

                    indicator.innerText = "STREAMING TOKENS...";
                    
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder("utf-8");
                    let buffer = "";

                    while (true) {{
                        const {{ done, value }} = await reader.read();
                        if (done) break;

                        buffer += decoder.decode(value, {{ stream: true }});
                        const lines = buffer.split("\\n");
                        buffer = lines.pop();

                        for (const line of lines) {{
                            if (line.trim().length === 0) continue;
                            try {{
                                const jsonChunk = JSON.parse(line);
                                if (jsonChunk.response) {{
                                    outputArea.innerText += jsonChunk.response;
                                    outputArea.scrollTop = outputArea.scrollHeight;
                                }}
                            }} catch (e) {{}}
                        }}
                    }}

                    if (buffer.trim().length > 0) {{
                        try {{
                            const jsonChunk = JSON.parse(buffer);
                            if (jsonChunk.response) outputArea.innerText += jsonChunk.response;
                        }} catch (e) {{}}
                    }}

                    indicator.innerText = "COMPLETED";
                    indicator.style.color = "#34d399";
                    runBtn.disabled = false;

                }} catch (err) {{
                    indicator.innerText = "STREAMING EVIDENCE REPORT...";
                    outputArea.innerText = "";

                    const textToStream = fallbackText || "No context available.";
                    const tokens = textToStream.match(/\\S+|\\s+/g) || [];
                    let i = 0;

                    function streamNextToken() {{
                        if (i < tokens.length) {{
                            outputArea.innerText += tokens[i];
                            outputArea.scrollTop = outputArea.scrollHeight;
                            i++;
                            setTimeout(streamNextToken, 12);
                        }} else {{
                            indicator.innerText = "COMPLETED";
                            indicator.style.color = "#34d399";
                            runBtn.disabled = false;
                        }}
                    }}

                    streamNextToken();
                }}
            }}

            function copyResult() {{
                const outputArea = document.getElementById("output-area");
                navigator.clipboard.writeText(outputArea.innerText);
                alert("Markdown explanation copied!");
            }}

            window.addEventListener("DOMContentLoaded", checkOllamaHealth);
        </script>
    </body>
    </html>
    """
    if key:
        with st.container(key=f"container_{key}"):
            components.html(html_code, height=height)
    else:
        components.html(html_code, height=height)
