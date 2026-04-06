"""
crawl.py — 公开人物自动采集模块

给定一个 YouTube 频道 URL（或人名），自动：
1. 获取频道视频列表
2. 优先下载有字幕的视频（速度快），无字幕则用 Whisper 转录
3. 按播放量排序，采集前 N 个最具代表性的视频
4. 同时抓取频道简介、About 页面等文字材料
5. 输出统一语料到 corpus/ 目录

策略：
- 优先使用 YouTube 自动字幕（英文/中文），避免 Whisper 转录耗时
- 字幕不可用时才下载音频并转录
- 长视频（>30分钟）优先，Shorts 作为补充
- 目标：采集 5-10 个视频，覆盖不同主题
"""

import os
import sys
import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
from openai import OpenAI

client = OpenAI()


def log(msg: str):
    print(f"[crawl] {msg}", flush=True)


# ─── YouTube 频道采集 ─────────────────────────────────────────────────────────

def get_channel_videos(channel_url: str, max_videos: int = 50) -> list[dict]:
    """获取频道视频列表，按播放量排序"""
    log(f"获取频道视频列表: {channel_url}")
    
    # 规范化 URL：如果是 shorts 页面，也获取主频道视频
    base_url = re.sub(r'/(shorts|videos|playlists|posts)$', '', channel_url.rstrip('/'))
    
    result = subprocess.run(
        ["yt-dlp", "--flat-playlist", "--print",
         "%(id)s\t%(title)s\t%(view_count)s\t%(duration)s\t%(description)s",
         f"{base_url}/videos"],
        capture_output=True, text=True, timeout=60
    )
    
    videos = []
    for line in result.stdout.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) >= 3:
            try:
                videos.append({
                    "id": parts[0],
                    "title": parts[1],
                    "view_count": int(parts[2]) if parts[2].isdigit() else 0,
                    "duration": float(parts[3]) if len(parts) > 3 and parts[3] else 0,
                    "description": parts[4] if len(parts) > 4 else "",
                    "url": f"https://www.youtube.com/watch?v={parts[0]}"
                })
            except (ValueError, IndexError):
                continue
    
    # 按播放量排序
    videos.sort(key=lambda x: x["view_count"], reverse=True)
    log(f"找到 {len(videos)} 个视频，取前 {max_videos} 个高播放量视频")
    return videos[:max_videos]


def get_shorts_videos(channel_url: str, max_shorts: int = 20) -> list[dict]:
    """获取 Shorts 列表"""
    base_url = re.sub(r'/(shorts|videos|playlists|posts)$', '', channel_url.rstrip('/'))
    
    result = subprocess.run(
        ["yt-dlp", "--flat-playlist", "--print",
         "%(id)s\t%(title)s\t%(view_count)s\t%(duration)s",
         f"{base_url}/shorts"],
        capture_output=True, text=True, timeout=60
    )
    
    shorts = []
    for line in result.stdout.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) >= 2:
            try:
                shorts.append({
                    "id": parts[0],
                    "title": parts[1],
                    "view_count": int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0,
                    "duration": float(parts[3]) if len(parts) > 3 and parts[3] else 60,
                    "url": f"https://www.youtube.com/watch?v={parts[0]}",
                    "is_short": True
                })
            except (ValueError, IndexError):
                continue
    
    shorts.sort(key=lambda x: x["view_count"], reverse=True)
    return shorts[:max_shorts]


