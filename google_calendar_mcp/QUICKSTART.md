# 🚀 Google Calendar MCP Server - Schnellstart

## ✅ Was bereits gemacht wurde:

1. ✅ Python 3.11.9 konfiguriert
2. ✅ Alle Dependencies installiert (mcp, httpx, pydantic, google-auth)
3. ✅ MCP Server implementiert mit 6 Tools
4. ✅ OAuth Helper-Script erstellt
5. ✅ Syntax validiert

## 📋 Nächste Schritte (DU musst diese machen):

### Schritt 1: Google Cloud Credentials erstellen (15 Minuten)

#### 1.1 Google Cloud Projekt
1. Gehe zu: https://console.cloud.google.com/
2. Klicke "Neues Projekt erstellen" (oder wähle existierendes)
3. Projekt-Name: z.B. "Calendar MCP"

#### 1.2 Calendar API aktivieren
1. Im Projekt: **APIs & Dienste** → **Bibliothek**
2. Suche: **"Google Calendar API"**
3. Klicke auf die API → **"Aktivieren"**

#### 1.3 OAuth Credentials erstellen
1. **APIs & Dienste** → **Anmeldedaten**
2. **Zustimmungsbildschirm konfigurieren** (falls nicht vorhanden):
   - Usertyp: "Extern" wählen (oder "Intern" für Workspace)
   - App-Name: z.B. "Calendar MCP"
   - Support-E-Mail: Deine E-Mail
   - Berechtigungen: `/auth/calendar` scope hinzufügen
   - Speichern

3. Zurück zu **Anmeldedaten** → **Anmeldedaten erstellen**
4. **OAuth-Client-ID** wählen
5. Anwendungstyp: **Desktop-App**
6. Name: z.B. "Calendar MCP Client"
7. **Erstellen** klicken

8. ⬇️ **WICHTIG**: **JSON herunterladen** klicken
9. Speichere die Datei als `credentials.json` im Projekt-Ordner:
   ```bash
   ~/google_calendar_mcp/credentials.json
   ```

### Schritt 2: Access Token erhalten (2 Minuten)

```bash
cd ~/google_calendar_mcp
python get_token.py
```

Dies wird:
- Einen Browser öffnen
- Dich bitten, dich anzumelden
- Nach Erlaubnis fragen, auf Calendar zuzugreifen
- Automatisch den Token speichern und anzeigen

**Output sieht so aus:**
```
✅ ACCESS TOKEN OBTAINED SUCCESSFULLY!
📝 Access Token:
ya29.a0AfB_byD...sehr_langer_token...XYZ

⏰ Expires at: 2024-01-15 15:30:00
```

### Schritt 3: Token setzen

Der `get_token.py` Script erstellt automatisch eine `.env` Datei. Du kannst auch manuell setzen:

```bash
export GOOGLE_CALENDAR_ACCESS_TOKEN="dein_token_hier"
```

### Schritt 4: Server testen

```bash
cd ~/google_calendar_mcp
python google_calendar_mcp.py
```

Der Server läuft jetzt und wartet auf MCP-Befehle via stdio.

### Schritt 5: Mit Claude Desktop integrieren

#### Option A: Automatisch (empfohlen)

```bash
cd ~/google_calendar_mcp
claude mcp add google_calendar_mcp.py
```

Dann manuell in der Config das Token hinzufügen (siehe Option B).

#### Option B: Manuell

Bearbeite die Claude Desktop Config:

```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

Füge hinzu:

```json
{
  "mcpServers": {
    "google-calendar": {
      "command": "python",
      "args": ["/Users/aiveo/google_calendar_mcp/google_calendar_mcp.py"],
      "env": {
        "GOOGLE_CALENDAR_ACCESS_TOKEN": "dein_access_token_hier"
      }
    }
  }
}
```

**WICHTIG**: Ersetze `"dein_access_token_hier"` mit deinem echten Token!

### Schritt 6: Claude Desktop neu starten

Beende Claude Desktop komplett und starte neu.

## 🧪 Testen in Claude

Probiere diese Befehle:

```
Zeig mir meine Termine heute
```

```
Erstelle ein Meeting morgen um 14:00 mit dem Titel "Team Sync"
```

```
Bin ich morgen zwischen 10 und 12 Uhr frei?
```

```
Suche nach Terminen mit "Zahnarzt"
```

## 🔧 Verfügbare Tools

1. **gcal_list_events** - Termine auflisten (heute, diese Woche, custom)
2. **gcal_create_event** - Neuen Termin erstellen (mit Teilnehmern, Meet-Link)
3. **gcal_update_event** - Termin ändern (Zeit, Ort, Titel, etc.)
4. **gcal_delete_event** - Termin löschen
5. **gcal_search_events** - Termine durchsuchen
6. **gcal_check_availability** - Verfügbarkeit prüfen (Freebusy)

## ⚠️ Troubleshooting

### "credentials.json not found"
- Stelle sicher, dass du die Datei heruntergeladen hast
- Speichere sie im richtigen Ordner: `~/google_calendar_mcp/`

### "Authentication failed"
- Prüfe, ob das Token korrekt gesetzt ist
- Token läuft nach ~1 Stunde ab → führe `python get_token.py` erneut aus
- Der Script speichert Refresh-Token in `token.pickle` für automatisches Refresh

### "Permission denied"
- Prüfe, ob Calendar API aktiviert ist
- Stelle sicher, dass der OAuth Consent Screen konfiguriert ist
- Prüfe, ob der richtige Scope verwendet wird

### Server startet nicht in Claude
- Prüfe Claude Desktop Logs: `~/Library/Logs/Claude/mcp*.log`
- Stelle sicher, dass der Python-Pfad korrekt ist
- Teste den Server manuell: `python google_calendar_mcp.py`

## 📚 Token Refresh

Der `get_token.py` Script speichert ein Refresh-Token in `token.pickle`.

**Wichtig**:
- Access Tokens laufen nach ~1 Stunde ab
- Der Script kann sie automatisch refreshen
- Für Produktion: Führe `python get_token.py` regelmäßig aus oder implementiere Auto-Refresh im Server

## 🎯 Projekt-Struktur

```
~/google_calendar_mcp/
├── google_calendar_mcp.py   # MCP Server (Hauptdatei)
├── get_token.py              # OAuth Helper
├── requirements.txt          # Dependencies
├── README.md                 # Vollständige Dokumentation (EN)
├── SETUP_GUIDE.md            # Detaillierte Anleitung (DE)
├── QUICKSTART.md             # Diese Datei
├── credentials.json          # DU musst diese erstellen!
├── token.pickle              # Wird automatisch erstellt
└── .env                      # Wird automatisch erstellt
```

## 🚀 Viel Erfolg!

Bei Fragen oder Problemen:
1. Lies die ausführliche [SETUP_GUIDE.md](SETUP_GUIDE.md)
2. Prüfe [README.md](README.md) für API-Details
3. Prüfe Google Calendar API Docs: https://developers.google.com/calendar/api
