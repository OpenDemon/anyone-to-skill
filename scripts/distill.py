"""
distill.py — Anyone to Skill · 交互式蒸馏引擎

用法（直接运行，进入交互模式）：
  python distill.py

或非交互式（CI/脚本）：
  python distill.py --target "Dan Koe" --files a.md b.pdf
  python distill.py --url https://www.youtube.com/@DanKoeTalks
  python distill.py --target "我" --files chats.json --self-mode
"""

import os
import sys
import json
import re
import argparse
import datetime
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ingest import ingest_file
from extract import run_parallel_extraction, run_synthesis
from assemble import assemble_with_qa_loop


# ─── 终端颜色 ─────────────────────────────────────────────────────────────────

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    BLUE   = "\033[94m"
    MAGENTA= "\033[95m"
    WHITE  = "\033[97m"

def c(color, text): return f"{color}{text}{C.RESET}"
def bold(text):     return c(C.BOLD, text)
def dim(text):      return c(C.DIM, text)


# ─── UI 组件 ──────────────────────────────────────────────────────────────────

BANNER = f"""
{C.CYAN}{C.BOLD}
  ╔═══════════════════════════════════════════════════════╗
  ║          A N Y O N E   T O   S K I L L               ║
  ║        把任何人蒸馏成可安装的 Skill                    ║
  ╚═══════════════════════════════════════════════════════╝
{C.RESET}"""

def print_banner():
    print(BANNER)

def print_section(title: str):
    print(f"\n{C.CYAN}{C.BOLD}{'─'*55}{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}  {title}{C.RESET}")
    print(f"{C.CYAN}{'─'*55}{C.RESET}")

def print_step(n: int, total: int, msg: str):
    print(f"\n{C.BLUE}{C.BOLD}[{n}/{total}]{C.RESET} {msg}", flush=True)

def print_ok(msg: str):
    print(f"  {C.GREEN}✓{C.RESET} {msg}", flush=True)

def print_warn(msg: str):
    print(f"  {C.YELLOW}⚠{C.RESET}  {msg}", flush=True)

def print_err(msg: str):
    print(f"  {C.RED}✗{C.RESET} {msg}", flush=True)

def ask(prompt: str, default: str = "") -> str:
    hint = f" {dim(f'[{default}]')}" if default else ""
    try:
        val = input(f"\n{C.YELLOW}▶{C.RESET} {prompt}{hint}: ").strip()
        return val if val else default
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)

def ask_choice(prompt: str, choices: list[tuple[str, str]], default: str = "1") -> str:
    """显示编号菜单，返回用户选择的 key"""
    print(f"\n{C.YELLOW}▶{C.RESET} {prompt}")
    for key, desc in choices:
        marker = f"{C.GREEN}●{C.RESET}" if key == default else f"{C.DIM}○{C.RESET}"
        print(f"    {marker} {C.BOLD}[{key}]{C.RESET} {desc}")
    try:
        val = input(f"\n  {dim('输入编号')} {dim(f'(默认 {default})')}: ").strip()
        val = val if val else default
        valid_keys = [k for k, _ in choices]
        if val not in valid_keys:
            print_warn(f"无效选项，使用默认值 {default}")
            return default
        return val
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)

def confirm(prompt: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    try:
        val = input(f"\n{C.YELLOW}▶{C.RESET} {prompt} {dim(f'[{hint}]')}: ").strip().lower()
        if not val:
            return default
        return val in ("y", "yes", "是", "ok")
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)


# ─── 核心流水线 ───────────────────────────────────────────────────────────────

def make_slug(name: str) -> str:
    return re.sub(r'[^\w\-]', '-', name.lower().strip()).strip('-')


