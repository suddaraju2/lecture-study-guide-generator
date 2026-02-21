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


def _svg_upload():
    return (
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='140'%3E"
        "%3Cdefs%3E%3ClinearGradient id='a' x1='0' y1='0' x2='1' y2='1'%3E"
        "%3Cstop offset='0%25' stop-color='%236366f1'/%3E%3Cstop offset='100%25' stop-color='%238b5cf6'/%3E%3C/linearGradient%3E%3C/defs%3E"
        "%3Crect x='20' y='50' width='120' height='80' rx='12' fill='%23eef2ff' stroke='url(%23a)' stroke-width='3'/%3E"
        "%3Cpath d='M50 70v20h30V70M50 95h30' stroke='%236366f1' stroke-width='2' fill='none'/%3E"
        "%3Ccircle cx='70' cy='35' r='15' fill='url(%23a)'/%3E"
        "%3Cpath d='M63 35l5 5 10-10' stroke='white' stroke-width='2' fill='none' stroke-linecap='round'/%3E"
        "%3C/svg%3E"
    )


def _svg_settings():
    return (
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='140'%3E"
        "%3Cdefs%3E%3ClinearGradient id='b' x1='0' y1='0' x2='1' y2='1'%3E"
        "%3Cstop offset='0%25' stop-color='%23f59e0b'/%3E%3Cstop offset='100%25' stop-color='%23ef4444'/%3E%3C/linearGradient%3E%3C/defs%3E"
        "%3Ccircle cx='80' cy='70' r='45' fill='%23fffbeb' stroke='url(%23b)' stroke-width='3'/%3E"
        "%3Ccircle cx='80' cy='45' r='4' fill='%23f59e0b'/%3E"
        "%3Cline x1='80' y1='55' x2='80' y2='75' stroke='%23f59e0b' stroke-width='3'/%3E"
        "%3Ccircle cx='95' cy='70' r='4' fill='%23f59e0b'/%3E"
        "%3Cline x1='85' y1='70' x2='105' y2='70' stroke='%23f59e0b' stroke-width='3'/%3E"
        "%3Ccircle cx='80' cy='95' r='4' fill='%23f59e0b'/%3E"
        "%3C/svg%3E"
    )


def _svg_generate():
    return (
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='140'%3E"
        "%3Cdefs%3E%3ClinearGradient id='c' x1='0' y1='0' x2='0' y2='1'%3E"
        "%3Cstop offset='0%25' stop-color='%2310b981'/%3E%3Cstop offset='100%25' stop-color='%2306b6d4'/%3E%3C/linearGradient%3E%3C/defs%3E"
        "%3Crect x='30' y='50' width='100' height='60' rx='12' fill='%23ecfdf5' stroke='url(%23c)' stroke-width='3'/%3E"
        "%3Cpath d='M45 75l15 15 35-35' stroke='%2310b981' stroke-width='4' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E"
        "%3Ccircle cx='80' cy='35' r='18' fill='url(%23c)' opacity='0.3'/%3E"
        "%3Cpath d='M80 25v20M80 45v10M75 55l10 10 10-10' stroke='%2310b981' stroke-width='2' fill='none'/%3E"
        "%3C/svg%3E"
    )


def _svg_download():
    return (
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='140'%3E"
        "%3Cdefs%3E%3ClinearGradient id='d' x1='0' y1='0' x2='1' y2='0'%3E"
        "%3Cstop offset='0%25' stop-color='%233b82f6'/%3E%3Cstop offset='100%25' stop-color='%238b5cf6'/%3E%3C/linearGradient%3E%3C/defs%3E"
        "%3Crect x='35' y='55' width='90' height='60' rx='10' fill='%23eff6ff' stroke='url(%23d)' stroke-width='3'/%3E"
        "%3Cpath d='M55 75l15-15 15 15 15-15' stroke='%233b82f6' stroke-width='2' fill='none' stroke-linecap='round'/%3E"
        "%3Cline x1='80' y1='60' x2='80' y2='95' stroke='%233b82f6' stroke-width='2'/%3E"
        "%3Cpath d='M65 95h30' stroke='%233b82f6' stroke-width='2' stroke-linecap='round'/%3E"
        "%3Ccircle cx='80' cy='35' r='12' fill='url(%23d)'/%3E"
        "%3Cpath d='M76 35l8 8 8-8' stroke='white' stroke-width='2' fill='none'/%3E"
        "%3C/svg%3E"
    )


def _svg_summary():
    return (
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='100'%3E"
        "%3Crect x='10' y='20' width='100' height='70' rx='8' fill='%236366f1' opacity='0.2'/%3E"
        "%3Crect x='15' y='25' width='70' height='6' rx='3' fill='%236366f1'/%3E"
        "%3Crect x='15' y='38' width='85' height='5' rx='2' fill='%239ca3af'/%3E"
        "%3Crect x='15' y='48' width='80' height='5' rx='2' fill='%239ca3af'/%3E"
        "%3Crect x='15' y='58' width='60' height='5' rx='2' fill='%239ca3af'/%3E"
        "%3C/svg%3E"
    )


