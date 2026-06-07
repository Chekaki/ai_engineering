Act as an Expert System Architect. I want you to initialize my "Personal OS & Second Brain" in this current empty directory. 

Please execute the following steps exactly as described. Do not ask for confirmation between steps, just create the files and folders.

### STEP 1: Create the PARA Directory Structure
Create the following folders:
- `00_Inbox`
- `01_Projects/ai-engineering-course`
- `02_Areas/Career`
- `03_Resources/RAG_and_Agents`
- `04_Archive`
- `99_System/Templates`

### STEP 2: Create the Global Context
Create a file named `.cursorrules` in the root directory. Then, make an exact copy of it and name it `CLAUDE.md`. Both files should contain the following content:

"""
# Personal OS Context
You are my Second Brain assistant. This workspace uses the PARA method.

**Rules:**
1. All notes must be in Markdown (.md).
2. Always add YAML frontmatter to new files: `tags: []`, `date: YYYY-MM-DD`.
3. Use Obsidian-style links `[[File Name]]` to connect concepts.
4. When I ask a question, always search `02_Areas` and `03_Resources` first before answering from your general knowledge.
5. Keep answers concise. Use bullet points or code blocks where applicable.
"""

### STEP 3: Create Core Templates
Create two files in `99_System/Templates/`:

1. File: `Project_Template.md`
"""
---
status: active
tags: [project]
---
# 🚀 [Project Name]
**Goal:** What is the definition of done?
## 📋 Action Items
- [ ] Task 1
## 🔗 Resources
- [[Resource 1]]
"""

2. File: `Concept_Node.md`
"""
---
tags: [resource, concept]
---
# 💡 [Concept Name]
## 📝 Summary
(3 sentences max)
## 🧠 Implementation / Code
(How to use this in practice)
"""

### STEP 4: Create the Agents & Prompts Library
Create a file named `agents.md` in `99_System/` with the following content. These are my execution prompts.

"""
# 🤖 AI Agent Prompts & Routines

Copy any of these prompts and paste them into the AI chat to run a routine.

## 🧹 1. Inbox Processor Agent
**Prompt:** "Read all `.md` files in `00_Inbox/`. For each file, extract the core entities, assign tags, rewrite it using the `Concept_Node.md` template, and move the finalized file to `03_Resources/`. Delete the original file from the Inbox."

## 🔍 2. Knowledge Retrieval Agent (Basic RAG)
**Prompt:** "Search my `03_Resources/` and `01_Projects/` for any mentions of [INSERT TOPIC]. Synthesize the findings into a structured summary with exact quotes and links `[[ ]]` back to my original files."

## 🏗️ 3. Project Scaffolding Agent
**Prompt:** "I want to start a new project about [INSERT PROJECT IDEA]. Create a new folder in `01_Projects/`, initialize a `README.md` using the `Project_Template.md`, and suggest 3 action items based on similar concepts in my `03_Resources/`."
"""

Please confirm when all folders and files have been successfully generated.
