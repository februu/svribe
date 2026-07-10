<div align="center">

### 𝚜𝚟𝚛𝚒𝚋𝚎

_Svribe is your personal Discord Assistant that will transform a server into your small auto-organized notespace._

⠀· · ─────── · 𖥸 · ─────── · ·

</div>

**Current features:**
- Auto server template — use `/init` to wipe all channels and set up categories
- Dynamic categorization based on existing text channels and their descriptions
- Handles plain messages, links, and file types

**Upcoming features:**
- Ability to customize category and channel names
- Response caching for file extensions and link domains
- Smarter link categorization via OpenGraph / fetched metadata
- Auto-sync messages and files to a local SQLite DB, with full server restore
- Reminders and events with reminder support
- Google Calendar integration
- More LLM provider interfaces

> Suggestions are welcome!

## Running the bot

Create a `.env` file based on `.env.example`, then use **uv** to sync dependencies and run:

```bash
uv run main.py
```

> Docker image coming soon.