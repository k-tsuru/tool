import os
import re
import openai
import sqlglot
from sqlglot import parse_one, exp

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("環境変数 OPENAI_API_KEY が設定されていません。")

def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"指定されたファイルが見つかりません: {filepath}")
    except IOError as e:
        raise IOError(f"ファイルの読み込み中にエラーが発生しました: {e}")

# --- ASTベースSQL診断 ---
def analyze_sql_ast(sql: str):
    issues = []
    try:
        ast = parse_one(sql)
    except Exception as e:
        return [f"SQL構文の解析に失敗しました: {e}"]

    if list(ast.find_all(exp.Star)):
        issues.append("SELECT * を使用しています。必要なカラムだけを指定してください。")

    where = ast.find(exp.Where)
    if where and list(where.find_all(exp.Func)):
        issues.append("WHERE句で関数を使用しています。インデックスが無効化される可能性があります。")

    or_count = sum(1 for _ in ast.find_all(exp.Or))
    if or_count >= 2:
        issues.append(f"OR条件が{or_count}回使われています。IN句や正規化を検討してください。")

    subqueries = list(ast.find_all(exp.Subquery))
    if subqueries:
        issues.append(f"サブクエリが{len(subqueries)}個使われています。JOINなどへの変換を検討してください。")

    for in_expr in ast.find_all(exp.In):
        if in_expr.args.get("not"):
            issues.append("NOT IN が使用されています。NOT EXISTS の方が効率的な場合があります。")

    for like_expr in ast.find_all(exp.Like):
        right = like_expr.args.get("expression")
        if right and "%" in str(right).strip("'").strip('"'):
            issues.append("前方一致を含む LIKE が使われています。インデックスが効かない可能性があります。")

    return issues

# --- 実行計画の診断（共通・コスト分析含む） ---
def diagnose_explain(explain_text):
    issues = []
    upper = explain_text.upper()

    if "SEQ SCAN" in upper or "FULL TABLE SCAN" in upper:
        issues.append("全表スキャンが検出されました。インデックス使用の見直しを。")

    if "INDEX" not in upper:
        issues.append("インデックスの使用が見られません。WHERE句やJOIN条件を見直してください。")

    cost_issues = diagnose_costs(explain_text)
    issues.extend(cost_issues)

    return issues

# --- 実行計画からコストを抽出し診断（PostgreSQL / MySQL / Oracle対応） ---
def diagnose_costs(explain_text, threshold=10000):
    issues = []
    costs = []

    # PostgreSQL cost=0.00..100.00
    pg_costs = re.findall(r"cost=\d+\.\d+\.\.(\d+\.\d+)", explain_text)
    costs += [float(c) for c in pg_costs]

    # MySQL: rows=N  filtered=M%  (no cost, fallback)
    # Oracle: cost=123
    oracle_costs = re.findall(r"COST=([0-9]+)", explain_text.upper())
    costs += [float(c) for c in oracle_costs]

    if not costs:
        return ["実行計画からコスト情報を抽出できませんでした。"]

    max_cost = max(costs)
    avg_cost = sum(costs) / len(costs)

    if max_cost > threshold:
        issues.append(f"高コストのノードがあります（最大 total cost: {max_cost:.2f}）。SQLの見直しを検討してください。")

    if max_cost > avg_cost * 3:
        issues.append(f"一部のノードのコストが平均の3倍以上です（平均: {avg_cost:.2f}, 最大: {max_cost:.2f}）。ボトルネックの可能性があります。")

    return issues

# --- ChatGPT改善レポート生成 ---
def generate_feedback(sql, issues_sql, issues_explain):
    prompt = f"""
以下のSQLとその実行計画に関する問題点を診断し、改善提案を出力してください。

[元のSQL]
{sql}

[指摘された問題点]
SQL構文:
{chr(10).join('- ' + issue for issue in issues_sql)}

実行計画:
{chr(10).join('- ' + issue for issue in issues_explain)}

[出力形式]
1. 修正案SQL
2. 各問題の解説と改善理由
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response['choices'][0]['message']['content']

# --- レポート出力 ---
def write_report(original_sql, issues_sql, issues_explain, gpt_feedback):
    with open("diagnosis_report.md", "w", encoding="utf-8") as f:
        f.write("# SQL診断レポート\n\n")
        f.write("## 元のSQL\n```sql\n" + original_sql.strip() + "\n```\n\n")
        f.write("## 構文に関する指摘\n")
        for i, issue in enumerate(issues_sql, 1):
            f.write(f"{i}. {issue}\n")
        f.write("\n## 実行計画に関する指摘\n")
        for i, issue in enumerate(issues_explain, 1):
            f.write(f"- {issue}\n")
        f.write("\n---\n\n")
        f.write("## ChatGPTによる改善案\n\n")
        f.write(gpt_feedback)

# --- メイン処理 ---
def main():
    sql_text = read_file("input.sql")
    explain_text = read_file("explain.txt")
    issues_sql = analyze_sql_ast(sql_text)
    issues_explain = diagnose_explain(explain_text)
    gpt_feedback = generate_feedback(sql_text, issues_sql, issues_explain)
    write_report(sql_text, issues_sql, issues_explain, gpt_feedback)
    print("✅ diagnosis_report.md を出力しました。")

if __name__ == "__main__":
    main()
