# YouTube Subtitle Downloader

A Claude Code skill for downloading YouTube subtitles and converting them into clean, structured Markdown for language learning.

**Manual subtitles first, auto-generated as fallback.**

## What This Does

Paste a YouTube URL, get a beautifully formatted Markdown file with:
- Subtitles merged into readable paragraphs (not fragmented lines)
- Timestamps for easy video navigation
- Video metadata (title, channel, duration, subtitle source)
- Works with any language: English, Russian, Chinese, Japanese, etc.

### Key Features

- **Smart Subtitle Detection** — Automatically finds and prefers manual subtitles over auto-generated
- **Clean Paragraph Merging** — Joins fragmented SRT lines into natural sentence groups
- **One-Command Workflow** — `./download.sh URL` handles everything
- **Universal Language Support** — Works with any YouTube video in any language
- **Chrome Cookie Auth** — Bypasses YouTube's bot detection using your browser session

## Installation

### Via Claude Code Plugin Marketplace (Recommended)

```bash
/plugin marketplace add wanxiao2018/youtube-subtitle-downloader
/plugin install youtube-subtitles@youtube-subtitle-downloader
```

Then use it by typing `/youtube-subtitles` in Claude Code.

### Manual Installation

```bash
# Clone to Claude Code skills directory
git clone https://github.com/wanxiao2018/youtube-subtitle-downloader.git \
  ~/.claude/skills/youtube-subtitle-downloader
```

### As Standalone CLI (No Claude Code)

```bash
git clone https://github.com/wanxiao2018/youtube-subtitle-downloader.git
cd youtube-subtitle-downloader
./scripts/download.sh "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Prerequisites

```bash
# yt-dlp — YouTube video downloader
brew install yt-dlp            # macOS
pip install yt-dlp             # Linux / Windows

# jq — JSON processor (for subtitle detection)
brew install jq                # macOS
apt install jq                 # Linux

# Chrome browser — must have logged into YouTube at least once
```

> **Why Chrome cookies?** YouTube aggressively blocks automated requests.
> `yt-dlp` reads your Chrome cookies to authenticate as a real browser session.

## Usage

### In Claude Code

```
/youtube-subtitles

> "Download English subtitles for this video: https://www.youtube.com/watch?v=UF8uR6Z6KLc"
```

The skill will:
1. Fetch video metadata (title, channel, duration)
2. Detect available subtitles (manual vs auto)
3. Download the best available subtitle
4. Convert to clean Markdown with timestamps
5. Open the result

### As CLI

```bash
cd youtube-subtitle-downloader

# One-step download + convert
./scripts/download.sh <youtube_url> [output_dir] [filename] [language]

# Examples
./scripts/download.sh "https://www.youtube.com/watch?v=ql74BfIjdIs"
./scripts/download.sh "https://youtu.be/UF8uR6Z6KLc" ~/Desktop steve-jobs en
./scripts/download.sh "URL" . my-video zh-Hans
```

### Step by Step

```bash
# 1. Check available subtitles
yt-dlp --cookies-from-browser chrome --list-subs "URL"

# 2. Download subtitles
yt-dlp --cookies-from-browser chrome \
  --write-sub --sub-lang en --sub-format srt \
  --skip-download --no-write-auto-sub \
  -o "output" "URL"

# 3. Convert to Markdown
python3 scripts/srt_to_md.py \
  --srt output.en.srt \
  --title "Video Title" \
  --video-url "URL" \
  --output output.md
```

## Output Format

```markdown
# Video Title

> **Channel:** [Channel Name](channel_url)
> **Video:** https://...
> **Duration:** 15:04
> **Subtitles:** manual (community)

---

**[00:00]**

Merged paragraph text. No more fragmented subtitle lines.
Every few sentences grouped into a readable block.

---

**[00:32]**

Next paragraph with natural sentence boundaries.
```

## Subtitle Priority

| Priority | Source | Quality |
|----------|--------|---------|
| 1st | Manual subtitles (creator / community) | Best — proper punctuation, reviewed by humans |
| 2nd | Auto-generated (YouTube speech recognition) | Good — minor errors possible |

## Examples

See the [`examples/`](examples/) directory:

| File | Video | Language | Subtitle Source |
|------|-------|----------|-----------------|
| [`steve-jobs.md`](examples/steve-jobs.md) | [Steve Jobs Stanford Speech](https://www.youtube.com/watch?v=UF8uR6Z6KLc) | English | Manual (community) |
| [`vlog31.md`](examples/vlog31.md) | [Vlog 31 — One Day in My Native Town](https://www.youtube.com/watch?v=ql74BfIjdIs) | Russian | Manual (from creator) |

## Architecture

| File | Purpose |
|------|---------|
| `SKILL.md` | Claude Code skill definition (AI reads this) |
| `scripts/download.sh` | Standalone CLI tool |
| `scripts/srt_to_md.py` | SRT → Markdown converter |
| `.claude-plugin/` | Plugin marketplace manifest |
| `examples/` | Sample SRT files and generated outputs |

## Troubleshooting

**"Sign in to confirm you're not a bot"**
Chrome must be installed and you've logged into YouTube at least once.

**No subtitles found for language X**
Run `yt-dlp --cookies-from-browser chrome --list-subs "URL"` to see available codes.

**Auto-generated subtitles have errors**
Expected. Manual subtitles are always preferred when available.

## Requirements

- Python 3.8+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [jq](https://jqlang.github.io/jq/)
- Chrome browser (for cookie extraction)

## License

MIT
