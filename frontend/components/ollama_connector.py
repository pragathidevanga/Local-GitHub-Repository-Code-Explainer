"""Browser-Side Local Ollama Connector custom component.

Enables the Streamlit frontend (hosted remotely or locally) to execute Qwen 2.5 3B inference
directly via the end-user's own local Ollama endpoint (http://127.0.0.1:11434) running on their laptop.
"""

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
                    ollamaBadge.innerText = "Local Ollama Disconnected / CORS Blocked";
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
    ollama_endpoint: str = "http://127.0.0.1:11434",
    target_model: str = "qwen2.5:3b",
    height: int = 650,
):
    """Render browser-side JavaScript generator component that streams Qwen inference live from user's local Ollama."""
    
    # Safely escape raw prompt text to avoid XSS injection or syntax errors
    escaped_prompt = json.dumps(prompt)

    html_code = f"""
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
                min-height: 480px;
                max-height: 580px;
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
                padding: 8px 18px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
                cursor: pointer;
            }}
            .btn:hover {{ opacity: 0.9; }}
            .btn:disabled {{ background: #475569; cursor: not-allowed; }}
            .status-text {{
                font-size: 13px;
                color: #38bdf8;
                font-weight: 500;
            }}
            .error-box {{
                background: #450a0a;
                border: 1px solid #991b1b;
                color: #fca5a5;
                padding: 16px;
                border-radius: 8px;
                margin-top: 10px;
                font-size: 14px;
            }}
            .setup-guide {{
                margin-top: 12px;
                background: #1e293b;
                border: 1px solid #0284c7;
                padding: 14px;
                border-radius: 8px;
                font-size: 13px;
                color: #93c5fd;
            }}
        </style>
    </head>
    <body>
        <div class="control-panel">
            <button id="gen-btn" class="btn" onclick="startGeneration()">Start Local Qwen Generation</button>
            <span id="status-label" class="status-text">Ready to run on your local laptop Ollama</span>
        </div>

        <div id="output" class="output-box">Click "Start Local Qwen Generation" above to stream explanation from your laptop's local Ollama instance...</div>
        <div id="error-container"></div>

        <script>
            const endpoint = "{ollama_endpoint}";
            const modelName = "{target_model}";
            const promptText = {escaped_prompt};

            async function startGeneration() {{
                const genBtn = document.getElementById("gen-btn");
                const statusLabel = document.getElementById("status-label");
                const outputBox = document.getElementById("output");
                const errorContainer = document.getElementById("error-container");

                genBtn.disabled = true;
                statusLabel.innerText = "Connecting to local Ollama on 127.0.0.1:11434...";
                outputBox.innerText = "";
                errorContainer.innerHTML = "";

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
                        throw new Error("Ollama returned HTTP status " + response.status + ": " + response.statusText);
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
                        buffer = lines.pop(); // Keep partial line in buffer

                        for (const line of lines) {{
                            if (line.trim().length === 0) continue;
                            try {{
                                const jsonChunk = JSON.parse(line);
                                if (jsonChunk.response) {{
                                    outputBox.innerText += jsonChunk.response;
                                    outputBox.scrollTop = outputBox.scrollHeight;
                                }}
                            }} catch (e) {{
                                // Skip malformed chunks
                            }}
                        }}
                    }}

                    // Flush remaining buffer
                    if (buffer.trim().length > 0) {{
                        try {{
                            const jsonChunk = JSON.parse(buffer);
                            if (jsonChunk.response) outputBox.innerText += jsonChunk.response;
                        }} catch (e) {{}}
                    }}

                    statusLabel.innerText = "Generation completed successfully!";
                    genBtn.disabled = false;

                }} catch (err) {{
                    statusLabel.innerText = "Generation failed.";
                    genBtn.disabled = false;
                    
                    let errorHtml = '<div class="error-box"><strong>Error:</strong> ' + escapeHtml(err.message) + '</div>';
                    errorHtml += `
                        <div class="setup-guide">
                            <strong>Local Ollama Setup & CORS Troubleshooting:</strong><br>
                            1. Install Ollama from <a href="https://ollama.com" target="_blank" style="color:#60a5fa;">ollama.com</a>.<br>
                            2. Open Terminal / PowerShell and run: <code>ollama pull qwen2.5:3b</code><br>
                            3. Ensure Ollama is running on your laptop.<br>
                            4. If deployed on Streamlit Cloud, configure browser origin permission:<br>
                            &nbsp;&nbsp;&nbsp;&nbsp;• <strong>Windows (PowerShell):</strong> <code>$env:OLLAMA_ORIGINS="*" ; ollama serve</code><br>
                            &nbsp;&nbsp;&nbsp;&nbsp;• <strong>macOS / Linux:</strong> <code>OLLAMA_ORIGINS="*" ollama serve</code><br>
                            5. Click "Start Local Qwen Generation" again.
                        </div>
                    `;
                    errorContainer.innerHTML = errorHtml;
                }}
            }}

            function escapeHtml(str) {{
                return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
            }}

            // Auto-trigger generation on mount
            window.addEventListener("DOMContentLoaded", () => {{
                setTimeout(startGeneration, 300);
            }});
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=height)
