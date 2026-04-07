"""
anyone2skill distill — 全自动蒸馏模块

用法：
    anyone2skill distill --name 黄仁勋
    anyone2skill distill --name "Jensen Huang" --videos 20
    anyone2skill distill --name 黄仁勋 --file interview.pdf
    anyone2skill distill --name 黄仁勋 --youtube "https://..."

流程：
    1. 自动搜索 YouTube，找该人物的采访/演讲/访谈视频
    2. 用 youtube-transcript-api 获取字幕
    3. 把所有文字稿喂给 LLM，提炼 SKILL.md
    4. 保存到 ~/.anyone2skill/persons/{name}/SKILL.md
"""

import os
import sys
import json
import re
import subprocess
from pathlib import Path
from openai import OpenAI

# ── 颜色 ──────────────────────────────────────────────────────────────────────
R   = "\033[0m"
B   = "\033[1m"
DIM = "\033[2m"
C   = "\033[96m"
G   = "\033[92m"
Y   = "\033[93m"
M   = "\033[95m"

CONFIG_DIR = Path.home() / ".anyone2skill"
PERSONS_DIR = CONFIG_DIR / "persons"


def ensure_deps():
    """确保依赖已安装"""
    missing = []
    try:
        import yt_dlp
    except ImportError:
        missing.append("yt-dlp")
    try:
        import youtube_transcript_api
    except ImportError:
        missing.append("youtube-transcript-api")

    if missing:
        print(f"  {Y}正在安装依赖: {', '.join(missing)}...{R}")
        subprocess.run(
            [sys.executable, "-m", "pip", "install"] + missing + ["-q"],
            check=True
        )
        print(f"  {G}✓ 依赖安装完成{R}")


