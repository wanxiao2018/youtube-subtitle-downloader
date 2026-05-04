---
name: youtube-subtitles
description: Download YouTube video subtitles and convert to clean Markdown for language learning. Supports any language. Manual subtitles prioritized over auto-generated. Use when the user wants to download subtitles, extract YouTube captions, or create learning materials from videos.
---

# YouTube Subtitle Downloader

Download subtitles from any YouTube video and convert them into structured, readable Markdown for language learning.

## Core Principles

1. **Manual First** — Always prefer manually uploaded subtitles over auto-generated. Better punctuation, fewer errors.
2. **Clean Output** — Merge fragmented SRT lines into readable paragraphs. No broken sentences.
3. **Universal** — Works with any YouTube video, any language.
4. **One Command** — Minimize user friction. Ideally: paste URL, get Markdown.

## Prerequisites

Before starting, verify these are installed:

```bash
command -v yt-dlp    # brew install yt-dlp
command -v python3   # Python 3.8+
command -v jq        # brew install jq
command -v gh        # brew install gh (optional, for GitHub operations)
```

Chrome browser must be installed with at least one YouTube login session.

---

## Phase 1: Get Video Info

When the user provides a YouTube URL:

1. **Extract metadata** using yt-dlp with Chrome cookies:

```bash
yt-dlp --cookies-from-browser chrome \
  --print "%(title)s---%(channel)s---%(channel_url)s---%(duration_string)s" \
  --skip-download "URL"
```

2. **Parse** the `---` separated output to get: title, channel name, channel URL, duration.

---

## Phase 2: Detect & Download Subtitles

1. **Get subtitle list** via JSON:

```bash
yt-dlp --cookies-from-browser chrome --dump-json --skip-download "URL"
```

2. **Check manual subtitles** in the `subtitles` field of the JSON.
3. **Check auto subtitles** in the `requested_subtitles` or `automatic_captions` field.
4. **Match language** — handle extended codes like `en-eEY6OEpapPo` for `en`:

```bash
# For each code in subtitles, check if code == LANG or code starts with LANG-
```

5. **Download** with appropriate flag:
   - Manual found: `--write-sub --sub-lang CODE --sub-format srt --no-write-auto-sub`
   - Auto only: `--write-sub --sub-lang CODE --sub-format srt --write-auto-sub`

6. **Rename** the SRT file to a clean `PREFIX.LANG.srt` name (yt-dlp may use extended codes in filename).

---

## Phase 3: Convert to Markdown

Run the converter script at `SKILL_DIR/scripts/srt_to_md.py`:

```bash
python3 SKILL_DIR/scripts/srt_to_md.py \
  --srt input.srt \
  --title "Video Title" \
  --video-url "URL" \
  --channel "Channel Name" \
  --channel-url "Channel URL" \
  --duration "15:04" \
  --sub-type "manual (from creator)" \
  --output output.md
```

### Output Format

```markdown
# Video Title

> **Channel:** [Name](url)
> **Video:** URL
> **Duration:** MM:SS
> **Subtitles:** manual / auto-generated

---

**[00:00]**

Merged paragraph text. Fragments joined into readable blocks.

---
```

---

## Phase 4: Deliver

1. **Open** the Markdown file: `open output.md`
2. **Summarize** to user:
   - Video title and channel
   - Subtitle source (manual vs auto)
   - Paragraph count and file size
   - File location
3. **If manual subtitles were used**, mention this explicitly — it's the quality differentiator.

---

## Pitfalls

| Issue | Solution |
|-------|----------|
| "Sign in to confirm you're not a bot" | Chrome must be installed with YouTube login |
| SSL warnings | Harmless, ignore |
| No subtitles for language X | Run `--list-subs` to show available codes |
| Auto subtitles have errors | Expected. Manual always preferred |
| yt-dlp puts extended codes in filename | Script auto-renames to clean `PREFIX.LANG.srt` |
| `jq` not installed | `brew install jq` required for JSON parsing |

---

## Batch Mode

For multiple videos (e.g., a playlist):

1. Get video list from playlist
2. Loop through each URL
3. Run Phase 1-3 for each
4. Report summary of all downloaded files

---

## Supporting Files

| File | Purpose | When to Read |
|------|---------|--------------|
| [scripts/srt_to_md.py](scripts/srt_to_md.py) | SRT → Markdown converter | Phase 3 |
| [scripts/download.sh](scripts/download.sh) | Standalone CLI tool (not required for skill) | User direct usage |
