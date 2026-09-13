#!/usr/bin/env bash
# Render PlantUML sources to SVG + PNG (requires podman, docker, or plantuml on PATH).
set -euo pipefail
cd "$(dirname "$0")"

build() {
  local name="$1"
  {
    head -1 "${name}.puml"
    cat _theme.puml
    tail -n +3 "${name}.puml"
  }
}

render_one() {
  local name="$1" format="$2" engine="$3"
  shift 3
  build "$name" | "$engine" "$@" -pipe -t"$format" > "${name}.${format}"
}

run_engine() {
  local engine=("$@")
  for f in system-overview data-flow dual-metering; do
    render_one "$f" svg "${engine[@]}"
    render_one "$f" png "${engine[@]}"
  done
}

if command -v plantuml >/dev/null 2>&1; then
  run_engine plantuml
elif command -v podman >/dev/null 2>&1; then
  run_engine podman run --rm -i docker.io/plantuml/plantuml
elif command -v docker >/dev/null 2>&1; then
  run_engine docker run --rm -i plantuml/plantuml
else
  echo "Install plantuml, or podman/docker with image docker.io/plantuml/plantuml" >&2
  exit 1
fi

echo "Rendered SVG + PNG for system-overview, data-flow, dual-metering"