def _svg_questions():
    return (
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='100'%3E"
        "%3Ccircle cx='50' cy='50' r='30' fill='%23f59e0b' opacity='0.2'/%3E"
        "%3Cpath d='M40 40h20v10l-8 8v4h-4v-6l8-8V40z' fill='%23f59e0b'/%3E"
        "%3Ccircle cx='40' cy='55' r='3' fill='%23f59e0b'/%3E"
        "%3C/svg%3E"
    )


def _svg_flashcards():
    return (
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='100'%3E"
        "%3Crect x='25' y='15' width='70' height='55' rx='6' fill='white' stroke='%2310b981' stroke-width='2'/%3E"
        "%3Crect x='30' y='20' width='60' height='8' rx='2' fill='%2310b981'/%3E"
        "%3Crect x='35' y='75' width='60' height='50' rx='6' fill='white' stroke='%2310b981' stroke-width='2' transform='rotate(-5 65 100)'/%3E"
        "%3Crect x='40' y='80' width='50' height='6' rx='2' fill='%2310b981' transform='rotate(-5 65 83)'/%3E"
        "%3C/svg%3E"
    )


def _svg_concept():
    return (
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='100'%3E"
        "%3Cellipse cx='60' cy='50' rx='35' ry='25' fill='%238b5cf6' opacity='0.2'/%3E"
        "%3Ccircle cx='45' cy='40' r='12' fill='%238b5cf6'/%3E"
        "%3Ccircle cx='75' cy='45' r='10' fill='%238b5cf6'/%3E"
        "%3Ccircle cx='60' cy='65' r='8' fill='%238b5cf6'/%3E"
        "%3Cpath d='M50 45 L68 52 M82 48 L70 58 M55 58 L62 62' stroke='%238b5cf6' stroke-width='2' fill='none'/%3E"
        "%3C/svg%3E"
    )


