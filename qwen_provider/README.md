# langextract-provider-qwen

A LangExtract provider that routes `qwen*` model IDs to Alibaba DashScope via the OpenAI-compatible API.

- Matches model_id by regex `^qwen`
- Higher priority than the built-in Ollama mapping, so `model_id="qwen-plus"` will use this provider automatically
- Uses environment defaults when not passed explicitly:
  - `DASHSCOPE_API_KEY`
  - `DASHSCOPE_BASE_URL` (defaults to `https://dashscope.aliyuncs.com/compatible-mode/v1`)

