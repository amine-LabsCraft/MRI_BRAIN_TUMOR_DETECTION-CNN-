# 📋 logs/ — Logs et traces d'entraînement

> **Tout l'historique** d'un run d'entraînement : TensorBoard event files + CSVs par-époque.

---

## ⚡ En 30 secondes

| | |
|---|---|
| 🎯 **Rôle** | Conserver toute l'instrumentation des runs (loss, acc, LR, par époque) |
| 📊 **Formats** | TensorBoard binaires (.tfevents) + CSV |
| 🔑 **Convention** | timestamp `YYYYMMDD_HHMMSS` partagé avec models/ et results/ |

---

## 🗺️ Architecture des logs

```
   src/model_trainer.py
        │
        ├──► writer = SummaryWriter(log_dir=logs/stage{n}_<ts>/)
        │       └──► logs/stage1_<ts>/{train,validation}/events.*.v2
        │
        ├──► CSV ligne par ligne (per epoch)
        │       └──► logs/training_log_stage1_<ts>.csv
        │
        └──► À la fin (consolidé) :
                └──► logs/training_history_<ts>.csv  ← SOURCE DE VÉRITÉ
```

---

## 📂 Inventaire

| Type | Pattern | Exemple | Tracké Git |
|---|---|---|:---:|
| **Run TensorBoard** | `stage{n}_<ts>/` | `stage1_20251106_124124/` | ❌ |
| **Log CSV stage** | `training_log_stage{n}_<ts>.csv` | `training_log_stage1_20251106_140409.csv` | ✅ |
| **Historique final** | `training_history_<ts>.csv` | `training_history_20251106_142153.csv` | ✅ |

---

## 🔑 Le fichier-clé

**`training_history_20251106_142153.csv`** = source utilisée par toutes les figures.

### Structure
```csv
train_loss,train_acc,val_loss,val_acc
0.5006,0.8135,0.3755,0.8624
0.4227,0.8429,0.3375,0.8851
...
```

### Caractéristiques
| Caractéristique | Valeur |
|---|---|
| **Lignes** | 50 (= époques) |
| **Colonnes** | 4 |
| **Encoding** | UTF-8 |
| **Split stages** | Lignes 1-20 = Stage 1, 21-50 = Stage 2 |

---

## 📊 Performance résumée

| Métrique | Stage 1 (epoch 20) | Stage 2 (epoch 50) | Best |
|---|---:|---:|---:|
| Train acc | ~95 % | 99.86 % | 99.86 % |
| Val acc | ~97 % | 99.24 % | 99.34 % @ ep 42 |
| Train loss | ~0.18 | ~0.005 | — |
| Val loss | ~0.15 | ~0.05 | 0.0450 |

---

## 🚀 Visualisation TensorBoard

```bash
# Tous les runs
venv\Scripts\python.exe -m tensorboard --logdir logs/

# Un run précis
venv\Scripts\python.exe -m tensorboard --logdir logs/stage1_20251106_140409/
```
→ http://localhost:6006

| Onglet TB | Contenu |
|---|---|
| **Scalars** | loss/train, loss/val, accuracy/train, accuracy/val, lr |
| **Histograms** | Distribution des poids (si activé) |
| **HParams** | batch_size, lr, image_size |

---

## 📋 stage1_*/ — pourquoi 5 dossiers ?

5 essais d'entraînement ont été faits pour ajuster les hyperparamètres :

| # | Timestamp | Verdict |
|---|---|---|
| 1 | `124124` | Premier essai (LR trop bas) |
| 2 | `134522` | Ajustement LR |
| 3 | `135921` | Test batch size |
| 4 | `140019` | Ajustement augmentation |
| 5 | `140409` | **Run retenu** → mène au final_model_142153 |

→ Seul le run #5 a abouti au modèle de référence.

---

## 🔌 Consommé par

| Outil | Lit quoi ? |
|---|---|
| `scripts/visualize_training.py` | `training_history_*.csv` |
| `dataset_stats/analyses/fig07_training_history.py` | `training_history_*.csv` (le plus récent) |
| TensorBoard | `stage{1,2}_*/events.*.v2` |
| Pandas / Excel (analyse manuelle) | n'importe quel CSV |

---

## 🧪 Cheat sheet — analyse Pandas

```python
import pandas as pd
df = pd.read_csv("logs/training_history_20251106_142153.csv")

# Best epoch
best = df["val_loss"].idxmin()
print(f"Best epoch: {best+1}")

# Comparer stages
print("Stage 1 final val_acc:", df.iloc[19]["val_acc"])
print("Stage 2 final val_acc:", df.iloc[49]["val_acc"])

# Détecter overfitting
gap = (df["train_acc"] - df["val_acc"]).max() * 100
print(f"Max train-val gap: {gap:.2f}%")
```

---

## 🔑 Convention timestamp

Le timestamp `20251106_142153` lie 3 dossiers :

```
models/final_model_20251106_142153.pth
        │ même timestamp
logs/training_history_20251106_142153.csv
        │ même timestamp
results/* (généré par evaluate.py utilisant ce modèle)
```

→ Permet de **tracer** un modèle à ses logs et ses métriques.

---

## 💾 Politique de stockage

| Type | Taille typique | Tracké ? | Pourquoi ? |
|---|---|:---:|---|
| `training_history_*.csv` | ~5 KB | ✅ | Source des figures, traçabilité |
| `training_log_stage{n}_*.csv` | ~3 KB | ✅ | Historique des essais |
| `stage{n}_*/events.*.v2` | ~MB | ❌ | TensorBoard binaire (régénérable) |

---

## ⚠️ Pièges courants

| Symptôme | Cause | Solution |
|---|---|---|
| `latest_training_csv()` → ancien run | Tri alphabétique sur timestamp | Renommer ou supprimer les vieux CSVs |
| TB n'affiche rien | Mauvais `--logdir` | Pointer le PARENT du dossier `train/` |
| Comparer 2 runs impossible | Timestamps différents | Loader chacun et plot Pandas manuel |
| Logs très gros | TB events accumulés | `.gitignore` couvre déjà `*.tfevents.*` |

---

## 🔗 Liens

- Trainer : [`../src/model_trainer.py`](../src/model_trainer.py)
- Script entraînement : [`../scripts/train.py`](../scripts/train.py)
- Visualisation : [`../scripts/visualize_training.py`](../scripts/visualize_training.py)
- Figure produite : [`../results/training_history.png`](../results/training_history.png)
- Analyse modulaire : [`../dataset_stats/analyses/fig07_training_history.py`](../dataset_stats/analyses/fig07_training_history.py)