def run_pipeline(target_name: str, files: list[str], output_base: Path, self_mode: bool = False):
    slug = make_slug(target_name)
    out_dir = output_base / slug
    corpus_dir = out_dir / "corpus"
    research_dir = out_dir / "research"

    out_dir.mkdir(parents=True, exist_ok=True)
    corpus_dir.mkdir(exist_ok=True)
    research_dir.mkdir(exist_ok=True)

    print_section(f"Phase 0 · 数据接入  ▸  目标: {target_name}")
    print(f"  输入文件数: {C.BOLD}{len(files)}{C.RESET}")

    all_corpus_texts = []
    for i, f in enumerate(files, 1):
        label = Path(f).name if Path(f).exists() else f[:60]
        print(f"  {dim(f'[{i}/{len(files)}]')} {label}", end=" ", flush=True)
        try:
            text = ingest_file(f, corpus_dir, target_name if not self_mode else None)
            all_corpus_texts.append(text)
            print(f"{C.GREEN}✓{C.RESET} {dim(f'{len(text):,} 字符')}")
        except Exception as e:
            print(f"{C.RED}✗{C.RESET} {dim(str(e))}")

    if not all_corpus_texts:
        print_err("所有文件处理失败，无法继续")
        sys.exit(1)

    corpus = "\n\n---\n\n".join(all_corpus_texts)
    print(f"\n  {C.BOLD}总语料:{C.RESET} {len(corpus):,} 字符")

    print_section("Phase 1 · 六路并行提取")
    raw_features = run_parallel_extraction(corpus, target_name, research_dir)

    print_section("Phase 2 · 知识图谱合成 + 三重验证")
    graph = run_synthesis(raw_features, target_name, research_dir)

    models = graph.get("mental_models", [])
    heuristics = graph.get("decision_heuristics", [])
    print_ok(f"心智模型: {C.BOLD}{len(models)}{C.RESET} 个  |  决策启发式: {C.BOLD}{len(heuristics)}{C.RESET} 条")

    print_section("Phase 3-4 · Skill 组装 + QA 验证闭环")
    skill_content, qa_result = assemble_with_qa_loop(graph, target_name, corpus[:5000], out_dir)

    meta = {
        "target": target_name,
        "slug": slug,
        "version": "1.0.0",
        "created_at": datetime.datetime.now().isoformat(),
        "sources": files,
        "source_count": len(files),
        "corpus_chars": len(corpus),
        "mental_models_count": len(models),
        "heuristics_count": len(heuristics),
        "qa_score": qa_result.get("quality_score", 0),
        "qa_verdict": qa_result.get("overall_verdict", "UNKNOWN")
    }
    with open(out_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    score = qa_result.get("quality_score", 0)
    verdict = qa_result.get("overall_verdict", "UNKNOWN")
    score_color = C.GREEN if score >= 80 else (C.YELLOW if score >= 60 else C.RED)

    print_section("完成！")
    print(f"""
  {C.BOLD}目标人物{C.RESET}  : {C.CYAN}{target_name}{C.RESET}
  {C.BOLD}输出目录{C.RESET}  : {out_dir}
  {C.BOLD}SKILL.md{C.RESET}  : {out_dir}/SKILL.md
  {C.BOLD}QA 质量分{C.RESET} : {score_color}{C.BOLD}{score}/100{C.RESET}
  {C.BOLD}QA 结论{C.RESET}   : {C.GREEN if verdict=='PASS' else C.RED}{verdict}{C.RESET}

  {C.BOLD}心智模型{C.RESET}  : {len(models)} 个
  {C.BOLD}决策启发式{C.RESET}: {len(heuristics)} 条
""")

    return out_dir


# ─── Mode 1: 本地文件 ─────────────────────────────────────────────────────────

def mode_files_interactive() -> tuple[str, list[str], bool]:
    """交互式收集目标名称和文件列表"""
    print_section("Mode 1 · 本地文件蒸馏")
    print(f"""
  {dim('支持格式: MP4/MP3 视频音频 · PDF · DOCX · TXT/MD · JSON 聊天记录 · EPUB')}
  {dim('可以一次输入多个文件，用空格分隔')}
""")

    target = ask("目标人物名称（如：乔布斯、我自己）")
    if not target:
        print_err("目标名称不能为空")
        sys.exit(1)

    print(f"\n  {dim('请输入文件路径（绝对路径或相对路径），多个文件用空格分隔:')}")
    raw = ask("文件路径")
    files = [f.strip().strip('"\'') for f in raw.split() if f.strip()]

    if not files:
        print_err("至少需要一个文件")
        sys.exit(1)

    # 验证文件存在
    valid_files = []
    for f in files:
        if Path(f).exists():
            print_ok(f"{Path(f).name}  {dim(f'({Path(f).stat().st_size//1024} KB)')}")
            valid_files.append(f)
        else:
            print_warn(f"文件不存在，跳过: {f}")

    if not valid_files:
        print_err("没有有效文件")
        sys.exit(1)

    self_mode = confirm("是否为自我蒸馏模式？（将所有材料视为你自己的）", default=False)
    return target, valid_files, self_mode


# ─── Mode 2: YouTube / 公开人物 ───────────────────────────────────────────────

def mode_youtube_interactive(output_base: Path):
    """交互式 YouTube 频道蒸馏"""
    print_section("Mode 2 · YouTube 频道 / 公开人物蒸馏")
    print(f"""
  {dim('输入 YouTube 频道主页或视频链接，系统自动:')}
  {dim('  1. 获取频道视频列表，按播放量排序')}
  {dim('  2. 用 AI 逐一分析视频内容（无需下载）')}
  {dim('  3. 运行六路并行提取 + 三重验证')}
  {dim('  4. 输出可安装的 SKILL.md')}
""")

    url = ask("YouTube 频道 URL（如 https://www.youtube.com/@DanKoeTalks）")
    if not url.strip():
        print_err("URL 不能为空")
        sys.exit(1)

    target = ask("目标人物名称（留空则从 URL 自动识别）")

    max_videos_str = ask("最多分析几个视频？", default="8")
    try:
        max_videos = int(max_videos_str)
    except ValueError:
        max_videos = 8

    strategy = ask_choice(
        "视频分析策略:",
        [
            ("1", f"Gemini 直接理解  {dim('— 最快，无需下载，推荐）')}"),
            ("2", f"Whisper API   {dim('— 下载音频 + OpenAI Whisper 转录')}"),
            ("3", f"本地 Whisper {dim('— 离线转录，不消耗 API（较慢）')}"),
            ("4", f"自动降级   {dim('— Gemini 失败则依次尝试其他方式')}"),
        ],
        default="1"
    )
    strategy_map = {"1": "gemini", "2": "whisper_api", "3": "whisper_local", "4": "auto"}
    analysis_strategy = strategy_map.get(strategy, "gemini")

    # 自动识别人名
    if not target:
        target = _extract_name_from_url(url)
        print_ok(f"自动识别目标: {C.BOLD}{target}{C.RESET}")

    # 获取视频列表
    print_step(1, 3, "获取频道视频列表...")
    videos = _get_top_videos(url, max_videos)

    if not videos:
        print_err("无法获取视频列表，请检查 URL 或网络连接")
        sys.exit(1)

    print(f"\n  {C.BOLD}找到 {len(videos)} 个高播放量视频:{C.RESET}")
    for i, v in enumerate(videos, 1):
        views = f"{v['view_count']:,}" if v.get('view_count') else "N/A"
        dur_min = int(v.get('duration', 0) // 60)
        print(f"  {dim(f'[{i:2d}]')} {v['title'][:55]:<55} {dim(f'{views} 播放 · {dur_min}min')}")

    if not confirm(f"\n  确认分析以上 {len(videos)} 个视频？", default=True):
        sys.exit(0)

    # 批量分析视频
    print_step(2, 3, f"AI 分析 {len(videos)} 个视频（并行处理）...")
    corpus_dir = output_base / make_slug(target) / "corpus"
    corpus_dir.mkdir(parents=True, exist_ok=True)

    analyzed_files = _analyze_videos_batch(videos, corpus_dir, strategy=analysis_strategy)

    if not analyzed_files:
        print_err("视频分析全部失败")
        sys.exit(1)

    print_ok(f"成功分析 {len(analyzed_files)}/{len(videos)} 个视频")

    # 运行蒸馏流水线
    print_step(3, 3, "运行蒸馏流水线...")
    run_pipeline(
        target_name=target,
        files=analyzed_files,
        output_base=output_base,
        self_mode=False
    )


def _extract_name_from_url(url: str) -> str:
    """从 YouTube URL 提取频道名"""
    # 尝试从 @handle 提取
    m = re.search(r'@([^/\s?]+)', url)
    if m:
        handle = m.group(1)
        # 转换 CamelCase 或驼峰为空格分隔
        name = re.sub(r'([A-Z])', r' \1', handle).strip()
        name = re.sub(r'[-_]', ' ', name).strip()
        return name.title()
    return "Unknown"


def _get_top_videos(channel_url: str, max_videos: int = 8) -> list[dict]:
    """获取频道播放量最高的视频"""
    import subprocess

    base_url = re.sub(r'/(shorts|videos|playlists|posts)/?$', '', channel_url.rstrip('/'))

    result = subprocess.run(
        ["yt-dlp", "--flat-playlist", "--print",
         "%(id)s\t%(title)s\t%(view_count)s\t%(duration)s",
         f"{base_url}/videos"],
        capture_output=True, text=True, timeout=90
    )

    videos = []
    for line in result.stdout.strip().split('\n'):
        if not line.strip():
            continue
        parts = line.split('\t')
        if len(parts) >= 2:
            try:
                videos.append({
                    "id": parts[0],
                    "title": parts[1],
                    "view_count": int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0,
                    "duration": float(parts[3]) if len(parts) > 3 and parts[3] else 0,
                    "url": f"https://www.youtube.com/watch?v={parts[0]}"
                })
            except (ValueError, IndexError):
                continue

    # 按播放量排序，过滤掉 Shorts（<= 3分钟）
    long_videos = [v for v in videos if v.get("duration", 0) > 180]
    long_videos.sort(key=lambda x: x["view_count"], reverse=True)

    return long_videos[:max_videos]


def _analyze_videos_batch(videos: list[dict], corpus_dir: Path, strategy: str = "auto") -> list[str]:
    """批量分析视频，使用开源 analyze_video 模块（Gemini / Whisper / 字幕自动降级）"""
    from analyze_video import analyze_videos_batch

    print(f"  {dim(f'分析策略: {strategy}  |  并发数: 4')}", flush=True)
    return analyze_videos_batch(videos, corpus_dir, strategy=strategy, max_workers=4)


# ─── Mode 3: NotebookLM 批量导入 ──────────────────────────────────────────────

def mode_notebooklm_interactive():
    """交互式 NotebookLM 批量导入模式"""
    print_section("Mode 3 · NotebookLM 批量导入")
    print(f"""
  {dim('此模式将 YouTube 链接批量导入 NotebookLM，由 NotebookLM AI 生成摘要后')}
  {dim('再蒸馏成 SKILL.md。适合需要更深度 AI 分析的场景。')}

  {C.YELLOW}工作流程:{C.RESET}
    1. 输入 YouTube 频道或视频链接
    2. 自动在浏览器中打开 NotebookLM 并批量添加来源
    3. 等待 NotebookLM 生成摘要（需要 Google 账号登录）
    4. 导出摘要后运行蒸馏流水线
""")

    print(f"""  {C.CYAN}┌─────────────────────────────────────────────────────┐{C.RESET}
  {C.CYAN}│{C.RESET}  {C.BOLD}使用前请确认:{C.RESET}                                      {C.CYAN}│{C.RESET}
  {C.CYAN}│{C.RESET}  • 已在浏览器中登录 Google 账号                       {C.CYAN}│{C.RESET}
  {C.CYAN}│{C.RESET}  • 已安装 "YouTube to NotebookLM" Chrome 扩展         {C.CYAN}│{C.RESET}
  {C.CYAN}│{C.RESET}    (或使用本工具的自动化模式)                          {C.CYAN}│{C.RESET}
  {C.CYAN}└─────────────────────────────────────────────────────┘{C.RESET}
""")

    sub_choice = ask_choice(
        "选择 NotebookLM 导入方式:",
        [
            ("1", f"自动化模式  {dim('— 脚本自动打开浏览器并批量添加来源')}"),
            ("2", f"手动模式    {dim('— 生成链接列表，你手动粘贴到 NotebookLM')}"),
            ("3", f"返回主菜单"),
        ],
        default="1"
    )

    if sub_choice == "3":
        return

    url = ask("YouTube 频道 URL（如 https://www.youtube.com/@DanKoeTalks）")
    target = ask("目标人物名称")
    max_videos_str = ask("最多导入几个视频？", default="10")
    try:
        max_videos = int(max_videos_str)
    except ValueError:
        max_videos = 10

    print_step(1, 2, "获取视频列表...")
    videos = _get_top_videos(url, max_videos)

    if not videos:
        print_err("无法获取视频列表")
        return

    video_urls = [v["url"] for v in videos]

    print(f"\n  {C.BOLD}将导入以下 {len(video_urls)} 个视频:{C.RESET}")
    for i, v in enumerate(videos, 1):
        print(f"  {dim(f'[{i:2d}]')} {v['title'][:60]}")

    if sub_choice == "2":
        # 手动模式：打印链接列表
        print_section("手动导入链接列表")
        print(f"\n  {dim('请将以下链接逐一添加到 NotebookLM 的来源中:')}\n")
        for v in videos:
            print(f"  {v['url']}")
        print(f"\n  {dim('NotebookLM 地址: https://notebooklm.google.com/')}")
        print(f"\n  {C.YELLOW}完成后，将 NotebookLM 生成的摘要文本保存为 .txt 文件，")
        print(f"  然后使用 Mode 1（本地文件）重新运行蒸馏。{C.RESET}\n")

    elif sub_choice == "1":
        # 自动化模式
        print_step(2, 2, "启动浏览器自动化...")
        try:
            from notebooklm import auto_import_to_notebooklm
            notebook_url = auto_import_to_notebooklm(
                video_urls=video_urls,
                notebook_name=f"{target} — Anyone to Skill"
            )
            if notebook_url:
                print_ok(f"NotebookLM 笔记本已创建: {notebook_url}")
                print(f"\n  {C.YELLOW}请在 NotebookLM 中等待 AI 生成摘要（约 2-5 分钟），")
                print(f"  完成后导出摘要文本，再使用 Mode 1 运行蒸馏。{C.RESET}\n")
            else:
                print_warn("自动化导入未完成，请手动操作")
        except ImportError:
            print_warn("notebooklm.py 模块未找到，切换到手动模式")
            print(f"\n  {dim('视频链接列表:')}")
            for v in videos:
                print(f"  {v['url']}")


# ─── 主交互界面 ───────────────────────────────────────────────────────────────

def interactive_main(output_base: Path):
    """主交互界面"""
    print_banner()

    print(f"""  {dim('将任何人的视频、文章、聊天记录、PDF 蒸馏成可安装的 AI Skill')}
  {dim('作者: OPENDEMON · github.com/OpenDemon/anyone-to-skill')}
""")

    mode = ask_choice(
        "选择蒸馏模式:",
        [
            ("1", f"本地文件    {dim('— 丢入视频/PDF/聊天记录/电子书等任意文件')}"),
            ("2", f"YouTube 频道 {dim('— 给频道链接，自动采集并蒸馏（公开人物首选）')}"),
            ("3", f"NotebookLM  {dim('— 批量导入 YouTube 到 NotebookLM 再蒸馏')}"),
            ("q", f"退出"),
        ],
        default="2"
    )

    if mode == "q":
        print(f"\n  {dim('再见！')}\n")
        sys.exit(0)

    elif mode == "1":
        target, files, self_mode = mode_files_interactive()
        run_pipeline(target, files, output_base, self_mode)

    elif mode == "2":
        mode_youtube_interactive(output_base)

    elif mode == "3":
        mode_notebooklm_interactive()


# ─── CLI 非交互模式 ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Anyone to Skill — 多模态认知蒸馏引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        示例:
          # 交互模式（推荐）
          python distill.py

          # 直接给文件
          python distill.py --target "乔布斯" --files interview.mp4 bio.pdf

          # YouTube 频道一键蒸馏
          python distill.py --url https://www.youtube.com/@DanKoeTalks

          # 自我蒸馏
          python distill.py --target "我" --files chats.json notes.txt --self-mode
        """)
    )
    parser.add_argument("--target", "-t", help="目标人物名称")
    parser.add_argument("--files", "-f", nargs="+", help="输入文件路径列表")
    parser.add_argument("--url", "-u", help="YouTube 频道 URL（公开人物一键模式）")
    parser.add_argument("--output", "-o", default="./output", help="输出根目录（默认: ./output）")
    parser.add_argument("--self-mode", action="store_true", help="自我蒸馏模式")
    parser.add_argument("--max-videos", type=int, default=8, help="YouTube 模式最多分析几个视频（默认: 8）")

    args = parser.parse_args()
    output_base = Path(args.output)

    # 无参数 → 进入交互模式
    if len(sys.argv) == 1:
        interactive_main(output_base)
        return

    # --url 模式
    if args.url:
        target = args.target or _extract_name_from_url(args.url)
        print_banner()
        print(f"  {C.BOLD}目标:{C.RESET} {target}  |  {C.BOLD}URL:{C.RESET} {args.url}\n")

        print_step(1, 2, "获取视频列表...")
        videos = _get_top_videos(args.url, args.max_videos)
        if not videos:
            print_err("无法获取视频列表")
            sys.exit(1)

        corpus_dir = output_base / make_slug(target) / "corpus"
        corpus_dir.mkdir(parents=True, exist_ok=True)

        print_step(2, 2, f"AI 分析 {len(videos)} 个视频...")
        analyzed_files = _analyze_videos_batch(videos, corpus_dir)

        if not analyzed_files:
            print_err("视频分析全部失败")
            sys.exit(1)

        run_pipeline(target, analyzed_files, output_base, False)
        return

    # --files 模式
    if args.target and args.files:
        print_banner()
        run_pipeline(args.target, args.files, output_base, args.self_mode)
        return

    # 参数不完整 → 进入交互模式
    interactive_main(output_base)


if __name__ == "__main__":
    main()
