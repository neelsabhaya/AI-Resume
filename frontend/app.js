/**
 * app.js — Recruiter Dashboard Logic
 * Handles JD upload, resume upload, results rendering, comparison, and modals.
 */

const API = '';  // Same origin
let currentJobId = null;
let allCandidates = [];
let selectedForCompare = new Set();
let selectedFiles = [];

// ── Navigation ──────────────────────────────────────────────────────────────
function showSection(name) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-pill').forEach(p => p.classList.remove('active'));
  document.getElementById(`section-${name}`).classList.add('active');
  event.target.classList.add('active');
}

// ── JD Character Count ──────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const jdText = document.getElementById('jd-text');
  const charCount = document.getElementById('jd-char-count');
  jdText.addEventListener('input', () => {
    charCount.textContent = `${jdText.value.length} characters`;
  });

  // Drag & drop
  const dropZone = document.getElementById('drop-zone');
  dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
  dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    const files = Array.from(e.dataTransfer.files);
    addFiles(files);
  });
});

// ── File Handling ───────────────────────────────────────────────────────────
function handleFileSelect(event) {
  addFiles(Array.from(event.target.files));
}

function addFiles(files) {
  const allowed = ['.pdf', '.docx', '.doc', '.txt'];
  files.forEach(file => {
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!allowed.includes(ext)) {
      showStatus('analyze-status', `❌ Unsupported file: ${file.name}`, 'error');
      return;
    }
    if (!selectedFiles.find(f => f.name === file.name)) {
      selectedFiles.push(file);
    }
  });
  renderFileList();
  document.getElementById('analyze-btn').disabled = selectedFiles.length === 0 || !currentJobId;
}

function removeFile(index) {
  selectedFiles.splice(index, 1);
  renderFileList();
  document.getElementById('analyze-btn').disabled = selectedFiles.length === 0 || !currentJobId;
}

function renderFileList() {
  const list = document.getElementById('file-list');
  list.innerHTML = selectedFiles.map((f, i) => `
    <div class="file-item">
      <span class="file-icon">${getFileIcon(f.name)}</span>
      <span class="file-name">${f.name}</span>
      <span class="file-size">${formatSize(f.size)}</span>
      <span class="file-remove" onclick="removeFile(${i})">✕</span>
    </div>
  `).join('');
}

function getFileIcon(name) {
  const ext = name.split('.').pop().toLowerCase();
  return ext === 'pdf' ? '📕' : ext === 'docx' || ext === 'doc' ? '📘' : '📄';
}

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

// ── Status Messages ─────────────────────────────────────────────────────────
function showStatus(id, message, type) {
  const el = document.getElementById(id);
  el.textContent = message;
  el.className = `status-badge ${type}`;
  el.style.display = 'block';
}

