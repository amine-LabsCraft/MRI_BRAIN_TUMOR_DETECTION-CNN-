# 🗺 docs/ FLOW — Documentation par phase

> Hub de documentation manuelle (setup, GPU, phases historiques).

---

## 📚 Quel guide pour quelle situation ?

```
                ┌──────────────────────────────────────┐
                │  Tu veux... ?                        │
                └──────────────────┬───────────────────┘
                                   │
       ┌──────────────────┬────────┴──────────┬────────────────────┐
       │                  │                   │                    │
       ▼                  ▼                   ▼                    ▼
   "Installer            "Configurer       "Comprendre        "Voir l'état
    le projet"            le GPU"           les phases         du projet"
       │                  │                   │                    │
       ▼                  ▼                   ▼                    ▼
INSTALLATION.md     GPU_SETUP.md      PHASE{1,2,3}_*.md   PROJECT_STATUS.md
```

---

## 🗂 Inventaire et utilité

```
docs/
│
├── INSTALLATION.md              Setup pas-à-pas (Python, venv, requirements)
│
├── GPU_SETUP.md                 Activer CUDA pour PyTorch
│   └─ NVIDIA driver, CUDA Toolkit, cuDNN versions
│
├── QUICK_START.md               TLDR pour démarrer en 5 min
│
├── PHASE1_COMPLETE.md           Bilan Phase 1 (data preparation)
│   └─ Étapes, décisions techniques, résultats obtenus
│
├── PHASE2_COMPLETE.md           Bilan Phase 2 (training)
├── PHASE2_SUMMARY.md            Résumé Phase 2
│
├── PHASE3_COMPLETE.md           Bilan Phase 3 (evaluation)
├── PHASE3_SUMMARY.md            Résumé Phase 3
├── PHASE3_STATUS.txt            Status diff (suivi avancement)
│
├── PROJECT_STATUS.md            État global du projet
│
└── README.md                    Index navigationnel
```

---

## 🎯 Ces docs sont des SNAPSHOTS historiques

```
docs/PHASE1_COMPLETE.md          → écrit fin de phase 1
docs/PHASE2_COMPLETE.md          → écrit fin de phase 2
docs/PHASE3_COMPLETE.md          → écrit fin de phase 3
docs/PROJECT_STATUS.md           → mis à jour à chaque jalon
```

→ Ils racontent **comment le projet a été construit**, pas comment il fonctionne aujourd'hui.

Pour la documentation **vivante** (à jour), voir :
- [`../README.md`](../README.md) — vue d'ensemble actuelle
- [`../FLOW.md`](../FLOW.md) — pipeline global actuel
- READMEs dans chaque dossier — état actuel par composant

---

## 🚀 Workflow recommandé pour un nouveau dev

```
1️⃣  Lire ../README.md (5 min)
        │
        ▼
2️⃣  Si Windows → ../README.md "Démarrage en 1 commande"
   Si setup détaillé → docs/INSTALLATION.md
        │
        ▼
3️⃣  Si problème GPU → docs/GPU_SETUP.md
        │
        ▼
4️⃣  Pour comprendre les choix → docs/PHASE{1,2,3}_COMPLETE.md
        │
        ▼
5️⃣  Pour modifier un composant → README.md du dossier concerné
        │
        ▼
6️⃣  Pour comprendre le flow → FLOW.md du dossier concerné
        │
        ▼
✅ Onboarding complet en ~30 min
```

---

## 📁 Pourquoi cette documentation manuelle ?

Avant le refactor en READMEs par dossier, **`docs/` était la seule source** de documentation. Aujourd'hui, on a 17 READMEs + 16 FLOW.md, mais on conserve `docs/` pour :

- **Archive historique** : trace des décisions des 3 phases
- **Onboarding initial** : `INSTALLATION.md` reste le guide canonique
- **Setup spécialisé** : `GPU_SETUP.md` couvre des cas non-triviaux

---

> Voir [`README.md`](README.md) pour la liste complète des guides disponibles.
