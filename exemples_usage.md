# Guide d'Utilisation GitIngest - Nouvelles Fonctionnalités

## 🎯 Format TXT par Défaut (Recommandé)

Toutes les commandes génèrent maintenant du **TXT optimisé pour l'IA** par défaut !

### ✅ Commandes de Base

```bash
# 1. Traitement simple - Format TXT automatique
gitingest ai batch ./mon_projet

# 2. Plusieurs projets en parallèle
gitingest ai batch ./projet1 ./projet2 ./projet3

# 3. Filtrage par extensions
gitingest ai batch ./src --include-ext .py .js .ts

# 4. Exclusion de fichiers/dossiers
gitingest ai batch ./projet --exclude-dirs node_modules .git --exclude-ext .log .tmp
```

### 🎯 Gestion de la Taille (Nouvelles Fonctionnalités)

```bash
# 1. Division automatique - Fichiers multiples de 1MB max
gitingest ai batch ./gros_projet --max-output-size 1MB --split-mode auto

# 2. Division forcée - Toujours diviser
gitingest ai batch ./projet --max-output-size 500KB --split-mode split

# 3. Troncature intelligente - Fichier unique tronqué
gitingest ai batch ./projet --max-output-size 2MB --split-mode truncate

# 4. Tailles supportées
gitingest ai batch ./projet --max-output-size 100KB  # Kilooctets
gitingest ai batch ./projet --max-output-size 5MB    # Mégaoctets
gitingest ai batch ./projet --max-output-size 1GB    # Gigaoctets
```

### 🚀 Utilisation Avancée

```bash
# 1. Dry-run pour tester
gitingest ai batch ./projet --max-output-size 1KB --dry-run

# 2. Répertoire de sortie personnalisé
gitingest ai batch ./projet --output-dir ./mes_digests

# 3. Modèle LLM spécifique
gitingest ai batch ./projet --model gpt-4o

# 4. Traitement parallèle accéléré
gitingest ai batch ./projet1 ./projet2 ./projet3 --parallel 10
```

### 📊 Exemples par Cas d'Usage

#### Développement Web
```bash
# Frontend React/Vue
gitingest ai batch ./frontend --include-ext .js .jsx .ts .tsx .vue .css

# Backend Node.js
gitingest ai batch ./backend --include-ext .js .ts .json --exclude-dirs node_modules
```

#### Data Science
```bash
# Projet Python
gitingest ai batch ./ml_project --include-ext .py .ipynb .yml .yaml

# Avec limitation de taille pour notebooks volumineux
gitingest ai batch ./notebooks --max-output-size 2MB --split-mode truncate
```

#### Projet Full-Stack
```bash
# Tout le projet avec exclusions
gitingest ai batch ./monapp --exclude-dirs node_modules dist build .git --exclude-ext .log .tmp .cache
```

## 📤 Formats de Sortie

### Format TXT (Défaut - Recommandé)
- ✅ Structure markdown lisible
- ✅ Métadonnées complètes
- ✅ Coloration syntaxique
- ✅ Optimisé pour ChatGPT/Claude

### Format JSONL (Optionnel)
```bash
# Seulement pour traitement programmé
gitingest ai batch ./projet --format jsonl
```

## 🎯 Script Quick-Ingest Amélioré

Le script `quick-ingest.sh` supporte maintenant toutes les nouvelles options :

```bash
# Utilisation simple
./scripts/quick-ingest.sh

# Avec limitation de taille
./scripts/quick-ingest.sh --max-output-size 1MB --split-mode auto

# Avec filtrage
./scripts/quick-ingest.sh --include-ext .py .js --exclude-dirs tests
```

## 🔧 Configuration Recommandée

### Pour ChatGPT/Claude (Recommandé)
```bash
gitingest ai batch ./projet --max-output-size 1MB --split-mode auto
```

### Pour Analyse Programmatique
```bash
gitingest ai batch ./projet --format jsonl --max-output-size 2MB
```

### Pour Gros Projets
```bash
gitingest ai batch ./projet --max-output-size 500KB --split-mode truncate --include-ext .py .js .ts
```

---

💡 **Astuce** : Le format TXT est maintenant par défaut et optimisé pour l'IA. Plus besoin de spécifier `--format txt` !
