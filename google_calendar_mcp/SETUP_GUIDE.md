# Google Calendar MCP Server - Schnellstart-Anleitung

Diese Anleitung hilft dir, den Google Calendar MCP Server einzurichten und zu nutzen.

## 📋 Schritt-für-Schritt Setup

### Schritt 1: Dependencies installieren

```bash
cd ~/google_calendar_mcp
pip3 install -r requirements.txt
```

### Schritt 2: Google Cloud Projekt einrichten

#### 2.1 Projekt erstellen
1. Gehe zu [Google Cloud Console](https://console.cloud.google.com/)
2. Klicke auf "Neues Projekt erstellen"
3. Gib einen Namen ein (z.B. "Calendar MCP")
4. Klicke auf "Erstellen"

#### 2.2 Calendar API aktivieren
1. Im Google Cloud Projekt, gehe zu **"APIs & Dienste" > "Bibliothek"**
2. Suche nach **"Google Calendar API"**
3. Klicke auf die API und dann auf **"Aktivieren"**

#### 2.3 OAuth 2.0 Credentials erstellen
1. Gehe zu **"APIs & Dienste" > "Anmeldedaten"**
2. Klicke auf **"Anmeldedaten erstellen" > "OAuth-Client-ID"**
3. Falls noch nicht geschehen, konfiguriere den OAuth-Zustimmungsbildschirm:
   - Wähle "Extern" (oder "Intern" für Workspace-Konten)
   - Fülle die erforderlichen Felder aus (App-Name, Support-E-Mail)
   - Klicke auf "Speichern und fortfahren"
   - Füge den Scope hinzu: `https://www.googleapis.com/auth/calendar`
   - Speichern

4. Zurück zu "Anmeldedaten erstellen":
   - Anwendungstyp: **"Desktop-App"** wählen
   - Name: z.B. "Calendar MCP Client"
   - Klicke auf **"Erstellen"**

5. **Wichtig**: Lade die Credentials-JSON-Datei herunter
   - Speichere sie als `credentials.json` in deinem Projekt-Ordner

### Schritt 3: Access Token erhalten

Du hast zwei Möglichkeiten:

#### Option A: OAuth Playground (Schnell für Testing)

1. Gehe zu [Google OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)
2. Klicke auf das Zahnrad-Symbol ⚙️ oben rechts
3. Aktiviere **"Use your own OAuth credentials"**
4. Gib deine Client ID und Client Secret ein (aus der credentials.json)
5. In **Step 1**:
   - Finde "Calendar API v3"
   - Wähle `https://www.googleapis.com/auth/calendar`
   - Klicke auf **"Authorize APIs"**
6. Melde dich mit deinem Google-Konto an und erlaube den Zugriff
7. In **Step 2**:
   - Klicke auf **"Exchange authorization code for tokens"**
8. Kopiere den **"Access token"**

⚠️ **Hinweis**: Dieser Token läuft nach ca. 1 Stunde ab!

#### Option B: Python Script (Empfohlen für längere Nutzung)

Erstelle eine Datei `get_token.py`:

```python
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_credentials():
    creds = None

    # Prüfe, ob bereits ein Token gespeichert ist
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # Wenn kein Token oder abgelaufen, neu authentifizieren
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Token für zukünftige Verwendung speichern
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

if __name__ == '__main__':
    creds = get_credentials()
    print(f"\n✅ Access Token erhalten!")
    print(f"Token: {creds.token}\n")
    print("Setze diesen Token als Umgebungsvariable:")
    print(f'export GOOGLE_CALENDAR_ACCESS_TOKEN="{creds.token}"')
```

Installiere die benötigte Library:
```bash
pip3 install google-auth-oauthlib
```

Führe das Script aus:
```bash
python3 get_token.py
```

Dies öffnet einen Browser, wo du dich anmelden und den Zugriff erlauben musst.

### Schritt 4: Token als Umgebungsvariable setzen

```bash
export GOOGLE_CALENDAR_ACCESS_TOKEN="dein_access_token_hier"
```

Oder erstelle eine `.env` Datei im Projekt-Ordner:
```
GOOGLE_CALENDAR_ACCESS_TOKEN=dein_access_token_hier
```

### Schritt 5: MCP Server testen

Teste den Server direkt:
```bash
cd ~/google_calendar_mcp
python3 google_calendar_mcp.py
```

Der Server sollte starten und auf Eingaben warten (Stdio-Transport).

### Schritt 6: Mit Claude Desktop integrieren

#### Option A: Manuelle Konfiguration

Bearbeite die Claude Desktop Config:
```bash
# macOS
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux
nano ~/.config/Claude/claude_desktop_config.json
```

Füge hinzu:
```json
{
  "mcpServers": {
    "google-calendar": {
      "command": "python3",
      "args": ["/Users/aiveo/google_calendar_mcp/google_calendar_mcp.py"],
      "env": {
        "GOOGLE_CALENDAR_ACCESS_TOKEN": "dein_access_token_hier"
      }
    }
  }
}
```

#### Option B: MCP CLI (falls installiert)

```bash
cd ~/google_calendar_mcp
mcp install google_calendar_mcp.py
```

Dann in der generierten Config das Access Token ergänzen.

### Schritt 7: Claude Desktop neu starten

Starte Claude Desktop neu, damit die Änderungen wirksam werden.

## ✅ Testen

Öffne Claude Desktop und probiere:

```
Zeig mir meine Termine heute
```

```
Erstelle ein Meeting morgen um 14 Uhr mit dem Titel "Team Sync"
```

```
Suche nach Events mit "Zahnarzt"
```

## 🔧 Fehlerbehebung

### "Authentication failed"
- **Prüfe**: Ist `GOOGLE_CALENDAR_ACCESS_TOKEN` richtig gesetzt?
- **Prüfe**: Ist der Token abgelaufen? (Hole einen neuen)

### "Permission denied"
- **Prüfe**: Ist die Google Calendar API aktiviert?
- **Prüfe**: Hat der OAuth Token den richtigen Scope?

### "Module not found: mcp"
- **Lösung**: `pip3 install mcp httpx pydantic`

### Server startet nicht
- **Prüfe**: Python 3.10+ installiert? (`python3 --version`)
- **Prüfe**: Sind alle Dependencies installiert?

## 🚀 Nächste Schritte

### Token Refresh automatisieren

Für Produktion: Implementiere automatisches Token-Refresh mit dem `token.pickle` Ansatz aus Option B.

### Mehr Kalender hinzufügen

Du kannst auf mehrere Kalender zugreifen, indem du die entsprechende Kalender-ID verwendest:
- Primär: `"primary"`
- Andere: E-Mail-Adresse des Kalenders (z.B. `"team@company.com"`)

### Weitere Tools erkunden

Der Server bietet 6 Tools:
1. `gcal_list_events` - Termine auflisten
2. `gcal_create_event` - Termin erstellen
3. `gcal_update_event` - Termin ändern
4. `gcal_delete_event` - Termin löschen
5. `gcal_search_events` - Termine durchsuchen
6. `gcal_check_availability` - Verfügbarkeit prüfen

## 📚 Weitere Ressourcen

- [Google Calendar API Docs](https://developers.google.com/calendar/api)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
