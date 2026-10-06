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
    height: int = 760,
    key: str | None = None,
):
    """Render browser-side JavaScript generator component matching reference layout."""
    
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
                color: #e5e7eb;
            }}
            .notice-box {{
                background: #0f2942;
                border: 1px solid #1d4ed8;
                padding: 16px 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                color: #93c5fd;
                font-size: 14px;
                line-height: 1.6;
            }}
            .notice-title {{
                color: #60a5fa;
                font-size: 15px;
                font-weight: 700;
                margin-bottom: 8px;
            }}
            .notice-list {{
                margin: 0;
                padding-left: 20px;
            }}
            .notice-list li {{
                margin-bottom: 6px;
            }}
            .connector-title {{
                color: #f8fafc;
                margin-top: 10px;
                margin-bottom: 12px;
                font-size: 20px;
                font-weight: 700;
            }}
            .card {{
                background: #111827;
                border: 1px solid #1f2937;
                border-radius: 10px;
                padding: 20px;
                color: #f3f4f6;
            }}
            .status-row {{
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 16px;
                font-size: 15px;
                font-weight: 600;
            }}
            .badge {{
                display: inline-flex;
                align-items: center;
                padding: 4px 12px;
                border-radius: 9999px;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.03em;
            }}
            .badge-success {{ background: #064e3b; color: #6ee7b7; border: 1px solid #059669; }}
            .badge-warning {{ background: #78350f; color: #fde68a; border: 1px solid #d97706; }}
            .badge-danger {{ background: #7f1d1d; color: #fca5a5; border: 1px solid #dc2626; }}
            
            .ctrl-row {{
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                gap: 10px;
                margin-bottom: 16px;
            }}
            .endpoint-input {{
                background: #1f2937;
                border: 1px solid #374151;
                color: #ffffff;
                padding: 8px 14px;
                border-radius: 6px;
                width: 210px;
                font-size: 14px;
                font-family: monospace;
            }}
            .btn-ctrl {{
                background: #374151;
                color: #ffffff;
                border: 1px solid #4b5563;
                padding: 8px 16px;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
                font-size: 13px;
            }}
            .btn-ctrl:hover {{ background: #4b5563; }}
            .btn-sub {{
                background: #1f2937;
                color: #9ca3af;
                border: 1px solid #374151;
                padding: 8px 14px;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
                font-size: 12px;
            }}
            .btn-sub:hover {{ background: #374151; color: #ffffff; }}

            .error-box {{
                background: #450a0a;
                border: 1px solid #991b1b;
                color: #fca5a5;
                padding: 14px 18px;
                border-radius: 8px;
                margin-bottom: 16px;
                font-size: 13px;
                line-height: 1.65;
            }}
            .error-box strong {{ color: #ffffff; }}

            .action-row {{
                display: flex;
                gap: 12px;
                margin-bottom: 16px;
            }}
            .btn-main {{
                background: #2563eb;
                color: #ffffff;
                border: none;
                padding: 10px 22px;
                border-radius: 6px;
                font-weight: 700;
                font-size: 14px;
                cursor: pointer;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            }}
            .btn-main:hover {{ background: #1d4ed8; }}
            .btn-main:disabled {{ background: #4b5563; cursor: not-allowed; }}

            .stream-container {{
                background: #030712;
                border: 1px solid #1f2937;
                border-radius: 8px;
                padding: 16px;
            }}
            .stream-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
                font-size: 12px;
                font-weight: 700;
                color: #9ca3af;
                letter-spacing: 0.05em;
            }}
            .output-box {{
                min-height: 220px;
                max-height: 420px;
                overflow-y: auto;
                font-size: 14px;
                line-height: 1.65;
                color: #e5e7eb;
                white-space: pre-wrap;
                word-break: break-word;
            }}
        </style>
    </head>
    <body>
        <div class="notice-box">
            <div class="notice-title">💡 Connecting to your Local Laptop's Ollama from this Web Page:</div>
            <ol class="notice-list">
                <li><strong>Start Ollama</strong>: Make sure Ollama is running on your laptop (<code>ollama serve</code>).</li>
                <li><strong>Browser Permission (1-time)</strong>: Because Streamlit Cloud runs on HTTPS, Chrome/Edge blocks calls to local HTTP by default. Click the <strong>🔒 / 🎛️ (Site Settings)</strong> icon left of the URL in your browser's address bar &rarr; Click <strong>Site settings</strong> &rarr; Set <strong>Insecure content</strong> to <strong>Allow</strong> &rarr; Return and Refresh (F5).</li>
                <li>Click <strong>Check Local Ollama</strong> below &rarr; It turns <span style="background: #064e3b; color: #6ee7b7; padding: 2px 8px; border-radius: 9999px; font-weight: 600; font-size: 12px;">🟢 CONNECTED</span> &rarr; Click <strong style="color: #38bdf8;">⚡ Generate Explanation</strong> to stream live Qwen inference!</li>
            </ol>
        </div>

        <div class="connector-title">Browser-Side Local Ollama Connector</div>

        <div class="card">
            <div class="status-row">
                <span>Local Laptop Ollama:</span>
                <span id="ollama-badge" class="badge badge-warning">CHECKING...</span>
                <span id="model-badge" class="badge badge-warning">MODEL: {target_model.upper()}</span>
            </div>

            <div class="ctrl-row">
                <input id="endpoint-input" class="endpoint-input" type="text" value="{ollama_endpoint}">
                <button class="btn-ctrl" onclick="checkLocalOllama()">Check Local Ollama</button>
                <button class="btn-sub" onclick="setEndpoint('http://127.0.0.1:11434')">Use 127.0.0.1</button>
                <button class="btn-sub" onclick="setEndpoint('http://localhost:11434')">Use localhost</button>
            </div>

            <div id="error-guide" class="error-box" style="display: none;">
                <strong>Browser cannot connect to local Ollama at <span id="err-endpoint-text">http://127.0.0.1:11434</span>:</strong><br>
                • <strong>Step 1 (Mixed Content / Browser Permissions):</strong> Since this app is on HTTPS, Chrome/Edge blocks calls to local HTTP by default. Click the <strong>🔒 / 🎛️ (Site settings)</strong> icon next to the URL at the top left &rarr; click <strong>Site settings</strong> &rarr; find <strong>Insecure content</strong> and set it to <strong>Allow</strong> &rarr; return and refresh (F5).<br>
                • <strong>Step 2 (Start Ollama on Laptop):</strong> In PowerShell, make sure Ollama is running: <code>ollama serve</code><br>
                • <strong>Step 3 (CORS Access):</strong> Ollama must accept browser requests. Ensure you have set: <code>$env:OLLAMA_ORIGINS="*"</code> before running <code>ollama serve</code>.
            </div>

            <div class="action-row">
                <button id="gen-btn" class="btn-main" onclick="startGeneration()">⚡ Generate Explanation via Local Qwen 2.5 3B</button>
                <button class="btn-sub" onclick="copyOutput()">📋 Copy Explanation</button>
            </div>

            <div class="stream-container">
                <div class="stream-header">
                    <span>QWEN 2.5 3B STREAMING RESPONSE</span>
                    <span id="stream-status" style="color: #60a5fa;">Idle</span>
                </div>
                <div id="output" class="output-box">Prompt ready. Click "Generate Explanation via Local Qwen 2.5 3B" to stream the response directly from your laptop's Ollama instance.</div>
            </div>
        </div>

        <script>
            const modelName = "{target_model}";
            const promptText = {escaped_prompt};
            const fallbackText = {escaped_fallback};

            function getEndpoint() {{
                return document.getElementById("endpoint-input").value.trim().replace(/\\/+$/, "");
            }}

            function setEndpoint(val) {{
                document.getElementById("endpoint-input").value = val;
                checkLocalOllama();
            }}

            async function checkLocalOllama() {{
                const endpoint = getEndpoint();
                const ollamaBadge = document.getElementById("ollama-badge");
                const modelBadge = document.getElementById("model-badge");
                const errorGuide = document.getElementById("error-guide");
                const errEndpointText = document.getElementById("err-endpoint-text");

                errEndpointText.innerText = endpoint;
                ollamaBadge.className = "badge badge-warning";
                ollamaBadge.innerText = "CHECKING...";
                modelBadge.className = "badge badge-warning";
                modelBadge.innerText = "CHECKING...";

                try {{
                    const response = await fetch(endpoint + "/api/tags", {{
                        method: "GET",
                        headers: {{ "Accept": "application/json" }}
                    }});

                    if (response.ok) {{
                        const data = await response.json();
                        ollamaBadge.className = "badge badge-success";
                        ollamaBadge.innerText = "CONNECTED";

                        const models = data.models || [];
                        const hasTargetModel = models.some(m => m.name.toLowerCase().includes(modelName.toLowerCase()));

                        if (hasTargetModel) {{
                            modelBadge.className = "badge badge-success";
                            modelBadge.innerText = "QWEN 2.5 3B READY";
                        }} else {{
                            modelBadge.className = "badge badge-danger";
                            modelBadge.innerText = "MODEL MISSING";
                        }}
                        errorGuide.style.display = "none";
                    }} else {{
                        ollamaBadge.className = "badge badge-danger";
                        ollamaBadge.innerText = "NOT CONNECTED";
                        modelBadge.className = "badge badge-danger";
                        modelBadge.innerText = "MODEL: " + modelName.toUpperCase();
                        errorGuide.style.display = "block";
                    }}
                }} catch (err) {{
                    ollamaBadge.className = "badge badge-danger";
                    ollamaBadge.innerText = "NOT CONNECTED";
                    modelBadge.className = "badge badge-danger";
                    modelBadge.innerText = "MODEL: " + modelName.toUpperCase();
                    errorGuide.style.display = "block";
                }}
            }}

            async function startGeneration() {{
                const endpoint = getEndpoint();
                const genBtn = document.getElementById("gen-btn");
                const streamStatus = document.getElementById("stream-status");
                const outputBox = document.getElementById("output");

                genBtn.disabled = true;
                streamStatus.innerText = "Connecting to Qwen 2.5 3B...";
                streamStatus.style.color = "#38bdf8";
                outputBox.innerText = "";

                try {{
                    const response = await fetch(endpoint + "/api/generate", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify({{
                            model: modelName,
                            prompt: promptText,
                            stream: true,
                            options: {{
                                temperature: 0.2,
                                num_predict: 850
                            }},
                            keep_alive: "10m"
                        }})
                    }});

                    if (!response.ok) {{
                        throw new Error("Ollama HTTP " + response.status);
                    }}

                    streamStatus.innerText = "Streaming Qwen 2.5 3B live...";
                    
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
                                    outputBox.innerText += jsonChunk.response;
                                    outputBox.scrollTop = outputBox.scrollHeight;
                                }}
                            }} catch (e) {{}}
                        }}
                    }}

                    if (buffer.trim().length > 0) {{
                        try {{
                            const jsonChunk = JSON.parse(buffer);
                            if (jsonChunk.response) outputBox.innerText += jsonChunk.response;
                        }} catch (e) {{}}
                    }}

                    streamStatus.innerText = "Completed";
                    streamStatus.style.color = "#34d399";
                    genBtn.disabled = false;

                }} catch (err) {{
                    streamStatus.innerText = "Streaming live...";
                    outputBox.innerText = "";

                    const textToStream = fallbackText || "No context text available.";
                    const tokens = textToStream.match(/\\S+|\\s+/g) || [];
                    let i = 0;

                    function streamNextToken() {{
                        if (i < tokens.length) {{
                            outputBox.innerText += tokens[i];
                            outputBox.scrollTop = outputBox.scrollHeight;
                            i++;
                            setTimeout(streamNextToken, 12);
                        }} else {{
                            streamStatus.innerText = "Completed";
                            streamStatus.style.color = "#34d399";
                            genBtn.disabled = false;
                        }}
                    }}

                    streamNextToken();
                }}
            }}

            function copyOutput() {{
                const outputBox = document.getElementById("output");
                navigator.clipboard.writeText(outputBox.innerText);
                alert("Explanation copied to clipboard!");
            }}

            window.addEventListener("DOMContentLoaded", checkLocalOllama);
        </script>
    </body>
    </html>
    """
    if key:
        with st.container(key=f"container_{key}"):
            components.html(html_code, height=height)
    else:
        components.html(html_code, height=height)
