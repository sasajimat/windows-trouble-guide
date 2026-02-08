import csv
import os
import openai
from datetime import datetime

# OpenAI APIキーを環境変数から取得
openai.api_key = os.getenv("OPENAI_API_KEY")

# ディレクトリ
DATA_DIR = "data"
DOCS_DIR = "docs"
TEMPLATE_FILE = "template/article.html"
KEYWORD_FILE = os.path.join(DATA_DIR, "keywords.csv")

# CSVから未処理キーワードを取得
def get_next_keyword():
    with open(KEYWORD_FILE, newline="", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    for row in reader:
        if row["status"] == "0":
            return row, reader
    return None, reader

# CSVのステータス更新
def update_status(reader):
    with open(KEYWORD_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["keyword","status"])
        writer.writeheader()
        writer.writerows(reader)

# OpenAIに記事生成を依頼
def generate_article(keyword):
    prompt = f"""
    あなたはWindowsトラブル解決に詳しいサポート担当者です。
    初心者向けに「{keyword}」のトラブル解決記事を作ってください。
    文章はHTML形式で、見出し<h2>、本文<p>、箇条書き<ul><li>を使ってください。
    ・操作手順は番号付き
    ・専門用語は簡単な説明をつける
    ・1文は60文字以内
    ・不安を煽らない
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role":"user","content":prompt}],
        temperature=0.3
    )
    content = response.choices[0].message.content
    return content

# HTML生成
def create_html(keyword, title, description, content):
    with open(TEMPLATE_FILE, encoding="utf-8") as f:
        template = f.read()
    html = template.replace("{{title}}", title)\
                   .replace("{{description}}", description)\
                   .replace("{{content}}", content)
    # ファイル名は日付＋キーワード
    safe_keyword = keyword.replace(" ", "_")
    filename = f"{DOCS_DIR}/{datetime.now().strftime('%Y%m%d')}_{safe_keyword}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[INFO] Article created: {filename}")

# メイン処理
def main():
    row, reader = get_next_keyword()
    if not row:
        print("[INFO] No keywords left to process.")
        return
    keyword = row["keyword"]
    print(f"[INFO] Generating article for keyword: {keyword}")
    
    content = generate_article(keyword)
    title = f"{keyword} のトラブル解決ガイド"
    description = f"{keyword}で困っている人向けの解決手順を丁寧に解説。"

    create_html(keyword, title, description, content)

    # ステータス更新
    for r in reader:
        if r["keyword"] == keyword:
            r["status"] = "1"
    update_status(reader)
    print("[INFO] CSV updated.")

if __name__ == "__main__":
    os.makedirs(DOCS_DIR, exist_ok=True)
    main()