def search_youtube_videos(name: str, max_videos: int = 15) -> list[dict]:
    """
    用 yt-dlp 搜索 YouTube，返回视频列表
    """
    import yt_dlp

    queries = [
        f"{name} interview",
        f"{name} keynote speech",
        f"{name} talk lecture",
        f"{name} conversation podcast",
    ]

    all_videos = []
    seen_ids = set()
    per_query = max(max_videos // len(queries) + 2, 5)

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for query in queries:
            if len(all_videos) >= max_videos:
                break
            print(f"  {DIM}搜索: {query}{R}")
            try:
                result = ydl.extract_info(f"ytsearch{per_query}:{query}", download=False)
                entries = result.get("entries", []) if result else []
                for entry in entries:
                    if not entry:
                        continue
                    vid_id = entry.get("id", "")
                    if not vid_id or vid_id in seen_ids:
                        continue
                    duration = entry.get("duration", 0) or 0
                    if duration < 300:  # 过滤 5 分钟以下的短视频
                        continue
                    seen_ids.add(vid_id)
                    all_videos.append({
                        "id": vid_id,
                        "title": entry.get("title", ""),
                        "url": f"https://www.youtube.com/watch?v={vid_id}",
                        "duration": duration,
                        "channel": entry.get("channel", entry.get("uploader", "")),
                    })
                    if len(all_videos) >= max_videos:
                        break
            except Exception as e:
                print(f"  {Y}搜索出错: {e}{R}")

    return all_videos[:max_videos]


def get_transcript(video_id: str) -> str | None:
    """
    用 youtube-transcript-api 获取字幕
    优先中文，其次英文
    """
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import (
        TranscriptsDisabled, NoTranscriptFound,
        VideoUnavailable, RequestBlocked
    )

    api = YouTubeTranscriptApi()
    # 优先中文，其次英文
    for langs in [["zh-Hans", "zh-TW", "zh"], ["en"]]:
        try:
            transcript = api.fetch(video_id, languages=langs)
            text = " ".join([t.text for t in transcript])
            return text
        except (NoTranscriptFound, TranscriptsDisabled):
            continue
        except RequestBlocked:
            raise  # 向上传递，让调用方处理
        except VideoUnavailable:
            return None
        except Exception:
            continue
    return None


def distill_skill_md(name: str, transcripts: list[str], client: OpenAI, model: str) -> str:
    """
    把所有文字稿喂给 LLM，提炼 SKILL.md
    """
    combined = "\n\n---\n\n".join(transcripts)
    # 截取前 80000 字符（约 60000 tokens）
    if len(combined) > 80000:
        combined = combined[:80000] + "\n\n[内容过长，已截断]"

    prompt = f"""你是一个专业的人物研究员。以下是 {name} 的多段采访、演讲和访谈文字稿。

请仔细阅读这些材料，提炼出 {name} 真实的心智模型、决策方式和表达风格，生成一份高质量的 SKILL.md 文件。

要求：
1. 只写从材料中能直接支撑的内容，不要编造
2. 尽量引用原话（用引号标注）
3. 心智模型要有具体案例，不要空洞的概括
4. 表达风格要描述他/她真实的说话方式（用词、句式、节奏、口头禅）
5. 诚实边界：写出他/她的局限、盲点、矛盾之处

SKILL.md 格式如下（严格按此格式输出）：

---
name: {name.lower().replace(" ", "-")}
description: |
  [一句话描述，基于材料]
---
# {name} · 认知操作系统

## 核心人格（Persona）
[2-3段，用第一人称，描述核心人格特质，引用原话]

## 心智模型（Mental Models）
[3-5个心智模型，每个有名称、描述、真实案例]

## 决策启发式（Decision Heuristics）
[4-6条，"在...时，我倾向于...，因为..."格式]

## 表达 DNA（Voice & Style）
[描述真实说话方式，包括常用词、句式、节奏，引用原话]

**回答深度要求：**
当话题涉及我真正在乎的领域，我会展开深度回答：
- 先给出核心判断（1-2句，直接、不废话）
- 然后用具体逻辑或真实案例展开（3-5句，有细节，有数字，有推导过程）
- 总长度通常在150-300字之间，不是三句话了事，也不是列清单
- 绝不用"首先...其次...最后..."这种格式

## 价值观与反模式（Values & Anti-patterns）
[核心价值观 + 绝不做的事]

## 诚实边界（Honest Limits）
[局限、盲点、矛盾]

---

以下是文字稿材料：

{combined}

---

现在请生成 SKILL.md："""

    print(f"  {DIM}正在提炼 {name} 的认知操作系统...{R}", end="", flush=True)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4000,
        )
        content = response.choices[0].message.content.strip()
        print(f" {G}✓{R}")
        return content
    except Exception as e:
        print(f" {Y}失败: {e}{R}")
        return None


