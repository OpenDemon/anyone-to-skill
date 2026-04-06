"""
notebooklm.py — NotebookLM 浏览器自动化模块

功能：
  1. 自动打开 NotebookLM，创建新笔记本
  2. 批量添加 YouTube 视频链接作为来源
  3. 等待 AI 生成摘要后导出内容
  4. 返回笔记本 URL 供用户查看

前置条件：
  - 已在浏览器中登录 Google 账号
  - 运行环境有图形界面或 headless Chrome

作者: OPENDEMON · github.com/OpenDemon/anyone-to-skill
"""

import os
import re
import time
import json
from pathlib import Path
from typing import Optional

NOTEBOOKLM_URL = "https://notebooklm.google.com/"


def log(msg: str):
    print(f"  [notebooklm] {msg}", flush=True)


# ─── Playwright 自动化（推荐，支持 headless） ─────────────────────────────────

def auto_import_to_notebooklm(
    video_urls: list[str],
    notebook_name: str = "Anyone to Skill",
    wait_for_summary: bool = False,
    headless: bool = False
) -> Optional[str]:
    """
    自动将 YouTube 视频链接批量导入 NotebookLM。

    参数:
      video_urls: YouTube 视频 URL 列表
      notebook_name: 笔记本名称
      wait_for_summary: 是否等待 AI 生成摘要（需要额外 2-5 分钟）
      headless: 是否无头模式（不显示浏览器窗口）

    返回:
      笔记本 URL（成功）或 None（失败）
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log("Playwright 未安装，运行: pip install playwright && playwright install chromium")
        return None

    log(f"启动浏览器（headless={headless}）...")
    log(f"目标: 导入 {len(video_urls)} 个视频到 NotebookLM")

    notebook_url = None

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )

        # 尝试复用已有的浏览器 profile（保持登录状态）
        user_data_dir = Path.home() / ".config" / "chromium"
        if user_data_dir.exists():
            context = p.chromium.launch_persistent_context(
                str(user_data_dir),
                headless=headless,
                args=["--no-sandbox"]
            )
            page = context.new_page()
        else:
            context = browser.new_context()
            page = context.new_page()

        try:
            # 1. 打开 NotebookLM
            log("打开 NotebookLM...")
            page.goto(NOTEBOOKLM_URL, wait_until="networkidle", timeout=30000)
            time.sleep(2)

            # 检查是否需要登录
            if "accounts.google.com" in page.url:
                log("需要 Google 登录，请手动登录后重试")
                log(f"当前页面: {page.url}")
                return None

            # 2. 创建新笔记本
            log("创建新笔记本...")
            new_notebook_btn = page.locator(
                "button:has-text('New notebook'), "
                "button:has-text('新建笔记本'), "
                "[aria-label='New notebook'], "
                "[data-test='create-notebook-button']"
            ).first

            if new_notebook_btn.is_visible(timeout=5000):
                new_notebook_btn.click()
                time.sleep(2)
            else:
                log("未找到'新建笔记本'按钮，尝试直接添加来源...")

            # 3. 批量添加 YouTube 来源
            log(f"批量添加 {len(video_urls)} 个 YouTube 来源...")
            added_count = 0

            for i, url in enumerate(video_urls, 1):
                log(f"  [{i}/{len(video_urls)}] 添加: {url}")
                success = _add_source_to_notebook(page, url)
                if success:
                    added_count += 1
                    time.sleep(1.5)  # 避免过快触发限流
                else:
                    log(f"  ✗ 添加失败: {url}")

            log(f"成功添加 {added_count}/{len(video_urls)} 个来源")

            # 4. 重命名笔记本
            if notebook_name:
                _rename_notebook(page, notebook_name)

            # 5. 获取笔记本 URL
            notebook_url = page.url
            log(f"笔记本 URL: {notebook_url}")

            # 6. 可选：等待 AI 摘要生成
            if wait_for_summary:
                log("等待 AI 生成摘要（最多 5 分钟）...")
                _wait_for_summary(page, timeout=300)

        except Exception as e:
            log(f"自动化过程出错: {e}")
        finally:
            page.close()
            try:
                context.close()
            except Exception:
                pass
            try:
                browser.close()
            except Exception:
                pass

    return notebook_url


def _add_source_to_notebook(page, youtube_url: str) -> bool:
    """向当前笔记本添加一个 YouTube 来源"""
    try:
        # 查找"添加来源"按钮
        add_source_selectors = [
            "button:has-text('Add source')",
            "button:has-text('添加来源')",
            "button:has-text('+ Add')",
            "[aria-label='Add source']",
            "[data-test='add-source-button']",
        ]

        add_btn = None
        for selector in add_source_selectors:
            try:
                btn = page.locator(selector).first
                if btn.is_visible(timeout=2000):
                    add_btn = btn
                    break
            except Exception:
                continue

        if not add_btn:
            log("未找到'添加来源'按钮")
            return False

        add_btn.click()
        time.sleep(1)

        # 查找 URL 输入框
        url_input_selectors = [
            "input[placeholder*='URL']",
            "input[placeholder*='url']",
            "input[placeholder*='YouTube']",
            "input[type='url']",
            "input[type='text']",
        ]

        url_input = None
        for selector in url_input_selectors:
            try:
                inp = page.locator(selector).first
                if inp.is_visible(timeout=2000):
                    url_input = inp
                    break
            except Exception:
                continue

        if not url_input:
            # 尝试找到弹出的对话框中的输入框
            try:
                url_input = page.locator("dialog input, [role='dialog'] input").first
                if not url_input.is_visible(timeout=2000):
                    url_input = None
            except Exception:
                pass

        if not url_input:
            log("未找到 URL 输入框")
            return False

        url_input.fill(youtube_url)
        time.sleep(0.5)

        # 提交
        submit_selectors = [
            "button:has-text('Insert')",
            "button:has-text('Add')",
            "button:has-text('添加')",
            "button:has-text('确认')",
            "button[type='submit']",
        ]

        for selector in submit_selectors:
            try:
                btn = page.locator(selector).last
                if btn.is_visible(timeout=2000):
                    btn.click()
                    return True
            except Exception:
                continue

        # 尝试按 Enter
        url_input.press("Enter")
        return True

    except Exception as e:
        log(f"添加来源失败: {e}")
        return False


def _rename_notebook(page, name: str):
    """重命名笔记本"""
    try:
        title_selectors = [
            "[data-test='notebook-title']",
            "h1[contenteditable]",
            "input[aria-label*='title']",
            "input[aria-label*='Title']",
        ]
        for selector in title_selectors:
            try:
                el = page.locator(selector).first
                if el.is_visible(timeout=2000):
                    el.triple_click()
                    el.fill(name)
                    el.press("Enter")
                    log(f"笔记本已命名: {name}")
                    return
            except Exception:
                continue
    except Exception as e:
        log(f"重命名失败（不影响主流程）: {e}")


def _wait_for_summary(page, timeout: int = 300):
    """等待 NotebookLM AI 摘要生成完成"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            # 检查是否有摘要内容出现
            summary_selectors = [
                "[data-test='notebook-guide']",
                ".notebook-guide",
                "text=Audio Overview",
                "text=FAQ",
            ]
            for selector in summary_selectors:
                if page.locator(selector).is_visible(timeout=1000):
                    log("AI 摘要已生成")
                    return
        except Exception:
            pass
        time.sleep(5)
        log(f"等待中... ({int(time.time() - start)}s / {timeout}s)")

    log("等待超时，摘要可能仍在生成中")


