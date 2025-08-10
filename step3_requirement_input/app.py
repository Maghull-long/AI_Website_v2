import os
import re
import subprocess
import tempfile
from flask import Flask, request, render_template, jsonify
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

def clean_code_block(code: str) -> str:
    """
    去除 ```python 或 ``` 代码块标记，保留纯代码。
    """
    lines = code.splitlines()
    # 去掉开头的 ``` 或 ```python
    while lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    # 去掉结尾的 ```
    while lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()

def run_pytest(code: str, test_code: str) -> str:
    # 清理代码块标记
    code_clean = clean_code_block(code)
    test_clean = clean_code_block(test_code)

    combined = code_clean + "\n\n" + test_clean

    with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=True) as f:
        f.write(combined)
        f.flush()
        try:
            result = subprocess.run(
                ["pytest", f.name, "--maxfail=1", "--disable-warnings", "-q"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            output = result.stdout + result.stderr
            return output
        except Exception as e:
            return f"运行测试时出错: {e}"

def call_model(requirement: str) -> dict:
    system_prompt = (
        "你是一个资深后端开发工程师兼测试工程师。"
        "请根据用户的自然语言需求，分别生成以下内容："
        "1. 主要代码，使用 Python Flask 写一个示例项目；"
        "2. 对应的 pytest 测试代码；"
        "3. 项目的 README 文档；"
        "4. 项目的架构说明。"
        "请返回内容用明确标签分隔：=== CODE ===，=== TEST ===，=== README ===，=== ARCHITECTURE ===。"
    )

    user_prompt = f"需求描述：{requirement}\n请生成上述4部分内容。"

    try:
        response = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=1500,
        )
        text = response.choices[0].message.content

        parts = {"code": "", "test": "", "readme": "", "architecture": ""}

        code_match = re.search(r"=== CODE ===\s*(.*?)\s*(=== TEST ===|$)", text, re.S)
        test_match = re.search(r"=== TEST ===\s*(.*?)\s*(=== README ===|$)", text, re.S)
        readme_match = re.search(r"=== README ===\s*(.*?)\s*(=== ARCHITECTURE ===|$)", text, re.S)
        arch_match = re.search(r"=== ARCHITECTURE ===\s*(.*)", text, re.S)

        if code_match:
            parts["code"] = code_match.group(1).strip()
        if test_match:
            parts["test"] = test_match.group(1).strip()
        if readme_match:
            parts["readme"] = readme_match.group(1).strip()
        if arch_match:
            parts["architecture"] = arch_match.group(1).strip()

        if parts["test"]:
            parts["test_result"] = run_pytest(parts["code"], parts["test"])
        else:
            parts["test_result"] = "未生成测试代码，无法执行。"

        return parts

    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_code', methods=['POST'])
def generate_code():
    data = request.json
    requirement = data.get('requirement', '').strip()
    if not requirement:
        return jsonify({"status": "error", "message": "需求不能为空"}), 400

    result = call_model(requirement)
    if "error" in result:
        return jsonify({"status": "error", "message": result["error"]}), 500

    return jsonify({"status": "success", "result": result})

if __name__ == '__main__':
    app.run(debug=True)