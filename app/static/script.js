// Second Opinion - Frontend JavaScript (Enhanced)

// Tab switching
function switchTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    // Remove active class from all tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });

    // Show selected tab
    const tabContent = document.getElementById(`${tabName}-tab`);
    tabContent.classList.add('active');

    // Mark clicked tab as active
    const clickedTab = document.querySelector(`[data-tab="${tabName}"]`);
    if (clickedTab) {
        clickedTab.classList.add('active');
    }
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

// Analyze pasted text
async function analyzePaste() {
    const documentText = document.getElementById('document-text').value.trim();

    if (!documentText) {
        alert('Please paste a document to analyze');
        return;
    }

    const context = {
        scale: document.getElementById('context-scale').value,
        slos: document.getElementById('context-slos').value,
        dependencies: document.getElementById('context-deps').value
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

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const scale = document.getElementById('upload-context-scale').value;
    const slos = document.getElementById('upload-context-slos').value;
    const deps = document.getElementById('upload-context-deps').value;

    if (scale) formData.append('context_scale', scale);
    if (slos) formData.append('context_slos', slos);
    if (deps) formData.append('context_dependencies', deps);

    await performAnalysisUpload(formData);
}

// Perform analysis (for paste)
async function performAnalysis(data) {
    showLoading();
    hideResults();

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
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

// Perform analysis (for upload)
async function performAnalysisUpload(formData) {
    showLoading();
    hideResults();

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
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

// Display results
function displayResults(results) {
    hideLoading();

    // Show results section
    const resultsSection = document.getElementById('results');
    resultsSection.classList.remove('hidden');

    // Display summary
    const summaryDiv = document.getElementById('summary');
    summaryDiv.textContent = results.summary || 'Analysis complete.';

    // Display failure modes
    displayFailureModes(results.failure_modes || []);

    // Display assumptions
    displayList('assumptions', results.implicit_assumptions || []);

    // Display known unknowns
    displayList('unknowns', results.known_unknowns || []);

    // Display ruled out risks
    displayList('ruled-out', results.ruled_out_risks || []);

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Display failure modes with expandable cards
function displayFailureModes(modes) {
    const container = document.getElementById('failure-modes');
    container.innerHTML = '';

    if (modes.length === 0) {
        container.innerHTML = '<div style="padding: 2rem; text-align: center; color: var(--accent-primary);"><strong>✓ No significant failure patterns detected</strong></div>';
        return;
    }

    modes.forEach(mode => {
        const card = createFailureModeCard(mode);
        container.appendChild(card);
    });
}

// Create expandable failure mode card
function createFailureModeCard(mode) {
    const card = document.createElement('div');
    card.className = 'failure-mode';

    const confidenceClass = `confidence-${mode.confidence}`;
    const score = Math.round(mode.match_score * 100);

    card.innerHTML = `
        <div class="failure-mode-header" onclick="toggleFailureMode(this)">
            <div class="failure-mode-title">${escapeHtml(mode.pattern_name)}</div>
            <div class="failure-mode-meta">
                <span class="confidence-badge ${confidenceClass}">${mode.confidence.toUpperCase()}</span>
                <span class="match-score">${score}%</span>
                <span class="expand-icon">▶</span>
            </div>
        </div>
        <div class="failure-mode-body">
            ${mode.evidence.length > 0 ? `
                <div class="failure-mode-section">
                    <h4>Evidence</h4>
                    <ul>
                        ${mode.evidence.map(e => `<li>${escapeHtml(e)}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}

            ${mode.trigger_conditions.length > 0 ? `
                <div class="failure-mode-section">
                    <h4>Trigger Conditions</h4>
                    <ul>
                        ${mode.trigger_conditions.map(t => `<li>${escapeHtml(t)}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}

            ${mode.why_easy_to_miss ? `
                <div class="failure-mode-section">
                    <h4>Why This Is Easy to Miss</h4>
                    <p>${escapeHtml(mode.why_easy_to_miss)}</p>
                </div>
            ` : ''}

            ${mode.discussion_questions.length > 0 ? `
                <div class="failure-mode-section">
                    <h4>Discussion Questions</h4>
                    <ul>
                        ${mode.discussion_questions.map(q => `<li>${escapeHtml(q)}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        </div>
    `;

    return card;
}

// Toggle failure mode expansion
function toggleFailureMode(header) {
    const card = header.parentElement;
    card.classList.toggle('expanded');
}

// Display simple list
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

// UI helpers
function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

function hideResults() {
    document.getElementById('results').classList.add('hidden');
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// File drag and drop
const fileLabel = document.querySelector('.file-label');
const fileInput = document.getElementById('file-input');

if (fileLabel && fileInput) {
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        fileLabel.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        fileLabel.addEventListener(eventName, () => {
            fileLabel.style.borderColor = 'var(--accent-primary)';
            fileLabel.style.background = 'var(--bg-tertiary)';
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        fileLabel.addEventListener(eventName, () => {
            fileLabel.style.borderColor = '';
            fileLabel.style.background = '';
        }, false);
    });

    fileLabel.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        fileInput.files = files;
        handleFileSelect();
    }, false);
}