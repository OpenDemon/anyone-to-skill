"""
ingest.py — 多模态数据接入层
支持：视频/音频、PDF、EPUB/TXT/DOCX、微信/Telegram 聊天记录导出
输出：统一的 Markdown 语料文件，附带来源元数据
"""

import os
import sys
import json
import re
import tempfile
import subprocess
from pathlib import Path
from typing import Optional


# ─── 工具函数 ────────────────────────────────────────────────────────────────

def log(msg: str):
    print(f"[ingest] {msg}", flush=True)


def write_corpus(output_path: Path, source_name: str, content: str, source_type: str):
    """将提取内容写入语料文件"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    meta = {
        "source": source_name,
        "type": source_type,
        "chars": len(content),
    }
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"<!-- META: {json.dumps(meta, ensure_ascii=False)} -->\n\n")
        f.write(content)
    log(f"写入语料: {output_path} ({len(content)} 字符)")


# ─── 视频 / 音频 ─────────────────────────────────────────────────────────────

def ingest_video(file_path: str, output_dir: Path) -> str:
    """
    视频/音频转录。
    本地文件用 Whisper；YouTube/B站 URL 先用 yt-dlp 下载音频再转录。
    返回转录文本。
    """
    import whisper

    src = Path(file_path)
    is_url = file_path.startswith("http://") or file_path.startswith("https://")

    if is_url:
        log(f"检测到 URL，使用 yt-dlp 下载音频: {file_path}")
        with tempfile.TemporaryDirectory() as tmpdir:
            audio_path = os.path.join(tmpdir, "audio.mp3")
            result = subprocess.run(
                ["yt-dlp", "-x", "--audio-format", "mp3", "-o", audio_path, file_path],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                raise RuntimeError(f"yt-dlp 失败: {result.stderr}")
            # yt-dlp 可能加了后缀
            candidates = list(Path(tmpdir).glob("*.mp3"))
            if not candidates:
                candidates = list(Path(tmpdir).glob("audio*"))
            if not candidates:
                raise FileNotFoundError("yt-dlp 未生成音频文件")
            audio_path = str(candidates[0])
            return _transcribe(audio_path, output_dir, file_path)
    else:
        log(f"本地视频/音频文件: {src.name}")
        return _transcribe(str(src), output_dir, src.name)


def _transcribe(audio_path: str, output_dir: Path, source_name: str) -> str:
    import whisper
    log("加载 Whisper base 模型（首次加载约需 1 分钟）...")
    model = whisper.load_model("base")
    log("开始转录...")
    result = model.transcribe(audio_path, verbose=False)
    
    # 构建带时间戳的文本
    lines = []
    for seg in result.get("segments", []):
        ts = f"[{int(seg['start']//60):02d}:{int(seg['start']%60):02d}]"
        lines.append(f"{ts} {seg['text'].strip()}")
    
    transcript = "\n".join(lines) if lines else result.get("text", "")
    
    safe_name = re.sub(r'[^\w\-]', '_', source_name)[:40]
    out_path = output_dir / f"video_{safe_name}.md"
    write_corpus(out_path, source_name, transcript, "video_transcript")
    return transcript


# ─── PDF ─────────────────────────────────────────────────────────────────────

def ingest_pdf(file_path: str, output_dir: Path) -> str:
    """提取 PDF 文本，保留标题层级结构"""
    import fitz  # PyMuPDF

    src = Path(file_path)
    log(f"解析 PDF: {src.name}")
    doc = fitz.open(str(src))
    
    pages = []
    for page_num, page in enumerate(doc, 1):
        blocks = page.get_text("dict")["blocks"]
        page_text = []
        for block in blocks:
            if block.get("type") == 0:  # 文本块
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span["text"].strip()
                        size = span.get("size", 12)
                        if not text:
                            continue
                        # 根据字体大小判断标题级别
                        if size >= 18:
                            page_text.append(f"\n## {text}")
                        elif size >= 14:
                            page_text.append(f"\n### {text}")
                        else:
                            page_text.append(text)
        if page_text:
            pages.append(f"\n<!-- Page {page_num} -->\n" + " ".join(page_text))
    
    content = "\n".join(pages)
    safe_name = re.sub(r'[^\w\-]', '_', src.stem)[:40]
    out_path = output_dir / f"pdf_{safe_name}.md"
    write_corpus(out_path, src.name, content, "pdf")
    return content


# ─── EPUB / TXT / DOCX ───────────────────────────────────────────────────────

def ingest_text_doc(file_path: str, output_dir: Path) -> str:
    """处理 TXT、DOCX、EPUB 等文本类文档"""
    src = Path(file_path)
    ext = src.suffix.lower()
    log(f"解析文档 ({ext}): {src.name}")

    if ext == ".txt" or ext == ".md":
        content = src.read_text(encoding="utf-8", errors="replace")

    elif ext == ".docx":
        from docx import Document
        doc = Document(str(src))
        lines = []
        for para in doc.paragraphs:
            if para.style.name.startswith("Heading"):
                level = para.style.name.split()[-1]
                lines.append(f"\n{'#' * int(level)} {para.text}")
            elif para.text.strip():
                lines.append(para.text)
        content = "\n".join(lines)

    elif ext == ".epub":
        # 用 ebooklib 或直接解压 zip
        try:
            import zipfile
            from bs4 import BeautifulSoup
            texts = []
            with zipfile.ZipFile(str(src)) as z:
                for name in z.namelist():
                    if name.endswith(".html") or name.endswith(".xhtml"):
                        html = z.read(name).decode("utf-8", errors="replace")
                        soup = BeautifulSoup(html, "html.parser")
                        texts.append(soup.get_text(separator="\n"))
            content = "\n\n".join(texts)
        except Exception as e:
            log(f"EPUB 解析失败，回退到纯文本: {e}")
            content = src.read_text(encoding="utf-8", errors="replace")
    else:
        content = src.read_text(encoding="utf-8", errors="replace")

    safe_name = re.sub(r'[^\w\-]', '_', src.stem)[:40]
    out_path = output_dir / f"doc_{safe_name}.md"
    write_corpus(out_path, src.name, content, f"document_{ext[1:]}")
    return content


# ─── 聊天记录 ─────────────────────────────────────────────────────────────────

def ingest_chat(file_path: str, output_dir: Path, target_name: Optional[str] = None) -> str:
    """
    解析聊天记录导出文件。
    支持格式：
    - 微信导出 TXT（"2024-01-01 12:00:00 张三\n内容"）
    - Telegram JSON 导出
    - WhatsApp TXT 导出（"[2024/1/1, 12:00:00] 张三: 内容"）
    - 通用 JSON 格式（messages 数组）
    """
    src = Path(file_path)
    ext = src.suffix.lower()
    log(f"解析聊天记录: {src.name}")

    if ext == ".json":
        content = _parse_chat_json(src, target_name)
    else:
        raw = src.read_text(encoding="utf-8", errors="replace")
        content = _parse_chat_txt(raw, target_name)

    safe_name = re.sub(r'[^\w\-]', '_', src.stem)[:40]
    out_path = output_dir / f"chat_{safe_name}.md"
    write_corpus(out_path, src.name, content, "chat_log")
    return content


def _parse_chat_json(src: Path, target_name: Optional[str]) -> str:
    """解析 Telegram / 通用 JSON 格式"""
    data = json.loads(src.read_text(encoding="utf-8"))
    
    # Telegram 格式
    messages = data.get("messages", data if isinstance(data, list) else [])
    
    lines = []
    for msg in messages:
        sender = msg.get("from", msg.get("sender", msg.get("author", "Unknown")))
        text = msg.get("text", msg.get("content", ""))
        date = msg.get("date", msg.get("timestamp", ""))
        
        # text 可能是列表（Telegram 富文本）
        if isinstance(text, list):
            text = "".join(
                t if isinstance(t, str) else t.get("text", "") for t in text
            )
        
        if not text or not str(text).strip():
            continue
        
        # 如果指定了目标人物，标记其消息
        prefix = "**[TARGET]**" if (target_name and target_name.lower() in str(sender).lower()) else ""
        lines.append(f"{prefix}**{sender}** [{date}]: {text}")
    
    return "\n\n".join(lines)


def _parse_chat_txt(raw: str, target_name: Optional[str]) -> str:
    """解析微信/WhatsApp TXT 格式"""
    # 微信格式: "2024-01-01 12:00:00 张三\n内容"
    wechat_pattern = re.compile(
        r'^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(.+?)$',
        re.MULTILINE
    )
    # WhatsApp 格式: "[2024/1/1, 12:00:00] 张三: 内容"
    whatsapp_pattern = re.compile(
        r'^\[(\d{4}/\d{1,2}/\d{1,2},\s*\d{1,2}:\d{2}:\d{2})\]\s+(.+?):\s+(.+)$',
        re.MULTILINE
    )

    lines = []

    # 尝试 WhatsApp 格式
    wa_matches = whatsapp_pattern.findall(raw)
    if wa_matches:
        for date, sender, text in wa_matches:
            prefix = "**[TARGET]**" if (target_name and target_name.lower() in sender.lower()) else ""
            lines.append(f"{prefix}**{sender}** [{date}]: {text}")
        return "\n\n".join(lines)

    # 尝试微信格式（多行消息）
    segments = re.split(r'\n(?=\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', raw.strip())
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        first_line, *rest = seg.split("\n", 1)
        m = wechat_pattern.match(first_line)
        if m:
            date, sender = m.group(1), m.group(2)
            text = rest[0].strip() if rest else ""
            if not text:
                continue
            prefix = "**[TARGET]**" if (target_name and target_name.lower() in sender.lower()) else ""
            lines.append(f"{prefix}**{sender}** [{date}]: {text}")
        else:
            # 无法识别格式，直接保留
            lines.append(seg)

    return "\n\n".join(lines) if lines else raw


# ─── 统一入口 ─────────────────────────────────────────────────────────────────

def ingest_file(file_path: str, output_dir: Path, target_name: Optional[str] = None) -> str:
    """
    根据文件类型自动分发到对应的解析器。
    返回提取的文本内容。
    """
    src = Path(file_path)
    ext = src.suffix.lower()

    # 视频/音频
    if ext in {".mp4", ".mkv", ".avi", ".mov", ".webm", ".mp3", ".wav", ".m4a", ".flac", ".ogg"}:
        return ingest_video(file_path, output_dir)
    
    # PDF
    elif ext == ".pdf":
        return ingest_pdf(file_path, output_dir)
    
    # 文本文档
    elif ext in {".txt", ".md", ".docx", ".epub"}:
        # 判断是否是聊天记录（启发式：文件名含 chat/聊天/对话/message）
        name_lower = src.stem.lower()
        chat_keywords = {"chat", "聊天", "对话", "message", "telegram", "wechat", "whatsapp"}
        if any(kw in name_lower for kw in chat_keywords):
            return ingest_chat(file_path, output_dir, target_name)
        return ingest_text_doc(file_path, output_dir)
    
    # JSON（聊天记录）
    elif ext == ".json":
        return ingest_chat(file_path, output_dir, target_name)
    
    # URL（视频链接）
    elif file_path.startswith("http://") or file_path.startswith("https://"):
        return ingest_video(file_path, output_dir)
    
    else:
        log(f"未知格式 {ext}，尝试作为纯文本处理")
        return ingest_text_doc(file_path, output_dir)


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="多模态数据接入层")
    parser.add_argument("files", nargs="+", help="输入文件路径或 URL")
    parser.add_argument("--output-dir", default="./corpus", help="语料输出目录")
    parser.add_argument("--target", default=None, help="目标人物名称（用于聊天记录标注）")
    args = parser.parse_args()

    out = Path(args.output_dir)
    for f in args.files:
        try:
            ingest_file(f, out, args.target)
        except Exception as e:
            log(f"ERROR 处理 {f}: {e}")
            import traceback; traceback.print_exc()