// ── Upload JD ───────────────────────────────────────────────────────────────
async function uploadJD() {
  const title = document.getElementById('jd-title').value.trim() || 'Untitled Position';
  const description = document.getElementById('jd-text').value.trim();

  if (description.length < 20) {
    showStatus('jd-status', '❌ Please enter a longer job description (at least 20 characters).', 'error');
    return;
  }

  const btn = document.getElementById('upload-jd-btn');
  btn.disabled = true;
  btn.innerHTML = '<span class="btn-icon">⏳</span> Uploading...';

  const formData = new FormData();
  formData.append('title', title);
  formData.append('description', description);

  try {
    const res = await fetch(`${API}/api/upload-jd`, { method: 'POST', body: formData });
    const data = await res.json();

    if (!res.ok) throw new Error(data.detail || 'Upload failed');

    currentJobId = data.job_id;
    showStatus('jd-status',
      `✅ JD uploaded! Job ID: ${data.job_id} · Found ${data.required_skills.length} required skills`,
      'success'
    );

    document.getElementById('analyze-btn').disabled = selectedFiles.length === 0;
  } catch (err) {
    showStatus('jd-status', `❌ ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span class="btn-icon">⚡</span> Upload Job Description';
  }
}

// ── Analyze Resumes ─────────────────────────────────────────────────────────
async function analyzeResumes() {
  if (!currentJobId) {
    showStatus('analyze-status', '❌ Please upload a job description first.', 'error');
    return;
  }
  if (selectedFiles.length === 0) {
    showStatus('analyze-status', '❌ Please select at least one resume file.', 'error');
    return;
  }

  document.getElementById('loading-overlay').style.display = 'flex';

  const formData = new FormData();
  selectedFiles.forEach(f => formData.append('files', f));

  try {
    const res = await fetch(`${API}/api/upload-resumes/${currentJobId}`, {
      method: 'POST', body: formData
    });
    const data = await res.json();

    if (!res.ok) throw new Error(data.detail || 'Analysis failed');

    allCandidates = data.candidates;
    renderResults(data);
    updateStats(data);

    showStatus('analyze-status',
      `✅ Analysis complete! ${data.total_candidates} candidates ranked in ${data.processing_time_seconds}s`,
      'success'
    );

    // Switch to results tab
    document.querySelectorAll('.nav-pill')[1].click();
  } catch (err) {
    showStatus('analyze-status', `❌ ${err.message}`, 'error');
  } finally {
    document.getElementById('loading-overlay').style.display = 'none';
  }
}

// ── Render Results Table ────────────────────────────────────────────────────
function renderResults(data) {
  const tbody = document.getElementById('results-body');
  if (!data.candidates || data.candidates.length === 0) {
    tbody.innerHTML = '<tr><td colspan="9" class="empty-state">No candidates found.</td></tr>';
    return;
  }

  tbody.innerHTML = data.candidates.map(c => {
    const rankClass = c.rank === 1 ? 'rank-1' : c.rank === 2 ? 'rank-2' : c.rank === 3 ? 'rank-3' : 'rank-n';
    const scoreColor = getScoreColor(c.final_score);
    const matchedSkillsPreview = c.matched_skills.slice(0, 3).map(s =>
      `<span class="skill-chip">${s}</span>`
    ).join('') + (c.matched_skills.length > 3 ? `<span class="skill-chip">+${c.matched_skills.length - 3}</span>` : '');

    return `
      <tr onclick="openModal(${c.candidate_id})" data-grade="${c.grade}" data-name="${c.name.toLowerCase()}" data-skills="${c.skills.join(' ').toLowerCase()}">
        <td><span class="rank-badge ${rankClass}">${c.rank}</span></td>
        <td>
          <div style="font-weight:600">${c.name}</div>
          <div style="font-size:0.75rem;color:var(--text3)">${c.filename}</div>
        </td>
        <td>
          <div class="score-bar-wrap">
            <div class="score-bar-bg">
              <div class="score-bar-fill" style="width:${c.final_score}%;background:${scoreColor}"></div>
            </div>
            <span class="score-text" style="color:${scoreColor}">${c.final_score.toFixed(1)}%</span>
          </div>
        </td>
        <td><span class="grade-badge grade-${c.grade}">${c.grade}</span></td>
        <td>${matchedSkillsPreview || '<span style="color:var(--text3)">None</span>'}</td>
        <td style="font-family:var(--font-mono)">${c.experience_years}y</td>
        <td style="font-size:0.8rem;color:var(--text2)">${capitalize(c.education)}</td>
        <td><span class="fraud-badge fraud-${c.fraud.risk_level}">${c.fraud.risk_level}</span></td>
        <td>
          <button class="btn btn-outline" style="width:auto;padding:4px 12px;font-size:0.78rem"
            onclick="event.stopPropagation();toggleCompare(${c.candidate_id})" id="cmp-btn-${c.candidate_id}">
            Compare
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

// ── Stats Bar ───────────────────────────────────────────────────────────────
function updateStats(data) {
  const bar = document.getElementById('stats-bar');
  bar.style.display = 'grid';

  const avg = data.candidates.reduce((s, c) => s + c.final_score, 0) / data.candidates.length;
  const flagged = data.candidates.filter(c => c.fraud.is_suspicious).length;

  document.getElementById('stat-total').textContent = data.total_candidates;
  document.getElementById('stat-shortlisted').textContent = data.shortlisted_count;
  document.getElementById('stat-avg').textContent = `${avg.toFixed(1)}%`;
  document.getElementById('stat-flagged').textContent = flagged;
  document.getElementById('stat-time').textContent = `${data.processing_time_seconds}s`;
}

// ── Filter Table ────────────────────────────────────────────────────────────
function filterTable() {
  const search = document.getElementById('search-input').value.toLowerCase();
  const grade = document.getElementById('grade-filter').value;
  const rows = document.querySelectorAll('#results-body tr[data-grade]');

  rows.forEach(row => {
    const name = row.dataset.name || '';
    const skills = row.dataset.skills || '';
    const rowGrade = row.dataset.grade || '';
    const matchSearch = !search || name.includes(search) || skills.includes(search);
    const matchGrade = !grade || rowGrade === grade;
    row.style.display = matchSearch && matchGrade ? '' : 'none';
  });
}

// ── Candidate Detail Modal ──────────────────────────────────────────────────
function openModal(candidateId) {
  const c = allCandidates.find(x => x.candidate_id === candidateId);
  if (!c) return;

  const scoreColor = getScoreColor(c.final_score);
  const content = document.getElementById('modal-content');

  content.innerHTML = `
    <div class="modal-candidate-name">${c.name}</div>
    <div class="modal-filename">📄 ${c.filename}</div>

    <div class="modal-score-hero">
      <div class="modal-score-circle" style="border-color:${scoreColor};color:${scoreColor}">
        <div class="modal-score-num">${c.final_score.toFixed(0)}</div>
        <div class="modal-score-label">/ 100</div>
      </div>
      <div>
        <div style="font-size:1.3rem;font-weight:700">Grade <span class="grade-badge grade-${c.grade}">${c.grade}</span></div>
        <div style="color:var(--text2);margin-top:4px">Rank #${c.rank} · ${c.experience_years} years exp · ${capitalize(c.education)}</div>
        <div style="margin-top:8px"><span class="fraud-badge fraud-${c.fraud.risk_level}">Fraud Risk: ${c.fraud.risk_level}</span></div>
      </div>
    </div>

    <div class="modal-section">
      <div class="modal-section-title">Score Breakdown</div>
      <div class="breakdown-grid">
        <div class="breakdown-item">
          <div class="breakdown-label">🎯 Skills Match</div>
          <div class="breakdown-value" style="color:${getScoreColor(c.breakdown.skills_score)}">${c.breakdown.skills_score.toFixed(1)}%</div>
        </div>
        <div class="breakdown-item">
          <div class="breakdown-label">📅 Experience</div>
          <div class="breakdown-value" style="color:${getScoreColor(c.breakdown.experience_score)}">${c.breakdown.experience_score.toFixed(1)}%</div>
        </div>
        <div class="breakdown-item">
          <div class="breakdown-label">🎓 Education</div>
          <div class="breakdown-value" style="color:${getScoreColor(c.breakdown.education_score)}">${c.breakdown.education_score.toFixed(1)}%</div>
        </div>
        <div class="breakdown-item">
          <div class="breakdown-label">🔍 Text Similarity</div>
          <div class="breakdown-value" style="color:${getScoreColor(c.breakdown.text_similarity_score)}">${c.breakdown.text_similarity_score.toFixed(1)}%</div>
        </div>
      </div>
    </div>

    ${c.matched_skills.length > 0 ? `
    <div class="modal-section">
      <div class="modal-section-title">✅ Matched Skills (${c.matched_skills.length})</div>
      <div>${c.matched_skills.map(s => `<span class="skill-chip">${s}</span>`).join('')}</div>
    </div>` : ''}

    ${c.missing_skills.length > 0 ? `
    <div class="modal-section">
      <div class="modal-section-title">❌ Missing Skills (${c.missing_skills.length})</div>
      <div>${c.missing_skills.map(s => `<span class="skill-chip missing">${s}</span>`).join('')}</div>
    </div>` : ''}

    ${c.fraud.is_suspicious ? `
    <div class="modal-section">
      <div class="modal-section-title">⚠️ Fraud Detection Warnings</div>
      ${c.fraud.reasons.map(r => `<div class="feedback-item" style="border-color:var(--red)">${r}</div>`).join('')}
    </div>` : ''}

    <div class="modal-section">
      <div class="modal-section-title">💡 AI Feedback & Suggestions</div>
      ${c.feedback.map(f => `<div class="feedback-item">${f}</div>`).join('')}
    </div>
  `;

  document.getElementById('modal-overlay').classList.add('open');
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('open');
}

// ── Compare ─────────────────────────────────────────────────────────────────
function toggleCompare(candidateId) {
  const btn = document.getElementById(`cmp-btn-${candidateId}`);
  if (selectedForCompare.has(candidateId)) {
    selectedForCompare.delete(candidateId);
    btn.textContent = 'Compare';
    btn.style.background = '';
  } else {
    if (selectedForCompare.size >= 4) {
      alert('You can compare up to 4 candidates at a time.');
      return;
    }
    selectedForCompare.add(candidateId);
    btn.textContent = '✓ Selected';
    btn.style.background = 'rgba(99,102,241,0.2)';
  }
  renderCompare();
}

function renderCompare() {
  const container = document.getElementById('compare-container');
  const ids = Array.from(selectedForCompare);

  if (ids.length === 0) {
    container.innerHTML = `<div class="empty-state-card"><div style="font-size:3rem">⚖️</div><div>Select candidates from the Results tab to compare them here.</div></div>`;
    return;
  }

  const candidates = ids.map(id => allCandidates.find(c => c.candidate_id === id)).filter(Boolean);
  container.innerHTML = candidates.map(c => {
    const scoreColor = getScoreColor(c.final_score);
    return `
      <div class="compare-card">
        <div class="compare-card-name">${c.name}</div>
        <div style="font-size:0.75rem;color:var(--text3);margin-bottom:0.5rem">${c.filename}</div>
        <div class="compare-card-score" style="color:${scoreColor}">${c.final_score.toFixed(1)}%</div>
        <div style="margin-bottom:1rem"><span class="grade-badge grade-${c.grade}">${c.grade}</span> · Rank #${c.rank}</div>

        <div style="font-size:0.78rem;color:var(--text3);margin-bottom:6px;font-weight:600">SCORE BREAKDOWN</div>
        ${['skills_score','experience_score','education_score','text_similarity_score'].map(key => {
          const label = key.replace('_score','').replace('_',' ');
          const val = c.breakdown[key];
          return `
            <div style="margin-bottom:8px">
              <div style="display:flex;justify-content:space-between;font-size:0.8rem;margin-bottom:3px">
                <span style="color:var(--text2);text-transform:capitalize">${label}</span>
                <span style="font-family:var(--font-mono);color:${getScoreColor(val)}">${val.toFixed(1)}%</span>
              </div>
              <div class="score-bar-bg"><div class="score-bar-fill" style="width:${val}%;background:${getScoreColor(val)}"></div></div>
            </div>
          `;
        }).join('')}

        <div style="margin-top:1rem;font-size:0.78rem;color:var(--text3);font-weight:600;margin-bottom:6px">MATCHED SKILLS</div>
        <div>${c.matched_skills.slice(0,6).map(s => `<span class="skill-chip">${s}</span>`).join('') || '<span style="color:var(--text3)">None</span>'}</div>
      </div>
    `;
  }).join('');
}

// ── Export CSV ───────────────────────────────────────────────────────────────
function downloadCSV() {
  if (allCandidates.length === 0) { alert('No results to export.'); return; }

  const headers = ['Rank','Name','File','Score','Grade','Experience (yrs)','Education','Skills Matched','Skills Missing','Fraud Risk'];
  const rows = allCandidates.map(c => [
    c.rank, c.name, c.filename, c.final_score.toFixed(2), c.grade,
    c.experience_years, c.education,
    c.matched_skills.join('; '), c.missing_skills.join('; '),
    c.fraud.risk_level,
  ]);

  const csv = [headers, ...rows].map(r => r.map(v => `"${v}"`).join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href = url; a.download = 'candidates_ranked.csv'; a.click();
  URL.revokeObjectURL(url);
}

// ── Helpers ──────────────────────────────────────────────────────────────────
function getScoreColor(score) {
  if (score >= 80) return 'var(--green)';
  if (score >= 60) return 'var(--accent3)';
  if (score >= 40) return 'var(--yellow)';
  return 'var(--red)';
}

function capitalize(str) {
  if (!str || str === 'unknown') return 'Not specified';
  return str.charAt(0).toUpperCase() + str.slice(1);
}
