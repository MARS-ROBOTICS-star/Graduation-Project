#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

INPUT_ROOT="${REPO_ROOT}/docs/literature"
OUTPUT_ROOT="${REPO_ROOT}/docs/literature/mineru_output"
SINGLE_PDF=""
declare -a EXTRA_ARGS=()

usage() {
  cat <<'EOF'
Usage:
  scripts/literature/mineru_batch_convert.sh [options] [-- <extra mineru args>]

Options:
  --input-root PATH   Directory containing source PDFs.
  --output-root PATH  Directory where MinerU outputs are written.
  --pdf PATH          Convert a single PDF instead of the whole directory.
  -h, --help          Show this help text.

Examples:
  scripts/literature/mineru_batch_convert.sh
  scripts/literature/mineru_batch_convert.sh --pdf docs/literature/Sartoretti\ 等\ -\ 2019\ -\ Distributed\ learning\ of\ decentralized\ control\ policies\ for\ articulated\ mobile\ robots.pdf
  scripts/literature/mineru_batch_convert.sh -- --lang en
EOF
}

while (($# > 0)); do
  case "$1" in
    --input-root)
      INPUT_ROOT="$2"
      shift 2
      ;;
    --output-root)
      OUTPUT_ROOT="$2"
      shift 2
      ;;
    --pdf)
      SINGLE_PDF="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      EXTRA_ARGS=("$@")
      break
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if ! command -v mineru >/dev/null 2>&1; then
  echo "The 'mineru' CLI is not available in PATH." >&2
  echo "Install MinerU first, then rerun this script." >&2
  exit 1
fi

export MPLCONFIGDIR="${MPLCONFIGDIR:-/tmp/matplotlib}"
export YOLO_CONFIG_DIR="${YOLO_CONFIG_DIR:-/tmp/Ultralytics}"
mkdir -p "${MPLCONFIGDIR}" "${YOLO_CONFIG_DIR}"

mkdir -p "${OUTPUT_ROOT}"

declare -a PDFS=()
if [[ -n "${SINGLE_PDF}" ]]; then
  if [[ ! -f "${SINGLE_PDF}" ]]; then
    echo "PDF not found: ${SINGLE_PDF}" >&2
    exit 1
  fi
  PDFS=("${SINGLE_PDF}")
else
  while IFS= read -r pdf; do
    PDFS+=("${pdf}")
  done < <(find "${INPUT_ROOT}" -maxdepth 1 -type f -name '*.pdf' | sort)
fi

if [[ "${#PDFS[@]}" -eq 0 ]]; then
  echo "No PDFs found to convert." >&2
  exit 1
fi

for pdf in "${PDFS[@]}"; do
  stem="$(basename "${pdf}" .pdf)"
  expected_dir="${OUTPUT_ROOT}/${stem}"
  if [[ -d "${expected_dir}" ]]; then
    echo "Skipping existing output: ${expected_dir}"
    continue
  fi

  echo "Converting: ${pdf}"
  mineru -p "${pdf}" -o "${OUTPUT_ROOT}" "${EXTRA_ARGS[@]}"

  if [[ ! -d "${expected_dir}" ]]; then
    echo "MinerU did not create the expected output directory: ${expected_dir}" >&2
    exit 1
  fi
  if ! find "${expected_dir}" -type f -name '*.md' | grep -q .; then
    echo "MinerU finished without producing Markdown under: ${expected_dir}" >&2
    exit 1
  fi
done

python3 "${SCRIPT_DIR}/build_literature_manifest.py" \
  --source-root "${INPUT_ROOT}" \
  --output-root "${OUTPUT_ROOT}" \
  --manifest "${INPUT_ROOT}/catalog.md"

echo "Manifest updated: ${INPUT_ROOT}/catalog.md"
