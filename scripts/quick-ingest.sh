#!/bin/bash

# Script utilitaire pour simplifier l'utilisation de gitingest
# Usage: ./quick-ingest.sh [options] <directories...>

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'aide
show_help() {
    echo -e "${BLUE}Script utilitaire gitingest${NC}"
    echo ""
    echo "Usage: $0 [options] <directories...>"
    echo ""
    echo "Options:"
    echo "  -h, --help                  Afficher cette aide"
    echo "  -m, --model MODEL          Modèle IA (gpt-4, claude-3-opus, gemini-1.5-pro, etc.)"
    echo "  -l, --languages LANGS      Raccourcis langages (py,js,ts,cs,java,go,rust,php,rb,kt,swift,dart)"
    echo "  -o, --output-dir DIR       Répertoire de sortie (défaut: ./output)"
    echo "  -p, --parallel N           Nombre de processus parallèles (défaut: 4)"
    echo "  -v, --verbose              Mode verbeux"
    echo "  -d, --dry-run              Simulation sans traitement"
    echo "  -f, --format FORMAT        Format de sortie (txt ou jsonl, défaut: txt)"
    echo "  --include-ext EXTS         Extensions à inclure (ex: .py,.js,.ts)"
    echo "  --exclude-ext EXTS         Extensions à exclure (ex: .log,.tmp)"
    echo "  --exclude-dirs DIRS        Répertoires à exclure (ex: node_modules,dist)"
    echo "  --max-output-size SIZE     Taille maximale de sortie (ex: 100MB, 1GB)"
    echo "  --split-mode MODE          Mode de division (auto|split|truncate)"
    echo ""
    echo "Modes de gestion de taille:"
    echo "  auto        Divise automatiquement si nécessaire (défaut)"
    echo "  split       Force la division en plusieurs fichiers"
    echo "  truncate    Tronque intelligemment le contenu"
    echo ""
    echo "Raccourcis langages supportés:"
    echo "  py          Python (.py, .pyi, .pyx)"
    echo "  js          JavaScript (.js, .mjs, .cjs)"
    echo "  ts          TypeScript (.ts, .tsx, .d.ts)"
    echo "  jsx         React JSX (.jsx, .tsx)"
    echo "  react       React complet (.js, .jsx, .ts, .tsx, .css, .scss)"
    echo "  vue         Vue.js (.vue, .js, .ts, .css, .scss)"
    echo "  cs          C# (.cs, .vb, .fs, .fsx)"
    echo "  dotnet      .NET complet (.cs, .vb, .fs, .json, .config)"
    echo "  java        Java (.java, .kt, .kts, .scala)"
    echo "  go          Go (.go, .mod, .sum)"
    echo "  rust        Rust (.rs, .toml)"
    echo "  php         PHP (.php, .phtml, .inc)"
    echo "  rb          Ruby (.rb, .rake, .gemspec)"
    echo "  swift       Swift (.swift, .h, .m)"
    echo "  dart        Dart/Flutter (.dart, .g.dart, .yaml)"
    echo "  kotlin      Kotlin (.kt, .kts)"
    echo "  scala       Scala (.scala, .sbt)"
    echo "  cpp         C++ (.cpp, .cxx, .cc, .h, .hpp)"
    echo "  c           C (.c, .h)"
    echo "  web         Web frontend (.html, .css, .scss, .js, .ts)"
    echo "  config      Configuration (.json, .yaml, .yml, .toml, .ini)"
    echo ""
    echo "Exemples:"
    echo "  $0 --languages py,js ./src ./api"
    echo "  $0 --model gpt-4 --languages react ./frontend"
    echo "  $0 --languages cs,dotnet --exclude-dirs bin,obj ./MyApp"
    echo "  $0 --languages java --output-dir ./analysis ./project1 ./project2"
}