def run_distill(args, client: OpenAI, model: str):
    """
    蒸馏主流程
    """
    name = args.name
    max_videos = getattr(args, "videos", 15)

    print(f"""
{M}{B}  ╔══════════════════════════════════════════════════════╗
  ║         蒸馏模式  D I S T I L L                      ║
  ╚══════════════════════════════════════════════════════╝{R}

  {B}目标人物：{name}{R}
  {DIM}将自动搜索 YouTube，获取字幕，提炼认知操作系统{R}
  {DIM}搜索视频数量：{max_videos}{R}
""")

    # 确保依赖已安装
    ensure_deps()

    transcripts = []
    ip_blocked = False

    # ── 1. 自动搜索 YouTube ────────────────────────────────────────────────────
    print(f"  {B}[1/3] 搜索 YouTube 视频...{R}")
    videos = search_youtube_videos(name, max_videos)

    # 加入手动指定的 YouTube URL
    extra_urls = getattr(args, "youtube", None) or []
    for url in extra_urls:
        vid_id = url.split("v=")[-1].split("&")[0] if "v=" in url else url
        videos.append({"id": vid_id, "title": url, "url": url, "duration": 999, "channel": ""})

    if not videos and not getattr(args, "file", None):
        print(f"  {Y}未找到任何视频，请检查人物名称或手动指定 --youtube URL{R}")
        sys.exit(1)

    print(f"  {G}✓ 找到 {len(videos)} 个视频{R}\n")

    # ── 2. 获取字幕 ────────────────────────────────────────────────────────────
    print(f"  {B}[2/3] 获取字幕...{R}")

    from youtube_transcript_api._errors import RequestBlocked

    for i, video in enumerate(videos, 1):
        title_short = video["title"][:55] if video["title"] else video["url"]
        duration_min = int(video.get("duration", 0) / 60)
        print(f"  [{i:2d}/{len(videos)}] {title_short} ({duration_min}min)", end="", flush=True)

        if ip_blocked:
            print(f"  {Y}跳过（IP被封）{R}")
            continue

        try:
            text = get_transcript(video["id"])
            if text and len(text) > 500:
                print(f"  {G}✓ {len(text):,}字{R}")
                transcripts.append(f"# {video['title']}\n\n{text}")
            else:
                print(f"  {Y}无字幕{R}")
        except RequestBlocked:
            ip_blocked = True
            print(f"  {Y}IP被YouTube封锁{R}")
        except Exception as e:
            print(f"  {Y}失败: {type(e).__name__}{R}")

    if ip_blocked and not transcripts:
        print(f"""
  {Y}YouTube 封锁了当前 IP（常见于企业网络或VPN）。{R}
  {DIM}解决方案：{R}
  {DIM}1. 切换到普通家庭网络重试{R}
  {DIM}2. 手动下载字幕文件后用 --file 参数指定{R}
  {DIM}3. 直接指定视频 URL：--youtube "https://youtube.com/watch?v=xxx"{R}
""")

    # ── 3. 处理本地文件 ────────────────────────────────────────────────────────
    extra_files = getattr(args, "file", None) or []
    if extra_files:
        print(f"\n  {B}处理本地文件...{R}")
        for fpath in extra_files:
            p = Path(fpath)
            if not p.exists():
                print(f"  {Y}文件不存在: {fpath}{R}")
                continue
            print(f"  处理: {p.name}", end="", flush=True)
            try:
                if p.suffix.lower() == ".pdf":
                    try:
                        import pypdf
                        reader = pypdf.PdfReader(str(p))
                        text = "\n".join(page.extract_text() or "" for page in reader.pages)
                    except ImportError:
                        result = subprocess.run(
                            ["pdftotext", str(p), "-"],
                            capture_output=True, text=True
                        )
                        text = result.stdout
                else:
                    text = p.read_text(encoding="utf-8", errors="ignore")

                if text.strip():
                    transcripts.append(f"# {p.name}\n\n{text}")
                    print(f"  {G}✓ {len(text):,}字{R}")
                else:
                    print(f"  {Y}内容为空{R}")
            except Exception as e:
                print(f"  {Y}失败: {e}{R}")

    if not transcripts:
        print(f"\n  {Y}没有获取到任何文字内容。{R}")
        print(f"  {DIM}建议：手动下载字幕/文字稿后用 --file 参数指定{R}")
        sys.exit(1)

    total_chars = sum(len(t) for t in transcripts)
    print(f"\n  {G}✓ 共 {len(transcripts)} 份材料，总字数约 {total_chars:,}{R}\n")

    # ── 4. 提炼 SKILL.md ──────────────────────────────────────────────────────
    print(f"  {B}[3/3] 提炼认知操作系统...{R}")
    skill_md = distill_skill_md(name, transcripts, client, model)

    if not skill_md:
        print(f"  {Y}提炼失败，请检查 API Key 或网络{R}")
        sys.exit(1)

    # ── 5. 保存 ───────────────────────────────────────────────────────────────
    person_dir = PERSONS_DIR / name
    person_dir.mkdir(parents=True, exist_ok=True)
    skill_path = person_dir / "SKILL.md"
    skill_path.write_text(skill_md, encoding="utf-8")

    print(f"""
  {G}{B}✓ 蒸馏完成！{R}

  {B}SKILL.md 已保存到：{R}
  {DIM}{skill_path}{R}

  {B}现在可以直接对话：{R}
  {C}anyone2skill --skill "{skill_path}"{R}
""")
