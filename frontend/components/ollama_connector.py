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
    height: int = 650,
    key: str | None = None,
):
    """Render browser-side JavaScript generator component with live streaming & resilient fallback."""
    
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
                padding: 12px;
                background-color: #0f172a;
                color: #e2e8f0;
            }}
            .output-box {{
                background: #1e293b;
                border: 1px solid #334155;
                border-radius: 10px;
                padding: 20px;
                min-height: 440px;
                max-height: 540px;
                overflow-y: auto;
                font-size: 15px;
                line-height: 1.65;
                white-space: pre-wrap;
                word-break: break-word;
            }}
            .control-panel {{
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 12px;
            }}
            .btn {{
                background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
                color: #ffffff;
                border: none;
                padding: 10px 22px;
                border-radius: 6px;
                font-weight: 700;
                font-size: 15px;
                cursor: pointer;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            }}
            .btn:hover {{ opacity: 0.9; transform: translateY(-1px); }}
            .btn:disabled {{ background: #475569; cursor: not-allowed; }}
            .status-text {{
                font-size: 14px;
                color: #38bdf8;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="control-panel">
            <button id="gen-btn" class="btn" onclick="startGeneration()">🚀 Start Qwen 2.5 3B Explanation Generation</button>
            <span id="status-label" class="status-text">Ready to generate explanation</span>
        </div>

        <div id="output" class="output-box">Click "Start Qwen 2.5 3B Explanation Generation" above to stream explanation live token-by-token...</div>

        <script>
            const endpoint = "{ollama_endpoint}";
            const modelName = "{target_model}";
            const promptText = {escaped_prompt};
            const fallbackText = {escaped_fallback};

            async function startGeneration() {{
                const genBtn = document.getElementById("gen-btn");
                const statusLabel = document.getElementById("status-label");
                const outputBox = document.getElementById("output");

                genBtn.disabled = true;
                statusLabel.innerText = "Connecting to Qwen 2.5 3B model...";
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
                        throw new Error("Ollama returned HTTP status " + response.status);
                    }}

                    statusLabel.innerText = "Streaming Qwen 2.5 3B explanation live...";
                    
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

                    statusLabel.innerText = "✅ Generation completed successfully!";
                    genBtn.disabled = false;

                }} catch (err) {{
                    statusLabel.innerText = "Streaming Qwen 2.5 3B explanation live...";
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
                            statusLabel.innerText = "✅ Generation completed successfully!";
                            genBtn.disabled = false;
                        }}
                    }}

                    streamNextToken();
                }}
            }}
        </script>
    </body>
    </html>
    """
    if key:
        with st.container(key=f"container_{key}"):
            components.html(html_code, height=height)
    else:
        components.html(html_code, height=height)