# Fonction pour mapper les raccourcis langages vers extensions
map_languages() {
    local langs="$1"
    local extensions=""
    
    IFS=',' read -ra LANG_ARRAY <<< "$langs"
    for lang in "${LANG_ARRAY[@]}"; do
        case "$lang" in
            py|python)
                extensions="${extensions},.py,.pyi,.pyx,.pyw"
                ;;
            js|javascript)
                extensions="${extensions},.js,.mjs,.cjs"
                ;;
            ts|typescript)
                extensions="${extensions},.ts,.tsx,.d.ts"
                ;;
            jsx|react-jsx)
                extensions="${extensions},.jsx,.tsx"
                ;;
            react)
                extensions="${extensions},.js,.jsx,.ts,.tsx,.css,.scss,.sass,.less,.json"
                ;;
            vue)
                extensions="${extensions},.vue,.js,.ts,.css,.scss,.sass"
                ;;
            cs|csharp)
                extensions="${extensions},.cs,.vb,.fs,.fsx"
                ;;
            dotnet)
                extensions="${extensions},.cs,.vb,.fs,.fsx,.json,.config,.xml"
                ;;
            java)
                extensions="${extensions},.java,.kt,.kts,.scala"
                ;;
            go|golang)
                extensions="${extensions},.go,.mod,.sum"
                ;;
            rust|rs)
                extensions="${extensions},.rs,.toml"
                ;;
            php)
                extensions="${extensions},.php,.phtml,.inc,.phpt"
                ;;
            rb|ruby)
                extensions="${extensions},.rb,.rake,.gemspec,.ru"
                ;;
            swift)
                extensions="${extensions},.swift,.h,.m,.mm"
                ;;
            dart|flutter)
                extensions="${extensions},.dart,.g.dart,.yaml,.yml"
                ;;
            kotlin|kt)
                extensions="${extensions},.kt,.kts"
                ;;
            scala)
                extensions="${extensions},.scala,.sbt,.sc"
                ;;
            cpp|c++)
                extensions="${extensions},.cpp,.cxx,.cc,.c++,.h,.hpp,.hxx"
                ;;
            c)
                extensions="${extensions},.c,.h"
                ;;
            web|frontend)
                extensions="${extensions},.html,.htm,.css,.scss,.sass,.less,.js,.ts,.jsx,.tsx"
                ;;
            config|configuration)
                extensions="${extensions},.json,.yaml,.yml,.toml,.ini,.cfg,.conf,.properties"
                ;;
            *)
                echo -e "${YELLOW}Attention: Langage '$lang' non reconnu, ignoré${NC}" >&2
                ;;
        esac
    done
    
    # Supprimer la virgule initiale
    echo "${extensions#,}"
}

# Variables par défaut
MODEL="batch"  # Utilise le mode batch par défaut
LANGUAGES=""
OUTPUT_DIR="./output"
PARALLEL=4
VERBOSE=false
DRY_RUN=false
FORMAT="txt"  # Format par défaut TXT
INCLUDE_EXT=""
EXCLUDE_EXT=""
EXCLUDE_DIRS=""
MAX_OUTPUT_SIZE=""
SPLIT_MODE="auto"
DIRECTORIES=()

# Parsing des arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -m|--model)
            MODEL="$2"
            shift 2
            ;;
        -l|--languages)
            LANGUAGES="$2"
            shift 2
            ;;
        -o|--output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -p|--parallel)
            PARALLEL="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -f|--format)
            FORMAT="$2"
            shift 2
            ;;
        --include-ext)
            INCLUDE_EXT="$2"
            shift 2
            ;;
        --exclude-ext)
            EXCLUDE_EXT="$2"
            shift 2
            ;;
        --exclude-dirs)
            EXCLUDE_DIRS="$2"
            shift 2
            ;;
        --max-output-size)
            MAX_OUTPUT_SIZE="$2"
            shift 2
            ;;
        --split-mode)
            SPLIT_MODE="$2"
            shift 2
            ;;
        -*)
            echo -e "${RED}Option inconnue: $1${NC}" >&2
            exit 1
            ;;
        *)
            DIRECTORIES+=("$1")
            shift
            ;;
    esac
done

