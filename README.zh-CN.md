# YouTube 字幕下载器

将 YouTube 视频字幕转换为结构化的 Markdown 文本，方便语言学习。

**优先下载人工字幕，没有才用自动字幕兜底。**

## 功能特点

- **智能字幕检测** — 自动优先选择人工上传的字幕，质量更高
- **干净的段落合并** — 将碎片化的 SRT 行合并成可读的段落
- **一键操作** — `./download.sh URL` 搞定一切
- **多语言支持** — 支持任何语言的 YouTube 视频
- **Chrome Cookie 认证** — 通过浏览器会话绕过 YouTube 的 bot 检测
- **多语言对齐** — 支持俄/英/中三语 30 秒窗口对齐，方便精听精读

## 安装

### Claude Code 插件市场（推荐）

```bash
/plugin marketplace add wanxiao2018/youtube-subtitle-downloader
/plugin install youtube-subtitles@youtube-subtitle-downloader
```

然后在 Claude Code 中输入 `/youtube-subtitles` 即可使用。

### Hermes Agent

```bash
# 克隆仓库
git clone https://github.com/wanxiao2018/youtube-subtitle-downloader.git

# 复制 skill 到 Hermes skills 目录
mkdir -p ~/.hermes/skills/media/youtube-subtitle-downloader
cp youtube-subtitle-downloader/SKILL.md ~/.hermes/skills/media/youtube-subtitle-downloader/
```

或者直接问 Hermes："下载这个 YouTube 视频的字幕"

### 独立 CLI

```bash
git clone https://github.com/wanxiao2018/youtube-subtitle-downloader.git
cd youtube-subtitle-downloader
./scripts/download.sh "https://www.youtube.com/watch?v=VIDEO_ID"
```

## 前置要求

```bash
# yt-dlp — YouTube 视频下载器
brew install yt-dlp            # macOS
pip install yt-dlp             # Linux / Windows

# jq — JSON 处理器（用于字幕检测）
brew install jq                # macOS
apt install jq                 # Linux

# Chrome 浏览器 — 必须至少登录过一次 YouTube
```

> **为什么用 Chrome cookies？** YouTube 会积极阻止自动化请求。`yt-dlp` 读取你的 Chrome cookies 来模拟真实浏览器会话。

## 使用方法

### 在 Claude Code 中

```
/youtube-subtitles

> "下载这个视频的英文字幕: https://www.youtube.com/watch?v=UF8uR6Z6KLc"
```

### 作为 CLI

```bash
cd youtube-subtitle-downloader

# 一步下载 + 转换
./scripts/download.sh <youtube_url> [output_dir] [filename] [language]

# 示例
./scripts/download.sh "https://www.youtube.com/watch?v=ql74BfIjdIs"
./scripts/download.sh "https://youtu.be/UF8uR6Z6KLc" ~/Desktop steve-jobs en
./scripts/download.sh "URL" . my-video zh-Hans
```

### 分步操作

```bash
# 1. 检查可用字幕
yt-dlp --cookies-from-browser chrome --list-subs "URL"

# 2. 下载字幕
yt-dlp --cookies-from-browser chrome \
  --write-sub --sub-lang en --sub-format srt \
  --skip-download --no-write-auto-sub \
  -o "output" "URL"

# 3. 转换为 Markdown
python3 scripts/srt_to_md.py \
  --srt output.en.srt \
  --title "视频标题" \
  --video-url "URL" \
  --output output.md
```

### 批量下载（搭建语料库）

```bash
# 批量下载播放列表
yt-dlp --cookies-from-browser chrome \
  --write-sub --sub-lang ru --sub-format srt \
  --skip-download --no-write-auto-sub \
  -o "语料库/%(title)s.%(ext)s" \
  "https://youtube.com/playlist?list=xxx"

# 批量转换为 Markdown
for srt in 语料库/*.srt; do
  python3 scripts/srt_to_md.py --srt "$srt" --output "${srt%.srt}.md"
done
```

### 多语言对齐

```bash
python3 scripts/srt_to_md_multilang.py \
  --ru sub.ru.srt --en sub.en.srt --zh sub.zh.srt \
  --title "视频标题" --video-url "URL" --output learn.md
```

## 输出格式

```markdown
# 视频标题

> **频道:** [频道名](频道链接)
> **视频:** https://...
> **时长:** 15:04
> **字幕:** 人工字幕（来自创作者/社区）

---

**[00:32]**

🇷🇺 Привет, сегодня мы поговорим о...
🇬🇧 Hello, today we'll talk about...
🇨🇳 大家好，今天我们来聊聊...
```

## 字幕优先级

| 优先级 | 来源 | 质量 |
|--------|------|------|
| 1 | 人工字幕（创作者/社区） | 最佳 — 标点正确，经过人工审核 |
| 2 | 自动字幕（YouTube 语音识别） | 良好 — 可能有小错误 |

## 故障排除

**"Sign in to confirm you're not a bot"**
Chrome 必须安装并至少登录过一次 YouTube。

**找不到语言 X 的字幕**
运行 `yt-dlp --cookies-from-browser chrome --list-subs "URL"` 查看可用代码。

**自动字幕有错误**
正常现象。有人工字幕时总是优先使用。

## 依赖

- Python 3.8+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [jq](https://jqlang.github.io/jq/)
- Chrome 浏览器（用于 cookie 提取）

## 许可证

MIT
