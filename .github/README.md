# 🤖 .github/ — CI/CD GitHub Actions

> **Pipeline automatique** déclenché à chaque `git push` ou `pull request` : lint → tests → build Docker. Garantit qu'aucune régression n'arrive en `main`.

---

## ⚡ En 30 secondes

| | |
|---|---|
| 🎯 **Rôle** | Vérifier automatiquement chaque commit avant merge |
| 🚦 **Stages** | Lint → Test → Docker build |
| 🐍 **Python** | 3.11 (cache pip activé) |
| 🐳 **Docker** | Build sans push (validation) |
| ⏱ **Durée** | ~3-5 min total |

---

## 📂 Inventaire

```
.github/
├── workflows/
│   └── ci.yml          ← Pipeline principal (lint + test + Docker)
└── README.md           ← Ce fichier
```

---

## 🚦 Pipeline `ci.yml` — flux d'exécution

### Déclencheurs

```yaml
on:
  push:
    branches: [main, master, develop]
  pull_request:
    branches: [main, master]
```

→ Le pipeline tourne sur :
- Tout push sur `main`, `master`, `develop`
- Toute pull request ciblant `main` ou `master`

### Job 1 — `lint` (ruff + black)

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
      - run: pip install ruff black
      - run: ruff check api/ src/ scripts/ dataset_stats/ tests/ start.py
      - run: black --check api/ src/ scripts/ tests/ start.py
```

**Vérifie** :
- ✅ Aucune erreur ruff (style PEP8, imports, bugs simples)
- ✅ Code formaté avec black (line-length 100, target Python 3.11)

**En cas d'échec** : exécuter localement `black api/ src/ scripts/` puis re-push.

### Job 2 — `test` (pytest, dépend de `lint`)

```yaml
test:
  runs-on: ubuntu-latest
  needs: lint              # ← attend que lint passe
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: "3.11"
        cache: "pip"
    - run: pip install -r requirements-dev.txt
    - run: python -m compileall -q api/ src/ scripts/ dataset_stats/ tests/ start.py
    - run: pytest tests/test_dataset_stats.py -v
```

**Vérifie** :
- ✅ Tous les fichiers Python compilent (pas d'erreur de syntaxe)
- ✅ Les 4 tests `test_dataset_stats.py` passent (registry auto-discovery)

**Note** : `tests/test_api.py` n'est pas exécuté en CI car il nécessite le checkpoint `.pth` (95 MB) absent du runner. Pour le faire tourner en CI, utiliser **Git LFS** (voir `.gitattributes`).

### Job 3 — `docker` (build image, dépend de `test`)

```yaml
docker:
  runs-on: ubuntu-latest
  needs: test              # ← attend test
  steps:
    - uses: actions/checkout@v4
    - uses: docker/setup-buildx-action@v3
    - uses: docker/build-push-action@v5
      with:
        context: .
        push: false
        tags: brainscan-ai:ci
        cache-from: type=gha    # ← cache GitHub Actions
        cache-to: type=gha,mode=max
```

**Vérifie** :
- ✅ Le `Dockerfile` build sans erreur
- ✅ Toutes les dépendances installables dans l'image

**Cache GitHub Actions** : les couches Docker sont mises en cache → builds suivants en ~30 s au lieu de ~3 min.

---

## 🧪 Tester localement avant push

### Reproduire le job `lint`

```bash
venv\Scripts\pip install ruff black
ruff check api/ src/ scripts/ dataset_stats/ tests/ start.py
black --check api/ src/ scripts/ tests/ start.py
```

→ Si black échoue, formater automatiquement :
```bash
black api/ src/ scripts/ tests/ start.py
```

### Reproduire le job `test`

```bash
venv\Scripts\pip install -r requirements-dev.txt
venv\Scripts\python.exe -m pytest tests/ -v
```

### Reproduire le job `docker`

```bash
docker build -t brainscan-ai:test .
```

---

## 📊 Statuts visibles

Une fois le pipeline lancé, le statut s'affiche :

- 🟡 **In progress** : pipeline en cours
- ✅ **Success** : tous les jobs passent
- ❌ **Failed** : au moins un job a échoué
- ⏸ **Cancelled** : annulé manuellement

→ Visible sur l'onglet **Actions** du repo GitHub, ou directement sur la PR.

### Badge README

Pour afficher le badge CI dans le README principal :

```markdown
![CI](https://github.com/USER/REPO/actions/workflows/ci.yml/badge.svg)
```

---

## 🔧 Étendre le pipeline

### Ajouter un job (ex: déploiement)

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    needs: docker
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - run: echo "Deploy to production"
      # ... étapes de déploiement ...
```

### Ajouter un linter (ex: mypy)

Dans le job `lint` existant :
```yaml
- run: pip install mypy
- run: mypy --ignore-missing-imports api/ src/
```

### Ajouter une matrice multi-Python

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.11", "3.12"]
```

→ Teste le code sur 3 versions de Python en parallèle.

---

## 🔑 Secrets GitHub (à ajouter manuellement)

Si vous voulez activer le **push Docker Hub** ou le **deploy**, ajoutez via Settings → Secrets :

| Secret | Usage |
|---|---|
| `DOCKERHUB_USERNAME` | Push image vers Docker Hub |
| `DOCKERHUB_TOKEN` | Token avec scope `Read & Write` |
| `BRAINSCAN_API_KEY` | Pour tests E2E avec auth |
| `RENDER_DEPLOY_HOOK` | URL webhook deploy Render |

→ Référencer dans le YAML avec `${{ secrets.DOCKERHUB_USERNAME }}`.

---

## 🛡 Sécurité du pipeline

| Bonne pratique | Implémenté ? |
|---|---|
| Pas de credentials en dur dans le YAML | ✅ |
| `actions/*@v4` pinning explicite | ✅ |
| Cache pip activé | ✅ |
| Cache Docker via GHA | ✅ |
| Pas de `pull_request_target` (évite injection) | ✅ |
| Tests avant build Docker | ✅ |

---

## ⚠️ Pièges courants

| Symptôme | Cause | Solution |
|---|---|---|
| `Error: Process completed with exit code 1` (lint) | black/ruff non passé localement | Lancer `black .` puis re-push |
| `tests/test_api.py is collected` | Le checkpoint .pth manque en CI | Le job ignore déjà ce test (skip) |
| Docker build timeout | Image trop grosse | Vérifier `.dockerignore` |
| `pip install` lent | Cache désactivé | Vérifier `cache: "pip"` dans setup-python |
| CI échoue mais pas localement | Diff Linux/Windows | Vérifier line endings (.gitattributes) |

---

## 📈 Métriques typiques

| Job | Durée | Cache hit |
|---|---|---|
| `lint` | ~30 s | pip |
| `test` | ~2 min | pip |
| `docker` (premier run) | ~3 min | rien |
| `docker` (cache) | ~30 s | GHA layers |
| **Total pipeline** | ~3-5 min | — |

---

## 📚 Voir aussi

- [`workflows/ci.yml`](workflows/ci.yml) — fichier de configuration
- [`../requirements-dev.txt`](../requirements-dev.txt) — dépendances de test
- [`../pyproject.toml`](../pyproject.toml) — config ruff, black, pytest
- [`../.pre-commit-config.yaml`](../.pre-commit-config.yaml) — équivalent local pre-push
- [`../Dockerfile`](../Dockerfile) — image Docker buildée par le pipeline

---

> **Tech stack** : GitHub Actions · ruff 0.1.9 · black 23.12 · pytest 7.4 · Docker Buildx
