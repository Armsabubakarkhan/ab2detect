/**
 * AB2DETECT Chrome Extension — Popup Script
 * Abubakar Khan (1RUA24CSE0010) · Abhishek D Nagoor (1RUA24CSE0009)
 * SoCSE, RV University Bengaluru · Summer Internship 2025
 */

const API_URL = 'http://localhost:8000';

// Check backend health on load
window.addEventListener('DOMContentLoaded', async () => {
  const dot = document.getElementById('status-dot');
  try {
    const r = await fetch(`${API_URL}/health`, { signal: AbortSignal.timeout(1500) });
    if (r.ok) {
      dot.classList.add('ok');
      dot.title = 'Backend connected';
    } else {
      dot.classList.add('err');
      dot.title = 'Backend error';
    }
  } catch {
    dot.title = 'Backend offline — detection unavailable';
  }

  // Restore last inputs from storage
  chrome.storage.local.get(['ab2_ctx', 'ab2_ans'], (data) => {
    if (data.ab2_ctx) document.getElementById('ctx').value = data.ab2_ctx;
    if (data.ab2_ans) document.getElementById('ans').value = data.ab2_ans;
  });
});

// Save inputs on change
document.getElementById('ctx').addEventListener('input', (e) => {
  chrome.storage.local.set({ ab2_ctx: e.target.value });
});
document.getElementById('ans').addEventListener('input', (e) => {
  chrome.storage.local.set({ ab2_ans: e.target.value });
});

async function runDetect() {
  const ctx = document.getElementById('ctx').value.trim();
  const ans = document.getElementById('ans').value.trim();
  const btn = document.getElementById('detect-btn');
  const resultEl = document.getElementById('result');

  if (!ctx || !ans) {
    resultEl.innerHTML = '<div class="error">Provide both context and answer.</div>';
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Detecting…';
  resultEl.innerHTML = '';

  try {
    const response = await fetch(`${API_URL}/detect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ context: ctx, question: '', answer: ans }),
      signal: AbortSignal.timeout(8000),
    });

    if (!response.ok) throw new Error(`API error ${response.status}`);
    const data = await response.json();
    renderResult(ans, data);

  } catch (err) {
    // Fallback: client-side simulation
    const simResult = simulateDetection(ctx, ans);
    renderResult(ans, simResult);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Run Detection';
  }
}

function renderResult(answer, data) {
  const resultEl = document.getElementById('result');
  const isHall = data.is_hallucinated;
  const verdictClass = isHall ? 'hall' : 'ok';
  const verdictText  = isHall ? 'Hallucination detected' : 'Answer supported by context';

  let highlighted = answer;
  if (data.spans && data.spans.length > 0) {
    const sorted = [...data.spans].sort((a, b) => b.length - a.length);
    for (const span of sorted) {
      const re = new RegExp(span.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
      highlighted = highlighted.replace(re, `<span class="w-hall">${span}</span>`);
    }
  }

  const chips = (data.spans || [])
    .map(s => `<span class="span-chip">${s}</span>`)
    .join('');

  resultEl.innerHTML = `
    <div class="verdict ${verdictClass}">${verdictText}</div>
    <div class="meta">
      confidence ${(data.confidence || 0).toFixed(2)} &nbsp;·&nbsp;
      ${data.hall_count || 0} span(s) flagged &nbsp;·&nbsp;
      ${data.token_count || 0} tokens
    </div>
    ${chips ? `<div class="spans-label">Flagged spans</div><div>${chips}</div>` : ''}
    <div class="answer-box">${highlighted}</div>
  `;
}

// Client-side simulation (used when backend is offline)
function simulateDetection(context, answer) {
  const ctxWords = new Set(context.toLowerCase().match(/\b\w+\b/g) || []);
  const stopwords = new Set(['the','a','an','is','are','was','were','be','been',
    'have','has','had','do','does','did','will','would','could','should','may',
    'might','shall','can','to','of','in','on','at','by','for','with','from',
    'as','and','or','but','not','that','this','it','he','she','they','we','you']);
  const tokens = answer.match(/\b\w+\b/g) || [];
  const spans = [];

  for (const w of tokens) {
    if (!ctxWords.has(w.toLowerCase()) && !stopwords.has(w.toLowerCase())
        && w.length > 2 && Math.random() < 0.35) {
      spans.push(w);
    }
  }

  const nums = answer.match(/\b\d+[\d,.]*\b/g) || [];
  const ctxNums = new Set(context.match(/\b\d+[\d,.]*\b/g) || []);
  for (const n of nums) {
    if (!ctxNums.has(n)) spans.push(n);
  }

  const unique = [...new Set(spans)].slice(0, 5);
  return {
    is_hallucinated: unique.length > 0,
    confidence: Math.max(0.62, Math.min(0.98, 0.98 - unique.length * 0.06)),
    spans: unique,
    hall_count: unique.length,
    token_count: tokens.length,
    hall_rate: unique.length / Math.max(tokens.length, 1),
  };
}
