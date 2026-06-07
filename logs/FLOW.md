# 🗺 logs/ FLOW — Trace d'un entraînement

> Tout ce qui est généré pendant `train_two_stages()`.

---

## 📋 Pipeline d'écriture des logs (pendant l'entraînement)

```
1️⃣  scripts/train.py démarre
        │
        ▼
2️⃣  PyTorchTrainer initialise
        │
        ├─ timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ├─ Crée logs/training_history_<ts>.csv (vide, headers)
        ├─ Crée logs/stage1_<ts>/ (TensorBoard SummaryWriter)
        └─ Crée logs/stage2_<ts>/ (deuxième stage plus tard)
        │
        ▼
3️⃣  Stage 1 — boucle 20 epochs
        │
        for epoch in 1..20 :
            │
            ├─ train_epoch()
            │     ├─ for batch in train_loader :
            │     │     ├─ forward + loss + backward + step
            │     │     └─ tensorboard.add_scalar("train/batch_loss", ...)
            │     └─ avg_loss, avg_acc
            │
            ├─ val_epoch()
            │     ├─ for batch in val_loader (no_grad) :
            │     │     └─ forward + loss
            │     └─ val_loss, val_acc
            │
            ├─ tensorboard.add_scalars("loss", {"train": ..., "val": ...})
            ├─ tensorboard.add_scalars("acc", {"train": ..., "val": ...})
            │
            ├─ Append row to training_history_<ts>.csv :
            │     {epoch, stage=1, train_loss, val_loss, train_acc, val_acc, lr}
            │
            ├─ ReduceLROnPlateau.step(val_loss)
            │     └─ Si stagnation → divise lr par 0.5
            │
            ├─ EarlyStopping check (patience=7)
            │
            └─ Si val_loss < best : save checkpoint
        │
        ▼
4️⃣  Transition Stage 1 → Stage 2
        │
        ├─ unfreeze_base_layers(num_layers=30)
        └─ optimizer = Adam(trainable, lr=1e-4)
        │
        ▼
5️⃣  Stage 2 — boucle 30 epochs (idem Stage 1, écrit dans CSV avec stage=2)
        │
        ▼
6️⃣  Final save
        │
        ├─ models/final_model_<ts>.pth
        ├─ logs/training_history_<ts>.csv (50 lignes)
        ├─ logs/stage1_<ts>/events.out.tfevents.*  (TensorBoard)
        └─ logs/stage2_<ts>/events.out.tfevents.*
```

---

## 📊 Structure de `training_history_<ts>.csv`

```
epoch,stage,train_loss,val_loss,train_acc,val_acc,lr,timestamp
1,1,0.8421,0.5234,0.7152,0.8350,0.001,2025-11-06 12:41:30
2,1,0.5123,0.3892,0.8210,0.8761,0.001,2025-11-06 12:42:15
...
20,1,0.0892,0.0823,0.9821,0.9745,0.0005,2025-11-06 12:51:32

21,2,0.0721,0.0654,0.9856,0.9802,0.0001,2025-11-06 12:52:28
...
50,2,0.0321,0.0345,0.9942,0.9912,0.00005,2025-11-06 14:21:53
```

---

## 📈 Pipeline de lecture des logs (post-training)

```
1️⃣  python scripts/visualize_training.py
        │
        ▼
2️⃣  Cherche le CSV le plus récent dans logs/
        │
        └─ glob("logs/training_history_*.csv") → max(mtime)
        │
        ▼
3️⃣  pandas.read_csv()
        │
        ▼
4️⃣  Construire 4 plots (grille 2×2) :
        │
        ├─ AX 1 : Loss curve
        │     ├─ train_loss (bleu) vs val_loss (orange)
        │     └─ Vertical line stage 1 → 2 boundary
        │
        ├─ AX 2 : Accuracy curve
        │     └─ idem (mais train_acc vs val_acc)
        │
        ├─ AX 3 : Loss scatter Stage 1 vs 2
        │
        └─ AX 4 : Accuracy scatter Stage 1 vs 2
        │
        ▼
5️⃣  Save → results/training_history.png
```

---

## 🧠 Diagnostic via les courbes

```
Symptôme visuel sur loss curve              Diagnostic
──────────────────────────────────          ───────────────────
train_loss ≪ val_loss                       Overfitting
                                            → Augmenter dropout / data augm
                                            → Réduire epochs

train_loss et val_loss plateau hauts        Underfitting
                                            → Plus de paramètres
                                            → Plus d'époques

val_acc s'effondre début Stage 2            Catastrophic forgetting
                                            → LR Stage 2 trop élevé
                                            → Diviser learning_rate_s2 par 2

Oscillations brutales                       LR mal réglé
                                            → Réduire LR
                                            → ReduceLROnPlateau plus agressif

Stage 2 n'améliore rien                     Modèle convergé en Stage 1
                                            → Réduire epochs Stage 2
```

---

## 📊 Visualisation alternative — TensorBoard

```bash
# Lancer TensorBoard sur les events files
tensorboard --logdir logs/

# → http://localhost:6006
```

→ Permet d'explorer :
- Loss/accuracy par batch (haute résolution)
- Distributions des activations par couche
- Histogrammes des poids
- Comparaison entre runs

---

## 📁 Structure typique

```
logs/
├── training_history_20251106_142153.csv     ← le run final
├── training_history_20251106_124124.csv     ← runs précédents (debug)
│
├── stage1_20251106_142153/
│   └── events.out.tfevents.*                ← TensorBoard Stage 1
│
└── stage2_20251106_142153/
    └── events.out.tfevents.*                ← TensorBoard Stage 2
```

---

## 🔌 Consommation des logs

```
logs/training_history_*.csv
        │
        ├──► scripts/visualize_training.py
        │       → results/training_history.png
        │
        ├──► dataset_stats/analyses/fig07_training_history.py
        │       → outputs/figures/training/07_training_history.png
        │
        └──► dataset_stats/analyses/fig13_lr_schedule.py
                → outputs/figures/training/13_lr_schedule.png
```

---

> Voir [`README.md`](README.md) pour la rétention et la rotation des logs.
