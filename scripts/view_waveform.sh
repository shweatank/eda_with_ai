#!/usr/bin/env bash
# ---------------------------------------------------------------------
# Open a generated VCD in GTKWave with the right signals pre-loaded.
#
#   ./scripts/view_waveform.sh traffic_light          newest traffic light run
#   ./scripts/view_waveform.sh alu                    newest ALU run
#   ./scripts/view_waveform.sh traffic_light failing  newest failing run
#   ./scripts/view_waveform.sh JOB-ac184cd73c5c       one specific job
#   ./scripts/view_waveform.sh --list                 list what is available
#
# Also strips the VS Code snap environment, which otherwise breaks the
# system gtkwave with a GLIBC/libpthread symbol error.
# ---------------------------------------------------------------------
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JOBS="$ROOT/data/jobs"
VIEWS="$ROOT/waveform_views"

if ! command -v gtkwave >/dev/null 2>&1; then
    echo "gtkwave is not installed. Install it with:" >&2
    echo "    sudo apt install gtkwave" >&2
    exit 1
fi

if [ ! -d "$JOBS" ] || [ -z "$(ls -A "$JOBS" 2>/dev/null | grep '^JOB-' || true)" ]; then
    echo "No verification runs found in $JOBS" >&2
    echo "Run a verification from Streamlit first." >&2
    exit 1
fi

# ---- describe a job directory by reading its simulation.log ----
describe() {
    local dir="$1" log="$1/simulation.log" kind="?" verdict="?"
    if [ -f "$log" ]; then
        grep -q "TRAFFIC LIGHT" "$log" && kind="traffic_light"
        grep -q "4-BIT ALU"     "$log" && kind="alu"
        verdict="$(grep -oE 'STATUS: (PASSED|FAILED)' "$log" | tail -1 | awk '{print $2}')"
    fi
    echo "$kind ${verdict:-?}"
}

if [ "${1:-}" = "--list" ] || [ "${1:-}" = "-l" ]; then
    printf "  %-20s %-14s %-7s %s\n" "JOB" "EXAMPLE" "RESULT" "VCD"
    for d in $(ls -td "$JOBS"/JOB-*/ 2>/dev/null); do
        read -r kind verdict <<<"$(describe "${d%/}")"
        vcd="OK"; [ -f "${d}waveform.vcd" ] || vcd="missing"
        printf "  %-20s %-14s %-7s %s\n" "$(basename "${d%/}")" "$kind" "$verdict" "$vcd"
    done
    exit 0
fi

TARGET="${1:-traffic_light}"
SCENARIO="${2:-}"
JOB_DIR=""

if [[ "$TARGET" == JOB-* ]]; then
    JOB_DIR="$JOBS/$TARGET"
    [ -d "$JOB_DIR" ] || { echo "No such job: $TARGET" >&2; exit 1; }
else
    # newest job matching the example (and scenario, if given)
    want_verdict=""
    case "$SCENARIO" in
        passing) want_verdict="PASSED" ;;
        failing) want_verdict="FAILED" ;;
        "")      want_verdict="" ;;
        *) echo "Scenario must be 'passing' or 'failing'." >&2; exit 1 ;;
    esac
    for d in $(ls -td "$JOBS"/JOB-*/ 2>/dev/null); do
        read -r kind verdict <<<"$(describe "${d%/}")"
        [ "$kind" = "$TARGET" ] || continue
        [ -f "${d}waveform.vcd" ] || continue
        if [ -n "$want_verdict" ] && [ "$verdict" != "$want_verdict" ]; then continue; fi
        JOB_DIR="${d%/}"; break
    done
    [ -n "$JOB_DIR" ] || {
        echo "No run found for '$TARGET' ${SCENARIO:+($SCENARIO)}." >&2
        echo "Run one from Streamlit, or list what exists:" >&2
        echo "    ./scripts/view_waveform.sh --list" >&2
        exit 1
    }
fi

VCD="$JOB_DIR/waveform.vcd"
[ -f "$VCD" ] || { echo "No waveform.vcd in $JOB_DIR" >&2; exit 1; }

read -r kind verdict <<<"$(describe "$JOB_DIR")"
SAVE="$VIEWS/${kind}.gtkw"

echo "Job      : $(basename "$JOB_DIR")"
echo "Example  : $kind   Result: $verdict"
echo "Waveform : $VCD"
[ -f "$SAVE" ] && echo "View     : $SAVE" || SAVE=""

# strip the VS Code snap environment so the system gtkwave can load
exec env -u SNAP -u SNAP_NAME -u SNAP_REVISION -u SNAP_INSTANCE_NAME \
         -u GTK_PATH -u GTK_EXE_PREFIX -u GDK_PIXBUF_MODULE_FILE \
         -u GIO_MODULE_DIR -u LOCPATH -u GSETTINGS_SCHEMA_DIR \
         gtkwave "$VCD" ${SAVE:+"$SAVE"}
