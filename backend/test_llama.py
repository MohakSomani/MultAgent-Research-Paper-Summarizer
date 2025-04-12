from langchain_community.llms import LlamaCpp

llm = LlamaCpp(
    model_path="./models/llama-2-7b.Q4_K_M.gguf",
    temperature=0.7,
    max_tokens=2000,
    n_ctx=2048,
    n_gpu_layers=40,
    verbose=True
)

response = llm.invoke("What are the latest advancements in transformer models?")
print(response)
