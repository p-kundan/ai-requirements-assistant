from llama_cpp import Llama

llm = Llama(model_path="reqAI\models\mistral-7b-instruct-v0.1.Q4_K_M.gguf")
output = llm("Q: What is AI?\nA:", max_tokens=20)
print(output)
