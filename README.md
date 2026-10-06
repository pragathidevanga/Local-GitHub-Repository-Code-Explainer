# Local GitHub Repository Code Explainer

An AI application built with **Streamlit**, **FastAPI**, **GitPython**, **Ollama**, and **Qwen 2.5 3B** that accepts ANY public HTTPS GitHub repository URL and generates a detailed, evidence-based, beginner-friendly explanation of the repository.

---

## 🌟 Key Features & Highlights

- **Multi-Laptop Architecture**: Streamlit Cloud hosts the frontend and repository analysis engine, while GenAI inference occurs directly on **each end-user's own laptop** using their local Ollama instance (`http://127.0.0.1:11434`).
- **Supports ANY Public GitHub Repository**: Accepts public repositories from any owner, language, framework, or project structure.
- **Dynamic File Categorization**: Scans complete repository inventory across 11 distinct categories (Source code, Notebooks `.ipynb`, Documentation, Configuration, Dependencies, Web, Data/Schema, Tests, Deployment, Binary assets, Unknown text).
- **README-Only & Docs-Only Support**: Seamlessly analyzes documentation-only, schema-only, or notebook-only repositories.
- **Smart Context & Low Latency**: Optimized single-pass inventory scanner and dynamic priority scoring engine limits LLM prompt context to ~38,000 characters and top relevant files to minimize generation latency.
- **Strict Evidence-Based Output**: Generates detailed explanations formatted under 23 explicit structural sections. Never invents unsupported frameworks or APIs.
- **Sensitive File Shielding**: Automatically identifies security-sensitive files (`.env`, private keys, secrets) and shields credentials from being sent to Ollama or displayed in UI.
- **FastAPI & Streamlit Combined**: Full FastAPI application backend with Swagger documentation (`/docs`) and a clean Streamlit user interface.

---

## 🏗️ Architecture & Multi-Laptop Pipeline

```
                               STREAMLIT CLOUD (Shared Host)
                                    ┌──────────────────┐
                                    │      app.py      │
                                    └────────┬─────────┘
                                             │
                                   User Inputs GitHub URL
                                             │
                                             ▼
                                  ┌────────────────────┐
                                  │   GitPython Repo   │
                                  │  (Shallow depth=1) │
                                  └──────────┬─────────┘
                                             │
                                             ▼
                                  ┌────────────────────┐
                                  │ Single-Pass Inventory│
                                  │  & Category Scanner│
                                  └──────────┬─────────┘
                                             │
                                             ▼
                                  ┌────────────────────┐
                                  │ Smart Context &    │
                                  │ Qwen Prompt Builder│
                                  └──────────┬─────────┘
                                             │
                                   Passes Prompt to Browser
                                             │
┌────────────────────────────────────────────┼────────────────────────────────────────────┐
│ LAPTOP A / LAPTOP B / LAPTOP C             │                                            │
│                                            ▼                                            │
│                                ┌──────────────────────┐                                 │
│                                │ Browser Custom       │                                 │
│                                │ JavaScript Component │                                 │
│                                └──────────┬───────────┘                                 │
│                                           │                                             │
│                                 Fetch HTTP / POST Request                               │
│                                           │                                             │
│                                           ▼                                             │
│                                ┌──────────────────────┐                                 │
│                                │ Local Laptop Ollama  │                                 │
│                                │ (127.0.0.1:11434)    │                                 │
│                                └──────────┬───────────┘                                 │
│                                           │                                             │
│                                           ▼                                             │
│                                ┌──────────────────────┐                                 │
│                                │ Qwen 2.5 3B Model    │                                 │
│                                └──────────┬───────────┘                                 │
│                                           │                                             │
│                                Streams Explanation Back                                 │
└───────────────────────────────────────────┼────────────────────────────────────────────┘
                                            ▼
                                ┌──────────────────────┐
                                │ Streamlit UI Display │
                                └──────────────────────┘
```

---

## 💻 First-Time Setup Instructions

### 1. Install Ollama
Download and install Ollama for your operating system from [ollama.com](https://ollama.com).

### 2. Pull Qwen 2.5 3B Model
Open your terminal (macOS/Linux) or PowerShell (Windows) and run:
```bash
ollama pull qwen2.5:3b
```

### 3. Start Ollama with Browser Origin Allowed (`OLLAMA_ORIGINS`)
Because the Streamlit app is hosted remotely while Ollama runs locally on your laptop, configure browser origin permissions:

- **Windows (PowerShell)**:
  ```powershell
  $env:OLLAMA_ORIGINS="*"
  ollama serve
  ```

- **macOS / Linux**:
  ```bash
  OLLAMA_ORIGINS="*" ollama serve
  ```

---

## 🚀 Running the Application

### Option A: Run Streamlit Frontend
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### Option B: Run FastAPI Backend
```bash
python -m uvicorn backend.main:app --reload --port 8000
```
- API Health Check: `http://localhost:8000/api/health`
- Swagger Documentation: `http://localhost:8000/docs`

---

## 🧪 Running Tests

Execute the full automated test suite:
```bash
python -m pytest -v
```

Verify clean Python compilation:
```bash
python -m compileall .
```

---

## 📊 Detailed Explanation Format

The Qwen 2.5 3B model generates detailed explanations structured into 23 explicit numbered sections:
1. **Project Overview**
2. **What the Project Does**
3. **Main Features**
4. **Repository Structure**
5. **Important Files**
6. **Main Technologies**
7. **Application Architecture**
8. **How the Project Works**
9. **Step-by-Step Workflow**
10. **Data Flow**
11. **Important Classes**
12. **Important Functions**
13. **Important Modules**
14. **Dependencies**
15. **Configuration**
16. **Database / Storage**
17. **APIs / External Services**
18. **Notebook Analysis**
19. **Testing**
20. **Running / Deployment**
21. **End-to-End Workflow**
22. **Key Takeaways**
23. **Limitations / Unknown Information**

---

## ❓ Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **Ollama Disconnected** | Ensure Ollama is running (`ollama serve`). Check if `http://127.0.0.1:11434` responds. |
| **Model Missing Error** | Run `ollama pull qwen2.5:3b` in terminal/PowerShell. |
| **CORS / Browser Blocked** | Set `OLLAMA_ORIGINS="*"` when launching `ollama serve`. |
| **Git Clone Failed** | Ensure the repository URL is public and HTTPS format (`https://github.com/owner/repo`). |

---

## 📜 License
MIT License. Created for the Mini Assessment.
