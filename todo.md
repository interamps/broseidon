**TODO**

**main.py**
- [ ] spawn llamacpp server via subprocess
- [ ] pick random port
- [ ] define blacklist var (list, incl 8080)
- [ ] on subprocess unexpected exit → print warning, exit (no auto-restart)

**settings.conf**
- [ ] add blacklist_ports field
- [ ] add whitelist_apis field (local only, active)
- [ ] add rag/db path fields (qdrant path, embed model path)
- [ ] confirm read-once-at-boot logic in whichever module parses this

**api/__init__.py**
- [ ] verify allocator + local exported/importable cleanly

**allocator.py**
- [ ] implement local branch (functional)
- [ ] stub gemini/openrouter/groq/server branches → raise NotImplementedError
- [ ] route tool-call dispatch through here (not local.py directly)

**local.py**
- [ ] confirm llamacpp server launched with `--jinja`
- [ ] confirm chat template is tool-aware (Qwen2.5/Hermes-style)
- [ ] wire tool-calling for Qwen9B

**tools/prober.py**
- [ ] read tools/ dir contents
- [ ] read soul/ dir contents
- [ ] return combined list on request (no format translation)

**decide first, before rag.py work:**
- [ ] rag-as-tool (model calls via tool-calling, listed in prober) vs rag-as-always-on (auto-injected every query) — pick one

**tools/rag.py**
- [ ] confirm qdrant running locally (docker or embedded)
- [ ] wire qdrant client connection
- [ ] wire embed.gguf loading (llamacpp embedding endpoint or llama-cpp-python)
- [ ] write ingest/chunking script (currently missing — where's source data from?)
- [ ] write retrieval fn: query → embed → qdrant search → return context
- [ ] hook retrieval output into prompt assembly (location depends on decision above)

**cleanup**
- [ ] .gitignore: exclude __pycache__, *.gguf, .env
- [ ] decide frontend/ — remove or keep as planned scope
- [ ] confirm database/qdrant has __init__.py if imported as package