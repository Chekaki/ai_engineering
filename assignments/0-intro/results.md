## 1. Idea Bank

The thing that connects these three ideas: I'm moving to a team that builds autonomous agents with access to our ecosystem, and right now my main goal is just to learn. I want to understand how agents really take actions, and how llms work inside. So the ideas go from "a useful agent" down to "understand the basics", on small things that I fully control.

### Case 1 - Coding agent on my own repos

An agent that works on my own github repos. Instead of me doing the boring triage, it watches new issues and PRs, tries to reproduce the bug, writes a fix or a review, runs the tests, and only then opens a PR. I give it limited access to the repo, CI and a few tools (search, run tests, open a PR) and let it plan the steps by itself. I don't want it to replace me, I want to learn how to build an agent that does real actions safely: how to design tools, how to handle permissions, the planning loop, and the guardrails. It's basically a small version of the "agent with ecosystem access" work I'm going into, but on a repo that I own.

### Case 2 - A local llm for a niche hobby

A small llm that runs fully on my laptop, made actually useful for some hobby I care about (board games / cooking / personal finance), where a generic small model is pretty weak. Here the experiment is the point. I start from a ready small model, then try the techniques you can do locally: quantization to make it fit, RAG over my own data, prompting and few-shot, maybe a small LoRA fine-tune. And I check how much each one improves the result compared to a big cloud model. I want to get a feeling for what really changes the quality on limited hardware, and also have a private assistant that doesn't send my data anywhere. I think this is the best way for me to understand llms better.

### Case 3 - A mini agent from scratch, no framework

A tiny agent for one boring personal task (like reminders, or some small thing I do again and again), built from scratch. Just an llm api call, a loop, 2-3 tools and a simple memory, no framework at all. By building the basic parts myself (the loop, the tool calls, when to stop, how to recover from a bad step) I can see what the frameworks hide from you. I keep it as simple as possible: small task, few tools, and I can see every step. The result here is not a product, it's understanding. Once I can build the loop by hand, I can think clearly about why the real agents behave the way they do.

## 2. Market Research

Note: I don't really have job postings that I'm chasing right now. Instead I'm moving to an internal team that builds (a) a platform to run agents and (b) agents that do repetitive engineering work, mostly big code migrations (language and version upgrades, or changing one data-access way to another). So instead of copying real vacancies, I tried to guess what such a role would ask for, and where I would need to grow. The background I'm comparing against: backend/infra (Java, Kubernetes, AWS, Kafka, MySQL, Grafana, and also Perl), and as an AI user I'm ok with MCP, RAG and tools like Claude Code.

### Role A - Agent Platform Engineer (builds the runtime that agents run on)

What they would probably ask for: a safe runtime to run agents (containers/VMs), the tools and integrations layer (MCP servers, Git/CI integrations, webhooks), multi-tenant reliability, observability of the agent runs, scheduling, cost and latency control, and safe actions (permissions, guardrails, audit trail). Plus strong general software engineering and distributed systems.

What I'm good at: Kubernetes, AWS, distributed systems, Kafka and Grafana fit almost directly to building and running an agent runtime and its observability. Sandboxing and CI integration are comfortable for me.

What I need to work on: the llm-specific part. Designing good tool / function-calling interfaces, agent observability (tracking tokens, tool calls, failures), and the guardrail/safety patterns that are specific to agents taking actions on their own.

### Role B - LLM / Agent Engineer for code migrations

What they would probably ask for: building agents that do automated, large code changes, program-analysis tooling (ASTs, codemods, refactoring engines), ways to handle repos that are much bigger than the context window (chunking, retrieval, planning over a codebase), and, the most important part, checking that the migration is actually correct (test generation, shadow traffic, diff review).

What I'm good at: I understand real production codebases and migrations from the inside, and my Perl/Java background is actually useful for migrating legacy code. I know what "correct" looks like for a backend change.

What I need to work on: context management for large repos (this is a known hard problem for these agents), program-analysis and codemod tooling, and the ways to automatically check the changes that an agent makes.

### Role C - Applied AI Engineer (designs agents, prompts and evals)

What they would probably ask for: prompt engineering on a production level, RAG as engineering (chunking, embeddings, retrieval tuning) and not just using it, building evaluation harnesses (llm-as-judge, regression suites, success metrics), and the LLMOps loop of measure → improve → ship. Python is the default language here.

What I'm good at: I already use MCP, RAG and agentic coding tools every day, so I have a working feeling for what good looks like. The general engineering basics transfer.

What I need to work on: moving from a user to a builder of RAG and agents, designing evals and treating reliability as something I can measure, and getting deeper in Python, because most of the AI tooling lives there while my main languages are Perl and Java.

### Summary - what I need to brush up on

1. Build agents, not just use them: orchestration, the planning/reasoning loop, tool design, memory, recovery from a bad step.
2. RAG: embeddings, chunking, retrieval tuning, and especially context management for large codebases.
3. Evaluation and reliability: eval harnesses, llm-as-judge, regression suites, treating agent reliability as a number I can measure.
4. Prompt engineering on a production level, including structured / constrained output.
5. Program-analysis / codemod tooling and automatic checking of migrations (test generation, shadow traffic), specific to the migration agents.
6. LLMOps and guardrails: observability of agent runs, cost/latency control, safety for agents taking actions, which I can partly start from my infra/Grafana background.