# 🗺 interface/ FLOW — Du chargement page à la prédiction affichée

> Trajet complet d'une analyse côté client.

---

## 🌐 Chargement initial de la page

```
   Browser visite http://localhost:3000
        │
        ▼
1️⃣  index.html chargé
        ├─ <script Chart.js> (CDN jsdelivr)
        ├─ <script Lucide>   (CDN unpkg)
        ├─ <script jsPDF>    (CDN cloudflare)
        └─ <link styles.css> (local)
        │
        ▼
2️⃣  app.js exécuté (DOMContentLoaded)
        ├─ lucide.createIcons()             ← icônes SVG remplacées
        ├─ initDarkMode()                   ← lit localStorage["brainscan_theme"]
        ├─ loadHistory()                    ← lit localStorage["brainscan_history_v2"]
        ├─ initHistoryFilters()             ← attache events filtres/pagination
        ├─ initZoomModal()                  ← clic sur Grad-CAM = modal full-screen
        ├─ initCompareMode()                ← bouton Compare + modal
        ├─ initBatchAnalysis()              ← bouton Batch + modal
        ├─ initOpacitySlider()              ← contrôle opacité Grad-CAM
        ├─ checkApiStatus()                 ← GET /health (badge vert/rouge)
        └─ setInterval(checkApiStatus, 30s) ← polling permanent
        │
        ▼
✅ UI prête → user voit "API Connected" en vert
```

---

## 🔍 Pipeline d'analyse (de l'upload au résultat)

```
1️⃣  User drag & drop IRM (ou click → file picker)
        │
        ▼
2️⃣  handleFile(file) [BLOC 5]
        ├─ valider type ∈ {jpeg, png, jpg}      → sinon toast erreur
        ├─ valider taille ≤ 10 MB                → sinon toast erreur
        ├─ AppState.currentFile = file
        ├─ Affichage preview (FileReader)
        └─ analyzeMRIQuality(file)              ← canvas heuristique 64×64
              │
              ├─ darkRatio > 0.35 + sat < 30 ?
              ▼
        ✅ Badge "MRI-like detected"
        │
        ▼
3️⃣  User clique "Analyze" (ou "Random Example")
        │
        ▼
4️⃣  showLoader() + fetch POST /predict avec FormData
        │
        ▼ (~150 ms)
5️⃣  Réponse JSON reçue
        │
        ▼
6️⃣  displayResults(data) [BLOC 7]
        ├─ predictionBadge ← classe + couleur CSS
        ├─ confidenceValue ← %
        ├─ confidenceFill width + classe (high/moderate/low)
        ├─ alertLevel ← "High" / "Moderate" / "Low"
        ├─ inferenceTime + cacheBadge si data.from_cache
        ├─ updateChart(data.probabilities) [BLOC 8]
        │     └─ Chart.js horizontal bars + plugin labels
        ├─ Grad-CAM images (3 colonnes : original/heatmap/overlay)
        └─ fetch GET /explain/{class} → accordion infos médicales
        │
        ▼
7️⃣  addToHistory(data) [BLOC 9]
        ├─ uid = Date.now().toString(36) + random()
        ├─ compressThumbnail(base64) → 60×60 JPEG quality 0.5
        ├─ AppState.analysisHistory.unshift(entry)
        ├─ trim si > 100 entrées
        ├─ saveHistory() → localStorage
        ├─ renderHistoryWithPagination() [BLOC 10]
        └─ updateSessionStats() [BLOC 11]
        │
        ▼
8️⃣  scrollIntoView({ behavior: "smooth" })
        │
        ▼
✅ Résultat visible · historique mis à jour · stats actualisées
```

---

## 💾 Persistance localStorage

```
brainscan_history_v2  ← liste des analyses (max 100)
        ├─ uid, predicted_class, confidence
        ├─ inference_time_ms, timestamp
        └─ thumbnail (60×60 JPEG base64)

brainscan_theme       ← "light" | "dark"
```

---

## 📁 Fichiers

| Fichier | Lignes | Rôle |
|---|---:|---|
| `index.html` | ~388 | Layout HTML5 sémantique |
| `styles.css` | ~922 | Design system light + dark |
| `app.js` | ~1350 | 16 blocs de logique applicative |

---

> Voir [`README.md`](README.md) pour les détails du design system et les 16 blocs.
