# Asana MCP Server

Ein umfassender Model Context Protocol (MCP) Server für Asana mit 18 Tools für vollständiges Task- und Projekt-Management.

## 🔧 Features - 18 Tools

### Task Management (1-5)
1. **`asana_list_tasks`** - Aufgaben auflisten mit Filtern
2. **`asana_create_task`** - Neue Aufgaben erstellen
3. **`asana_update_task`** - Aufgaben bearbeiten
4. **`asana_complete_task`** - Als erledigt markieren
5. **`asana_search_tasks`** - Tasks durchsuchen

### Project Management (6-7)
6. **`asana_list_projects`** - Projekte auflisten
7. **`asana_get_project_tasks`** - Alle Tasks eines Projekts

### Communication (8-9)
8. **`asana_add_comment`** - Kommentare hinzufügen
9. **`asana_get_task_comments`** - Kommentare lesen

### Section Management (10-11)
10. **`asana_list_sections`** - Projekt-Sections auflisten
11. **`asana_move_task_to_section`** - Task in Section verschieben

### Task Hierarchy (12-13)
12. **`asana_add_subtask`** - Subtasks erstellen
13. **`asana_get_task_details`** - Vollständige Task-Details

### Tagging (14-15)
14. **`asana_list_tags`** - Workspace Tags auflisten
15. **`asana_add_tag_to_task`** - Tag zu Task hinzufügen

### Quick Actions (16-17)
16. **`asana_set_due_date`** - Fälligkeitsdatum setzen
17. **`asana_assign_task`** - Task zuweisen

### User Task List (18)
18. **`asana_get_user_task_list`** - My Tasks GID abrufen (für Section-Management)

## 🚀 Setup

### 1. Dependencies installieren

```bash
cd ~/asana_mcp
pip install -r requirements.txt
```

### 2. Asana Personal Access Token erhalten

1. Gehe zu [Asana Developer Console](https://app.asana.com/0/developer-console)
2. Klicke auf **"Personal access tokens"**
3. Klicke **"+ Create new token"**
4. Gib einen Namen ein (z.B. "MCP Server")
5. Kopiere den Token (wird nur einmal angezeigt!)

### 3. Token setzen

```bash
export ASANA_ACCESS_TOKEN="your_token_here"
```

Oder erstelle eine `.env` Datei:
```
ASANA_ACCESS_TOKEN=your_token_here
```

### 4. Mit Claude Code verbinden

```bash
cd ~/asana_mcp
claude mcp add --transport stdio --scope user asana \
  --env ASANA_ACCESS_TOKEN=your_token_here \
  -- python /Users/aiveo/asana_mcp/asana_mcp.py
```

## 📋 Verwendung

Nach dem Setup kannst du in Claude Code Befehle verwenden wie:

```
Zeig mir meine Asana Tasks
```

```
Erstelle eine neue Aufgabe "Budget Review" im Projekt X
```

```
Markiere Task Y als erledigt
```

```
Welche Sections hat Projekt Z?
```

```
Füge einen Kommentar zu Task A hinzu: "Bitte Review bis morgen"
```

## 🔑 Wichtige Konzepte

### GIDs (Global IDs)
Asana verwendet GIDs für alle Ressourcen. Du findest sie:
- In der URL (z.B. `https://app.asana.com/0/1234567890/1234567890`)
- Im Task-Details durch rechtsklick → "Copy link"
- Durch Tools wie `asana_list_projects` oder `asana_list_tasks`

### Workspaces
Die meisten Tools benötigen eine `workspace_gid`. Finde deine:
1. Öffne Asana im Browser
2. Die erste Zahl in der URL ist deine Workspace GID

## 📊 Response Formate

Alle Read-Tools unterstützen zwei Formate:
- **`markdown`** (default): Menschenlesbar, formatiert
- **`json`**: Maschinenlesbar, strukturiert

## 🔒 Sicherheit

- **Nie** den Token in Git committen
- Token läuft nicht ab (aber kann widerrufen werden)
- Minimale Berechtigungen verwenden wenn möglich

## 💡 Tipps

1. **Workspace GID finden**: Nutze Asana URL oder Browser DevTools
2. **Bulk Operations**: Nutze Search mit Filtern
3. **Kanban Workflow**: Nutze Sections für To Do/In Progress/Done
4. **Hierarchie**: Nutze Subtasks für komplexe Aufgaben
5. **My Tasks Sections**:
   - Nutze `asana_get_user_task_list` um deine User Task List GID zu erhalten
   - Verwende diese GID mit `asana_list_sections` um deine My Tasks Sections zu sehen
   - User Task Lists funktionieren genau wie Projekte für Section-Management

## 🐛 Troubleshooting

### "Authentication failed"
→ Prüfe ob `ASANA_ACCESS_TOKEN` gesetzt ist und gültig

### "Resource not found"
→ Prüfe die GID, manche Ressourcen sind workspace-spezifisch

### "Permission denied"
→ Token hat nicht genug Berechtigungen für diese Aktion

## 📚 Weitere Ressourcen

- [Asana API Dokumentation](https://developers.asana.com/docs)
- [Personal Access Tokens](https://developers.asana.com/docs/personal-access-token)
- [MCP Documentation](https://modelcontextprotocol.io/)
