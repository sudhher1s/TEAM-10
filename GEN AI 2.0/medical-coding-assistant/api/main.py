from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse
from starlette.requests import Request
from starlette.routing import Route
import os
from src.predict import AdvancedPredictor, Predictor

# Use AdvancedPredictor (AI-powered) if dependencies available, else fallback
try:
    print("🚀 Initializing AI-Powered Predictor...")
    predictor = AdvancedPredictor(enable_llm=bool(os.getenv("OPENAI_API_KEY")))
    predictor.load()
    AI_MODE = True
except Exception as e:
    print(f"⚠ AI mode unavailable: {e}")
    print("Using Legacy Predictor...")
    predictor = Predictor()
    predictor.load()
    AI_MODE = False




async def predict(request: Request):
    try:
        data = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)
    note_text = str(data.get("note_text", "")).strip()
    try:
        top_k = int(data.get("top_k", 5))
    except Exception:
        top_k = 5
    
    # Get method for AI mode
    method = str(data.get("method", "ensemble")).lower()
    if method not in ["ensemble", "llm", "retrieval", "classifier"]:
        method = "ensemble"
    
    if not note_text:
        return JSONResponse({"error": "note_text is required"}, status_code=400)
    
    # Use appropriate method
    if AI_MODE:
        result = predictor.predict(note_text, top_k=top_k, method=method)
    else:
        result = predictor.predict(note_text, top_k=top_k)
    
    return JSONResponse(result)


