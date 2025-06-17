# 🚀 Guide Pratique GitIngest - Cas d'Usage Réels

## 🎯 Développement Web

### Frontend React/Vue
```bash
# Projet React complet
gitingest ai batch ./my-react-app --include-ext .js .jsx .ts .tsx .css --exclude-dirs node_modules build

# Seulement les composants principaux
gitingest ai batch ./src/components --max-output-size 1MB --split-mode auto
```

### Backend API
```bash
# API Node.js/Express
gitingest ai batch ./backend --include-ext .js .ts .json --exclude-dirs node_modules logs

# API avec limitation pour ChatGPT
gitingest ai batch ./api --max-output-size 500KB --split-mode truncate
```

## 📊 Data Science & ML

### Notebooks Jupyter
```bash
# Projet ML avec notebooks
gitingest ai batch ./ml_project --include-ext .py .ipynb .yml .yaml

# Limitation pour gros notebooks
gitingest ai batch ./notebooks --max-output-size 2MB --split-mode auto
```

### Scripts Python
```bash
# Scripts de traitement de données
gitingest ai batch ./data_processing --include-ext .py --exclude-dirs __pycache__ .pytest_cache
```

## 🛠️ Projets Full-Stack

### Monorepo
```bash
# Traitement complet avec exclusions intelligentes
gitingest ai batch ./monorepo --exclude-dirs node_modules dist build .git logs --max-output-size 1MB
```

### Microservices
```bash
# Plusieurs services en parallèle
gitingest ai batch ./service1 ./service2 ./service3 --parallel 10 --output-dir ./digests
```

## 📱 Mobile & App

### React Native
```bash
gitingest ai batch ./mobile-app --include-ext .js .jsx .ts .tsx .json --exclude-dirs node_modules ios android
```

### Flutter
```bash
gitingest ai batch ./flutter_app --include-ext .dart .yaml --exclude-dirs build .dart_tool
```

## 🔧 Configuration & DevOps

### Infrastructure as Code
```bash
gitingest ai batch ./terraform --include-ext .tf .yml .yaml .json --max-output-size 800KB
```

### CI/CD
```bash
gitingest ai batch ./.github ./docker --include-ext .yml .yaml .dockerfile .sh
```

## 📚 Documentation & Content

### Projets avec docs
```bash
gitingest ai batch ./project --include-ext .md .rst .txt --exclude-dirs node_modules dist
```

## 🎯 Recommandations par Taille de Projet

### Petit Projet (< 50 fichiers)
```bash
gitingest ai batch ./small_project
# Résultat: 1 fichier TXT, facile à copier-coller
```

### Projet Moyen (50-200 fichiers)
```bash
gitingest ai batch ./medium_project --max-output-size 1MB --split-mode auto
# Résultat: 2-5 fichiers, parfait pour ChatGPT
```

### Gros Projet (200+ fichiers)
```bash
gitingest ai batch ./large_project --max-output-size 500KB --split-mode truncate --include-ext .py .js .ts
# Résultat: 1 fichier tronqué intelligemment, garde l'essentiel
```

### Énorme Projet (1000+ fichiers)
```bash
gitingest ai batch ./huge_project --include-ext .py .js .ts --exclude-dirs tests docs examples --max-output-size 2MB --split-mode auto
# Résultat: Fichiers multiples, focus sur le code principal
```

## 💡 Astuces Pro

### Test Rapide
```bash
# Voir ce qui serait généré sans créer les fichiers
gitingest ai batch ./projet --dry-run --verbose
```

### Optimisation de Performance
```bash
# Traitement parallèle maximal
gitingest ai batch ./projet1 ./projet2 ./projet3 --parallel 20
```

### Format Spécifique
```bash
# JSONL pour traitement automatisé (rare)
gitingest ai batch ./projet --format jsonl
```

---

## 🔄 Workflow Recommandé

1. **Test avec dry-run** : `--dry-run --verbose`
2. **Ajustement des filtres** : `--include-ext` ou `--exclude-ext`
3. **Limitation de taille** : `--max-output-size 1MB --split-mode auto`
4. **Production** : Commande finale sans dry-run

## 📊 Métriques de Performance

- **Petit projet** : < 1 seconde
- **Projet moyen** : 1-5 secondes  
- **Gros projet** : 5-30 secondes
- **Parallélisme** : 3-5x plus rapide avec `--parallel`

---

💡 **Conseil** : Le format TXT est parfait pour 95% des cas d'usage. GitIngest est maintenant optimisé pour l'IA par défaut ! 