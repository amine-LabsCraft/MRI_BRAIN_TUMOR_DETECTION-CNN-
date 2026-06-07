# 📄 Compiler le rapport LaTeX (`RAPPORT_PROJET.tex`)

> 3 méthodes au choix : **Overleaf** (en ligne, sans install), **MiKTeX/TeX Live** (Windows/macOS/Linux), ou **Docker**.

---

## 🌐 Méthode 1 — Overleaf (la plus simple, recommandée)

1. Va sur **https://www.overleaf.com** (compte gratuit)
2. Clique sur **"New Project"** → **"Upload Project"**
3. Upload le fichier `docs/RAPPORT_PROJET.tex`
4. Sélectionne le compilateur **pdfLaTeX** (en haut à droite, ⚙ Menu)
5. Clique sur **"Recompile"**

→ ✅ PDF généré en quelques secondes, téléchargeable.

**Avantages** :
- Aucune install
- Auto-complétion + preview live
- Compile à chaque sauvegarde

---

## 💻 Méthode 2 — Compilation locale (Windows/macOS/Linux)

### Prérequis

| OS | Distribution LaTeX | Taille |
|---|---|---|
| **Windows** | [MiKTeX](https://miktex.org/download) | ~250 MB |
| **macOS** | [MacTeX](https://www.tug.org/mactex/) | ~4 GB |
| **Linux** | `apt install texlive-full` | ~5 GB |

> 💡 Sous Windows, MiKTeX télécharge les packages à la demande → install rapide.

### Compilation (3 passes pour TOC + références)

```bash
cd docs/

# Passe 1 — génère .aux pour les références
pdflatex RAPPORT_PROJET.tex

# Passe 2 — résout TOC + références internes
pdflatex RAPPORT_PROJET.tex

# Passe 3 — finalise (numéros de pages, liens corrects)
pdflatex RAPPORT_PROJET.tex
```

→ Génère `RAPPORT_PROJET.pdf` (~50-80 pages).

### Script "tout-en-un"

**Windows (PowerShell)** :
```powershell
cd docs
1..3 | ForEach-Object { pdflatex -interaction=nonstopmode RAPPORT_PROJET.tex }
```

**macOS / Linux (Bash)** :
```bash
cd docs/
for i in 1 2 3; do pdflatex -interaction=nonstopmode RAPPORT_PROJET.tex; done
```

### Avec `latexmk` (recommandé — gère les passes automatiquement)

```bash
cd docs/
latexmk -pdf -interaction=nonstopmode RAPPORT_PROJET.tex

# Nettoyer les fichiers auxiliaires (.aux, .log, .toc, .out)
latexmk -c
```

---

## 🐳 Méthode 3 — Docker (zéro install LaTeX)

```bash
cd docs/

# Compile via image Docker officielle TeX Live
docker run --rm -v "$PWD":/workdir -w /workdir texlive/texlive:latest \
    pdflatex -interaction=nonstopmode RAPPORT_PROJET.tex

# Répéter 2 fois de plus pour les références
```

> Image Docker : ~1 GB, mais aucune dépendance permanente.

---

## 📦 Packages LaTeX requis

Le rapport utilise ces packages standards (tous inclus dans MiKTeX/TeX Live) :

```latex
inputenc · fontenc · babel · lmodern · geometry · setspace · parskip
microtype · xcolor · titlesec · booktabs · tabularx · longtable
multirow · array · makecell · listings · tcolorbox · hyperref
fancyhdr · enumitem · graphicx · float · caption
```

→ Aucune dépendance exotique. Compile out-of-the-box.

---

## 🐛 Erreurs fréquentes

| Erreur | Cause | Solution |
|---|---|---|
| `! LaTeX Error: File 'X.sty' not found` | Package manquant | MiKTeX install auto, ou `tlmgr install X` |
| Caractères français mal rendus | Encoding | Vérifier que le `.tex` est en UTF-8 |
| Liens hyperref cassés | Références non résolues | Relancer `pdflatex` 2-3 fois |
| TOC vide | Première compilation | Lancer 2-3 fois (TOC après .aux) |
| Image manquante | Pas de `.png` lié | Le rapport n'inclut pas d'images externes — ignorer ou ajouter |

---

## 📥 Inclure les figures dataset_stats/

Si tu veux que le rapport contienne les **22 figures générées**, ajoute dans le préambule :

```latex
\graphicspath{{../dataset_stats/outputs/figures/overview/}
              {../dataset_stats/outputs/figures/image/}
              {../dataset_stats/outputs/figures/training/}
              {../dataset_stats/outputs/figures/evaluation/}
              {../dataset_stats/outputs/figures/errors/}}
```

Puis dans les chapitres :

```latex
\begin{figure}[H]
\centering
\includegraphics[width=0.9\textwidth]{08_confusion_matrix.png}
\caption{Matrice de confusion sur le test set}
\end{figure}
```

→ Lance d'abord `python dataset_stats/run.py` pour générer les PNG.

---

## 📤 Distribuer le rapport

Une fois compilé, tu peux :

1. **Partager le PDF** : `RAPPORT_PROJET.pdf` (~5-10 MB sans images, ~25 MB avec)
2. **Envoyer le `.tex`** : pour que d'autres puissent éditer
3. **Publier sur Overleaf** : projet partageable avec lien
4. **Inclure dans le repo** : `git add docs/RAPPORT_PROJET.pdf` (avec Git LFS si > 50 MB)

---

## 🎨 Personnaliser le rapport

### Changer les couleurs (palette)

Dans le préambule, modifie :
```latex
\definecolor{navy}{HTML}{0A2540}        % Couleur principale
\definecolor{cyan}{HTML}{00D4AA}        % Accent
\definecolor{accentred}{HTML}{EF4444}   % Glioma
\definecolor{accentorange}{HTML}{F59E0B}% Meningioma
\definecolor{accentgreen}{HTML}{10B981} % No Tumor
\definecolor{accentblue}{HTML}{3B82F6}  % Pituitary
```

### Changer la police

```latex
% Au lieu de \usepackage{lmodern} :
\usepackage[default]{sourcesanspro}      % Source Sans Pro
% OU
\usepackage[default]{opensans}           % Open Sans
% OU
\usepackage{mathpazo}                     % Palatino
```

### Ajouter un logo

```latex
% Dans la titlepage, après \vspace*{2cm} :
\includegraphics[width=4cm]{logo.png}
\vspace{1cm}
```

---

## 📊 Statistiques du rapport

| Métrique | Valeur |
|---|---|
| Lignes de LaTeX | ~1\,200 |
| Chapitres | 10 + 3 annexes |
| Tableaux | ~25 |
| Listings code | ~20 |
| Compilation | ~5-10 secondes |
| Pages PDF estimées | 50-80 |

---

> **TL;DR** : Pour le plus simple, upload `RAPPORT_PROJET.tex` sur **Overleaf**. Tu auras le PDF en 30 secondes.
