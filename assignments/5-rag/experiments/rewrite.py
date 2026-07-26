# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx"]
# ///

import sys
from pathlib import Path

HW_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HW_DIR))            # -> `import rag...`

from rag.query_transform import rewrite_query, decompose, hyde

print(rewrite_query("The user asked about the Titanic.", "How many people died?"))
print(rewrite_query("The user asked about Paris.", "What about its most famous landmark?"))
print(rewrite_query("", "What is alchemy?")) 

print(decompose("How are the Sun, gravity, and photosynthesis connected?"))
print(decompose("Compare Paris and the Eiffel Tower. What is the relation between them?"))
print(decompose("What is the Sun?")) 

print(hyde("How many people died on the Titanic?"))
print(hyde("What is alchemy?"))