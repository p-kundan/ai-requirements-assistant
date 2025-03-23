import sys
import os

# 📁 Adjust the path so we can import from /src
current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, '..'))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

sys.path.insert(0, src_path)

# 🔄 Imports from /src
from extractor import extract_requirements
from nlp import classify_with_llm

# 📂 Check for the file
if os.path.exists(data_path):
    print(f"\n🔍 Extracting from: {data_path}")
    requirements = extract_requirements(data_path)
    print(f"\n✅ Extracted {len(requirements)} requirements.")

    # 🧠 LLM Classification
    print("\n🔮 Classifying with LLM (LangChain + llama-cpp-python):\n")

    for i, req in enumerate(requirements[:5]):  # show first 5
        print(f"\n🧾 Requirement {i+1}: {req}")
        try:
            label = classify_with_llm(req)
            print(f"🔖 LLM Classification: {label}")
        except Exception as e:
            print(f"❌ Failed to classify: {e}")

else:
    print(f"\n❌ File not found at: {data_path}")
