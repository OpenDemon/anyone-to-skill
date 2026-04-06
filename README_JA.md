<div align="center">

# Anyone to Skill

> *"先人たちと対話してみたいと思いませんか？誰とでも対話し、誰の思考モデルでも学ぶことができる、それが Anyone to Skill です。今すぐ、イーロン・マスク、ジェンスン・フアン、孔子と直接対話できます。"*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![AgentSkills](https://img.shields.io/badge/AgentSkills-Standard-green)](https://agentskills.io)

<br>

動画、PDF、チャット履歴、電子書籍など、あらゆる資料を投入してください。<br>
システムがメンタルモデル、意思決定のヒューリスティクス、表現の DNA を抽出します。<br>
インストール可能な `SKILL.md` を出力し、あらゆる AI ツールで有効化できます。<br>

**誰でもインストール可能な AI Skill に蒸留し、いつでもあなたの質問に答えます。**

<br>

[データソース](#サポートされるデータソース) · [インストール](#インストール) · [使い方](#使い方) · [実行例](#実行例) · [**简体中文**](README.md) · [**English**](README_EN.md) · [**繁體中文**](README_ZH_TW.md) · [**한국어**](README_KO.md)

</div>

---

## 実行例

> これは単に有名人のマスクを被った ChatGPT ではありません。すべての回答は、その人物の具体的なメンタルモデルと表現の DNA を適用しています。

### シナリオ 1: Naval が語るエネルギー管理

```
ユーザー  ❯ コンテンツ制作、執筆、個人開発を同時にやりたいのですが、エネルギーが足りません。

Naval     ❯ あなたは3つの欲望を挙げました。すべての欲望は、あなたが不幸になるために自分と結んだ契約です。
            エネルギーが足りないのではなく、契約が多すぎるのです。
            
            自分に問いかけてください：どれをやっている時、時間を忘れますか？
            そこにあなたの「特定の知識」があります。
            
            3つから1つを選ぶのではありません。まず1つ、次に1つ、そしてまた1つ。
            直列の複利であり、並列の消耗ではありません。
```

### シナリオ 2: スティーブ・ジョブズが語る製品デザイン

```
ユーザー  ❯ 新製品に15個の新機能を追加しましたが、ユーザーから複雑すぎると言われました。どう最適化すべきですか？

Steve Jobs ❯ 14個を削れ。
             なぜ製品にゴミを詰め込むんだ？ユーザーが本当に求めているものを知らないから、量で無知を隠そうとしているんだ。
             
             ホワイトボードに戻れ。自分に問え：この製品が存在する唯一の理由は何だ？
             一言で説明できないなら、作るな。
             
             シンプルであることは複雑であることより難しい。思考をクリアにしてシンプルにするためには、懸命に努力しなければならない。
```

### シナリオ 3: イーロン・マスクが語るコスト管理

```
ユーザー  ❯ バッテリーのコストが下がりません。サプライヤーはこれが限界だと言っています。

Elon Musk ❯ サプライヤーの言うことはナンセンスだ。
            第一原理から考えろ：バッテリーは何でできている？炭素、ニッケル、アルミニウム、ポリマー、スチールだ。
            ロンドン金属取引所でのこれらの材料のスポット価格はいくらだ？
            
            自分で材料を買い、自分で作ったら、コストはいくらになる？
            もしその数字がサプライヤーの見積もりより80%低いなら、彼らは君から「バカ税」を取っているということだ。
            
            既存の解決策を受け入れるな。自分で作れ。
```

---

## 蒸留済みの人物ライブラリ

以下の蒸留済み Skill を直接インストールできます：

| 人物 | 分野 | インストールコマンド |
|------|------|--------------------|
| [イーロン・マスク](https://github.com/OpenDemon/elon-musk-skill) | テック起業 · 第一原理 | `npx skills add OpenDemon/elon-musk-skill` |
| [スティーブ・ジョブズ](https://github.com/OpenDemon/steve-jobs-skill) | プロダクト · ミニマリズム | `npx skills add OpenDemon/steve-jobs-skill` |
| [ビル・ゲイツ](https://github.com/OpenDemon/bill-gates-skill) | ソフトウェア戦略 · グローバルヘルス | `npx skills add OpenDemon/bill-gates-skill` |
| [Naval](https://github.com/OpenDemon/naval-ravikant-skill) | 経済的自由 · 特定の知識 | `npx skills add OpenDemon/naval-ravikant-skill` |
| [Andrej Karpathy](https://github.com/OpenDemon/andrej-karpathy-skill) | ディープラーニング · AI 教育 | `npx skills add OpenDemon/andrej-karpathy-skill` |
| [ジェンスン・フアン](https://github.com/OpenDemon/jensen-huang-skill) | 半導体戦略 · 加速主義 | `npx skills add OpenDemon/jensen-huang-skill` |
| [Dan Koe](https://github.com/OpenDemon/dan-koe-skill) | 1人企業 · パーソナルブランド | `npx skills add OpenDemon/dan-koe-skill` |

---

## 使い方

### 方法 1: ターミナルで直接チャット（推奨）

AI ツールなしで、ターミナルから直接彼らとチャットできます：

```bash
git clone https://github.com/OpenDemon/anyone-to-skill
cd anyone-to-skill
pip install openai

# API Key を設定（OpenAI / Gemini / GLM 対応）
export OPENAI_API_KEY="sk-..."

# チャットを開始
python chat.py
```

### 方法 2: AI コーディングツールにインストール

Claude Code や Cursor などのツールを使用している場合は、直接インストールできます：

```bash
npx skills add OpenDemon/elon-musk-skill
```

インストール後、ツール内で直接質問してください：`イーロン・マスクの視点でこのビジネスモデルを分析して`

---

## 新しい人物を蒸留する

```bash
# 依存関係のインストール
pip install openai PyMuPDF python-docx yt-dlp beautifulsoup4 requests

# 方法 1: ローカルファイル
python scripts/distill.py --target "Dan Koe" --files video.mp4 book.pdf

# 方法 2: YouTube チャンネル URL
python scripts/distill.py --url https://www.youtube.com/@DanKoeTalks

# 方法 3: インタラクティブモード（推奨）
python scripts/distill.py
```

---

## サポートされるデータソース

| ソース | ステータス | 備考 |
|--------|:--------:|------|
| YouTube チャンネル/動画 | ✅ | 字幕または音声文字起こしを自動ダウンロード |
| ローカル動画/音声 | ✅ | mp4, mp3, wav などに対応 |
| PDF ドキュメント | ✅ | テキストを自動抽出 |
| Word ドキュメント | ✅ | docx に対応 |
| チャット履歴 JSON | ✅ | 標準エクスポート形式に対応 |
| プレーンテキスト/Markdown | ✅ | 直接解析 |

---

Created by [@OpenDemon](https://github.com/OpenDemon)
