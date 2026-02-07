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
    <title>Lecture Study Guide Generator</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 2rem; }
      label { display: block; margin-top: 0.75rem; }
      input, select { padding: 0.5rem; width: 320px; }
      button { margin-top: 1rem; padding: 0.6rem 1rem; }
      .links a { display: block; margin-top: 0.5rem; }
      .status { margin-top: 1rem; color: #444; }
    </style>
  </head>
  <body>
    <h1>Lecture Study Guide Generator</h1>
    <form id="upload-form">
      <label>Lecture File (.pptx, .ppt, .pdf)</label>
      <input type="file" name="file" required />

      <label>Provider</label>
      <select name="provider">
        <option value="anthropic">anthropic</option>
        <option value="openai">openai</option>
      </select>

      <label>Model (optional)</label>
      <input type="text" name="model" placeholder="e.g. gpt-4o-mini" />

      <label>API Key (optional)</label>
      <input type="password" name="api_key" placeholder="uses env var if empty" />

      <label>Practice Questions</label>
      <input type="number" name="questions" value="20" min="1" />

      <label>Flashcards</label>
      <input type="number" name="flashcards" value="30" min="1" />

      <label>Formats (space-separated)</label>
      <input type="text" name="formats" placeholder="markdown json anki_txt anki_csv flashcards_md" />

      <button type="submit">Generate</button>
    </form>

    <div class="status" id="status"></div>
    <div class="links" id="links"></div>

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
