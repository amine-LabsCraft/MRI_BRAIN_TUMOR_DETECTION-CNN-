# 🎨 streamlit_app/ — Frontend Streamlit (NeuroScan AI)

> **Interface mono-fichier** : 1 commande, 0 backend séparé, démo en 2 minutes.

---

## ⚡ En 30 secondes

| | |
|---|---|
| 🎯 **Rôle** | UI web premium tout-en-un (pas d'API à lancer à part) |
| 🚪 **Port** | 8501 |
| 📦 **Fichier** | 1 seul (~1000 lignes) |
| 🧠 **Inférence** | In-process (modèle chargé dans le serveur Streamlit) |
| 🔥 **Grad-CAM** | Calculé inline via hooks PyTorch |
| 🎨 **Thème** | Dark glassmorphism custom (CSS injection) |
| 📤 **Formats** | PNG, JPG, JPEG, **NPY** (avantage vs interface/) |

---

## 🗺️ Position dans le projet

```
                    Utilisateur
                         │
                         ▼
                ┌──────────────────┐
                │  streamlit_app/  │
                │     app.py       │
                │   port 8501      │
                └────────┬─────────┘
                         │ in-process
       ┌─────────────────┼─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
  src/model_*.py    models/*.pth    data/processed/
                                    (pour upload NPY)
```

**Pas d'appel HTTP** — tout est résolu dans le processus Python du serveur Streamlit.

---

## 📂 Fichiers

| Fichier | Lignes | Rôle |
|---|---:|---|
| `app.py` | ~1000 | Application Streamlit complète mono-fichier |

---

## 🧩 Sections d'`app.py` (par bannières)

| Lignes | Section | Rôle |
|---|---|---|
| 1–40 | Imports + path patches | Patch pathlib, sys.path, torch, streamlit |
| 42–48 | Page config | Titre, icône, layout wide |
| 50–130 | Constants | CLASS_NAMES, CLASS_COLORS, TUMOR_INFO, MODEL_STATS |
| 132–310 | CSS injection | ~180 lignes de design glassmorphism |
| 313–365 | Model loading | `@st.cache_resource` singleton + patch pathlib |
| 367–376 | Preprocessing | Resize 224 + ImageNet norm |
| 379–387 | Prediction | Forward + softmax |
| 390–434 | Grad-CAM | Hooks layer4[-1] + overlay jet |
| 437–520 | HTML helpers | SVG gauge, prob bars, severity badge |
| 521–575 | Text report | Rapport ASCII formaté |
| 577–666 | Sidebar | Logo, status, GPU/CPU, guide tumeurs |
| 669–733 | Upload zone | Streamlit file_uploader + placeholder |
| 736–767 | History | 8 dernières analyses (HTML grid) |
| 770–957 | Main view | 3 colonnes + 3 onglets |
| 960–991 | `main()` | Orchestration |

---

## 🚀 Pipeline d'analyse

```
1️⃣  Upload (drag-drop ou click)             ←  PNG/JPG/JPEG/NPY
2️⃣  Décode l'image (PIL ou np.load pour NPY)
3️⃣  Preprocessing (resize 224 + normalize ImageNet)
4️⃣  Forward pass + softmax                   ←  @st.cache_resource model
5️⃣  Calcul Grad-CAM (hooks layer4[-1])
6️⃣  Affichage 3 colonnes :
       ┌───────────┬─────────────┬───────────┐
       │  Image    │  Grad-CAM   │  Jauge    │
       │  IRM      │  overlay    │  SVG      │
       └───────────┴─────────────┴───────────┘
7️⃣  3 onglets : Probabilités · Médical · Rapport
8️⃣  Mise à jour historique (8 dernières)
```

---

## 🎨 Composants UI

| Section | Élément | Type |
|---|---|---|
| **Hero header** | Titre dégradé + badge ResNet50 | HTML |
| **Sidebar** | Logo, status modèle, GPU indicator, performance, guide tumeurs | st.sidebar |
| **Upload zone** | Drag-drop + placeholder éducatif | st.file_uploader |
| **Image préview** | IRM affichée + métadonnées (taille, dimensions) | st.image |
| **Grad-CAM** | Original + overlay côte à côte | st.pyplot |
| **Confidence gauge** | SVG circulaire animé | HTML inline |
| **Verdict chip** | Badge couleur classe | HTML |
| **Severity badge** | None/Moderate/High avec couleur | HTML |
| **Tabs** | Probabilités · Médical · Rapport | st.tabs |
| **Probability bars** | HTML custom + valeurs % | HTML |
| **Medical card** | Card couleur + symptômes + recommandation | HTML |
| **Text report** | Code-block ASCII + bouton DL | st.code + st.download_button |
| **History grid** | 8 dernières analyses (file, classe, conf, heure) | HTML grid |

---

## 🆚 Comparaison avec interface/

| Critère | streamlit_app/ | interface/ |
|---|---|---|
| **Stack** | Python + Streamlit | HTML/CSS/JS vanilla |
| **Backend séparé** | ❌ Non (in-process) | ✅ Oui (FastAPI) |
| **Démarrage** | 1 commande | 2 services |
| **Multi-utilisateurs** | ⚠️ Limité (rerun complet) | ✅ Illimité |
| **Persistance historique** | Session uniquement | localStorage |
| **Format NPY** | ✅ | ❌ (via /random seulement) |
| **Latence** | Très faible | Faible |
| **Customisation UI** | CSS injection | Natif HTML/CSS |
| **Use case** | Démos, pédagogie | Production, multi-users |

---

## 🚀 Lancement

```bash
# Méthode rapide
venv\Scripts\python.exe -m streamlit run streamlit_app\app.py

# Avec arguments
streamlit run streamlit_app\app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true
```

→ http://localhost:8501

---

## 🔥 Grad-CAM PyTorch (sans TensorFlow)

```
1. Hooks installés sur model.base_model.layer4[-1]
        │
        ▼
2. Forward pass → activations stockées
        │
        ▼
3. one_hot[target_class] = 1.0
        │
        ▼
4. Backward → gradients stockés
        │
        ▼
5. weights = gradients.mean(dim=(1,2))
        │
        ▼
6. CAM = sum(weights × activations) → ReLU → normalize
        │
        ▼
7. Resize 224×224 + colormap jet + alpha blend → overlay
```

---

## ⚠️ Pièges courants

| Symptôme | Cause | Solution |
|---|---|---|
| `pathlib._local` AttributeError | Torch import avant patch | Patch fait au top du fichier (ligne 13-17) |
| Modèle ne se charge pas | Mauvais path | Vérifier `models/final_model_20251106_142153.pth` existe |
| Grad-CAM noir | Image trop uniforme | Essayer une autre IRM avec contraste |
| Streamlit cache obsolète | Code modifié | `streamlit cache clear` |
| Slow first prediction | Modèle pas en cache | Normal, 1ère exécution charge ~98 MB |

---

## 🔗 Liens

- Architecture : [`../src/model_architecture.py`](../src/model_architecture.py)
- Modèle : [`../models/`](../models/)
- Frontend alternatif : [`../interface/`](../interface/)
- Backend alternatif : [`../api/`](../api/)
