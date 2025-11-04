# Changelog - Asana MCP Server

## 2025-11-03 - My Tasks Section Support

### Neue Features

#### Tool 18: `asana_get_user_task_list`
- Neues Tool zum Abrufen der User Task List GID
- Ermöglicht das Arbeiten mit My Tasks Sections
- Standard-Parameter: `user_gid="me"` für den aktuellen Benutzer

### Verbesserungen

#### `asana_list_sections` - Erweiterte Unterstützung
- Unterstützt jetzt sowohl Projekte als auch User Task Lists (My Tasks)
- Aktualisierte Dokumentation und Beispiele
- Titel geändert zu "List Project or My Tasks Sections"

### Wichtige Erkenntnisse

**User Task Lists und Sections:**
- User Task Lists funktionieren in der Asana API wie reguläre Projekte
- Der Endpunkt `GET /projects/{user_task_list_gid}/sections` funktioniert mit User Task List GIDs
- Es gibt KEINEN separaten `/user_task_lists/{gid}/sections` Endpunkt
- Sections in My Tasks können genauso verwaltet werden wie Projekt-Sections

### Workflow für My Tasks Sections

1. **User Task List GID abrufen:**
   ```
   asana_get_user_task_list(user_gid="me")
   ```

2. **Sections auflisten:**
   ```
   asana_list_sections(project_gid=<user_task_list_gid>)
   ```

3. **Task zu Section verschieben:**
   ```
   asana_move_task_to_section(task_gid=<task_gid>, section_gid=<section_gid>)
   ```

### Beispiel-Nutzung

```python
# 1. My Tasks GID abrufen
user_task_list_gid = "1205656411889926"

# 2. Sections anzeigen
sections = [
    {"gid": "1205656411889940", "name": "🔎 Today"},
    {"gid": "1205656411889941", "name": "📆 This week"},
    {"gid": "1211206976525042", "name": "🌙 This month"},
    # ... weitere Sections
]

# 3. Task zu "Today" Section verschieben
asana_move_task_to_section(
    task_gid="1211819567509721",
    section_gid="1205656411889940"
)
```

### API-Dokumentation Referenzen

- [Asana API: User Task Lists](https://developers.asana.com/reference/getusertasklistforuser)
- [Asana API: Sections](https://developers.asana.com/reference/getsectionsforproject)
- [Forum: My Tasks Section Changes](https://forum.asana.com/t/upcoming-changes-coming-to-my-tasks-in-asana-and-the-api-breaking-changes/109717)

### Tool-Anzahl

- **Vorher:** 17 Tools
- **Jetzt:** 18 Tools
