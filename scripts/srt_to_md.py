#!/usr/bin/env python3
"""
Convert SRT subtitle files into clean, structured Markdown for language learning.

Takes raw SRT subtitles (with fragmented short lines) and merges them into
readable paragraphs with timestamps for easy video navigation.
"""

import re
import argparse


def parse_srt(filepath):
    """Parse SRT file into list of (timestamp_str, text) tuples."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = re.split(r'\n\n+', content.strip())
    lines = []
    for block in blocks:
        parts = block.strip().split('\n')
        if len(parts) >= 3:
            # parts[0] = subtitle index, parts[1] = timestamp, parts[2:] = text
            time_str = parts[1].split(' --> ')[0].strip()
            text = ' '.join(parts[2:]).strip()
            text = re.sub(r'\s+', ' ', text)  # collapse whitespace
            if text:
                lines.append((time_str, text))
    return lines


def time_to_sec(t):
    """Convert SRT timestamp (HH:MM:SS,mmm) to seconds."""
    h, m, s = t.replace(',', '.').split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def format_ts(sec):
    """Format seconds as MM:SS."""
    mm = int(sec) // 60
    ss = int(sec) % 60
    return f"{mm:02d}:{ss:02d}"


def merge_into_paragraphs(lines, sentences_per_para=4):
    """Merge subtitle lines into paragraphs by sentence count.

    Splits on sentence-ending punctuation (.!?…), then groups
    N sentences per paragraph for readability.
    """
    all_text = ' '.join(t for _, t in lines)
    sentences = re.split(r'(?<=[.!?…])\s+', all_text)

    paragraphs = []
    current = []
    for s in sentences:
        current.append(s)
        if len(current) >= sentences_per_para:
            paragraphs.append(' '.join(current))
            current = []
    if current:
        paragraphs.append(' '.join(current))
    return paragraphs


def get_timestamps_for_paragraphs(lines, paragraphs):
    """Assign proportional timestamps to paragraphs."""
    total_subs = len(lines)
    if not paragraphs:
        return []
    subs_per_para = max(1, total_subs // len(paragraphs))
    timestamps = []
    for i in range(len(paragraphs)):
        idx = min(i * subs_per_para, len(lines) - 1)
        sec = time_to_sec(lines[idx][0])
        timestamps.append(format_ts(sec))
    return timestamps


def generate_md(title, video_url, channel_name, channel_url, duration, sub_type, paragraphs, timestamps):
    """Generate Markdown content from paragraphs and timestamps."""
    md = []
    md.append(f'# {title}')
    md.append('')
    if channel_name:
        md.append(f'> **Channel:** [{channel_name}]({channel_url})')
    md.append(f'> **Video:** {video_url}')
    if duration:
        md.append(f'> **Duration:** {duration}')
    md.append(f'> **Subtitles:** {sub_type}')
    md.append('')
    md.append('---')
    md.append('')

    for ts, para in zip(timestamps, paragraphs):
        md.append(f'**[{ts}]**')
        md.append('')
        md.append(para)
        md.append('')
        md.append('---')
        md.append('')

    return '\n'.join(md)


def main():
    parser = argparse.ArgumentParser(
        description='Convert SRT subtitles to learning Markdown')
    parser.add_argument('--srt', required=True, help='Path to SRT file')
    parser.add_argument('--title', default='Untitled', help='Video title')
    parser.add_argument('--video-url', default='', help='YouTube video URL')
    parser.add_argument('--channel', default='', help='Channel name')
    parser.add_argument('--channel-url', default='', help='Channel URL')
    parser.add_argument('--duration', default='', help='Video duration (e.g. 15:04)')
    parser.add_argument('--sub-type', default='auto-generated',
                        help='Subtitle type: manual / auto-generated')
    parser.add_argument('--sentences', type=int, default=4,
                        help='Sentences per paragraph (default: 4)')
    parser.add_argument('--output', required=True, help='Output Markdown file path')
    args = parser.parse_args()

    lines = parse_srt(args.srt)
    paragraphs = merge_into_paragraphs(lines, args.sentences)
    timestamps = get_timestamps_for_paragraphs(lines, paragraphs)
    md = generate_md(
        args.title, args.video_url, args.channel, args.channel_url,
        args.duration, args.sub_type, paragraphs, timestamps
    )

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f'Generated {len(paragraphs)} paragraphs, {len(md)} chars -> {args.output}')


if __name__ == '__main__':
    main()