# ─── 生成手动导入指南 ─────────────────────────────────────────────────────────

def generate_import_guide(
    video_urls: list[str],
    target_name: str,
    output_path: Optional[Path] = None
) -> str:
    """
    生成手动导入 NotebookLM 的操作指南（当自动化不可用时）。
    返回 Markdown 格式的指南文本。
    """
    urls_list = "\n".join(f"{i+1}. {url}" for i, url in enumerate(video_urls))

    guide = f"""# {target_name} — NotebookLM 导入指南

## 操作步骤

1. 打开 [NotebookLM](https://notebooklm.google.com/) 并登录 Google 账号
2. 点击 **New notebook**（新建笔记本）
3. 将以下 YouTube 链接逐一添加为来源（点击 **Add source** → 粘贴 URL）

## 视频链接列表（共 {len(video_urls)} 个）

{urls_list}

## 导入完成后

1. 等待 NotebookLM AI 生成摘要（约 2-5 分钟）
2. 在左侧面板查看每个来源的摘要
3. 点击 **Notebook guide** 获取整体概览
4. 将摘要内容复制并保存为 `.txt` 文件
5. 使用 `python distill.py --target "{target_name}" --files your_summary.txt` 运行蒸馏

## 提示

- 可以使用 [YouTube to NotebookLM](https://chrome.google.com/webstore/detail/youtube-to-notebooklm) Chrome 扩展批量导入
- NotebookLM 每个笔记本最多支持 50 个来源
- 建议选择播放量最高的 10-15 个视频，覆盖不同主题
"""

    if output_path:
        output_path.write_text(guide, encoding="utf-8")
        log(f"导入指南已保存: {output_path}")

    return guide


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="NotebookLM 批量导入工具")
    parser.add_argument("urls", nargs="+", help="YouTube 视频 URL 列表")
    parser.add_argument("--name", default="Anyone to Skill", help="笔记本名称")
    parser.add_argument("--headless", action="store_true", help="无头模式")
    parser.add_argument("--guide-only", action="store_true", help="只生成手动导入指南，不启动浏览器")
    parser.add_argument("--output", "-o", help="指南输出路径")
    args = parser.parse_args()

    if args.guide_only:
        guide = generate_import_guide(
            args.urls,
            args.name,
            Path(args.output) if args.output else None
        )
        if not args.output:
            print(guide)
    else:
        result = auto_import_to_notebooklm(
            video_urls=args.urls,
            notebook_name=args.name,
            headless=args.headless
        )
        if result:
            print(f"\n✓ 笔记本已创建: {result}")
        else:
            print("\n✗ 自动化导入失败，请使用手动模式")
            guide = generate_import_guide(args.urls, args.name)
            print(guide)
