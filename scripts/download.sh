#!/usr/bin/env bash
#
# download.sh — Download YouTube subtitles and convert to learning Markdown
#
# Usage:
#   ./download.sh <youtube_url> [output_dir] [filename] [language]
#
# Examples:
#   ./download.sh "https://www.youtube.com/watch?v=ql74BfIjdIs"
#   ./download.sh "https://youtu.be/xxxxx" ~/Desktop steve-jobs en
#   ./download.sh "URL" . my-video zh-Hans
#
# Priority: manual subtitles > auto-generated subtitles
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRT_TO_MD="$SCRIPT_DIR/srt_to_md.py"

# ── Args ──────────────────────────────────────────────
URL="${1:?Usage: $0 <youtube_url> [output_dir] [filename] [language]}"
OUTPUT_DIR="${2:-.}"
FILENAME="${3:-subtitle}"
LANG="${4:-ru}"

# ── Helpers ───────────────────────────────────────────
info()  { echo "[INFO]  $*"; }
ok()    { echo "[OK]    $*"; }
warn()  { echo "[WARN]  $*"; }
fail()  { echo "[ERROR] $*"; exit 1; }

# ── Check prerequisites ──────────────────────────────
command -v yt-dlp >/dev/null 2>&1 || fail "yt-dlp not installed. Run: brew install yt-dlp (macOS) or pip install yt-dlp"
command -v python3 >/dev/null 2>&1 || fail "python3 not found"
command -v jq >/dev/null 2>&1 || fail "jq not installed. Run: brew install jq"

mkdir -p "$OUTPUT_DIR"

# ── Step 1: Get video info ───────────────────────────
info "Fetching video info..."
VIDEO_JSON=$(yt-dlp --cookies-from-browser chrome \
  --print "%(title)s---%(channel)s---%(channel_url)s---%(duration_string)s" \
  --skip-download "$URL" 2>/dev/null) \
  || fail "Failed to fetch video info. Make sure Chrome is installed and you've logged into YouTube."

TITLE=$(echo "$VIDEO_JSON" | awk -F'---' '{print $1}')
CHANNEL=$(echo "$VIDEO_JSON" | awk -F'---' '{print $2}')
CHANNEL_URL=$(echo "$VIDEO_JSON" | awk -F'---' '{print $3}')
DURATION=$(echo "$VIDEO_JSON" | awk -F'---' '{print $4}')

info "Title:    $TITLE"
info "Channel:  $CHANNEL"
info "Duration: $DURATION"

# ── Step 2: Detect subtitles via JSON ────────────────
info "Checking available subtitles..."
SUB_JSON=$(yt-dlp --cookies-from-browser chrome --dump-json --skip-download "$URL" 2>/dev/null)

# Check manual subtitles (requested_subtitles or subtitles field)
MANUAL_LANGS=$(echo "$SUB_JSON" | jq -r '.subtitles // {} | keys[]' 2>/dev/null)
AUTO_LANGS=$(echo "$SUB_JSON" | jq -r '.requested_subtitles // .automatic_captions // {} | keys[]' 2>/dev/null)

# Find matching manual subtitle (handles codes like "en-eEY6OEpapPo" for "en")
MANUAL_MATCH=""
for code in $MANUAL_LANGS; do
    if [[ "$code" == "$LANG" || "$code" == "$LANG-"* ]]; then
        MANUAL_MATCH="$code"
        break
    fi
done

AUTO_MATCH=""
for code in $AUTO_LANGS; do
    if [[ "$code" == "$LANG" || "$code" == "$LANG-"* || "$code" == "$LANG-orig" ]]; then
        AUTO_MATCH="$code"
        break
    fi
done

# Determine download strategy
SUB_TYPE=""
SUBLANG=""
if [ -n "$MANUAL_MATCH" ]; then
    info "Found manual subtitles: '$MANUAL_MATCH' (best quality)"
    SUB_TYPE="manual (from creator/community)"
    SUBLANG="$MANUAL_MATCH"
    AUTO_FLAG="--no-write-auto-sub"
elif [ -n "$AUTO_MATCH" ]; then
    warn "No manual subtitles found. Using auto-generated: '$AUTO_MATCH'"
    SUB_TYPE="auto-generated (YouTube speech recognition)"
    SUBLANG="$AUTO_MATCH"
    AUTO_FLAG="--write-auto-sub"
else
    echo ""
    echo "No subtitles found for language '$LANG'."
    echo ""
    echo "Available manual: $(echo "$MANUAL_LANGS" | tr '\n' ' ')"
    echo "Available auto:   $(echo "$AUTO_LANGS" | head -5 | tr '\n' ' ')..."
    fail "Try a different language code."
fi

# ── Step 3: Download subtitles ───────────────────────
SRT_PATH="$OUTPUT_DIR/$FILENAME.$LANG.srt"
info "Downloading subtitles ($SUBLANG)..."
yt-dlp --cookies-from-browser chrome \
    --write-sub --sub-lang "$SUBLANG" --sub-format srt \
    --skip-download $AUTO_FLAG \
    -o "$OUTPUT_DIR/$FILENAME" \
    "$URL" 2>&1 | grep -E "(Writing|download)" || true

# Handle yt-dlp naming variations
if [ ! -f "$SRT_PATH" ]; then
    # Try the exact subtitle code in filename
    ALT_PATH="$OUTPUT_DIR/$FILENAME.$SUBLANG.srt"
    if [ -f "$ALT_PATH" ]; then
        mv "$ALT_PATH" "$SRT_PATH"
    else
        # Find any matching .srt file
        FOUND=$(find "$OUTPUT_DIR" -maxdepth 1 -name "$FILENAME*.srt" -newer "$OUTPUT_DIR" | head -1)
        if [ -n "$FOUND" ]; then
            mv "$FOUND" "$SRT_PATH"
        else
            fail "SRT file not found after download. Check $OUTPUT_DIR/"
        fi
    fi
fi

ok "Subtitles saved: $SRT_PATH"

# ── Step 4: Convert to Markdown ──────────────────────
MD_PATH="$OUTPUT_DIR/$FILENAME.md"
info "Converting to Markdown..."
python3 "$SRT_TO_MD" \
    --srt "$SRT_PATH" \
    --title "$TITLE" \
    --video-url "$URL" \
    --channel "$CHANNEL" \
    --channel-url "$CHANNEL_URL" \
    --duration "$DURATION" \
    --sub-type "$SUB_TYPE" \
    --output "$MD_PATH"

ok "Done! Output: $MD_PATH"
