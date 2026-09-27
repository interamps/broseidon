# Anatomy of Broseidon
This markdown file lists out the objectives of each file

---

## backend

### api
1. gemini.py: Interaction with Gemini API
2. local.py: Interaction with local models using LlamaCPP Web server API
3. server.py: Interaction with industrial grade servers
4. groq.py: Interaction with Groq API
5. openrouter.py: Interaction with OpenRouter API
6. allocator.py: An orchestrator which manages which methods to use, like which API and what flags to pass into it. A middle man where purification and instructions could be added.
    *Example:* Verify if internet is working, only then use APIs

### database
#### qdrant
*Empty*

### models
1. embed.gguf: Qwen3-Embedding-0.6B-Q8_0 for embedding
2. a9b.gguf: Qwen3.5-9B-Q4_K_M for advanced communication and vision learning

### soul

### tools
1. db.py: Interact with vector, sql and md databases
2. prober.py: Indexes and returns all tools and soul for model
3. rag.py: Interacts with documents, for obtaining document relevant data
4. web.py: Interacts with web for information 

---

## frontend

*Empty*

---

## root
1. .env: Environment variable definitions for credentials and secrets
2. anatomy.md: Structural blueprint and file objective documentation
3. LICENSE: Project open-source license definitions and terms
4. README.md: Repository overview, setup instructions, and primary project documentation
5. main.py: Startup, model runs through this and makes function calls from here

---

# .env anatomy
*You have to create your own .env file with your own APIs to start interactions*
API_GEMINI
API_OPENROUTER
API_GROQ