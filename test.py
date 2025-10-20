import os
import langextract as lx

# 确保内置 providers 已加载（避免在显式 provider=... 时路由未加载的问题）
try:
    lx.providers.load_builtins_once()
except Exception:
    pass

# Load environment variables from .env if present (for DASHCOPE_* settings)
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()  # loads .env in current working directory
except Exception:
    # If python-dotenv is not installed, continue; os.environ.get will still work
    pass


# 1) 定义一个最小的示例（LangExtract 要求有 examples 才会抽取）
examples = [
    lx.data.ExampleData(
        text="阿里巴巴于2024年10月12日发布新品。",
        extractions=[
            lx.data.Extraction(extraction_class="company", extraction_text="阿里巴巴"),
            lx.data.Extraction(extraction_class="date",    extraction_text="2024年10月12日"),
        ],
    )
]

# 2) 显式选择 OpenAI provider，并把 DashScope 的 base_url/api_key 传过去
config = lx.factory.ModelConfig(
    model_id="qwen-plus",                # 换成你要用的 Qwen 模型，如 qwen-turbo、qwen2.5-7b-instruct 等
    provider="OpenAILanguageModel",      # 关键：强制使用 OpenAI provider（OpenAI 兼容模式）
    provider_kwargs={
        # 从环境变量读取，支持 .env（通过上面的 load_dotenv 加载）
        "api_key": os.environ.get("DASHSCOPE_API_KEY"),
        "base_url": os.environ.get("DASHSCOPE_BASE_URL"),
        # 选填：超参，如 "temperature": 0.2, "max_output_tokens": 800, "top_p": 0.9, ...
    },
)

# 3) 运行抽取
result = lx.extract(
    text_or_documents="字节跳动在2023年5月10日举办开发者大会。",
    prompt_description="抽取公司名(company)与日期(date)。",
    examples=examples,
    config=config,                # 用 config 明确 provider
    # 按当前实现，OpenAI provider 在 JSON 模式会自动启用 response_format=json_object
    # 因此一般不需要 fence_output=True；留空让库自动判定即可。
)

print(result)  # AnnotatedDocument，含 .extractions 等
