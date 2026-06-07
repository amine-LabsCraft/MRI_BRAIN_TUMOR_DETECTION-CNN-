/* ═══════════════════════════════════════════════════════════════════
   BrainScan AI — app.js (v2.0 · ResNet50 · 98.96%)
   Vanilla JS · Chart.js · Lucide · jsPDF
   ═══════════════════════════════════════════════════════════════════ */
"use strict";

/* ─────────────────────────────────────────────────────────────────
   BLOC 1 — CONFIG · CLASS_STYLES · AppState · activeFilters · DOM
   ───────────────────────────────────────────────────────────────── */
const CONFIG = {
    API_BASE:            "http://localhost:8000",
    MAX_FILE_SIZE:       10 * 1024 * 1024,
    MAX_HISTORY:         100,
    HEALTH_INTERVAL:     30_000,
    TOAST_DURATION:      4_000,
    VALID_TYPES:         ["image/jpeg", "image/png", "image/jpg"],
    STORAGE_KEY:         "brainscan_history_v2",
    ITEMS_PER_PAGE:      10,
    REJECTION_THRESHOLD: 0.55,
};

const CLASS_STYLES = {
    "Glioma":     { cssClass: "glioma",     color: "#EF4444" },
    "Meningioma": { cssClass: "meningioma", color: "#F59E0B" },
    "No Tumor":   { cssClass: "no-tumor",   color: "#10B981" },
    "Pituitary":  { cssClass: "pituitary",  color: "#3B82F6" },
};

const AppState = {
    currentFile:     null,
    probChart:       null,
    analysisHistory: [],
    currentPage:     1,
    itemsPerPage:    CONFIG.ITEMS_PER_PAGE,
    isLoading:       false,
    lastResult:      null,
    batchFiles:      [],
    batchResults:    [],
    compareFileA:    null,
    compareFileB:    null,
};

const activeFilters = {
    classFilter: "all",
    dateFrom:    "",
    dateTo:      "",
    confMin:     0,
    confMax:     100,
};

const DOM = {
    uploadZone:         document.getElementById("upload-zone"),
    uploadContent:      document.getElementById("upload-content"),
    fileInput:          document.getElementById("file-input"),
    previewImage:       document.getElementById("preview-image"),
    uploadValidation:   document.getElementById("upload-validation"),
    analyzeBtn:         document.getElementById("analyze-btn"),
    randomBtn:          document.getElementById("random-btn"),
    clearBtn:           document.getElementById("clear-btn"),
    loader:             document.getElementById("loader"),
    resultsSection:     document.getElementById("results-section"),
    apiStatus:          document.getElementById("api-status"),
    toastContainer:     document.getElementById("toast-container"),
    predictionBadge:    document.getElementById("prediction-badge"),
    confidenceValue:    document.getElementById("confidence-value"),
    confidenceFill:     document.getElementById("confidence-fill"),
    alertLevel:         document.getElementById("alert-level"),
    inferenceTime:      document.getElementById("inference-time"),
    inferenceTimeValue: document.getElementById("inference-time-value"),
    gradcamOriginal:    document.getElementById("gradcam-original"),
    gradcamHeatmap:     document.getElementById("gradcam-heatmap"),
    gradcamOverlay:     document.getElementById("gradcam-overlay"),
    opacitySlider:      document.getElementById("opacity-slider"),
    opacityValue:       document.getElementById("opacity-value"),
    downloadGradcamBtn: document.getElementById("download-gradcam-btn"),
    historyEmpty:       document.getElementById("history-empty"),
    historyTable:       document.getElementById("history-table"),
    historyBody:        document.getElementById("history-body"),
    exportCsvBtn:       document.getElementById("export-csv-btn"),
    clearHistoryBtn:    document.getElementById("clear-history-btn"),
    logoIcon:           document.getElementById("logo-icon"),
};

/* ─────────────────────────────────────────────────────────────────
   BLOC 2 — API
   ───────────────────────────────────────────────────────────────── */
const API = {
    async health() {
        const r = await fetch(`${CONFIG.API_BASE}/health`,
            { signal: AbortSignal.timeout(5000) });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
    },
    async predict(file) {
        const fd = new FormData();
        fd.append("file", file);
        const r = await fetch(`${CONFIG.API_BASE}/predict`, { method: "POST", body: fd });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
    },
    async random() {
        const r = await fetch(`${CONFIG.API_BASE}/random`);
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
    },
    async explain(classKey) {
        const r = await fetch(`${CONFIG.API_BASE}/explain/${classKey}`);
        if (!r.ok) return null;
        return r.json();
    },
    async sample(classKey) {
        const r = await fetch(`${CONFIG.API_BASE}/sample/${classKey}`);
        if (!r.ok) return null;
        return r.json();
    },
    async batch(files) {
        const fd = new FormData();
        files.forEach(f => fd.append("files", f));
        const r = await fetch(`${CONFIG.API_BASE}/batch`, { method: "POST", body: fd });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
    },
};

/* ─────────────────────────────────────────────────────────────────
   BLOC 3 — Toasts
   ───────────────────────────────────────────────────────────────── */
