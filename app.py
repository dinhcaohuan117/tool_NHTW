from flask import Flask, render_template_string, request
import pandas as pd

app = Flask(__name__)

# --- Đọc dữ liệu CSV ---
df1 = pd.read_csv("questions_extracted_1_158_Vie.csv")
df2 = pd.read_csv("questions_extracted_159_349_Vie.csv")
df = pd.concat([df1, df2], ignore_index=True)

# --- Giao diện HTML ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>Question Search Tool</title>
    <style>
        body { font-family: Arial; margin: 40px; background-color: #f5f7fa; }
        h1 { color: #007acc; }
        form { margin-bottom: 20px; }
        input[type=text] { width: 400px; padding: 8px; font-size: 16px; }
        button { padding: 8px 16px; font-size: 16px; background: #007acc; color: white; border: none; cursor: pointer; }
        .result { background: white; padding: 15px; margin-bottom: 10px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .answer { color: #333; margin-top: 5px; }
        .type { font-size: 13px; color: gray; }
    </style>
</head>
<body>
    <h1>🔍 Question Search Tool</h1>
    <form method="post">
        <input type="text" name="query" placeholder="Nhập từ khóa tìm kiếm..." value="{{ query|default('') }}">
        <button type="submit">Tìm kiếm</button>
    </form>

    {% if results %}
        <h3>Kết quả tìm được: {{ results|length }}</h3>
        {% for row in results %}
            <div class="result">
                <div class="type">[{{ row['type'] }}]</div>
                <strong>Q{{ loop.index }}:</strong> {{ row['question'] }}<br>

                {% if row['type'] == 'multiple_choice' %}
                    {% if row['option_A'] %}A. {{ row['option_A'] }}<br>{% endif %}
                    {% if row['option_B'] %}B. {{ row['option_B'] }}<br>{% endif %}
                    {% if row['option_C'] %}C. {{ row['option_C'] }}<br>{% endif %}
                    {% if row['option_D'] %}D. {{ row['option_D'] }}<br>{% endif %}
                    <div class="answer"><b>→ Correct answer:</b> {{ row['correct_answer'] }}</div>
                {% elif row['type'] == 'essay' %}
                    <div class="answer"><b>→ Answer:</b> {{ row['answer_text'] }}</div>
                {% else %}
                    <div class="answer"><i>(No answer data)</i></div>
                {% endif %}
            </div>
        {% endfor %}
    {% elif query %}
        <p><i>Không tìm thấy kết quả nào cho "{{ query }}"</i></p>
    {% endif %}
</body>
</html>
"""

# --- Xử lý tìm kiếm ---
@app.route("/", methods=["GET", "POST"])
def index():
    query = ""
    results = []
    if request.method == "POST":
        query = request.form.get("query", "").strip().lower()
        if query:
            def match(row):
                # ghép nội dung có thể tìm kiếm
                combined_text = " ".join([
                    str(row.get('question', '')),
                    str(row.get('correct_answer', '')),
                    str(row.get('answer_text', ''))
                ]).lower()
                return query in combined_text

            mask = df.apply(match, axis=1)
            results = df[mask].to_dict(orient="records")
    return render_template_string(HTML_TEMPLATE, results=results, query=query)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


