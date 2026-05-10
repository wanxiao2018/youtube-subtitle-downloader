#!/usr/bin/env python3
"""
Merge multilingual SRT subtitles into a single learning Markdown file.
Uses fixed time windows for alignment so all languages stay in sync.
"""

import re
import argparse


def parse_srt(filepath):
    """Parse SRT into list of (start_sec, end_sec, text)."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = re.split(r'\n\n+', content.strip())
    lines = []
    for block in blocks:
        parts = block.strip().split('\n')
        if len(parts) >= 3:
            times = parts[1].split(' --> ')
            start = time_to_sec(times[0].strip())
            end = time_to_sec(times[1].strip())
            text = ' '.join(parts[2:]).strip()
            text = re.sub(r'\s+', ' ', text)
            if text:
                lines.append((start, end, text))
    return lines


def time_to_sec(t):
    h, m, s = t.replace(',', '.').split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def format_ts(sec):
    mm = int(sec) // 60
    ss = int(sec) % 60
    return f"{mm:02d}:{ss:02d}"


def group_by_time_windows(lines, window_sec=30):
    """Group subtitle lines into fixed time windows."""
    if not lines:
        return []

    max_time = max(e for _, e, _ in lines)
    windows = []
    t = 0
    while t < max_time:
        texts = []
        for start, end, text in lines:
            if start < t + window_sec and end > t:
                texts.append(text)
        if texts:
            windows.append((t, t + window_sec, ' '.join(texts)))
        t += window_sec
    return windows


def generate_md(title, video_url, channel, duration, windows, has_en, has_zh):
    """Generate trilingual Markdown."""
    md = []
    md.append(f'# {title}')
    md.append('')
    md.append(f'> **Channel:** {channel}')
    md.append(f'> **Video:** {video_url}')
    if duration:
        md.append(f'> **Duration:** {duration}')
    lang_desc = 'Russian'
    if has_en:
        lang_desc += ' / English'
    if has_zh:
        lang_desc += ' / Chinese'
    md.append(f'> **Languages:** {lang_desc}')
    md.append('')
    md.append('---')
    md.append('')

    for t_start, t_end, ru_text, en_text, zh_text in windows:
        ts = format_ts(t_start)
        md.append(f'**[{ts}]**')
        md.append('')
        md.append(f'🇷🇺 {ru_text}')
        md.append('')
        if has_en and en_text:
            md.append(f'🇬🇧 {en_text}')
            md.append('')
        if has_zh and zh_text:
            md.append(f'🇨🇳 {zh_text}')
            md.append('')
        md.append('---')
        md.append('')

    return '\n'.join(md)


def merge_multilang(ru_lines, en_lines, zh_lines, window_sec=30):
    """Merge all three languages using fixed time windows."""
    # Get all time windows from Russian (master)
    max_time = max(e for _, e, _ in ru_lines) if ru_lines else 0

    windows = []
    t = 0
    while t < max_time:
        ru_texts = [txt for s, e, txt in ru_lines if s < t + window_sec and e > t]
        en_texts = [txt for s, e, txt in en_lines if s < t + window_sec and e > t] if en_lines else []
        zh_texts = [txt for s, e, txt in zh_lines if s < t + window_sec and e > t] if zh_lines else []

        if ru_texts:  # Only include windows with Russian content
            windows.append((
                t, t + window_sec,
                ' '.join(ru_texts),
                ' '.join(en_texts) if en_texts else '',
                ' '.join(zh_texts) if zh_texts else ''
            ))
        t += window_sec

    return windows


def main():
    parser = argparse.ArgumentParser(description='Merge multilingual SRT into learning Markdown')
    parser.add_argument('--ru', required=True, help='Russian SRT file')
    parser.add_argument('--en', default='', help='English SRT file (optional)')
    parser.add_argument('--zh', default='', help='Chinese SRT file (optional)')
    parser.add_argument('--title', default='Untitled')
    parser.add_argument('--video-url', default='')
    parser.add_argument('--channel', default='')
    parser.add_argument('--duration', default='')
    parser.add_argument('--window', type=int, default=30, help='Time window in seconds (default: 30)')
    parser.add_argument('--output', required=True, help='Output MD file')
    args = parser.parse_args()

    ru_lines = parse_srt(args.ru)
    en_lines = parse_srt(args.en) if args.en else []
    zh_lines = parse_srt(args.zh) if args.zh else []

    windows = merge_multilang(ru_lines, en_lines, zh_lines, args.window)

    md = generate_md(
        args.title, args.video_url, args.channel, args.duration,
        windows, bool(en_lines), bool(zh_lines)
    )

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f'Generated {len(windows)} paragraphs, {len(md)} chars -> {args.output}')


if __name__ == '__main__':
    main()
