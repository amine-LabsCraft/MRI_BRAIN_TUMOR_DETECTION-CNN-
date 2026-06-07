# 🗺 .github/ FLOW — CI/CD GitHub Actions

> Du `git push` au statut vert sur la PR : pipeline lint → test → docker.

---

## 🚦 Déclenchement

```
Trigger event
        │
        ├─ git push origin main / master / develop
        ├─ git push sur une branche en PR ouverte
        └─ pull_request → branche main / master
        │
        ▼
GitHub Actions activé sur .github/workflows/ci.yml
```

---

## 🏗 Pipeline complet (3 jobs séquentiels)

```
1️⃣  JOB : lint   (~30 s)
        │
        ├─ runs-on: ubuntu-latest
        ├─ checkout@v4
        ├─ setup-python@v5 (Python 3.11, cache pip)
        ├─ pip install ruff black
        ├─ ruff check api/ src/ scripts/ dataset_stats/ tests/ start.py
        └─ black --check api/ src/ scripts/ tests/ start.py
        │
        │  ❌ Échec ?  → CI rouge, jobs suivants skippés
        │
        ▼ ✅ Vert
2️⃣  JOB : test   (~2 min)   [needs: lint]
        │
        ├─ checkout@v4
        ├─ setup-python@v5 (Python 3.11, cache pip)
        ├─ pip install -r requirements-dev.txt
        ├─ python -m compileall -q api/ src/ scripts/ dataset_stats/ tests/ start.py
        └─ pytest tests/test_dataset_stats.py -v
              │
              └─ test_api.py SKIP en CI car .pth absent
                  (commit via Git LFS pour activer)
        │
        │  ❌ Échec ?  → CI rouge, docker skippé
        │
        ▼ ✅ Vert
3️⃣  JOB : docker   (~1-3 min)   [needs: test]
        │
        ├─ checkout@v4
        ├─ docker/setup-buildx-action@v3
        ├─ docker/build-push-action@v5
        │     ├─ context: .
        │     ├─ push: false  (validation uniquement)
        │     ├─ tags: brainscan-ai:ci
        │     ├─ cache-from: type=gha
        │     └─ cache-to: type=gha, mode=max
        │
        ▼ ✅ Vert
🟢  CI complete · prêt à merger
```

---

## 🛠 Reproduction locale

```
git push (CI échoue)
        │
        ▼
Reproduire chaque job localement :

# Job lint
venv\Scripts\pip install ruff black
ruff check api/ src/ scripts/ dataset_stats/ tests/ start.py
black --check api/ src/ scripts/ tests/ start.py

# Job test
venv\Scripts\pip install -r requirements-dev.txt
venv\Scripts\python.exe -m pytest tests/

# Job docker
docker build -t brainscan-ai:test .
        │
        ▼
Fix les erreurs détectées
        │
        ▼
git commit -m "fix" + git push
        │
        ▼
✅ CI verte
```

---

## 🚀 Pre-commit (avant le push)

Pour intercepter les problèmes **avant** GitHub Actions :

```
1️⃣  pip install pre-commit
        │
        ▼
2️⃣  pre-commit install
        │
        └─ installe le hook git pre-commit
        │
        ▼
3️⃣  git commit (à chaque commit)
        │
        ├─ Hooks lancés automatiquement :
        │     ├─ trailing-whitespace
        │     ├─ end-of-file-fixer
        │     ├─ check-yaml / check-json
        │     ├─ check-added-large-files (max 500 KB)
        │     ├─ detect-private-key
        │     ├─ ruff --fix
        │     └─ black
        │
        ├─ ❌ Échec ? → commit annulé, fichiers re-formatés à add
        │
        └─ ✅ OK ? → commit créé
        │
        ▼
4️⃣  git push
        │
        └─ CI GitHub Actions devrait passer du premier coup ✅
```

---

## 📁 Fichiers

| Fichier | Rôle |
|---|---|
| `workflows/ci.yml` | Pipeline GitHub Actions |
| `README.md` | Documentation détaillée du CI |

---

## 🔑 Secrets disponibles (à configurer manuellement)

```
GitHub repo → Settings → Secrets → Actions
        │
        ├─ DOCKERHUB_USERNAME      (optionnel, pour push image)
        ├─ DOCKERHUB_TOKEN         (idem)
        ├─ BRAINSCAN_API_KEY       (pour tests E2E avec auth)
        └─ RENDER_DEPLOY_HOOK      (optionnel, deploy auto)
```

→ Référencer dans le YAML : `${{ secrets.DOCKERHUB_TOKEN }}`

---

> Voir [`README.md`](README.md) pour étendre le pipeline (matrice multi-Python, deploy job, etc.)
