"""
analyze_video.py — 开源视频分析模块

完全不依赖任何平台内置工具，只需用户自己的 OpenAI API key。

策略（按优先级自动降级）：
  1. Gemini 2.5 Flash 直接理解 YouTube URL（最快，无需下载）
  2. yt-dlp 下载音频 + OpenAI Whisper API 转录（需要 API key）
  3. yt-dlp 下载音频 + 本地 Whisper 模型转录（离线，较慢）
  4. youtube_transcript_api 获取字幕（仅限有字幕的视频）

作者: OPENDEMON · github.com/OpenDemon/anyone-to-skill
"""

import os
import re
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
from openai import OpenAI

client = OpenAI()

ANALYSIS_PROMPT = """Analyze this YouTube video in detail. Extract and structure the following:

1. **Core Philosophical Beliefs & Mental Models** — What does this person fundamentally believe? List 5-7 distinct mental models with specific examples from the video.

2. **Recurring Themes & Key Concepts** — What topics do they return to repeatedly? What vocabulary is uniquely theirs?

3. **Contrarian Positions** — Where does this person disagree with mainstream thinking? Be specific.

4. **Speaking Style & Rhetoric** — How do they communicate? Favorite metaphors, analogies, rhetorical patterns, sentence structures.

5. **Specific Quotes** — Extract 5-10 verbatim or near-verbatim quotes that best capture their voice.

6. **Personal Stories & Case Studies** — What experiences do they draw from? What examples do they use?

7. **Decision Frameworks & Heuristics** — How do they make decisions? What rules of thumb do they apply?

8. **Values & Anti-Patterns** — What do they stand for? What do they explicitly reject or warn against?

9. **Honest Limits** — Where do they show uncertainty or acknowledge they don't have answers?

Be as detailed and specific as possible. Preserve their exact language and phrasing."""


def log(msg: str):
    print(f"  [analyze_video] {msg}", flush=True)


# ─── Strategy 1: Gemini 直接理解 YouTube URL ──────────────────────────────────

def analyze_with_gemini(youtube_url: str) -> Optional[str]:
    """
    用 Gemini 2.5 Flash 直接分析 YouTube 视频。
    Gemini 原生支持 YouTube URL，无需下载，速度最快。
    """
    try:
        resp = client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[{
                "role": "user",
                "content": f"Please watch and analyze this YouTube video: {youtube_url}\n\n{ANALYSIS_PROMPT}"
            }],
            max_tokens=4000,
            timeout=180
        )
        content = resp.choices[0].message.content
        if content and len(content) > 300:
            return content
        return None
    except Exception as e:
        log(f"Gemini 分析失败: {e}")
        return None


# ─── Strategy 2: yt-dlp + OpenAI Whisper API ─────────────────────────────────