async def index(request: Request):
    # Enhanced UI with evidence highlighting, prediction grid, and raw JSON toggle
    html = r"""
        <!doctype html>
        <html lang="en">
            <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title>Medical Coding Assistant</title>
                <style>
                    :root {
                        --bg: #0f1115; --panel: #141821; --muted: #9aa4b2; --text: #e6edf3;
                        --accent: #3b82f6; --accent-2: #10b981; --chip: #1f2937; --danger: #ef4444;
                    }
                    * { box-sizing: border-box; }
                    body { margin: 0; font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, sans-serif; color: var(--text); background: var(--bg); }
                    .container { max-width: 1100px; margin: 2rem auto; padding: 0 1.2rem; }
                    header { display: flex; align-items: baseline; gap: .75rem; margin-bottom: 1rem; }
                    h1 { font-size: 1.75rem; margin: 0; }
                    .subtitle { color: var(--muted); }
                    .card { background: var(--panel); border: 1px solid #252b36; border-radius: .75rem; padding: 1rem; box-shadow: 0 1px 0 rgba(255,255,255,0.04) inset; }
                    .row { display: grid; grid-template-columns: 1fr 120px; gap: .75rem; }
                    .row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: .9rem; margin-top: 1rem; }
                    label { display: block; font-size: .9rem; color: var(--muted); margin-bottom: .4rem; }
                    input[type=number] { width: 100%; background: #0c0f14; color: var(--text); border: 1px solid #2a3240; border-radius: .5rem; padding: .5rem .6rem; }
                    textarea { width: 100%; min-height: 160px; resize: vertical; background: #0c0f14; color: var(--text); border: 1px solid #2a3240; border-radius: .5rem; padding: .75rem .9rem; line-height: 1.5; }
                    .actions { display: flex; gap: .75rem; align-items: center; margin-top: .75rem; }
                    button { background: var(--accent); color: white; border: none; border-radius: .5rem; padding: .6rem .9rem; font-weight: 600; cursor: pointer; }
                    button:disabled { opacity: .6; cursor: not-allowed; }
                    .meta { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: .75rem; margin-top: 1rem; }
                    .meta .item { background: #11151c; border: 1px solid #212734; border-radius: .5rem; padding: .6rem .75rem; }
                    .pred-grid { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: .9rem; }
                    .pred { border: 1px solid #252b36; border-radius: .75rem; padding: .9rem; background: #121722; margin-top: .9rem; }
                    .code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-weight: 700; color: var(--accent-2); }
                    .title { font-weight: 700; margin-left: .5rem; }
                    .score { float: right; color: var(--muted); }
                    .chips { display: flex; gap: .4rem; flex-wrap: wrap; margin-top: .5rem; }
                    .chip { background: var(--chip); border: 1px solid #2a3240; color: #cbd5e1; padding: .2rem .5rem; border-radius: 999px; font-size: .8rem; }
                    .explain { color: var(--muted); font-size: .9rem; margin-top: .5rem; }
                    .raw-toggle { margin-top: 1rem; }
                    .raw { margin-top: .5rem; background: #0c0f14; border: 1px solid #2a3240; border-radius: .5rem; padding: .75rem; overflow: auto; max-height: 280px; }
                    .danger { color: var(--danger); }
                    .note-preview { background: #0c0f14; border: 1px solid #2a3240; border-radius: .5rem; padding: .75rem; min-height: 160px; line-height: 1.6; white-space: pre-wrap; }
                    mark { background: rgba(59,130,246,.25); color: #e6f0ff; padding: 0 .15rem; border-radius: .2rem; }
                </style>
            </head>
            <body>
                <main class="container">
                    <header>
                        <h1>Medical Coding Assistant</h1>
                        <span class="subtitle">Submit a de-identified note → POST <code>/predict</code></span>
                    </header>

                    <section class="card">
                        <div class="row">
                            <div>
                                <label>Clinical Note (≥ 10 words)</label>
                                <textarea id="note">Patient 45yo male presents with crushing chest pain for 3 days, SOB, diaphoresis. EKG shows ST elevation.</textarea>
                            </div>
                            <div>
                                <label>Top K</label>
                                <input id="topk" type="number" value="5" min="1" max="20" />
                            </div>
                        </div>
                        <div class="actions">
                            <button id="btn">Predict</button>
                            <span id="status" class="subtitle"></span>
                        </div>
                    </section>

                    <section id="result" style="margin-top:1rem;"></section>
                </main>

                <script>
                    function el(tag, cls, text) {
                        const e = document.createElement(tag); if (cls) e.className = cls; if (text) e.textContent = text; return e;
                    }
                    function fmt(num) { try { return Number(num).toFixed(3); } catch { return String(num); } }
                    function escapeHtml(str){return str.replace(/[&<>"']/g,(c)=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));}
                    function highlightText(text, spans){
                        if(!spans || !spans.length) return escapeHtml(text);
                        const uniq = Array.from(new Set(spans.filter(s=>s && s.trim()).map(s=>s.trim()))).sort((a,b)=>b.length-a.length).slice(0,20);
                        let html = escapeHtml(text);
                        for(const s of uniq){
                            const pat = new RegExp(s.replace(/[-\/\\^$*+?.()|[\]{}]/g,'\\$&'), 'gi');
                            html = html.replace(pat, (m)=>`<mark title="${s}">${m}</mark>`);
                        }
                        return html;
                    }

                    async function runPredict() {
                        const note = document.getElementById('note').value.trim();
                        const topk = parseInt(document.getElementById('topk').value || '5');
                        const btn = document.getElementById('btn');
                        const status = document.getElementById('status');
                        const result = document.getElementById('result');
                        btn.disabled = true; status.textContent = 'Running…'; result.innerHTML = '';
                        try {
                            const resp = await fetch('/predict', {
                                method: 'POST', headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ note_text: note, top_k: topk })
                            });
                            if(!resp.ok){
                                const text = await resp.text();
                                throw new Error(`HTTP ${resp.status}: ${text}`);
                            }
                            const json = await resp.json();

                            const wrap = el('div');
                            // Meta summary
                            const meta = el('div', 'meta');
                            const m1 = el('div', 'item'); m1.innerHTML = '<strong>Top K:</strong> ' + (json.top_k ?? topk);
                            const m2 = el('div', 'item'); m2.innerHTML = '<strong>Latency:</strong> ' + (json.latency_ms ?? '-') + ' ms';
                            const m3 = el('div', 'item');
                            let safetyTxt = (json.safety && json.safety.checks_passed) ? 'Passed' : '<span class="danger">Failed</span>';
                            if(json.safety && json.safety.reason && !json.safety.checks_passed){ safetyTxt += ' — ' + json.safety.reason; }
                            m3.innerHTML = '<strong>Safety:</strong> ' + safetyTxt;
                            const m4 = el('div', 'item'); m4.innerHTML = '<strong>Disclaimer:</strong> ' + (json.safety?.disclaimer ?? '');
                            meta.append(m1,m2,m3,m4);
                            wrap.append(meta);

                            // Note preview + Predictions
                            const row2 = el('div','row-2');
                            const left = el('div','card');
                            const lh = el('div'); lh.innerHTML = '<strong>Note Preview</strong>';
                            const lbody = el('div','note-preview');
                            const spans = (json.predictions && json.predictions[0] && json.predictions[0].evidence_spans) ? json.predictions[0].evidence_spans : [];
                            lbody.innerHTML = highlightText(note, spans);
                            left.append(lh,lbody);

                            const grid = el('div', 'pred-grid');
                            (json.predictions || []).forEach(p => {
                                const card = el('div', 'pred');
                                const header = el('div');
                                const code = el('span', 'code', p.icd10_code || '');
                                const title = el('span', 'title', p.title || '');
                                const score = el('span', 'score', 'score ' + fmt(p.score));
                                header.append(code, title, score);
                                card.append(header);
                                const chips = el('div', 'chips');
                                (p.evidence_spans || []).forEach(s => chips.append(el('span','chip', s)));
                                if (p.category) chips.append(el('span','chip', p.category));
                                card.append(chips);
                                if (p.explanation) card.append(el('div','explain', p.explanation));
                                grid.append(card);
                            });
                            const right = el('div'); right.append(grid);
                            row2.append(left,right);
                            wrap.append(row2);

                            // Raw JSON toggle
                            const toggle = el('div', 'raw-toggle');
                            const btnRaw = el('button'); btnRaw.textContent = 'Show Raw JSON';
                            const pre = el('pre', 'raw'); pre.style.display = 'none'; pre.textContent = JSON.stringify(json, null, 2);
                            btnRaw.onclick = () => { const show = pre.style.display === 'none'; pre.style.display = show ? 'block' : 'none'; btnRaw.textContent = show ? 'Hide Raw JSON' : 'Show Raw JSON'; };
                            toggle.append(btnRaw); wrap.append(toggle, pre);

                            result.append(wrap);
                            status.textContent = 'Done';
                        } catch (e) {
                            status.textContent = 'Error';
                            const box = el('div','card');
                            const title = el('div'); title.innerHTML = '<strong>Request failed</strong>';
                            const pre = el('pre','raw'); pre.textContent = String(e);
                            box.append(title, pre); result.append(box);
                        } finally {
                            btn.disabled = false;
                        }
                    }
                    document.getElementById('btn').onclick = runPredict;
                </script>
            </body>
        </html>
    """
    return HTMLResponse(html)


routes = [
    Route("/", index, methods=["GET"]),
    Route("/predict", predict, methods=["POST"]),
]
app = Starlette(debug=True, routes=routes)