def fetch_subtitles(video_id: str, output_dir: Path) -> Optional[str]:
    """
    尝试下载 YouTube 自动字幕（优先英文）。
    成功返回字幕文本，失败返回 None。
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["yt-dlp",
             "--write-auto-sub", "--skip-download",
             "--sub-lang", "en,zh-Hans,zh",
             "--sub-format", "vtt",
             "-o", os.path.join(tmpdir, "%(id)s"),
             f"https://www.youtube.com/watch?v={video_id}"],
            capture_output=True, text=True, timeout=30
        )
        
        # 找到下载的字幕文件
        vtt_files = list(Path(tmpdir).glob("*.vtt"))
        if not vtt_files:
            return None
        
        # 解析 VTT 格式，提取纯文本
        vtt_content = vtt_files[0].read_text(encoding="utf-8", errors="replace")
        return parse_vtt(vtt_content)


def parse_vtt(vtt_content: str) -> str:
    """解析 WebVTT 字幕，提取去重后的纯文本"""
    lines = vtt_content.split('\n')
    texts = []
    seen = set()
    
    for line in lines:
        line = line.strip()
        # 跳过时间戳行、WEBVTT 头、空行
        if not line or '-->' in line or line.startswith('WEBVTT') or line.isdigit():
            continue
        # 去除 HTML 标签
        clean = re.sub(r'<[^>]+>', '', line).strip()
        if clean and clean not in seen:
            seen.add(clean)
            texts.append(clean)
    
    return ' '.join(texts)


def transcribe_with_whisper(video_url: str) -> Optional[str]:
    """下载音频并用 Whisper 转录（字幕不可用时的备选方案）"""
    import whisper
    
    log(f"  字幕不可用，使用 Whisper 转录...")
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.mp3")
        
        result = subprocess.run(
            ["yt-dlp", "-x", "--audio-format", "mp3",
             "--audio-quality", "5",  # 较低质量，转录够用
             "-o", audio_path, video_url],
            capture_output=True, text=True, timeout=120
        )
        
        if result.returncode != 0:
            log(f"  yt-dlp 下载失败: {result.stderr[:200]}")
            return None
        
        # 找到实际文件
        candidates = list(Path(tmpdir).glob("*.mp3")) + list(Path(tmpdir).glob("audio*"))
        if not candidates:
            return None
        
        model = whisper.load_model("base")
        result = model.transcribe(str(candidates[0]), verbose=False)
        return result.get("text", "")


def crawl_youtube_channel(
    channel_url: str,
    output_dir: Path,
    max_long_videos: int = 6,
    max_shorts: int = 10,
    use_whisper_fallback: bool = False
) -> list[str]:
    """
    采集 YouTube 频道的核心内容。
    返回所有语料文件路径列表。
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    corpus_files = []
    
    # 1. 获取视频列表
    long_videos = get_channel_videos(channel_url, max_videos=50)
    shorts = get_shorts_videos(channel_url, max_shorts=max_shorts)
    
    # 2. 采集长视频（优先高播放量）
    log(f"\n采集长视频（目标 {max_long_videos} 个）...")
    collected = 0
    for video in long_videos:
        if collected >= max_long_videos:
            break
        
        vid_id = video["id"]
        title = video["title"]
        views = video["view_count"]
        duration_min = int(video["duration"] // 60)
        
        log(f"  [{collected+1}/{max_long_videos}] {title} ({views:,} 播放, {duration_min}分钟)")
        
        # 优先尝试字幕
        text = fetch_subtitles(vid_id, output_dir)
        
        if text and len(text) > 200:
            log(f"  ✓ 字幕获取成功 ({len(text)} 字符)")
        elif use_whisper_fallback:
            text = transcribe_with_whisper(video["url"])
            if text:
                log(f"  ✓ Whisper 转录成功 ({len(text)} 字符)")
        
        if text and len(text) > 100:
            safe_title = re.sub(r'[^\w\-]', '_', title)[:50]
            out_path = output_dir / f"video_{collected+1:02d}_{safe_title}.md"
            
            content = f"# {title}\n\n**播放量**: {views:,} | **时长**: {duration_min} 分钟\n**URL**: {video['url']}\n\n{text}"
            out_path.write_text(content, encoding="utf-8")
            corpus_files.append(str(out_path))
            collected += 1
        else:
            log(f"  ✗ 无法获取内容，跳过")
    
    # 3. 采集 Shorts 字幕（快速，内容密集）
    log(f"\n采集 Shorts（目标 {max_shorts} 个）...")
    shorts_texts = []
    shorts_collected = 0
    
    for short in shorts[:max_shorts]:
        vid_id = short["id"]
        title = short["title"]
        views = short["view_count"]
        
        text = fetch_subtitles(vid_id, output_dir)
        if text and len(text) > 50:
            shorts_texts.append(f"### {title} ({views:,} 播放)\n{text}")
            shorts_collected += 1
            log(f"  ✓ {title} ({len(text)} 字符)")
        else:
            log(f"  ✗ {title} — 无字幕")
    
    if shorts_texts:
        shorts_path = output_dir / "shorts_compilation.md"
        shorts_path.write_text(
            "# Shorts 合集\n\n" + "\n\n---\n\n".join(shorts_texts),
            encoding="utf-8"
        )
        corpus_files.append(str(shorts_path))
        log(f"\n✓ Shorts 合集: {shorts_collected} 个短视频")
    
    log(f"\n采集完成: {len(corpus_files)} 个语料文件")
    return corpus_files


# ─── 频道 About 页面采集 ──────────────────────────────────────────────────────

def crawl_channel_about(channel_url: str, output_dir: Path) -> Optional[str]:
    """抓取频道 About 页面的简介信息"""
    base_url = re.sub(r'/(shorts|videos|playlists|posts)$', '', channel_url.rstrip('/'))
    about_url = f"{base_url}/about"
    
    result = subprocess.run(
        ["yt-dlp", "--print", "%(channel)s\t%(channel_follower_count)s\t%(description)s",
         "--playlist-items", "1",
         f"{base_url}/videos"],
        capture_output=True, text=True, timeout=30
    )
    
    if result.returncode == 0 and result.stdout.strip():
        parts = result.stdout.strip().split('\t')
        if len(parts) >= 3:
            channel_name = parts[0]
            followers = parts[1]
            description = parts[2]
            
            about_text = f"# {channel_name} — 频道简介\n\n**订阅数**: {followers}\n\n{description}"
            about_path = output_dir / "channel_about.md"
            about_path.write_text(about_text, encoding="utf-8")
            log(f"✓ 频道简介已保存")
            return str(about_path)
    
    return None


# ─── 网页内容采集（通用） ─────────────────────────────────────────────────────

def crawl_webpage(url: str, output_dir: Path, label: str = "webpage") -> Optional[str]:
    """抓取网页文本内容（用于博客、Newsletter 等）"""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {"User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # 移除无用标签
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        
        # 提取主要文本
        text = soup.get_text(separator="\n", strip=True)
        # 清理多余空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        if len(text) < 200:
            return None
        
        safe_label = re.sub(r'[^\w\-]', '_', label)[:40]
        out_path = output_dir / f"web_{safe_label}.md"
        out_path.write_text(f"# {label}\n**URL**: {url}\n\n{text}", encoding="utf-8")
        log(f"✓ 网页内容: {label} ({len(text)} 字符)")
        return str(out_path)
    
    except Exception as e:
        log(f"✗ 网页抓取失败 {url}: {e}")
        return None


# ─── 主入口 ───────────────────────────────────────────────────────────────────

def crawl_public_figure(
    source_url: str,
    output_dir: Path,
    max_long_videos: int = 6,
    max_shorts: int = 10,
    extra_urls: list[str] = None
) -> list[str]:
    """
    公开人物全量采集入口。
    支持 YouTube 频道 URL，可附加额外网页 URL。
    返回所有语料文件路径。
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    all_files = []
    
    # YouTube 频道
    if "youtube.com/@" in source_url or "youtube.com/c/" in source_url or "youtube.com/channel/" in source_url:
        log("检测到 YouTube 频道，开始采集...")
        
        # 频道简介
        about_file = crawl_channel_about(source_url, output_dir)
        if about_file:
            all_files.append(about_file)
        
        # 视频内容
        video_files = crawl_youtube_channel(
            source_url, output_dir,
            max_long_videos=max_long_videos,
            max_shorts=max_shorts
        )
        all_files.extend(video_files)
    
    # 额外网页
    if extra_urls:
        for url in extra_urls:
            label = re.sub(r'https?://(www\.)?', '', url).split('/')[0]
            f = crawl_webpage(url, output_dir, label)
            if f:
                all_files.append(f)
    
    log(f"\n总计采集: {len(all_files)} 个语料文件")
    return all_files


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="公开人物自动采集模块")
    parser.add_argument("url", help="YouTube 频道 URL 或网页 URL")
    parser.add_argument("--output-dir", default="./corpus", help="输出目录")
    parser.add_argument("--max-videos", type=int, default=6, help="最多采集几个长视频")
    parser.add_argument("--max-shorts", type=int, default=10, help="最多采集几个 Shorts")
    parser.add_argument("--extra-urls", nargs="*", help="额外抓取的网页 URL")
    args = parser.parse_args()
    
    files = crawl_public_figure(
        args.url,
        Path(args.output_dir),
        max_long_videos=args.max_videos,
        max_shorts=args.max_shorts,
        extra_urls=args.extra_urls or []
    )
    
    print(f"\n采集完成，共 {len(files)} 个文件:")
    for f in files:
        size = Path(f).stat().st_size
        print(f"  {f} ({size:,} bytes)")
