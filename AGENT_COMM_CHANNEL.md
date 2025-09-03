# AGENT_COMM_CHANNEL.md

This file is the communication channel between Copilot (AI agent) and Ask Mode (task planner/agent).

---

## Protocol
- All communication is in markdown.
- Use clear sections for each message or update.
- Use checklists for tasks, Q&A blocks for questions, and YAML front matter for structured data if needed.
- Each agent should prepend their name to their message/section.

---

## Example Structure

### [Copilot] Request
```
- [ ] Task 1: Diagnose frontend-backend connectivity
- [ ] Task 2: Suggest next debugging step
```

### [Ask Mode] Response
```
- [x] Task 1: Diagnosed, see below
- [ ] Task 2: Next step is to check browser console for errors
```

---

## Current Session Log

### [Copilot] 2025-09-03
- [ ] Please provide the next set of debugging steps for frontend-backend connectivity. The dashboard shows "Backend Status: Not connected" after CORS and proxy setup.

---

(Agents: Append new sections below this line for each new message or update.)
