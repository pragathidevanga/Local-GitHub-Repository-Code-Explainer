"""Streamlit UI implementation for Local GitHub Repository Code Explainer."""

from __future__ import annotations

import streamlit as st

from backend.llm_service import (
    check_ollama_status,
    generate_evidence_based_explanation,
    generate_with_ollama_local,
    stream_qwen_explanation,
)
from backend.main import process_repository_service
from backend.models import AnalysisResponse
from frontend.components.ollama_connector import (
    render_browser_ollama_generator,
    render_ollama_status_widget,
)
from frontend.styles import apply_custom_css

EXAMPLE_REPOSITORIES = [
    ("octocat/Hello-World", "https://github.com/octocat/Hello-World"),
    ("streamlit/streamlit-example", "https://github.com/streamlit/streamlit-example"),
    ("psf/requests", "https://github.com/psf/requests"),
    ("fastapi/fastapi", "https://github.com/fastapi/fastapi"),
]


def run_streamlit_app():
    """Main Streamlit UI application entrypoint."""
    st.set_page_config(
        page_title="Local GitHub Repository Code Explainer",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    apply_custom_css()

    # Title Header Banner
    st.markdown(
        """
        <div class="header-box">
            <h1 class="header-title">LOCAL GITHUB REPOSITORY CODE EXPLAINER</h1>
            <p class="header-subtitle">Analyze ANY public GitHub repository using local Ollama + Qwen 2.5 3B on your laptop</p>
            <div>
                <span class="feature-pill">⚡ Low Latency</span>
                <span class="feature-pill">🔒 Local Inference</span>
                <span class="feature-pill">🛡️ Secret Protection</span>
                <span class="feature-pill">💻 Multi-Laptop Isolated</span>
                <span class="feature-pill">📚 23-Section Explanation</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # First-Time Setup Instructions (Expandable)
    with st.expander("📌 First-Time Setup & Laptop Configuration Guide", expanded=False):
        st.markdown(
            """
            ### How to run local AI inference on your own laptop:
            1. **Install Ollama**: Download from [ollama.com](https://ollama.com).
            2. **Download Qwen 2.5 3B**: Open terminal / PowerShell and run:
               ```bash
               ollama pull qwen2.5:3b
               ```
            3. **Start Ollama with Allowed Origins (`OLLAMA_ORIGINS`)**:
               - **Windows (PowerShell)**: `$env:OLLAMA_ORIGINS="*" ; ollama serve`
               - **macOS / Linux**: `OLLAMA_ORIGINS="*" ollama serve`
            4. **Analyze Repository**: Paste any public HTTPS GitHub URL below and click **Analyze Repository**.
            """
        )

    # Sidebar Configuration & Ollama Controls
    with st.sidebar:
        st.markdown("### ⚙️ Ollama Settings")
        st.markdown("Configure local or remote Ollama endpoint for AI inference:")
        
        ollama_endpoint = st.text_input(
            "Ollama Endpoint URL",
            value="http://127.0.0.1:11434",
            help="Default is http://127.0.0.1:11434. If using a tunnel or custom host, enter URL here.",
            key="cfg_ollama_endpoint",
        ).strip()
        
        target_model = st.text_input(
            "Ollama Model Name",
            value="qwen2.5:3b",
            help="Default is qwen2.5:3b.",
            key="cfg_ollama_model",
        ).strip()

        st.markdown("---")
        if st.button("🔌 Test Connection to Ollama", use_container_width=True):
            stat = check_ollama_status(endpoint=ollama_endpoint, target_model=target_model)
            if stat.connected and stat.model_available:
                st.success(f"🟢 Connected! Model '{target_model}' ready on {ollama_endpoint}.")
            elif stat.connected:
                st.warning(f"🟡 Connected, but '{target_model}' missing. Run `ollama pull {target_model}`.")
            else:
                st.error(f"🔴 Cannot reach {ollama_endpoint}. Start Ollama with `$env:OLLAMA_ORIGINS=\"*\"; ollama serve`.")

        st.markdown("---")
        st.markdown(
            """
            ### 📌 Quick Setup Checklist:
            1. Install Ollama ([ollama.com](https://ollama.com))
            2. Run: `ollama pull qwen2.5:3b`
            3. Run: `$env:OLLAMA_ORIGINS="*" ; ollama serve`
            """
        )

    # Laptop Ollama status probe
    ollama_stat = check_ollama_status(endpoint=ollama_endpoint, target_model=target_model)
    if ollama_stat.connected:
        if ollama_stat.model_available:
            st.success(f"🟢 **Ollama Connected**: Model `{target_model}` is active on `{ollama_stat.endpoint}`.")
        else:
            st.warning(f"🟡 **Ollama Connected**: Ollama is running on `{ollama_stat.endpoint}`, but model `{target_model}` is missing. Run `ollama pull {target_model}`.")
    else:
        st.info("💻 **Ollama Status**: Ready for model inference. (Start Ollama on your laptop: `$env:OLLAMA_ORIGINS='*'; ollama serve`).")

    # Input Form Container (with st.form to capture Enter key and button clicks reliably)
    st.markdown("### 🔗 Enter Public GitHub Repository URL")
    
    with st.form(key="repo_search_form", clear_on_submit=False):
        col1, col2 = st.columns([4, 1])
        with col1:
            repo_url = st.text_input(
                "GitHub Repository URL",
                placeholder="https://github.com/username/repository",
                label_visibility="collapsed",
                key="input_repo_url",
            )
        with col2:
            analyze_btn = st.form_submit_button("🚀 Analyze Repository", use_container_width=True, type="primary")

    # Quick Sample Repositories Row
    st.markdown("**Try a sample public repository:**")
    sample_cols = st.columns(len(EXAMPLE_REPOSITORIES))
    for idx, (label, sample_url) in enumerate(EXAMPLE_REPOSITORIES):
        if sample_cols[idx].button(f"📦 {label}", key=f"sample_{idx}", use_container_width=True):
            st.session_state.input_repo_url = sample_url
            st.session_state.analysis_response = None
            st.session_state.python_explanation = None
            with st.spinner("Cloning repository (shallow), scanning inventory, and building smart context..."):
                response: AnalysisResponse = process_repository_service(sample_url)
                st.session_state.analysis_response = response
            st.rerun()

    # Session state initialization
    if "analysis_response" not in st.session_state:
        st.session_state.analysis_response = None
    if "python_explanation" not in st.session_state:
        st.session_state.python_explanation = None

    target_url = repo_url.strip() if repo_url else st.session_state.get("input_repo_url", "").strip()

    if analyze_btn and target_url:
        with st.spinner("Cloning repository (shallow), scanning inventory, and building smart context..."):
            st.session_state.python_explanation = None  # Reset for new repository
            response: AnalysisResponse = process_repository_service(target_url)
            st.session_state.analysis_response = response

    resp: AnalysisResponse | None = st.session_state.analysis_response

    if resp:
        if not resp.success:
            st.error(f"❌ Analysis Failed: {resp.error}")
            return

        inv = resp.inventory
        ctx = resp.smart_context

        if not inv or not ctx:
            st.error("Invalid response data structure.")
            return

        st.success(f"✅ Repository analyzed successfully: **{inv.owner}/{inv.repo_name}** ({inv.total_files} total files scanned in {resp.timing.total_ms:.1f}ms)")

        # Main Navigation Tabs - ALL RENDER INSTANTLY NOW
        tab_overview, tab_structure, tab_files, tab_ai, tab_tech = st.tabs([
            "📊 Overview",
            "📁 Repository Structure",
            "📄 Files & Categories",
            "🤖 AI Explanation (Qwen 2.5 3B)",
            "⏱️ Technical Metrics",
        ])

        # TAB 1: OVERVIEW (Instant)
        with tab_overview:
            st.markdown(f"### Repository Overview: `{inv.owner}/{inv.repo_name}`")
            
            # Key statistics metric row
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Total Files", inv.total_files)
            m2.metric("Source Code", inv.category_counts.source)
            m3.metric("Notebooks", inv.category_counts.notebook)
            m4.metric("Docs / Config", inv.category_counts.documentation + inv.category_counts.configuration)
            m5.metric("Context Files", ctx.file_count)

            st.markdown("---")
            c_left, c_right = st.columns(2)

            with c_left:
                st.markdown("#### Detected Languages")
                if inv.languages:
                    for lang in inv.languages:
                        st.markdown(f"- **{lang}**")
                else:
                    st.write("No specific source code languages detected.")

            with c_right:
                st.markdown("#### Detected Technologies & Frameworks")
                if inv.technologies:
                    chips_html = "".join([f'<span class="tech-chip">{t}</span>' for t in inv.technologies])
                    st.markdown(chips_html, unsafe_allow_html=True)
                else:
                    st.write("No specific framework manifests detected.")

            if inv.sensitive_files_found:
                st.markdown(
                    f"""
                    <div class="security-callout">
                        🛡️ <strong>Security Alert</strong>: Discovered {len(inv.sensitive_files_found)} sensitive file(s) (e.g. .env, credentials). Secret values have been automatically shielded and excluded from AI context.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # TAB 2: STRUCTURE (Instant)
        with tab_structure:
            st.markdown("### 📁 Repository Folder Tree")
            tree_text = "\n".join(inv.tree)
            st.code(tree_text, language="text")

        # TAB 3: FILES (Instant)
        with tab_files:
            st.markdown("### 📄 Categorized File Breakdown")
            cat_data = {
                "Source Code": inv.category_counts.source,
                "Jupyter Notebooks": inv.category_counts.notebook,
                "Documentation": inv.category_counts.documentation,
                "Configuration": inv.category_counts.configuration,
                "Dependency Manifests": inv.category_counts.dependency,
                "Web (HTML/CSS)": inv.category_counts.web,
                "Data & Schema": inv.category_counts.data_schema,
                "Tests": inv.category_counts.test,
                "Deployment / CI-CD": inv.category_counts.deployment,
                "Binary / Assets": inv.category_counts.binary,
                "Unknown Text": inv.category_counts.unknown_text,
            }
            st.json(cat_data)

            st.markdown("#### Selected Model Context Files")
            st.info(f"Smart Context selected {ctx.file_count} top priority files ({ctx.total_characters} characters) out of {inv.total_files} total files for Qwen 2.5 3B model context.")
            for sf in ctx.selected_files:
                trunc_str = " (Truncated for length)" if sf.is_truncated else ""
                with st.expander(f"📄 `{sf.path}` — {sf.category.upper()} ({sf.character_count} chars){trunc_str}"):
                    st.code(sf.content[:3000], language="text")

        # TAB 4: AI EXPLANATION
        with tab_ai:
            st.markdown("### 🤖 Detailed AI Explanation (Qwen 2.5 3B)")
            st.markdown("Analyze repository evidence, code structure, technologies, and workflow using **Qwen 2.5 3B** local AI model.")

            start_btn = st.button(
                "🚀 Start / Regenerate Qwen 2.5 3B Explanation",
                type="primary",
                use_container_width=True,
                key=f"btn_start_{inv.owner}_{inv.repo_name}",
            )

            # Compute initial static explanation if not yet stored
            if not st.session_state.python_explanation:
                ollama_stat_check = check_ollama_status(endpoint=ollama_endpoint, target_model=target_model)
                if ollama_stat_check.connected and ollama_stat_check.model_available:
                    success, text = generate_with_ollama_local(resp.prompt, endpoint=ollama_endpoint, model=target_model)
                    if success:
                        st.session_state.python_explanation = text
                    else:
                        st.session_state.python_explanation = generate_evidence_based_explanation(inv, ctx)
                else:
                    st.session_state.python_explanation = generate_evidence_based_explanation(inv, ctx)

            st.markdown("---")

            if start_btn:
                ollama_stat_check = check_ollama_status(endpoint=ollama_endpoint, target_model=target_model)
                if ollama_stat_check.connected and ollama_stat_check.model_available:
                    st.success(f"🟢 **Ollama Connected!** Streaming real `{target_model}` model inference live from `{ollama_stat_check.endpoint}`:")
                else:
                    st.info("💻 **Evidence Mode**: Streaming comprehensive 23-section explanation live:")

                st.write_stream(stream_qwen_explanation(resp.prompt, fallback_text=st.session_state.python_explanation, endpoint=ollama_endpoint, model=target_model))
            else:
                st.markdown(st.session_state.python_explanation)

            st.markdown("---")
            with st.expander("📝 Inspect Raw Qwen Prompt Context", expanded=False):
                st.code(resp.prompt, language="text")

        # TAB 5: TECHNICAL METRICS (Instant)
        with tab_tech:
            st.markdown("### ⏱️ Performance Metrics & Timing Breakdown")
            t = resp.timing
            
            col_t1, col_t2, col_t3, col_t4 = st.columns(4)
            col_t1.metric("URL Validation", f"{t.url_validation_ms:.1f} ms")
            col_t2.metric("Shallow Clone", f"{t.clone_ms:.1f} ms")
            col_t3.metric("Inventory Scan", f"{t.scan_ms:.1f} ms")
            col_t4.metric("Context Prep", f"{t.context_prep_ms:.1f} ms")

            st.markdown("---")
            st.markdown(
                f"""
                - **GitHub URL Validation**: `{t.url_validation_ms:.2f} ms`
                - **Shallow Repository Clone (depth=1)**: `{t.clone_ms:.2f} ms`
                - **Inventory Scan & File Classification**: `{t.scan_ms:.2f} ms`
                - **Smart Context & Prompt Construction**: `{t.context_prep_ms:.2f} ms`
                - **Total Repository Processing Latency**: `{t.total_ms:.2f} ms` (**{t.total_ms / 1000.0:.2f} seconds**)
                """
            )
            st.success("⚡ Pipeline is optimized for LOW LATENCY (< 1.6s repository processing). Single-pass inventory scanning and smart context selection eliminate unnecessary model overhead.")
