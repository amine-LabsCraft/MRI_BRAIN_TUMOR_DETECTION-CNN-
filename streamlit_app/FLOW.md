# 🗺 streamlit_app/ FLOW — Démo en 1 ligne

> Alternative à FastAPI : interface Streamlit mono-fichier qui charge le modèle directement (pas d'API séparée).

---

## 🚀 Pipeline complet d'une session Streamlit

```
1️⃣  streamlit run streamlit_app/app.py
        │
        ▼
2️⃣  Pathlib patch (cross-OS) [tout en haut du fichier]
        │
        ▼
3️⃣  set_page_config(layout="wide", title="NeuroScan AI")
        │
        ▼
4️⃣  Inject premium CSS (gradient cards, pulse animations, dark theme)
        │
        ▼
5️⃣  @st.cache_resource → load_model() (UNE SEULE FOIS)
        ├─ ResNet50Classifier(num_classes=4, pretrained=False)
        ├─ torch.load(MODEL_PATH) avec patch portable
        ├─ load_state_dict + .eval() + .to(device)
        └─ return (model, device)
        │
        ▼
6️⃣  Render header
        ├─ Logo gradient + titre "NeuroScan AI"
        └─ Badges : ResNet50 · 98.96% · Educational use
        │
        ▼
7️⃣  Render sidebar
        ├─ Card "Model Info"        (architecture, parameters, device)
        ├─ Card "Performance"       (test accuracy 98.96%)
        ├─ Card "Classes"           (4 classes avec couleurs)
        ├─ Card "Disclaimer"        (warning médical)
        └─ Card "Tips"              (conseils utilisateur)
        │
        ▼
8️⃣  st.file_uploader (PNG/JPG/JPEG/NPY)
        │
        ▼
   ┌──── No upload yet ────┐
   ▼                       ▼
   Render placeholder      User uploads image
   (welcome card)          │
                           ▼
              9️⃣  Image affichée + métadonnées
                           │
                           ▼
              🔟  preprocess_image()
                  ├─ Resize 224
                  ├─ ToTensor
                  └─ Normalize ImageNet
                           │
                           ▼
              1️⃣1️⃣  predict(model, device, tensor)
                  ├─ forward pass
                  └─ softmax → probabilities
                           │
                           ▼
              1️⃣2️⃣  generate_gradcam() (PyTorch hooks inline)
                  ├─ register hooks sur layer4[-1]
                  ├─ backward sur predicted class
                  └─ cam = (weights × activations) · ReLU
                           │
                           ▼
              1️⃣3️⃣  Render results dans 3 colonnes
                  ├─ COL 1 : Image + Grad-CAM overlay (matplotlib)
                  ├─ COL 2 : Confidence gauge SVG circulaire
                  │           + barres de probabilité animées
                  └─ COL 3 : Tabs (Diagnosis | Medical Info | History)
                           │
                           ▼
              1️⃣4️⃣  Render bottom section
                  ├─ Severity badge (High/Moderate/Low)
                  ├─ Recommendation card (couleur par classe)
                  └─ Download report button (TXT)
                           │
                           ▼
              1️⃣5️⃣  Add to st.session_state.history
                  └─ List dict {time, file, prediction, confidence}
```

---

## 🎯 Différences vs FastAPI + interface/

| Critère | streamlit_app/ | api/ + interface/ |
|---|---|---|
| **Démarrage** | 1 commande | 2 services à lancer |
| **Architecture** | Monolithique | Découplée (REST API) |
| **Multi-utilisateurs** | ❌ (1 utilisateur à la fois) | ✅ (plusieurs simultanés) |
| **Personnalisation UI** | Limitée à Streamlit | Totale (HTML/CSS/JS) |
| **Idéal pour** | Démos, prototypage rapide | Production, déploiement public |

---

## 📁 Fichier unique

| Fichier | Lignes | Rôle |
|---|---:|---|
| `app.py` | ~580 | Tout : UI + chargement modèle + Grad-CAM + inférence |

---

> Lance avec : `venv\Scripts\python.exe -m streamlit run streamlit_app\app.py`
> → Accessible sur http://localhost:8501