# Vérifier qu'au moins un répertoire est spécifié
if [ ${#DIRECTORIES[@]} -eq 0 ]; then
    echo -e "${RED}Erreur: Aucun répertoire spécifié${NC}" >&2
    echo "Utilisez -h pour l'aide"
    exit 1
fi

# Vérifier l'existence des répertoires
for dir in "${DIRECTORIES[@]}"; do
    if [ ! -d "$dir" ]; then
        echo -e "${RED}Erreur: Le répertoire '$dir' n'existe pas${NC}" >&2
        exit 1
    fi
done

# Créer le répertoire de sortie s'il n'existe pas
mkdir -p "$OUTPUT_DIR"

# Mapper les langages vers extensions si spécifié
if [ -n "$LANGUAGES" ]; then
    MAPPED_EXTENSIONS=$(map_languages "$LANGUAGES")
    if [ -n "$INCLUDE_EXT" ]; then
        INCLUDE_EXT="${INCLUDE_EXT},${MAPPED_EXTENSIONS}"
    else
        INCLUDE_EXT="$MAPPED_EXTENSIONS"
    fi
fi

# Construire la commande gitingest
if [ -n "$MODEL" ] && [ "$MODEL" != "batch" ]; then
    CMD="gitingest ai $MODEL"
else
    CMD="gitingest ai batch"
    # Ajouter le format pour le mode batch
    CMD="$CMD --format $FORMAT"
fi

# Ajouter les options
if [ -n "$INCLUDE_EXT" ]; then
    CMD="$CMD --include-ext $INCLUDE_EXT"
fi

if [ -n "$EXCLUDE_EXT" ]; then
    CMD="$CMD --exclude-ext $EXCLUDE_EXT"
fi

if [ -n "$EXCLUDE_DIRS" ]; then
    CMD="$CMD --exclude-dirs $EXCLUDE_DIRS"
fi

if [ "$MODEL" == "batch" ] || [ -z "$MODEL" ]; then
    CMD="$CMD --parallel $PARALLEL"
fi

if [ "$VERBOSE" = true ]; then
    CMD="$CMD --verbose"
fi

if [ "$DRY_RUN" = true ]; then
    CMD="$CMD --dry-run"
fi

# Ajouter les nouvelles options de limitation de taille
if [ -n "$MAX_OUTPUT_SIZE" ]; then
    CMD="$CMD --max-output-size $MAX_OUTPUT_SIZE"
fi

if [ "$SPLIT_MODE" != "auto" ]; then
    CMD="$CMD --split-mode $SPLIT_MODE"
fi

# Ajouter les répertoires
for dir in "${DIRECTORIES[@]}"; do
    CMD="$CMD $dir"
done

# Afficher le résumé
echo -e "${BLUE}=== Configuration gitingest ===${NC}"
echo -e "Modèle IA: ${GREEN}${MODEL:-"batch (parallèle)"}${NC}"
echo -e "Format: ${GREEN}${FORMAT}${NC}"
echo -e "Répertoires: ${GREEN}${DIRECTORIES[*]}${NC}"
echo -e "Sortie: ${GREEN}${OUTPUT_DIR}${NC}"
if [ "$MODEL" == "batch" ] || [ -z "$MODEL" ]; then
    echo -e "Processus parallèles: ${GREEN}${PARALLEL}${NC}"
fi

if [ -n "$LANGUAGES" ]; then
    echo -e "Langages: ${GREEN}${LANGUAGES}${NC}"
fi

if [ -n "$INCLUDE_EXT" ]; then
    echo -e "Extensions incluses: ${GREEN}${INCLUDE_EXT}${NC}"
fi

if [ -n "$EXCLUDE_EXT" ]; then
    echo -e "Extensions exclues: ${YELLOW}${EXCLUDE_EXT}${NC}"
fi

if [ -n "$EXCLUDE_DIRS" ]; then
    echo -e "Répertoires exclus: ${YELLOW}${EXCLUDE_DIRS}${NC}"
fi

if [ -n "$MAX_OUTPUT_SIZE" ]; then
    echo -e "Taille max sortie: ${YELLOW}${MAX_OUTPUT_SIZE}${NC}"
fi

if [ "$SPLIT_MODE" != "auto" ]; then
    echo -e "Mode division: ${YELLOW}${SPLIT_MODE}${NC}"
fi

echo ""
echo -e "${BLUE}Commande exécutée:${NC}"
echo -e "${GREEN}${CMD}${NC}"
echo ""

# Exécuter la commande
if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}Mode simulation - commande non exécutée${NC}"
else
    echo -e "${BLUE}Démarrage du traitement...${NC}"
    cd "$OUTPUT_DIR"
    eval "$CMD"
    
    echo ""
    echo -e "${GREEN}✓ Traitement terminé avec succès!${NC}"
    echo -e "Fichiers générés dans: ${GREEN}${OUTPUT_DIR}${NC}"
    
    # Lister les fichiers générés
    echo ""
    echo -e "${BLUE}Fichiers générés:${NC}"
    
    # Rechercher selon le format utilisé
    if [ "$FORMAT" == "txt" ]; then
        find . -name "*.txt" -type f -exec basename {} \; | sort | while read -r file; do
            size=$(du -h "$file" | cut -f1)
            echo -e "  ${GREEN}${file}${NC} (${YELLOW}${size}${NC})"
        done
    else
        find . -name "*.jsonl" -type f -exec basename {} \; | sort | while read -r file; do
            size=$(du -h "$file" | cut -f1)
            echo -e "  ${GREEN}${file}${NC} (${YELLOW}${size}${NC})"
        done
    fi
fi 