def analyze_with_whisper_api(youtube_url: str) -> Optional[str]:
    """
    下载音频后用 OpenAI Whisper API 转录，再用 GPT 分析。
    需要 OPENAI_API_KEY，适合标准 OpenAI 账号。
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = Path(tmpdir) / "audio.mp3"

        # 下载音频
        log("下载音频...")
        result = subprocess.run(
            ["yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "5",
             "-o", str(audio_path), youtube_url],
            capture_output=True, text=True, timeout=120
        )

        if result.returncode != 0 or not audio_path.exists():
            log(f"音频下载失败: {result.stderr[:200]}")
            return None

        file_size_mb = audio_path.stat().st_size / (1024 * 1024)
        log(f"音频下载完成: {file_size_mb:.1f} MB")

        # Whisper API 有 25MB 限制，超出则截取前 20 分钟
        if file_size_mb > 24:
            log("文件过大，截取前 20 分钟...")
            trimmed = Path(tmpdir) / "audio_trimmed.mp3"
            subprocess.run(
                ["ffmpeg", "-i", str(audio_path), "-t", "1200",
                 "-acodec", "copy", str(trimmed), "-y"],
                capture_output=True
            )
            if trimmed.exists():
                audio_path = trimmed

        # 转录
        log("Whisper API 转录...")
        try:
            with open(audio_path, "rb") as f:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                    response_format="text"
                )
        except Exception as e:
            log(f"Whisper API 失败: {e}")
            return None

        if not transcript or len(transcript) < 200:
            return None

        log(f"转录完成: {len(transcript)} 字符")

        # GPT 分析
        return _analyze_transcript_with_gpt(transcript, youtube_url)


# ─── Strategy 3: yt-dlp + 本地 Whisper ───────────────────────────────────────

def analyze_with_local_whisper(youtube_url: str, model_size: str = "base") -> Optional[str]:
    """
    下载音频后用本地 Whisper 模型转录（离线，不消耗 API 费用）。
    model_size: tiny/base/small/medium（越大越准但越慢）
    """
    try:
        import whisper
    except ImportError:
        log("本地 Whisper 未安装，运行: pip install openai-whisper")
        return None

    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = Path(tmpdir) / "audio.mp3"

        log("下载音频...")
        result = subprocess.run(
            ["yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "5",
             "-o", str(audio_path), youtube_url],
            capture_output=True, text=True, timeout=120
        )

        if result.returncode != 0 or not audio_path.exists():
            log(f"音频下载失败: {result.stderr[:200]}")
            return None

        log(f"加载 Whisper {model_size} 模型并转录...")
        try:
            model = whisper.load_model(model_size)
            result = model.transcribe(str(audio_path))
            transcript = result["text"]
        except Exception as e:
            log(f"本地 Whisper 转录失败: {e}")
            return None

        if not transcript or len(transcript) < 200:
            return None

        log(f"转录完成: {len(transcript)} 字符")
        return _analyze_transcript_with_gpt(transcript, youtube_url)


# ─── Strategy 4: youtube_transcript_api 字幕 ─────────────────────────────────

def analyze_with_subtitles(youtube_url: str) -> Optional[str]:
    """
    尝试获取 YouTube 自动字幕（无需下载，速度最快，但不是所有视频都有）。
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
    except ImportError:
        log("youtube_transcript_api 未安装，运行: pip install youtube-transcript-api")
        return None

    # 提取 video ID
    vid_id = _extract_video_id(youtube_url)
    if not vid_id:
        return None

    try:
        # 优先英文，其次中文，最后任意语言
        for lang in [["en"], ["zh", "zh-Hans", "zh-Hant"], None]:
            try:
                if lang:
                    segments = YouTubeTranscriptApi.get_transcript(vid_id, languages=lang)
                else:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(vid_id)
                    segments = transcript_list.find_transcript(
                        transcript_list._manually_created_transcripts or
                        list(transcript_list._generated_transcripts.keys())
                    ).fetch()

                text = " ".join(s["text"] for s in segments)
                if len(text) > 200:
                    log(f"字幕获取成功: {len(text)} 字符")
                    return _analyze_transcript_with_gpt(text, youtube_url)
            except Exception:
                continue
    except Exception as e:
        log(f"字幕获取失败: {e}")

    return None


# ─── 共用 GPT 分析函数 ────────────────────────────────────────────────────────

def _analyze_transcript_with_gpt(transcript: str, source_url: str = "") -> Optional[str]:
    """将转录文本发给 GPT 进行深度分析"""
    # 截断过长的转录（保留前 12000 字符，约 30 分钟内容）
    if len(transcript) > 12000:
        transcript = transcript[:12000] + "\n\n[... transcript truncated ...]"

    prompt = f"""Here is a transcript from: {source_url}

---TRANSCRIPT---
{transcript}
---END TRANSCRIPT---

{ANALYSIS_PROMPT}"""

    try:
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000,
            timeout=120
        )
        content = resp.choices[0].message.content
        return content if content and len(content) > 200 else None
    except Exception as e:
        log(f"GPT 分析失败: {e}")
        return None


# ─── 主入口：自动降级策略 ─────────────────────────────────────────────────────