function showToast(message, type = "info") {
    if (!DOM.toastContainer) return;
    const existing = DOM.toastContainer.querySelectorAll(".toast:not(.removing)");
    if (existing.length >= 3) removeToast(existing[0]);

    const icons = { success: "check-circle", error: "x-circle", warning: "alert-triangle", info: "info" };
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<i data-lucide="${icons[type] || "info"}"></i><span>${message}</span>`;
    toast.addEventListener("click", () => removeToast(toast));
    DOM.toastContainer.appendChild(toast);
    if (typeof lucide !== "undefined") lucide.createIcons({ nodes: [toast] });

    setTimeout(() => removeToast(toast), CONFIG.TOAST_DURATION);
}

function removeToast(toast) {
    if (!toast || toast.classList.contains("removing")) return;
    toast.classList.add("removing");
    setTimeout(() => toast.remove(), 300);
}

/* ─────────────────────────────────────────────────────────────────
   BLOC 4 — API status
   ───────────────────────────────────────────────────────────────── */
async function checkApiStatus() {
    const el = DOM.apiStatus;
    if (!el) return;
    try {
        await API.health();
        el.className = "badge badge-status connected";
        el.innerHTML = `<span class="status-dot"></span> API Connected`;
    } catch {
        el.className = "badge badge-status disconnected";
        el.innerHTML = `<span class="status-dot"></span> API Offline`;
    }
}

/* ─────────────────────────────────────────────────────────────────
   BLOC 5 — File handling + MRI quality
   ───────────────────────────────────────────────────────────────── */
function handleFile(file) {
    if (!file) return;

    if (!CONFIG.VALID_TYPES.includes(file.type)) {
        showUploadError("Invalid format. Please use JPG or PNG.");
        return;
    }
    if (file.size > CONFIG.MAX_FILE_SIZE) {
        showUploadError("File too large. Maximum 10MB.");
        return;
    }

    AppState.currentFile = file;
    const url = URL.createObjectURL(file);
    if (DOM.previewImage) {
        DOM.previewImage.src = url;
        DOM.previewImage.classList.remove("hidden");
    }
    DOM.uploadContent?.classList.add("hidden");
    DOM.uploadZone?.classList.add("has-preview");

    if (DOM.uploadValidation) {
        DOM.uploadValidation.className = "upload-validation success";
        DOM.uploadValidation.textContent =
            `${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB) — Ready for analysis`;
        DOM.uploadValidation.classList.remove("hidden");
    }

    if (DOM.analyzeBtn) DOM.analyzeBtn.disabled = false;
    if (DOM.clearBtn)   DOM.clearBtn.disabled   = false;

    analyzeMRIQuality(file, ({ isMRI }) => {
        const badge = document.getElementById("mri-quality-badge");
        if (!badge) return;
        badge.className = "quality-badge " + (isMRI ? "quality-ok" : "quality-warn");
        badge.textContent = isMRI
            ? "✅ MRI-like image detected"
            : "⚠️ Image may not be an MRI scan";
        badge.classList.remove("hidden");
    });
}

function showUploadError(msg) {
    DOM.uploadZone?.classList.add("error");
    if (DOM.uploadValidation) {
        DOM.uploadValidation.className = "upload-validation error";
        DOM.uploadValidation.textContent = msg;
        DOM.uploadValidation.classList.remove("hidden");
    }
    setTimeout(() => {
        DOM.uploadZone?.classList.remove("error");
        DOM.uploadValidation?.classList.add("hidden");
    }, 3000);
}

function analyzeMRIQuality(file, callback) {
    const img = new Image();
    const url = URL.createObjectURL(file);
    img.onload = () => {
        const c = document.createElement("canvas");
        c.width = 64; c.height = 64;
        const ctx = c.getContext("2d");
        ctx.drawImage(img, 0, 0, 64, 64);
        const px = ctx.getImageData(0, 0, 64, 64).data;
        let dark = 0, sat = 0;
        for (let i = 0; i < px.length; i += 4) {
            const br = (px[i] + px[i + 1] + px[i + 2]) / 3;
            if (br < 50) dark++;
            sat += Math.max(px[i], px[i + 1], px[i + 2]) - Math.min(px[i], px[i + 1], px[i + 2]);
        }
        URL.revokeObjectURL(url);
        callback({ isMRI: dark / 4096 > 0.35 && sat / 4096 < 30 });
    };
    img.src = url;
}

/* ─────────────────────────────────────────────────────────────────
   BLOC 6 — Clear + Loader
   ───────────────────────────────────────────────────────────────── */
function clearUpload() {
    AppState.currentFile = null;
    if (DOM.previewImage) {
        DOM.previewImage.classList.add("hidden");
        DOM.previewImage.src = "";
    }
    DOM.uploadContent?.classList.remove("hidden");
    DOM.uploadZone?.classList.remove("has-preview", "error");
    DOM.uploadValidation?.classList.add("hidden");
    if (DOM.analyzeBtn) DOM.analyzeBtn.disabled = true;
    if (DOM.clearBtn)   DOM.clearBtn.disabled   = true;
    if (DOM.fileInput)  DOM.fileInput.value     = "";
    document.getElementById("mri-quality-badge")?.classList.add("hidden");
}

function showLoader() {
    DOM.loader?.classList.remove("hidden");
    DOM.resultsSection?.classList.add("hidden");
    DOM.logoIcon?.classList.add("analyzing");
    AppState.isLoading = true;
    if (DOM.analyzeBtn) {
        DOM.analyzeBtn.classList.add("loading");
        DOM.analyzeBtn.disabled = true;
    }
}

function hideLoader() {
    DOM.loader?.classList.add("hidden");
    DOM.logoIcon?.classList.remove("analyzing");
    AppState.isLoading = false;
    if (DOM.analyzeBtn) {
        DOM.analyzeBtn.classList.remove("loading");
        DOM.analyzeBtn.disabled = !AppState.currentFile;
    }
}

/* ─────────────────────────────────────────────────────────────────
   BLOC 7 — displayResults
   ───────────────────────────────────────────────────────────────── */
function displayResults(data) {
    DOM.resultsSection?.classList.remove("hidden");
    AppState.lastResult = { ...data };

    const predicted = data.predicted_class;
    const conf      = data.confidence ?? 0;
    const style     = CLASS_STYLES[predicted] || { cssClass: "", color: "#666" };

    if (DOM.predictionBadge) {
        DOM.predictionBadge.textContent = predicted;
        DOM.predictionBadge.className = `prediction-badge ${style.cssClass}`;
    }

    if (DOM.confidenceValue) DOM.confidenceValue.textContent = `${(conf * 100).toFixed(1)}%`;
    if (DOM.confidenceFill) {
        DOM.confidenceFill.style.width = `${conf * 100}%`;
        const lvl = conf >= 0.9 ? "high" : conf >= 0.7 ? "moderate" : "low";
        DOM.confidenceFill.className = `confidence-fill ${lvl}`;
    }

    if (DOM.alertLevel) {
        if (conf >= 0.85) {
            DOM.alertLevel.className = "alert-level high";
            DOM.alertLevel.textContent = "High diagnostic confidence";
        } else if (conf >= 0.60) {
            DOM.alertLevel.className = "alert-level moderate";
            DOM.alertLevel.textContent = "Moderate confidence — additional analysis recommended";
        } else {
            DOM.alertLevel.className = "alert-level low";
            DOM.alertLevel.textContent = "Low confidence — additional examinations needed";
        }
    }

    if (data.inference_time_ms) {
        DOM.inferenceTime?.classList.remove("hidden");
        const t = data.inference_time_ms;
        if (DOM.inferenceTimeValue) {
            DOM.inferenceTimeValue.textContent = t >= 1000
                ? `${(t / 1000).toFixed(2)}s`
                : `${t.toFixed(0)}ms`;
        }
    } else {
        DOM.inferenceTime?.classList.add("hidden");
    }

    const cacheBadge = document.getElementById("cache-badge");
    if (cacheBadge) {
        cacheBadge.classList.toggle("hidden", !data.from_cache);
        if (data.from_cache) showToast("Result from cache", "info");
    }

    updateChart(data.probabilities);

    if (data.original_image && DOM.gradcamOriginal) {
        DOM.gradcamOriginal.src = `data:image/jpeg;base64,${data.original_image}`;
    }
    if (data.gradcam_heatmap && DOM.gradcamHeatmap) {
        DOM.gradcamHeatmap.src = `data:image/png;base64,${data.gradcam_heatmap}`;
    }
    if (data.gradcam_overlay && DOM.gradcamOverlay) {
        DOM.gradcamOverlay.src = `data:image/png;base64,${data.gradcam_overlay}`;
    }
    if (data.gradcam_overlay && DOM.downloadGradcamBtn) {
        DOM.downloadGradcamBtn.disabled = false;
    }

    const explainCard    = document.getElementById("explain-card");
    const explainContent = document.getElementById("explain-content");
    if (explainCard && explainContent) {
        const key = predicted.toLowerCase().replace(/ /g, "_");
        API.explain(key).then(info => {
            if (!info) { explainCard.classList.add("hidden"); return; }
            explainCard.classList.remove("hidden");
            const sym = info.symptoms?.length
                ? `<p><strong>Symptoms:</strong> ${info.symptoms.join(", ")}</p>` : "";
            explainContent.innerHTML = `
                <div class="explain-body">
                    <p>${info.description}</p>
                    <p><strong>Prevalence:</strong> ${info.prevalence}</p>
                    <p><strong>Grade:</strong> ${info.grade}</p>
                    <p><strong>Typical MRI:</strong> ${info.typical_mri}</p>
                    ${sym}
                    <p class="urgency-tag" style="color:${info.color}">
                        <strong>Urgency:</strong> ${info.urgency}
                    </p>
                </div>`;
        }).catch(() => explainCard.classList.add("hidden"));
    }

    DOM.resultsSection?.scrollIntoView({ behavior: "smooth", block: "start" });

    if (typeof lucide !== "undefined") lucide.createIcons();
}

/* ─────────────────────────────────────────────────────────────────
   BLOC 8 — Chart
   ───────────────────────────────────────────────────────────────── */
function updateChart(probabilities) {
    if (!probabilities) return;
    const labels = Object.keys(probabilities);
    const values = Object.values(probabilities).map(v => parseFloat((v * 100).toFixed(1)));
    const colors = labels.map(l => CLASS_STYLES[l]?.color || "#666");

    const ctx = document.getElementById("probChart")?.getContext("2d");
    if (!ctx) return;

    if (AppState.probChart) AppState.probChart.destroy();

    const isDark    = document.documentElement.getAttribute("data-theme") === "dark";
    const textColor = isDark ? "#94A3B8" : "#334155";
    const gridColor = isDark ? "rgba(255,255,255,0.06)" : "#F1F5F9";

    AppState.probChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: colors.map(c => c + "33"),
                borderColor: colors,
                borderWidth: 2,
                borderRadius: 6,
                barPercentage: 0.78,
                categoryPercentage: 0.92,
                minBarLength: 4,
            }],
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            layout: { padding: { top: 8, bottom: 8, left: 0, right: 56 } },
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: c => ` ${parseFloat(c.raw).toFixed(2)}%` } },
            },
            scales: {
                x: {
                    min: 0, max: 100,
                    ticks: { callback: v => `${v}%`, color: textColor, font: { family: "Inter", size: 11 } },
                    grid: { color: gridColor, drawBorder: false },
                },
                y: {
                    ticks: { color: textColor, font: { family: "Inter", size: 13, weight: "700" }, padding: 6 },
                    grid: { display: false, drawBorder: false },
                },
            },
            animation: { duration: 700, easing: "easeOutQuart" },
        },
        plugins: [{
            id: "valueLabels",
            afterDatasetsDraw(chart) {
                const { ctx: c, data, chartArea, scales } = chart;
                chart.getDatasetMeta(0).data.forEach((bar, i) => {
                    const v = parseFloat(data.datasets[0].data[i]);
                    const label = `${v.toFixed(1)}%`;
                    const color = data.datasets[0].borderColor[i];
                    c.save();
                    c.font = "bold 12px Inter,sans-serif";
                    c.textBaseline = "middle";

                    // If bar fills > 60%, render label INSIDE the bar (right-aligned, white)
                    // Otherwise render OUTSIDE on the right (colored)
                    if (v >= 60) {
                        c.fillStyle = "#FFFFFF";
                        c.textAlign = "right";
                        c.shadowColor = "rgba(0,0,0,0.25)";
                        c.shadowBlur = 2;
                        c.fillText(label, bar.x - 8, bar.y);
                    } else {
                        c.fillStyle = color;
                        c.textAlign = "left";
                        const x = Math.max(bar.x + 6, scales.x.getPixelForValue(0) + 4);
                        c.fillText(label, x, bar.y);
                    }
                    c.restore();
                });
            }
        }],
    });
}

/* ─────────────────────────────────────────────────────────────────
   BLOC 9 — History (compress, save, load, addToHistory)
   ───────────────────────────────────────────────────────────────── */
function compressThumbnail(base64) {
    return new Promise(resolve => {
        const img = new Image();
        img.onload = () => {
            const c = document.createElement("canvas");
            c.width = 60; c.height = 60;
            c.getContext("2d").drawImage(img, 0, 0, 60, 60);
            resolve(c.toDataURL("image/jpeg", 0.5));
        };
        img.onerror = () => resolve(null);
        img.src = base64.startsWith("data:") ? base64 : `data:image/jpeg;base64,${base64}`;
    });
}

async function addToHistory(data) {
    const uid = Date.now().toString(36).toUpperCase()
              + Math.random().toString(36).substr(2, 3).toUpperCase();
    let thumb = null;
    if (data.original_image) thumb = await compressThumbnail(data.original_image);

    const entry = {
        uid,
        predicted_class:   data.predicted_class,
        confidence:        data.confidence,
        inference_time_ms: data.inference_time_ms || null,
        timestamp:         new Date().toLocaleString(),
        thumbnail:         thumb,
    };
    AppState.analysisHistory.unshift(entry);
    if (AppState.analysisHistory.length > CONFIG.MAX_HISTORY) AppState.analysisHistory.pop();
    saveHistory();
    AppState.currentPage = 1;
    renderHistoryWithPagination();
    updateSessionStats();
}

function saveHistory() {
    try {
        localStorage.setItem(CONFIG.STORAGE_KEY, JSON.stringify(AppState.analysisHistory));
    } catch (e) { console.warn("localStorage full", e); }
}

function loadHistory() {
    try {
        const s = localStorage.getItem(CONFIG.STORAGE_KEY);
        if (s) AppState.analysisHistory = JSON.parse(s);
    } catch { AppState.analysisHistory = []; }
    AppState.currentPage = 1;
    renderHistoryWithPagination();
    updateSessionStats();
}

/* ─────────────────────────────────────────────────────────────────
   BLOC 10 — Filters · Pagination · Render
   ───────────────────────────────────────────────────────────────── */
function getFilteredEntries() {
    return AppState.analysisHistory.filter(e => {
        if (activeFilters.classFilter !== "all" && e.predicted_class !== activeFilters.classFilter) return false;
        const ts = new Date(e.timestamp);
        if (activeFilters.dateFrom && ts < new Date(activeFilters.dateFrom + "T00:00:00")) return false;
        if (activeFilters.dateTo   && ts > new Date(activeFilters.dateTo   + "T23:59:59")) return false;
        const pct = (e.confidence ?? 0) * 100;
        if (pct < activeFilters.confMin) return false;
        if (pct > activeFilters.confMax) return false;
        return true;
    });
}

function applyFilters() {
    AppState.currentPage = 1;
    const filtered = getFilteredEntries();
    const countEl = document.getElementById("filter-count");
    if (countEl) {
        countEl.textContent = filtered.length < AppState.analysisHistory.length
            ? `${filtered.length} / ${AppState.analysisHistory.length}` : "";
    }
    renderHistoryWithPagination(filtered);
}

function initHistoryFilters() {
    document.querySelectorAll(".filter-class-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".filter-class-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            activeFilters.classFilter = btn.dataset.class;
            applyFilters();
        });
    });

    document.getElementById("filter-date-from")?.addEventListener("change", e => {
        activeFilters.dateFrom = e.target.value; applyFilters();
    });
    document.getElementById("filter-date-to")?.addEventListener("change", e => {
        activeFilters.dateTo = e.target.value; applyFilters();
    });

    const sanitize = (v, fb) => {
        const n = parseInt(v, 10);
        return isNaN(n) ? fb : Math.max(0, Math.min(100, n));
    };
    document.getElementById("filter-conf-min")?.addEventListener("input", e => {
        const v = sanitize(e.target.value, 0);
        e.target.value = v;
        activeFilters.confMin = v;
        if (v > activeFilters.confMax) {
            activeFilters.confMax = v;
            const el = document.getElementById("filter-conf-max");
            if (el) el.value = v;
        }
        applyFilters();
    });
    document.getElementById("filter-conf-max")?.addEventListener("input", e => {
        const v = sanitize(e.target.value, 100);
        e.target.value = v;
        activeFilters.confMax = v;
        if (v < activeFilters.confMin) {
            activeFilters.confMin = v;
            const el = document.getElementById("filter-conf-min");
            if (el) el.value = v;
        }
        applyFilters();
    });

    document.getElementById("filter-reset-btn")?.addEventListener("click", () => {
        Object.assign(activeFilters, { classFilter: "all", dateFrom: "", dateTo: "", confMin: 0, confMax: 100 });
        document.querySelectorAll(".filter-class-btn").forEach(b => b.classList.remove("active"));
        document.querySelector('.filter-class-btn[data-class="all"]')?.classList.add("active");
        ["filter-date-from", "filter-date-to"].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = "";
        });
        const cmi = document.getElementById("filter-conf-min");
        const cma = document.getElementById("filter-conf-max");
        if (cmi) cmi.value = "0";
        if (cma) cma.value = "100";
        applyFilters();
    });
}

function renderHistoryRows(entries) {
    const pageOffset = (AppState.currentPage - 1) * AppState.itemsPerPage;
    const totalFiltered = getFilteredEntries().length;
    if (!DOM.historyBody) return;
    DOM.historyBody.innerHTML = entries.map((entry, idx) => {
        const style = CLASS_STYLES[entry.predicted_class] || { cssClass: "", color: "#666" };
        const initials = entry.predicted_class.split(" ").map(w => w[0]).join("");
        const thumbHtml = entry.thumbnail
            ? `<img class="thumb" src="${entry.thumbnail}" alt="">`
            : `<div class="thumb thumb-placeholder ${style.cssClass}">${initials}</div>`;
        const timeStr = entry.inference_time_ms
            ? (entry.inference_time_ms >= 1000
                ? `${(entry.inference_time_ms / 1000).toFixed(2)}s`
                : `${entry.inference_time_ms.toFixed(0)}ms`)
            : "--";
        const displayNum = totalFiltered - pageOffset - idx;
        return `
            <tr class="${idx === 0 && AppState.currentPage === 1 ? "latest" : ""}">
                <td>${displayNum}</td>
                <td>${thumbHtml}</td>
                <td><span class="class-tag ${style.cssClass}">${entry.predicted_class}</span></td>
                <td>${(entry.confidence * 100).toFixed(1)}%</td>
                <td>${timeStr}</td>
                <td>${entry.timestamp}</td>
            </tr>`;
    }).join("");
}

function renderHistoryWithPagination(entries = null) {
    const filtered = entries || getFilteredEntries();
    const totalPages = Math.max(1, Math.ceil(filtered.length / AppState.itemsPerPage));
    if (AppState.currentPage > totalPages) AppState.currentPage = totalPages;
    if (AppState.currentPage < 1) AppState.currentPage = 1;

    const start = (AppState.currentPage - 1) * AppState.itemsPerPage;
    const pageEntries = filtered.slice(start, start + AppState.itemsPerPage);

    if (filtered.length === 0 && AppState.analysisHistory.length === 0) {
        DOM.historyEmpty?.classList.remove("hidden");
        DOM.historyTable?.classList.add("hidden");
        document.getElementById("pagination-wrapper")?.classList.add("hidden");
        document.getElementById("session-stats")?.classList.add("hidden");
    } else {
        DOM.historyEmpty?.classList.add("hidden");
        DOM.historyTable?.classList.remove("hidden");
        renderHistoryRows(pageEntries);
        if (DOM.exportCsvBtn)    DOM.exportCsvBtn.disabled    = false;
        if (DOM.clearHistoryBtn) DOM.clearHistoryBtn.disabled = false;
    }

    const infoEl = document.getElementById("pagination-info");
    if (infoEl) {
        if (filtered.length === 0) {
            infoEl.textContent = "No results";
        } else {
            const s = start + 1;
            const e = Math.min(start + AppState.itemsPerPage, filtered.length);
            infoEl.textContent = filtered.length < AppState.analysisHistory.length
                ? `${s}–${e} of ${filtered.length} (filtered)`
                : `${s}–${e} of ${filtered.length}`;
        }
    }

    const cur  = AppState.currentPage;
    const btnF = document.getElementById("page-first");
    const btnP = document.getElementById("page-prev");
    const btnN = document.getElementById("page-next");
    const btnL = document.getElementById("page-last");
    if (btnF) btnF.disabled = cur <= 1;
    if (btnP) btnP.disabled = cur <= 1;
    if (btnN) btnN.disabled = cur >= totalPages;
    if (btnL) btnL.disabled = cur >= totalPages;
    renderPageNumbers(cur, totalPages);

    const wrapper = document.getElementById("pagination-wrapper");
    if (wrapper) wrapper.classList.toggle("hidden", filtered.length <= AppState.itemsPerPage);
}

function renderPageNumbers(current, total) {
    const container = document.getElementById("page-numbers");
    if (!container) return;
    if (total <= 1) { container.innerHTML = ""; return; }

    const range = [];
    for (let i = 1; i <= total; i++) {
        if (i === 1 || i === total || (i >= current - 2 && i <= current + 2)) range.push(i);
    }
    let prev = 0;
    const pages = [];
    range.forEach(p => {
        if (p - prev > 1) pages.push("...");
        pages.push(p);
        prev = p;
    });

    container.innerHTML = "";
    pages.forEach(p => {
        if (p === "...") {
            const s = document.createElement("span");
            s.className = "page-ellipsis";
            s.textContent = "…";
            container.appendChild(s);
            return;
        }
        const btn = document.createElement("button");
        btn.className = "page-btn" + (p === current ? " active" : "");
        btn.textContent = p;
        btn.addEventListener("click", () => {
            AppState.currentPage = p;
            renderHistoryWithPagination();
        });
        container.appendChild(btn);
    });
}

/* ─────────────────────────────────────────────────────────────────
   BLOC 11 — Session stats + CSV export
   ───────────────────────────────────────────────────────────────── */
function updateSessionStats() {
    const statsSection = document.getElementById("session-stats");
    const statsGrid    = document.getElementById("stats-grid");
    const h = AppState.analysisHistory;
    if (!statsSection || !statsGrid) return;
    if (h.length === 0) { statsSection.classList.add("hidden"); return; }
    statsSection.classList.remove("hidden");

    const freq = {};
    h.forEach(e => freq[e.predicted_class] = (freq[e.predicted_class] || 0) + 1);
    const top = Object.entries(freq).sort((a, b) => b[1] - a[1])[0];
    const avgConf = (h.reduce((s, e) => s + e.confidence, 0) / h.length * 100).toFixed(1);
    const timings = h.filter(e => e.inference_time_ms);
    const avgTime = timings.length
        ? (timings.reduce((s, e) => s + e.inference_time_ms, 0) / timings.length).toFixed(0) + "ms"
        : "--";

    statsGrid.innerHTML = `
        <div class="stat-item">
            <span class="stat-label">Total analyses</span>
            <span class="stat-value">${h.length}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Most frequent</span>
            <span class="stat-value">${top[0]} <small>(${top[1]}×)</small></span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Avg confidence</span>
            <span class="stat-value">${avgConf}%</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Avg time</span>
            <span class="stat-value">${avgTime}</span>
        </div>`;
}

function exportCSV() {
    const h = AppState.analysisHistory;
    if (!h.length) return;
    const rows = ["#,Prediction,Confidence,Time,Timestamp",
        ...h.map((e, i) => [
            i + 1,
            e.predicted_class,
            `${(e.confidence * 100).toFixed(1)}%`,
            e.inference_time_ms ? `${e.inference_time_ms.toFixed(0)}ms` : "--",
            e.timestamp
        ].join(","))
    ].join("\n");
    const blob = new Blob([rows], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `brainscan_history_${Date.now()}.csv`;
    a.click();
    showToast("CSV exported", "success");
}

/* ─────────────────────────────────────────────────────────────────
   BLOC 12 — Zoom modal · Dark mode · Opacity slider
   ───────────────────────────────────────────────────────────────── */
function initZoomModal() {
    const modal    = document.getElementById("zoom-modal");
    const zoomImg  = document.getElementById("zoom-image");
    const zoomLbl  = document.getElementById("zoom-label");
    const closeBtn = document.getElementById("zoom-close");
    const backdrop = modal?.querySelector(".modal-backdrop");

    document.querySelectorAll(".gradcam-item img").forEach(img => {
        img.style.cursor = "zoom-in";
        img.addEventListener("click", () => {
            if (!img.src || img.src.endsWith("undefined")) return;
            if (zoomImg) zoomImg.src = img.src;
            if (zoomLbl) zoomLbl.textContent = img.nextElementSibling?.textContent || "";
            modal?.classList.remove("hidden");
        });
    });
    closeBtn?.addEventListener("click", () => modal?.classList.add("hidden"));
    backdrop?.addEventListener("click", () => modal?.classList.add("hidden"));
    document.addEventListener("keydown", e => {
        if (e.key === "Escape") {
            modal?.classList.add("hidden");
            document.getElementById("compare-modal")?.classList.add("hidden");
            document.getElementById("batch-modal")?.classList.add("hidden");
        }
    });
}

function initDarkMode() {
    const btn  = document.getElementById("theme-toggle");
    const icon = document.getElementById("theme-icon");
    const saved = localStorage.getItem("brainscan_theme") || "light";
    document.documentElement.setAttribute("data-theme", saved);
    if (icon) icon.setAttribute("data-lucide", saved === "dark" ? "sun" : "moon");
    if (typeof lucide !== "undefined") lucide.createIcons();

    btn?.addEventListener("click", () => {
        const cur  = document.documentElement.getAttribute("data-theme");
        const next = cur === "dark" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", next);
        localStorage.setItem("brainscan_theme", next);
        if (icon) icon.setAttribute("data-lucide", next === "dark" ? "sun" : "moon");
        if (typeof lucide !== "undefined") lucide.createIcons();
        // Refresh chart colors
        if (AppState.lastResult?.probabilities) updateChart(AppState.lastResult.probabilities);
    });
}

function initOpacitySlider() {
    DOM.opacitySlider?.addEventListener("input", e => {
        const val = e.target.value / 100;
        const heatmap = document.querySelector(".gradcam-heatmap-img");
        if (heatmap) heatmap.style.opacity = val;
        if (DOM.opacityValue) DOM.opacityValue.textContent = `${e.target.value}%`;
    });
    DOM.downloadGradcamBtn?.addEventListener("click", () => {
        if (!DOM.gradcamOverlay?.src || DOM.gradcamOverlay.src.endsWith("undefined")) return;
        const a = document.createElement("a");
        a.href = DOM.gradcamOverlay.src;
        a.download = `brainscan_gradcam_${Date.now()}.png`;
        a.click();
    });
}

/* ─────────────────────────────────────────────────────────────────
   BLOC 13 — Export PNG + PDF
   ───────────────────────────────────────────────────────────────── */
async function exportResultAsPNG() {
    const data = AppState.lastResult;
    if (!data) { showToast("No result to share", "warning"); return; }

    const canvas = document.createElement("canvas");
    canvas.width = 800; canvas.height = 420;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#0A2540";
    ctx.fillRect(0, 0, 800, 420);

    ctx.fillStyle = "#FFFFFF";
    ctx.font = "bold 22px Inter,sans-serif";
    ctx.fillText("BrainScan AI", 20, 35);

    ctx.font = "12px Inter,sans-serif";
    ctx.fillStyle = "#94A3B8";
    ctx.fillText(new Date().toLocaleString(), 20, 52);

    if (DOM.gradcamOriginal?.src?.startsWith("data:")) {
        const img = new Image();
        img.src = DOM.gradcamOriginal.src;
        await new Promise(r => { img.onload = r; img.onerror = r; });
        try { ctx.drawImage(img, 20, 65, 180, 180); } catch (_) {}
    }
    if (DOM.gradcamOverlay?.src?.startsWith("data:")) {
        const img = new Image();
        img.src = DOM.gradcamOverlay.src;
        await new Promise(r => { img.onload = r; img.onerror = r; });
        try { ctx.drawImage(img, 215, 65, 180, 180); } catch (_) {}
    }

    const style = CLASS_STYLES[data.predicted_class] || { color: "#FFFFFF" };
    ctx.fillStyle = style.color;
    ctx.font = "bold 30px Inter,sans-serif";
    ctx.fillText(data.predicted_class, 415, 110);

    ctx.fillStyle = "#FFFFFF";
    ctx.font = "bold 42px Inter,sans-serif";
    ctx.fillText(`${(data.confidence * 100).toFixed(1)}%`, 415, 165);

    ctx.font = "11px Inter,sans-serif";
    ctx.fillStyle = "#64748B";
    ctx.fillText("For research only — not a medical diagnosis", 20, 408);

    const a = document.createElement("a");
    a.download = `brainscan_result_${Date.now()}.png`;
    a.href = canvas.toDataURL("image/png");
    a.click();
    showToast("PNG saved", "success");
}

function exportPDF() {
    const data = AppState.lastResult;
    if (!data) { showToast("No result to export", "warning"); return; }
    if (typeof window.jspdf === "undefined") { showToast("jsPDF not loaded", "error"); return; }

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    const M = 14, W = 210;

    // Header
    doc.setFillColor(10, 37, 64);
    doc.rect(0, 0, W, 30, "F");
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(17);
    doc.text("BrainScan AI — Diagnostic Report", M, 13);
    doc.setFontSize(8);
    doc.setTextColor(180, 220, 255);
    doc.text(`Generated: ${new Date().toLocaleString()}`, M, 22);
    doc.text("ResNet50 · 98.96% Accuracy", W - M, 22, { align: "right" });

    let yContent = 38;
    const origB64 = data.original_image
        ? (data.original_image.startsWith("data:") ? data.original_image : "data:image/jpeg;base64," + data.original_image)
        : null;
    const ovB64 = data.gradcam_overlay
        ? (data.gradcam_overlay.startsWith("data:") ? data.gradcam_overlay : "data:image/png;base64," + data.gradcam_overlay)
        : null;

    if (origB64 || ovB64) {
        yContent = 116;
        if (origB64) {
            try { doc.addImage(origB64, "JPEG", M, 36, 68, 68); } catch (e) { console.warn(e); }
            doc.setFontSize(8); doc.setTextColor(120, 120, 120);
            doc.text("Original MRI", M + 34, 108, { align: "center" });
        }
        if (ovB64) {
            try { doc.addImage(ovB64, "PNG", M + 76, 36, 68, 68); } catch (e) { console.warn(e); }
            doc.setFontSize(8); doc.setTextColor(120, 120, 120);
            doc.text("Grad-CAM Overlay", M + 76 + 34, 108, { align: "center" });
        }
    }

    const style = CLASS_STYLES[data.predicted_class] || { color: "#666666" };
    const rgb = [
        parseInt(style.color.slice(1, 3), 16),
        parseInt(style.color.slice(3, 5), 16),
        parseInt(style.color.slice(5, 7), 16),
    ];
    doc.setFontSize(16); doc.setTextColor(rgb[0], rgb[1], rgb[2]);
    doc.text(`Prediction: ${data.predicted_class}`, M, yContent);

    doc.setFontSize(11); doc.setTextColor(71, 85, 105);
    let y = yContent + 10;
    doc.text(`Confidence: ${(data.confidence * 100).toFixed(1)}%`, M, y); y += 8;
    if (data.inference_time_ms) {
        doc.text(`Inference: ${data.inference_time_ms.toFixed(0)}ms`, M, y); y += 8;
    }

    y += 4;
    doc.setFontSize(13); doc.setTextColor(15, 23, 42);
    doc.text("Class Probabilities", M, y); y += 8;
    doc.setFontSize(10);

    if (data.probabilities) {
        Object.entries(data.probabilities).sort((a, b) => b[1] - a[1]).forEach(([cls, prob]) => {
            const s = CLASS_STYLES[cls] || { color: "#666666" };
            const cr = [
                parseInt(s.color.slice(1, 3), 16),
                parseInt(s.color.slice(3, 5), 16),
                parseInt(s.color.slice(5, 7), 16),
            ];
            doc.setTextColor(71, 85, 105);
            doc.text(`${cls}: ${(prob * 100).toFixed(1)}%`, M, y);
            doc.setFillColor(220, 220, 220);
            doc.rect(M + 50, y - 3.5, 90, 5, "F");
            doc.setFillColor(cr[0], cr[1], cr[2]);
            if (prob * 90 > 0) doc.rect(M + 50, y - 3.5, prob * 90, 5, "F");
            y += 10;
        });
    }

    doc.setFillColor(255, 243, 205);
    doc.rect(M, 268, W - M * 2, 16, "F");
    doc.setFontSize(8); doc.setTextColor(160, 90, 0);
    doc.text("⚠ For research only — not a medical diagnosis.", M + 2, 275);
    doc.text("Always consult a qualified healthcare professional.", M + 2, 281);

    doc.save(`BrainScan_${data.predicted_class}_${Date.now()}.pdf`);
    showToast("PDF exported", "success");
}

/* ─────────────────────────────────────────────────────────────────
   BLOC 14 — Compare mode
   ───────────────────────────────────────────────────────────────── */
function buildCompareSlot(side) {
    return `
        <h3 style="font-size:1rem;font-weight:600;color:var(--text-primary);margin-bottom:1rem">Image ${side}</h3>
        <div class="compare-upload">
            <button type="button" class="btn btn-secondary btn-sm" data-compare-trigger="${side}">
                Select Image ${side}
            </button>
            <input type="file" id="compare-input-${side}" accept=".jpg,.jpeg,.png" hidden>
            <img id="compare-preview-${side}" alt=""
                 style="display:none;max-width:100%;max-height:160px;border-radius:var(--radius-sm);object-fit:contain">
        </div>
        <div id="compare-result-${side}" class="compare-result-card" style="display:none"></div>`;
}

function buildCompareResult(data) {
    const style = CLASS_STYLES[data.predicted_class] || { cssClass: "", color: "#666" };
    return `
        <div style="display:block">
            <span class="prediction-badge ${style.cssClass}" style="display:inline-block;margin-bottom:0.5rem">
                ${data.predicted_class}
            </span>
            <div class="confidence-value" style="font-size:1.5rem">
                ${(data.confidence * 100).toFixed(1)}%
            </div>
        </div>`;
}

function initCompareMode() {
    const modal    = document.getElementById("compare-modal");
    const closeBtn = document.getElementById("compare-close");
    const backdrop = modal?.querySelector(".modal-backdrop");
    const leftDiv  = document.getElementById("compare-left");
    const rightDiv = document.getElementById("compare-right");

    document.getElementById("compare-btn")?.addEventListener("click", () => {
        if (leftDiv)  leftDiv.innerHTML  = buildCompareSlot("A");
        if (rightDiv) rightDiv.innerHTML = buildCompareSlot("B");

        // Add a single Analyze Both button at the bottom of right slot if missing
        if (rightDiv && !document.getElementById("compare-run-btn")) {
            const runBtn = document.createElement("button");
            runBtn.id = "compare-run-btn";
            runBtn.className = "btn btn-primary btn-sm";
            runBtn.style.cssText = "margin-top:1rem;width:100%";
            runBtn.innerHTML = `<i data-lucide="play"></i> <span>Analyze Both</span>`;
            rightDiv.appendChild(runBtn);
        }

        modal?.classList.remove("hidden");

        // Wire triggers (button → input)
        document.querySelectorAll("[data-compare-trigger]").forEach(b => {
            b.addEventListener("click", () => {
                document.getElementById(`compare-input-${b.dataset.compareTrigger}`)?.click();
            });
        });

        ["A", "B"].forEach(side => {
            const inp  = document.getElementById(`compare-input-${side}`);
            const prev = document.getElementById(`compare-preview-${side}`);
            inp?.addEventListener("change", e => {
                const f = e.target.files?.[0];
                if (!f) return;
                AppState[side === "A" ? "compareFileA" : "compareFileB"] = f;
                if (prev) {
                    prev.src = URL.createObjectURL(f);
                    prev.style.display = "block";
                }
            });
        });

        document.getElementById("compare-run-btn")?.addEventListener("click", async () => {
            const fA = AppState.compareFileA;
            const fB = AppState.compareFileB;
            if (!fA || !fB) { showToast("Please select both images", "warning"); return; }
            try {
                showToast("Analyzing both images...", "info");
                const [rA, rB] = await Promise.all([API.predict(fA), API.predict(fB)]);
                const resA = document.getElementById("compare-result-A");
                const resB = document.getElementById("compare-result-B");
                if (resA) { resA.innerHTML = buildCompareResult(rA); resA.style.display = "block"; }
                if (resB) { resB.innerHTML = buildCompareResult(rB); resB.style.display = "block"; }
            } catch (e) {
                showToast("Analysis failed: " + e.message, "error");
            }
        });

        if (typeof lucide !== "undefined") lucide.createIcons();
    });

    closeBtn?.addEventListener("click", () => modal?.classList.add("hidden"));
    backdrop?.addEventListener("click", () => modal?.classList.add("hidden"));
}

/* ─────────────────────────────────────────────────────────────────
   BLOC 15 — Batch analysis
   ───────────────────────────────────────────────────────────────── */
function initBatchAnalysis() {
    const modal    = document.getElementById("batch-modal");
    const closeBtn = document.getElementById("batch-close");
    const backdrop = document.getElementById("batch-backdrop");
    const dropZone = document.getElementById("batch-drop-zone");
    const fileInp  = document.getElementById("batch-file-input");
    const runBtn   = document.getElementById("batch-run-btn");
    const expBtn   = document.getElementById("batch-export-btn");

    document.getElementById("batch-btn")?.addEventListener("click", () => {
        modal?.classList.remove("hidden");
        if (typeof lucide !== "undefined") lucide.createIcons();
    });
    closeBtn?.addEventListener("click", () => modal?.classList.add("hidden"));
    backdrop?.addEventListener("click", () => modal?.classList.add("hidden"));

    dropZone?.addEventListener("click", () => fileInp?.click());
    dropZone?.addEventListener("dragover", e => {
        e.preventDefault();
        dropZone.style.borderColor = "var(--cyan)";
    });
    dropZone?.addEventListener("dragleave", () => { dropZone.style.borderColor = ""; });
    dropZone?.addEventListener("drop", e => {
        e.preventDefault();
        dropZone.style.borderColor = "";
        const files = Array.from(e.dataTransfer.files).filter(f => CONFIG.VALID_TYPES.includes(f.type));
        setBatchFiles(files);
    });

    fileInp?.addEventListener("change", e => {
        setBatchFiles(Array.from(e.target.files));
    });

    function setBatchFiles(files) {
        AppState.batchFiles = files;
        const listEl = document.getElementById("batch-file-list");
        if (listEl) {
            listEl.style.display = files.length ? "block" : "none";
            listEl.innerHTML = files.map(f =>
                `<div class="batch-file-item">📎 ${f.name}</div>`
            ).join("");
        }
        if (runBtn) runBtn.disabled = files.length === 0;
    }

    runBtn?.addEventListener("click", async () => {
        if (!AppState.batchFiles.length) return;
        const progress     = document.getElementById("batch-progress");
        const progressBar  = document.getElementById("batch-progress-bar");
        const progressText = document.getElementById("batch-progress-text");
        const resultsDiv   = document.getElementById("batch-results-table");
        if (progress) progress.style.display = "block";

        AppState.batchResults = [];
        let done = 0;

        for (const file of AppState.batchFiles) {
            try {
                const r = await API.predict(file);
                r.filename = file.name;
                AppState.batchResults.push(r);
                await addToHistory(r);
            } catch (e) {
                AppState.batchResults.push({
                    filename: file.name,
                    predicted_class: "Error",
                    confidence: 0,
                    error: e.message,
                });
            }
            done++;
            const pct = (done / AppState.batchFiles.length * 100).toFixed(0);
            if (progressBar)  progressBar.style.width = `${pct}%`;
            if (progressText) progressText.textContent = `${done}/${AppState.batchFiles.length} analyzed`;
        }

        if (resultsDiv) {
            resultsDiv.style.display = "block";
            resultsDiv.innerHTML = `
                <table>
                    <thead>
                        <tr>
                            <th>File</th>
                            <th>Prediction</th>
                            <th>Confidence</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${AppState.batchResults.map(r => `
                            <tr>
                                <td>${r.filename}</td>
                                <td>${r.error || r.predicted_class}</td>
                                <td>${r.confidence ? (r.confidence * 100).toFixed(1) + "%" : "--"}</td>
                            </tr>`).join("")}
                    </tbody>
                </table>`;
        }
        if (expBtn) expBtn.disabled = false;
        showToast(`${done} images analyzed`, "success");
    });

    expBtn?.addEventListener("click", () => {
        if (!AppState.batchResults.length) return;
        const rows = ["Filename,Prediction,Confidence",
            ...AppState.batchResults.map(r =>
                `${r.filename},${r.predicted_class || "Error"},`
                + `${r.confidence ? (r.confidence * 100).toFixed(1) + "%" : "--"}`)
        ].join("\n");
        const blob = new Blob([rows], { type: "text/csv" });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = `batch_results_${Date.now()}.csv`;
        a.click();
        showToast("Batch CSV exported", "success");
    });
}

/* ─────────────────────────────────────────────────────────────────
   BLOC 16 — Main listeners + DOMContentLoaded
   ───────────────────────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
    if (typeof lucide !== "undefined") lucide.createIcons();

    initDarkMode();
    loadHistory();
    initHistoryFilters();
    initZoomModal();
    initCompareMode();
    initBatchAnalysis();
    initOpacitySlider();
    checkApiStatus();
    setInterval(checkApiStatus, CONFIG.HEALTH_INTERVAL);

    // Upload zone events
    DOM.uploadZone?.addEventListener("click", e => {
        if (!e.target.closest("img")) DOM.fileInput?.click();
    });
    DOM.uploadZone?.addEventListener("dragover", e => {
        e.preventDefault();
        DOM.uploadZone.classList.add("dragover");
    });
    DOM.uploadZone?.addEventListener("dragleave", () => DOM.uploadZone?.classList.remove("dragover"));
    DOM.uploadZone?.addEventListener("drop", e => {
        e.preventDefault();
        DOM.uploadZone?.classList.remove("dragover");
        const f = e.dataTransfer.files[0];
        if (f) handleFile(f);
    });
    DOM.fileInput?.addEventListener("change", e => {
        if (e.target.files[0]) handleFile(e.target.files[0]);
    });

    // Analyze button
    DOM.analyzeBtn?.addEventListener("click", async () => {
        if (!AppState.currentFile || AppState.isLoading) return;
        showLoader();
        try {
            const data = await API.predict(AppState.currentFile);
            hideLoader();
            displayResults(data);
            await addToHistory(data);
            showToast(
                `Detected: ${data.predicted_class} (${(data.confidence * 100).toFixed(1)}%)`,
                data.confidence >= 0.85 ? "success" : "warning"
            );
        } catch (e) {
            hideLoader();
            showToast(`Analysis failed: ${e.message}`, "error");
        }
    });

    // Random button
    DOM.randomBtn?.addEventListener("click", async () => {
        if (AppState.isLoading) return;
        showLoader();
        try {
            const data = await API.random();
            if (data.original_image) {
                const src = data.original_image.startsWith("data:")
                    ? data.original_image
                    : `data:image/jpeg;base64,${data.original_image}`;
                if (DOM.previewImage) {
                    DOM.previewImage.src = src;
                    DOM.previewImage.classList.remove("hidden");
                }
                DOM.uploadContent?.classList.add("hidden");
                DOM.uploadZone?.classList.add("has-preview");
            }
            hideLoader();
            displayResults(data);
            await addToHistory(data);
            showToast(
                `Random: ${data.predicted_class} — True: ${data.true_class || "?"}`,
                data.predicted_class === data.true_class ? "success" : "warning"
            );
        } catch (e) {
            hideLoader();
            showToast(`Failed: ${e.message}`, "error");
        }
    });

    // Clear button
    DOM.clearBtn?.addEventListener("click", clearUpload);

    // History buttons
    DOM.clearHistoryBtn?.addEventListener("click", () => {
        AppState.analysisHistory = [];
        localStorage.removeItem(CONFIG.STORAGE_KEY);
        AppState.currentPage = 1;
        renderHistoryWithPagination();
        updateSessionStats();
        showToast("History cleared", "info");
    });
    DOM.exportCsvBtn?.addEventListener("click", exportCSV);

    // Export buttons
    document.getElementById("export-png-btn")?.addEventListener("click", exportResultAsPNG);
    document.getElementById("export-pdf-btn")?.addEventListener("click", exportPDF);

    // Pagination buttons
    document.getElementById("page-first")?.addEventListener("click", () => {
        AppState.currentPage = 1; renderHistoryWithPagination();
    });
    document.getElementById("page-prev")?.addEventListener("click", () => {
        if (AppState.currentPage > 1) AppState.currentPage--;
        renderHistoryWithPagination();
    });
    document.getElementById("page-next")?.addEventListener("click", () => {
        AppState.currentPage++; renderHistoryWithPagination();
    });
    document.getElementById("page-last")?.addEventListener("click", () => {
        const total = Math.ceil(getFilteredEntries().length / AppState.itemsPerPage);
        AppState.currentPage = Math.max(1, total);
        renderHistoryWithPagination();
    });
    document.getElementById("items-per-page")?.addEventListener("change", e => {
        AppState.itemsPerPage = parseInt(e.target.value, 10);
        AppState.currentPage = 1;
        renderHistoryWithPagination();
    });

    // Keyboard navigation (Alt + arrows)
    document.addEventListener("keydown", e => {
        const tag = document.activeElement?.tagName;
        if (["INPUT", "SELECT", "TEXTAREA"].includes(tag)) return;
        if (e.altKey && e.key === "ArrowRight") {
            AppState.currentPage++;
            renderHistoryWithPagination();
        }
        if (e.altKey && e.key === "ArrowLeft") {
            if (AppState.currentPage > 1) AppState.currentPage--;
            renderHistoryWithPagination();
        }
    });
});
