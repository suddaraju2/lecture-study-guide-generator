"""
FastAPI web application for the Lecture Study Guide Generator.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from lecture_study_guide import StudyGuideGenerator


app = FastAPI(title="Lecture Study Guide Generator")

BASE_OUTPUT_DIR = Path("web_output").resolve()
ALLOWED_EXTENSIONS = {".pptx", ".ppt", ".pdf"}


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Lecture Study Guide Generator</title>
    <style>
      :root {
        color-scheme: light;
        --bg: #f6f7fb;
        --card: #ffffff;
        --text: #0f172a;
        --muted: #64748b;
        --primary: #3b82f6;
        --primary-600: #2563eb;
        --border: #e2e8f0;
        --shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
      }
      * { box-sizing: border-box; }
      body {
        font-family: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif;
        margin: 0;
        color: var(--text);
        background: radial-gradient(circle at top, #eef2ff 0%, var(--bg) 45%);
      }
      a { color: var(--primary); text-decoration: none; }
      a:hover { text-decoration: underline; }
      .container {
        max-width: 1100px;
        margin: 0 auto;
        padding: 2.5rem 1.5rem 4rem;
      }
      .top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
      }
      .badge {
        font-size: 0.8rem;
        background: #e0e7ff;
        color: #3730a3;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        font-weight: 600;
      }
      .hero {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 2rem;
        align-items: center;
      }
      .hero h1 { font-size: clamp(2rem, 3vw, 3rem); margin: 0 0 0.75rem; }
      .hero p { color: var(--muted); margin: 0 0 1.5rem; line-height: 1.6; }
      .hero-card {
        background: var(--card);
        border-radius: 24px;
        padding: 2rem;
        box-shadow: var(--shadow);
        border: 1px solid rgba(226, 232, 240, 0.7);
      }
      .hero-img {
        width: 100%;
        border-radius: 20px;
        box-shadow: 0 16px 35px rgba(37, 99, 235, 0.2);
      }
      .grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1.5rem;
        margin-top: 2.5rem;
      }
      .card {
        background: var(--card);
        border-radius: 18px;
        padding: 1.25rem;
        border: 1px solid var(--border);
        box-shadow: 0 10px 25px rgba(15, 23, 42, 0.05);
      }
      .card h3 { margin: 0.5rem 0 0.5rem; font-size: 1.05rem; }
      .card p { margin: 0; color: var(--muted); font-size: 0.95rem; line-height: 1.5; }
      .form-card {
        margin-top: 2.5rem;
        background: var(--card);
        padding: 2rem;
        border-radius: 24px;
        box-shadow: var(--shadow);
      }
      .form-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1rem 1.5rem;
      }
      label { display: block; font-weight: 600; margin-bottom: 0.35rem; }
      input, select {
        width: 100%;
        padding: 0.65rem 0.75rem;
        border-radius: 12px;
        border: 1px solid var(--border);
        font-size: 0.95rem;
      }
      input[type="file"] { padding: 0.55rem; }
      .hint { color: var(--muted); font-size: 0.85rem; margin-top: 0.35rem; }
      .actions {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        align-items: center;
        margin-top: 1.5rem;
      }
      button {
        background: var(--primary);
        color: #fff;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: transform 0.2s ease, background 0.2s ease;
      }
      button:hover { background: var(--primary-600); transform: translateY(-1px); }
      .status { margin-top: 1rem; color: var(--muted); font-weight: 500; }
      .links a {
        display: block;
        margin-top: 0.5rem;
        font-weight: 600;
      }
      footer {
        margin-top: 3rem;
        color: var(--muted);
        text-align: center;
        font-size: 0.85rem;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="top-bar">
        <strong>Lecture Study Guide Generator</strong>
        <span class="badge">Powered by Claude / OpenAI</span>
      </div>

      <section class="hero">
        <div>
          <h1>Turn lecture slides into a complete study pack.</h1>
          <p>
            Upload your PDF or PowerPoint. Get a structured study guide, practice
            questions, flashcards, and concept maps in minutes.
          </p>
          <div class="actions">
            <a href="#generator" class="badge">Try it now</a>
            <span class="hint">Works best with clean lecture slides</span>
          </div>
        </div>
        <img
          class="hero-img"
          alt="Study guide preview"
          src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='640' height='420'><defs><linearGradient id='g' x1='0' y1='0' x2='1' y2='1'><stop offset='0%' stop-color='%233b82f6'/><stop offset='100%' stop-color='%23818cf8'/></linearGradient></defs><rect width='640' height='420' rx='28' fill='%23ffffff'/><rect x='28' y='28' width='584' height='120' rx='18' fill='url(%23g)'/><rect x='28' y='170' width='350' height='18' rx='9' fill='%23e2e8f0'/><rect x='28' y='205' width='420' height='16' rx='8' fill='%23e2e8f0'/><rect x='28' y='240' width='260' height='16' rx='8' fill='%23e2e8f0'/><rect x='28' y='285' width='200' height='90' rx='16' fill='%23eef2ff'/><rect x='250' y='285' width='180' height='90' rx='16' fill='%23f1f5f9'/><rect x='450' y='285' width='140' height='90' rx='16' fill='%23dbeafe'/></svg>"
        />
      </section>

      <section class="grid">
        <div class="card">
          <h3>Structured summaries</h3>
          <p>Clean, organized outlines with key concepts and definitions.</p>
        </div>
        <div class="card">
          <h3>Practice questions</h3>
          <p>MCQ, short answer, true/false, and essay-style prompts.</p>
        </div>
        <div class="card">
          <h3>Flashcards</h3>
          <p>Anki-ready exports for fast review and spaced repetition.</p>
        </div>
        <div class="card">
          <h3>Concept maps</h3>
          <p>Visualize relationships with auto-generated diagrams.</p>
        </div>
      </section>

      <section id="generator" class="form-card">
        <h2>Generate your study pack</h2>
        <p class="hint">Upload a lecture file and customize your outputs.</p>
        <form id="upload-form">
          <div class="form-grid">
            <div>
              <label>Lecture File</label>
              <input type="file" name="file" required />
              <div class="hint">Supported: .pptx, .ppt, .pdf</div>
            </div>
            <div>
              <label>Provider</label>
              <select name="provider">
                <option value="anthropic">anthropic</option>
                <option value="openai">openai</option>
              </select>
              <div class="hint">Uses your configured API key</div>
            </div>
            <div>
              <label>Model (optional)</label>
              <input type="text" name="model" placeholder="e.g. gpt-4o-mini" />
            </div>
            <div>
              <label>API Key (optional)</label>
              <input type="password" name="api_key" placeholder="uses env var if empty" />
            </div>
            <div>
              <label>Practice Questions</label>
              <input type="number" name="questions" value="20" min="1" />
            </div>
            <div>
              <label>Flashcards</label>
              <input type="number" name="flashcards" value="30" min="1" />
            </div>
            <div>
              <label>Formats</label>
              <input type="text" name="formats" placeholder="markdown json anki_txt anki_csv flashcards_md" />
              <div class="hint">Space-separated (leave blank for all)</div>
            </div>
          </div>
          <div class="actions">
            <button type="submit">Generate study pack</button>
            <span class="hint">Processing may take a few minutes.</span>
          </div>
        </form>
        <div class="status" id="status"></div>
        <div class="links" id="links"></div>
      </section>

      <footer>
        Tip: For faster results, upload slides with clear titles and minimal animations.
      </footer>
    </div>

    <script>
      const form = document.getElementById("upload-form");
      const statusEl = document.getElementById("status");
      const linksEl = document.getElementById("links");

      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        statusEl.textContent = "Generating... this may take a few minutes.";
        linksEl.innerHTML = "";

        const formData = new FormData(form);
        const res = await fetch("/api/generate", { method: "POST", body: formData });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          statusEl.textContent = err.detail || "Generation failed.";
          return;
        }
        const data = await res.json();
        statusEl.textContent = `Done. Job ID: ${data.job_id}`;
        data.outputs.forEach((item) => {
          const a = document.createElement("a");
          a.href = item.url;
          a.textContent = `${item.format}: ${item.filename}`;
          a.target = "_blank";
          linksEl.appendChild(a);
        });
      });
    </script>
  </body>
</html>
"""


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/generate")
async def generate(
    file: UploadFile = File(...),
    questions: int = Form(20),
    flashcards: int = Form(30),
    provider: str = Form("anthropic"),
    model: str | None = Form(None),
    api_key: str | None = Form(None),
    formats: str | None = Form(None),
) -> JSONResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing file.")

    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Use .pptx, .ppt, or .pdf.",
        )

    job_id = str(uuid4())
    job_dir = BASE_OUTPUT_DIR / job_id
    upload_path = job_dir / file.filename
    job_dir.mkdir(parents=True, exist_ok=True)

    content = await file.read()
    upload_path.write_bytes(content)

    generator = StudyGuideGenerator(api_key=api_key, provider=provider, model=model)

    def run_generation():
        study_guide = generator.generate(
            upload_path,
            num_questions=questions,
            num_flashcards=flashcards,
        )
        formats_list = formats.split() if formats else None
        outputs = generator.export_all(study_guide, job_dir, formats=formats_list)
        return outputs

    outputs = await asyncio.to_thread(run_generation)

    response_outputs = [
        {
            "format": fmt,
            "filename": path.name,
            "url": f"/api/output/{job_id}/{path.name}",
        }
        for fmt, path in outputs.items()
    ]

    return JSONResponse(
        {
            "job_id": job_id,
            "outputs": response_outputs,
        }
    )


@app.get("/api/output/{job_id}/{filename}")
def download(job_id: str, filename: str) -> FileResponse:
    job_dir = (BASE_OUTPUT_DIR / job_id).resolve()
    file_path = (job_dir / filename).resolve()

    if not str(file_path).startswith(str(job_dir)):
        raise HTTPException(status_code=400, detail="Invalid file path.")

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found.")

    return FileResponse(file_path)