def analyze_video(
    youtube_url: str,
    strategy: str = "auto",
    whisper_model: str = "base"
) -> Optional[str]:
    """
    分析 YouTube 视频，返回结构化分析文本。

    strategy 选项:
      "auto"    — 自动选择最佳策略（推荐）
      "gemini"  — 强制使用 Gemini 直接理解
      "whisper_api" — 强制使用 OpenAI Whisper API
      "whisper_local" — 强制使用本地 Whisper
      "subtitles" — 强制使用字幕

    whisper_model: tiny/base/small/medium（仅 whisper_local 模式有效）
    """
    log(f"分析视频: {youtube_url}")
    log(f"策略: {strategy}")

    if strategy == "gemini":
        return analyze_with_gemini(youtube_url)

    elif strategy == "whisper_api":
        return analyze_with_whisper_api(youtube_url)

    elif strategy == "whisper_local":
        return analyze_with_local_whisper(youtube_url, whisper_model)

    elif strategy == "subtitles":
        return analyze_with_subtitles(youtube_url)

    elif strategy == "auto":
        # 自动降级：Gemini → 字幕 → Whisper API → 本地 Whisper
        log("尝试 Strategy 1: Gemini 直接理解...")
        result = analyze_with_gemini(youtube_url)
        if result:
            log("✓ Gemini 分析成功")
            return result

        log("尝试 Strategy 2: YouTube 字幕...")
        result = analyze_with_subtitles(youtube_url)
        if result:
            log("✓ 字幕分析成功")
            return result

        log("尝试 Strategy 3: Whisper API...")
        result = analyze_with_whisper_api(youtube_url)
        if result:
            log("✓ Whisper API 分析成功")
            return result

        log("尝试 Strategy 4: 本地 Whisper...")
        result = analyze_with_local_whisper(youtube_url, whisper_model)
        if result:
            log("✓ 本地 Whisper 分析成功")
            return result

        log("✗ 所有策略均失败")
        return None

    else:
        raise ValueError(f"未知策略: {strategy}，可选: auto/gemini/whisper_api/whisper_local/subtitles")


# ─── 批量分析 ─────────────────────────────────────────────────────────────────

def analyze_videos_batch(
    videos: list[dict],
    corpus_dir: Path,
    strategy: str = "auto",
    max_workers: int = 4
) -> list[str]:
    """
    批量分析多个视频，并发执行。

    videos: [{"id": "xxx", "title": "...", "url": "...", "view_count": 0, "duration": 0}]
    corpus_dir: 输出目录
    strategy: 分析策略（见 analyze_video）
    max_workers: 最大并发数（Gemini 模式建议 4，本地 Whisper 建议 1）

    返回: 生成的语料文件路径列表
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    corpus_dir.mkdir(parents=True, exist_ok=True)
    collected = []

    def process_one(video: dict) -> Optional[str]:
        vid_id = video["id"]
        title = video["title"]
        url = video["url"]
        views = video.get("view_count", 0)
        dur_min = int(video.get("duration", 0) // 60)

        print(f"  → 分析: {title[:55]}", flush=True)

        content = analyze_video(url, strategy=strategy)

        if content and len(content) > 200:
            safe_title = re.sub(r'[^\w\-]', '_', title)[:50]
            out_path = corpus_dir / f"video_{safe_title}.md"
            out_path.write_text(
                f"# {title}\n\n"
                f"**URL**: {url}\n"
                f"**播放量**: {views:,}  |  **时长**: {dur_min} 分钟\n\n"
                f"{content}",
                encoding="utf-8"
            )
            print(f"  ✓ {title[:50]}  ({len(content):,} 字符)", flush=True)
            return str(out_path)
        else:
            print(f"  ✗ {title[:50]}  (内容不足，跳过)", flush=True)
            return None

    # Gemini 模式支持并发，其他模式串行（避免资源竞争）
    actual_workers = max_workers if strategy in ("gemini", "auto") else 1

    with ThreadPoolExecutor(max_workers=actual_workers) as executor:
        futures = {executor.submit(process_one, v): v for v in videos}
        for future in as_completed(futures):
            result = future.result()
            if result:
                collected.append(result)

    return collected


# ─── 工具函数 ─────────────────────────────────────────────────────────────────

def _extract_video_id(url: str) -> Optional[str]:
    """从 YouTube URL 提取 video ID"""
    patterns = [
        r'(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        m = re.search(pattern, url)
        if m:
            return m.group(1)
    return None


# ─── CLI 测试 ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="开源视频分析工具")
    parser.add_argument("url", help="YouTube 视频 URL")
    parser.add_argument("--strategy", default="auto",
                        choices=["auto", "gemini", "whisper_api", "whisper_local", "subtitles"],
                        help="分析策略（默认: auto）")
    parser.add_argument("--output", "-o", help="输出文件路径（默认: 打印到终端）")
    args = parser.parse_args()

    result = analyze_video(args.url, strategy=args.strategy)

    if result:
        if args.output:
            Path(args.output).write_text(result, encoding="utf-8")
            print(f"\n✓ 分析结果已保存到: {args.output}")
        else:
            print("\n" + "="*60)
            print(result)
    else:
        print("✗ 分析失败")
        exit(1)
