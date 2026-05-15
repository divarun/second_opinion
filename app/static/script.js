// Second Opinion - Frontend JavaScript

let lastResults = null;

// Tab switching
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById(`${tabName}-tab`).classList.add('active');
    const clicked = document.querySelector(`[data-tab="${tabName}"]`);
    if (clicked) clicked.classList.add('active');
}

// File selection handler
function handleFileSelect() {
    const fileInput = document.getElementById('file-input');
    const fileName = document.getElementById('file-name');
    const uploadBtn = document.getElementById('upload-btn');

    if (fileInput.files.length > 0) {
        fileName.textContent = fileInput.files[0].name;
        uploadBtn.disabled = false;
    } else {
        fileName.textContent = 'Drop file here or click to browse';
        uploadBtn.disabled = true;
    }
}

// Analyze pasted text — uses streaming endpoint
async function analyzePaste() {
    const documentText = document.getElementById('document-text').value.trim();
    if (!documentText) {
        alert('Please paste a document to analyze');
        return;
    }

    const context = {
        scale: document.getElementById('context-scale').value,
        slos: document.getElementById('context-slos').value,
        dependencies: document.getElementById('context-deps').value,
    };

    await performAnalysis({ document: documentText, context });
}

// Analyze uploaded file
async function analyzeUpload() {
    const fileInput = document.getElementById('file-input');
    if (!fileInput.files.length) {
        alert('Please select a file to upload');
        return;
    }

    const file = fileInput.files[0];
    const ext = file.name.split('.').pop().toLowerCase();

    const context = {
        scale: document.getElementById('upload-context-scale').value,
        slos: document.getElementById('upload-context-slos').value,
        dependencies: document.getElementById('upload-context-deps').value,
    };

    if (ext !== 'pdf') {
        // Text files: read client-side and use streaming endpoint
        try {
            const text = await file.text();
            await performAnalysis({ document: text, context });
        } catch (e) {
            alert(`Error reading file: ${e.message}`);
        }
    } else {
        // PDF: must be processed server-side
        const formData = new FormData();
        formData.append('file', file);
        if (context.scale) formData.append('context_scale', context.scale);
        if (context.slos) formData.append('context_slos', context.slos);
        if (context.dependencies) formData.append('context_dependencies', context.dependencies);
        await performAnalysisUpload(formData);
    }
}

// Streaming analysis (SSE via fetch)
async function performAnalysis(data) {
    showLoading('Starting analysis...');
    hideResults();

    try {
        const response = await fetch('/api/analyze/stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Analysis failed');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // hold incomplete last line

            for (const line of lines) {
                if (!line.startsWith('data: ')) continue;
                const event = JSON.parse(line.slice(6));

                if (event.type === 'progress') {
                    handleProgressEvent(event);
                } else if (event.type === 'complete') {
                    displayResults(event.results);
                    return;
                } else if (event.type === 'error') {
                    throw new Error(event.message);
                }
            }
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
        hideLoading();
    }
}

// Non-streaming analysis (for PDF uploads)
async function performAnalysisUpload(formData) {
    showLoading('Uploading and analyzing document...');
    hideResults();

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Analysis failed');
        }

        const results = await response.json();
        displayResults(results);
    } catch (error) {
        alert(`Error: ${error.message}`);
        hideLoading();
    }
}

// Map SSE progress events to UI updates
const PROGRESS_STEPS = {
    start: { text: 'Analyzing patterns, assumptions, and unknowns in parallel...', pct: 15 },
    patterns_done: { text: null, pct: 70 },  // text is dynamic
    analysis_done: { text: 'Generating final report...', pct: 90 },
    complete: { text: 'Done.', pct: 100 },
};

function handleProgressEvent(event) {
    const step = PROGRESS_STEPS[event.step];
    if (!step) return;

    let text = step.text;
    if (event.step === 'patterns_done') {
        const count = event.data?.count ?? 0;
        text = `Found ${count} pattern match${count !== 1 ? 'es' : ''}. Checking ruled-out risks...`;
    }

    updateLoadingProgress(text, step.pct);
}

function updateLoadingProgress(text, percent) {
    const el = document.getElementById('loading-text');
    const bar = document.getElementById('progress-bar');
    if (el && text) el.textContent = text;
    if (bar) bar.style.width = `${percent}%`;
}