def _svg_hero():
    return (
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='640' height='400' viewBox='0 0 640 400'%3E"
        "%3Cdefs%3E"
        "%3ClinearGradient id='g1' x1='0' y1='0' x2='1' y2='1'%3E%3Cstop offset='0%25' stop-color='%236366f1'/%3E%3Cstop offset='100%25' stop-color='%238b5cf6'/%3E%3C/linearGradient%3E"
        "%3ClinearGradient id='g2' x1='0' y1='0' x2='0' y2='1'%3E%3Cstop offset='0%25' stop-color='%23c7d2fe'/%3E%3Cstop offset='100%25' stop-color='%23e9d5ff'/%3E%3C/linearGradient%3E"
        "%3C/defs%3E"
        "%3Crect width='640' height='400' rx='32' fill='%23ffffff'/%3E"
        "%3Crect x='24' y='24' width='592' height='140' rx='20' fill='url(%23g1)'/%3E"
        "%3Crect x='44' y='44' width='120' height='100' rx='16' fill='rgba(255,255,255,0.3)'/%3E"
        "%3Crect x='54' y='54' width='60' height='8' rx='4' fill='white'/%3E"
        "%3Crect x='54' y='70' width='90' height='6' rx='3' fill='rgba(255,255,255,0.8)'/%3E"
        "%3Crect x='54' y='82' width='70' height='6' rx='3' fill='rgba(255,255,255,0.8)'/%3E"
        "%3Crect x='180' y='50' width='140' height='90' rx='14' fill='%23fef3c7' stroke='%23f59e0b' stroke-width='2'/%3E"
        "%3Ctext x='250' y='95' text-anchor='middle' font-size='32' fill='%23f59e0b' font-weight='bold'%3E?%3C/text%3E"
        "%3Crect x='340' y='50' width='130' height='90' rx='14' fill='%23d1fae5' stroke='%2310b981' stroke-width='2'/%3E"
        "%3Cpath d='M385 95 l25 20 40-45' stroke='%2310b981' stroke-width='6' fill='none' stroke-linecap='round'/%3E"
        "%3Crect x='490' y='50' width='110' height='90' rx='14' fill='%23dbeafe' stroke='%233b82f6' stroke-width='2'/%3E"
        "%3Crect x='505' y='70' width='80' height='50' rx='8' fill='%233b82f6' opacity='0.3'/%3E"
        "%3Crect x='24' y='180' width='280' height='16' rx='8' fill='%23e2e8f0'/%3E"
        "%3Crect x='24' y='210' width='340' height='14' rx='7' fill='%23e2e8f0'/%3E"
        "%3Crect x='24' y='240' width='220' height='14' rx='7' fill='%23e2e8f0'/%3E"
        "%3Crect x='24' y='280' width='180' height='90' rx='16' fill='url(%23g2)'/%3E"
        "%3Crect x='220' y='280' width='160' height='90' rx='16' fill='%23ecfdf5'/%3E"
        "%3Crect x='400' y='280' width='200' height='90' rx='16' fill='%23fef3c7'/%3E"
        "%3C/svg%3E"
    )


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Lecture Study Guide Generator</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap" rel="stylesheet" />
    <style>
      :root {{
        --bg: #0f0f23;
        --card: #1a1a2e;
        --card-hover: #252542;
        --text: #f1f5f9;
        --muted: #94a3b8;
        --primary: #6366f1;
        --primary-light: #818cf8;
        --accent: #8b5cf6;
        --success: #10b981;
        --warning: #f59e0b;
        --border: #334155;
        --gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
        --shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
        --glow: 0 0 40px rgba(99, 102, 241, 0.2);
      }}
      * {{ box-sizing: border-box; }}
      body {{
        font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
        margin: 0;
        color: var(--text);
        background: var(--bg);
        background-image: radial-gradient(ellipse 80% 50% at 50% -20%, rgba(99,102,241,0.25), transparent),
                          radial-gradient(ellipse 60% 40% at 80% 50%, rgba(139,92,246,0.15), transparent);
      }}
      a {{ color: var(--primary-light); text-decoration: none; }}
      a:hover {{ text-decoration: underline; }}
      .container {{ max-width: 1200px; margin: 0 auto; padding: 2.5rem 1.5rem 5rem; }}
      .top-bar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 3rem;
      }}
      .badge {{
        font-size: 0.8rem;
        background: rgba(99,102,241,0.2);
        color: #a5b4fc;
        padding: 0.4rem 1rem;
        border-radius: 999px;
        font-weight: 600;
        border: 1px solid rgba(99,102,241,0.3);
      }}
      .hero {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 3rem;
        align-items: center;
        margin-bottom: 4rem;
      }}
      @media (max-width: 768px) {{ .hero {{ grid-template-columns: 1fr; }} }}
      .hero h1 {{
        font-size: clamp(2.25rem, 4vw, 3.5rem);
        margin: 0 0 1rem;
        font-weight: 800;
        line-height: 1.2;
        background: var(--gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }}
      .hero p {{ color: var(--muted); margin: 0 0 1.5rem; font-size: 1.1rem; line-height: 1.7; }}
      .hero-img {{
        width: 100%;
        border-radius: 24px;
        box-shadow: var(--glow);
        border: 1px solid rgba(99,102,241,0.2);
      }}
      .section-title {{
        font-size: 1.75rem;
        font-weight: 700;
        margin: 0 0 0.5rem;
        text-align: center;
      }}
      .section-sub {{
        color: var(--muted);
        text-align: center;
        margin-bottom: 2.5rem;
      }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin-bottom: 4rem;
      }}
      @media (max-width: 900px) {{ .grid {{ grid-template-columns: repeat(2, 1fr); }} }}
      @media (max-width: 500px) {{ .grid {{ grid-template-columns: 1fr; }} }}
      .card {{
        background: var(--card);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid var(--border);
        transition: all 0.3s ease;
      }}
      .card:hover {{ background: var(--card-hover); border-color: var(--primary); transform: translateY(-4px); box-shadow: var(--glow); }}
      .card-img {{ width: 80px; height: 70px; margin-bottom: 1rem; object-fit: contain; }}
      .card h3 {{ margin: 0 0 0.5rem; font-size: 1.1rem; font-weight: 700; }}
      .card p {{ margin: 0; color: var(--muted); font-size: 0.9rem; line-height: 1.5; }}
      .tutorial {{
        background: var(--card);
        border-radius: 24px;
        padding: 2.5rem;
        margin-bottom: 4rem;
        border: 1px solid var(--border);
      }}
      .tutorial-steps {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin-top: 2rem;
      }}
      @media (max-width: 900px) {{ .tutorial-steps {{ grid-template-columns: repeat(2, 1fr); }} }}
      @media (max-width: 500px) {{ .tutorial-steps {{ grid-template-columns: 1fr; }} }}
      .step {{
        text-align: center;
        padding: 1.5rem;
        background: rgba(99,102,241,0.05);
        border-radius: 16px;
        border: 1px solid rgba(99,102,241,0.2);
      }}
      .step-num {{
        display: inline-block;
        width: 36px;
        height: 36px;
        line-height: 36px;
        background: var(--gradient);
        border-radius: 50%;
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 1rem;
      }}
      .step-img {{ width: 120px; height: 100px; margin: 0 auto 1rem; display: block; object-fit: contain; }}
      .step h4 {{ margin: 0 0 0.5rem; font-size: 1rem; }}
      .step p {{ margin: 0; color: var(--muted); font-size: 0.85rem; line-height: 1.5; }}
      .form-card {{
        background: var(--card);
        padding: 2.5rem;
        border-radius: 24px;
        border: 1px solid var(--border);
        box-shadow: var(--shadow);
      }}
      .form-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.25rem 1.5rem;
      }}
      label {{ display: block; font-weight: 600; margin-bottom: 0.5rem; font-size: 0.95rem; }}
      input, select {{
        width: 100%;
        padding: 0.75rem 1rem;
        border-radius: 12px;
        border: 1px solid var(--border);
        background: var(--bg);
        color: var(--text);
        font-size: 0.95rem;
      }}
      input::file-selector-button {{
        padding: 0.4rem 0.8rem;
        border-radius: 8px;
        border: 1px solid var(--primary);
        background: rgba(99,102,241,0.2);
        color: var(--primary-light);
        cursor: pointer;
      }}
      .hint {{ color: var(--muted); font-size: 0.8rem; margin-top: 0.35rem; }}
      .actions {{ display: flex; flex-wrap: wrap; gap: 1rem; align-items: center; margin-top: 1.5rem; }}
      button {{
        background: var(--gradient);
        color: #fff;
        border: none;
        padding: 0.9rem 2rem;
        border-radius: 14px;
        font-weight: 700;
        cursor: pointer;
        font-size: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
      }}
      button:hover {{ transform: translateY(-2px); box-shadow: var(--glow); }}
      .status {{ margin-top: 1rem; color: var(--success); font-weight: 600; }}
      .links a {{
        display: inline-block;
        margin: 0.5rem 1rem 0 0;
        font-weight: 600;
        color: var(--primary-light);
      }}
      .links a:hover {{ text-decoration: underline; }}
      footer {{ margin-top: 3rem; color: var(--muted); text-align: center; font-size: 0.9rem; }}
    </style>
  </head>
  <body>
    <div class="container">
      <div class="top-bar">
        <strong style="font-size: 1.2rem;">Lecture Study Guide Generator</strong>
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
            <a href="#tutorial" class="badge">How to use</a>
            <span class="hint">Works best with clean lecture slides</span>
          </div>
        </div>
        <img class="hero-img" alt="Study guide preview" src="{_svg_hero()}" />
      </section>

      <section class="grid">
        <div class="card">
          <img class="card-img" alt="Summary" src="{_svg_summary()}" />
          <h3>Structured summaries</h3>
          <p>Clean, organized outlines with key concepts and definitions.</p>
        </div>
        <div class="card">
          <img class="card-img" alt="Questions" src="{_svg_questions()}" />
          <h3>Practice questions</h3>
          <p>MCQ, short answer, true/false, and essay-style prompts.</p>
        </div>
        <div class="card">
          <img class="card-img" alt="Flashcards" src="{_svg_flashcards()}" />
          <h3>Flashcards</h3>
          <p>Anki-ready exports for fast review and spaced repetition.</p>
        </div>
        <div class="card">
          <img class="card-img" alt="Concept maps" src="{_svg_concept()}" />
          <h3>Concept maps</h3>
          <p>Visualize relationships with auto-generated diagrams.</p>
        </div>
      </section>

      <section id="tutorial" class="tutorial">
        <h2 class="section-title">How to use this tool</h2>
        <p class="section-sub">Follow these 4 simple steps to generate your study materials</p>
        <div class="tutorial-steps">
          <div class="step">
            <span class="step-num">1</span>
            <img class="step-img" alt="Upload" src="{_svg_upload()}" />
            <h4>Upload your lecture</h4>
            <p>Choose a .pptx, .ppt, or .pdf file from your computer.</p>
          </div>
          <div class="step">
            <span class="step-num">2</span>
            <img class="step-img" alt="Settings" src="{_svg_settings()}" />
            <h4>Choose your options</h4>
            <p>Pick AI provider, number of questions & flashcards, and formats.</p>
          </div>
          <div class="step">
            <span class="step-num">3</span>
            <img class="step-img" alt="Generate" src="{_svg_generate()}" />
            <h4>Click Generate</h4>
            <p>Wait a few minutes while AI analyzes and creates your materials.</p>
          </div>
          <div class="step">
            <span class="step-num">4</span>
            <img class="step-img" alt="Download" src="{_svg_download()}" />
            <h4>Download your pack</h4>
            <p>Get markdown, JSON, Anki decks, flashcards, and concept maps.</p>
          </div>
        </div>
      </section>

      <section id="generator" class="form-card">
        <h2 class="section-title">Generate your study pack</h2>
        <p class="section-sub">Upload a lecture file and customize your outputs</p>
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
