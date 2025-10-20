import os
import langextract as lx

try:
    lx.providers.load_builtins_once()
except Exception:
    pass


try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()  # loads .env in current working directory
except Exception:
    pass



examples = [
    lx.data.ExampleData(
        text="阿里巴巴于2024年10月12日发布新品。",
        extractions=[
            lx.data.Extraction(extraction_class="company", extraction_text="阿里巴巴"),
            lx.data.Extraction(extraction_class="date",    extraction_text="2024年10月12日"),
        ],
    )
]


config = lx.factory.ModelConfig(
    model_id="qwen-plus",                
    provider="OpenAILanguageModel",      
    provider_kwargs={
        "api_key": os.environ.get("DASHSCOPE_API_KEY"),
        "base_url": os.environ.get("DASHSCOPE_BASE_URL"),
        # "temperature": 0.2
    },
)


result = lx.extract(
    text_or_documents="字节跳动在2023年5月10日举办开发者大会。",
    prompt_description="抽取公司名(company)与日期(date)。",
    examples=examples,
    config=config,                
)

print(result) 