// Display results
function displayResults(results) {
    hideLoading();
    lastResults = results;

    const section = document.getElementById('results');
    section.classList.remove('hidden');

    document.getElementById('summary').textContent = results.summary || 'Analysis complete.';

    displayFailureModes(results.failure_modes || []);
    displayList('assumptions', results.implicit_assumptions || []);
    displayList('unknowns', results.known_unknowns || []);
    displayList('ruled-out', results.ruled_out_risks || []);

    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Display failure mode cards
function displayFailureModes(modes) {
    const container = document.getElementById('failure-modes');
    container.innerHTML = '';

    if (modes.length === 0) {
        container.innerHTML = '<div style="padding: 2rem; text-align: center; color: var(--accent-primary);"><strong>✓ No significant failure patterns detected</strong></div>';
        return;
    }

    modes.forEach(mode => container.appendChild(createFailureModeCard(mode)));
}

function createFailureModeCard(mode) {
    const card = document.createElement('div');
    card.className = 'failure-mode';
    const score = Math.round(mode.match_score * 100);

    card.innerHTML = `
        <div class="failure-mode-header" onclick="toggleFailureMode(this)">
            <div class="failure-mode-title">${escapeHtml(mode.pattern_name)}</div>
            <div class="failure-mode-meta">
                <span class="confidence-badge confidence-${mode.confidence}">${mode.confidence.toUpperCase()}</span>
                <span class="match-score">${score}%</span>
                <span class="expand-icon">▶</span>
            </div>
        </div>
        <div class="failure-mode-body">
            ${mode.evidence.length > 0 ? `
                <div class="failure-mode-section">
                    <h4>Evidence</h4>
                    <ul>${mode.evidence.map(e => `<li>${escapeHtml(e)}</li>`).join('')}</ul>
                </div>` : ''}
            ${mode.trigger_conditions.length > 0 ? `
                <div class="failure-mode-section">
                    <h4>Trigger Conditions</h4>
                    <ul>${mode.trigger_conditions.map(t => `<li>${escapeHtml(t)}</li>`).join('')}</ul>
                </div>` : ''}
            ${mode.why_easy_to_miss ? `
                <div class="failure-mode-section">
                    <h4>Why This Is Easy to Miss</h4>
                    <p>${escapeHtml(mode.why_easy_to_miss)}</p>
                </div>` : ''}
            ${mode.discussion_questions.length > 0 ? `
                <div class="failure-mode-section">
                    <h4>Discussion Questions</h4>
                    <ul>${mode.discussion_questions.map(q => `<li>${escapeHtml(q)}</li>`).join('')}</ul>
                </div>` : ''}
        </div>
    `;

    return card;
}

function toggleFailureMode(header) {
    header.parentElement.classList.toggle('expanded');
}

function displayList(elementId, items) {
    const list = document.getElementById(elementId);
    list.innerHTML = '';

    if (items.length === 0) {
        list.innerHTML = '<li style="color: var(--text-tertiary); opacity: 0.7;">None identified</li>';
        return;
    }

    items.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        list.appendChild(li);
    });
}

// ─── Export ───────────────────────────────────────────────────────────────────

function resultsToMarkdown(results) {
    const lines = ['# Second Opinion — Analysis Report', ''];

    lines.push(`## Summary`, '', results.summary, '');

    if (results.failure_modes.length > 0) {
        lines.push('## Failure Modes', '');
        results.failure_modes.forEach(mode => {
            const score = Math.round(mode.match_score * 100);
            lines.push(`### ${mode.pattern_name}`, '');
            lines.push(`**Confidence:** ${mode.confidence.toUpperCase()} (${score}%)`, '');

            if (mode.evidence.length > 0) {
                lines.push('**Evidence:**');
                mode.evidence.forEach(e => lines.push(`- ${e}`));
                lines.push('');
            }
            if (mode.trigger_conditions.length > 0) {
                lines.push('**Trigger Conditions:**');
                mode.trigger_conditions.forEach(t => lines.push(`- ${t}`));
                lines.push('');
            }
            if (mode.why_easy_to_miss) {
                lines.push(`**Why Easy to Miss:** ${mode.why_easy_to_miss}`, '');
            }
            if (mode.discussion_questions.length > 0) {
                lines.push('**Discussion Questions:**');
                mode.discussion_questions.forEach(q => lines.push(`- ${q}`));
                lines.push('');
            }
        });
    }

    if (results.implicit_assumptions.length > 0) {
        lines.push('## Implicit Assumptions', '');
        results.implicit_assumptions.forEach(a => lines.push(`- ${a}`));
        lines.push('');
    }

    if (results.known_unknowns.length > 0) {
        lines.push('## Known Unknowns', '');
        results.known_unknowns.forEach(u => lines.push(`- ${u}`));
        lines.push('');
    }

    if (results.ruled_out_risks.length > 0) {
        lines.push('## Ruled Out Risks', '');
        results.ruled_out_risks.forEach(r => lines.push(`- ${r}`));
        lines.push('');
    }

    return lines.join('\n');
}

async function copyMarkdown() {
    if (!lastResults) return;
    const md = resultsToMarkdown(lastResults);
    try {
        await navigator.clipboard.writeText(md);
        const btn = document.getElementById('btn-copy-md');
        const original = btn.innerHTML;
        btn.innerHTML = btn.innerHTML.replace('Copy as Markdown', 'Copied!');
        btn.classList.add('copied');
        setTimeout(() => {
            btn.innerHTML = original;
            btn.classList.remove('copied');
        }, 2000);
    } catch {
        alert('Copy failed. Please copy the results manually.');
    }
}

function downloadJSON() {
    if (!lastResults) return;
    const blob = new Blob([JSON.stringify(lastResults, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'second-opinion-analysis.json';
    a.click();
    URL.revokeObjectURL(url);
}

// ─── UI Helpers ───────────────────────────────────────────────────────────────

function showLoading(text = 'Starting analysis...') {
    document.getElementById('loading').classList.remove('hidden');
    updateLoadingProgress(text, 5);
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function hideResults() {
    document.getElementById('results').classList.add('hidden');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ─── Drag & Drop ──────────────────────────────────────────────────────────────

const fileLabel = document.querySelector('.file-label');
const fileInput = document.getElementById('file-input');

if (fileLabel && fileInput) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(e => {
        fileLabel.addEventListener(e, evt => { evt.preventDefault(); evt.stopPropagation(); }, false);
    });

    ['dragenter', 'dragover'].forEach(e => {
        fileLabel.addEventListener(e, () => {
            fileLabel.style.borderColor = 'var(--accent-primary)';
            fileLabel.style.background = 'var(--bg-tertiary)';
        }, false);
    });

    ['dragleave', 'drop'].forEach(e => {
        fileLabel.addEventListener(e, () => {
            fileLabel.style.borderColor = '';
            fileLabel.style.background = '';
        }, false);
    });

    fileLabel.addEventListener('drop', e => {
        fileInput.files = e.dataTransfer.files;
        handleFileSelect();
    }, false);
}
