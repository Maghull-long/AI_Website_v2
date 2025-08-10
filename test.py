from openai import OpenAI

client = OpenAI(
    api_key="sk-130adf13cbb94076a97c89ae8c24e64b",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

resp = client.chat.completions.create(
    model="qwen-plus",
    messages=[
        {"role": "system", "content": "你是一个AI助手"},
        {"role": "user", "content": "你好，介绍一下你自己"}
    ]
)

print(resp.choices[0].message.content)