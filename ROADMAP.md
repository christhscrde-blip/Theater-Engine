# ROADMAP.md

Diese Roadmap beschreibt die Entwicklung von `Theater.Formatierung` als robuste Theater-Engine.

## v0.1 – Projektbasis

Status: weitgehend erledigt

Ziele:

- Repository-Struktur anlegen
- README erstellen
- Styleguide erstellen
- Grundmodelle anlegen
- Verifier für sichtbaren Texthash bauen
- ersten Klassifikator bauen
- CLI für Analyse bereitstellen
- erste Tests schreiben

Erfolgskriterium:

- `pytest` läuft erfolgreich
- `python -m src.cli analyse <datei.docx>` erzeugt Reports

## v0.2 – Klassifikator stabilisieren

Ziele:

- echte Beispiel-DOCX in `samples/` verwenden
- alle Absatztypen aus `ENGINE_SPEC.md` zuverlässig erkennen
- Sprecher-Aliase erweitern
- unklare Stellen reduzieren
- Problemstellen aus Screenshots als Regression-Tests sichern
- Analysebericht verbessern

Erfolgskriterium:

- möglichst wenige `UNCLASSIFIED`-Absätze
- alle bekannten Problemfälle haben Tests
- keine Replik wird als Regie oder Sprecher fehlklassifiziert

## v0.3 – Style-Konfiguration

Ziele:

- `styles/theater.yaml` einführen
- Stylewerte aus Datei laden
- Farben, Größen und Abstände aus Code entfernen
- Theme-System vorbereiten

Geplante Styles:

- `theater.yaml`
- `classic.yaml`
- `minimal.yaml`

Erfolgskriterium:

- Formatierungsregeln sind datengetrieben
- Styles können geändert werden, ohne Python-Code anzufassen

## v0.4 – Formatierungs-Engine v1

Ziele:

- DOCX formatieren, ohne sichtbaren Text zu ändern
- `SPEAKER`, `REPLIQUE`, `STAGE_DIRECTION`, `PAGE_MARKER`, `ACT_HEADING`, `SCENE_HEADING`, `LOCATION` formatieren
- Inline-Regie erkennen und separat formatieren
- schwierige Wörter markieren
- Hash-Prüfung erzwingen

Erfolgskriterium:

- Ausgabe-DOCX wird erzeugt
- sichtbarer Texthash bleibt identisch
- Repliken bleiben schwarz und nicht kursiv

## v0.5 – Qualitätsberichte

Ziele:

- Formatierungsbericht erstellen
- Anzahl erkannter Sprecher, Repliken und Regieanweisungen ausgeben
- Warnungen für unsichere Absätze ausgeben
- potenziell gefährliche Formatierungen melden

Erfolgskriterium:

- jeder Engine-Lauf erzeugt einen menschlich lesbaren Bericht
- Prüffälle können gezielt nachbearbeitet werden

## v0.6 – Renderer und visuelle Kontrolle

Ziele:

- DOCX optional zu PDF rendern
- Seitenbilder erzeugen
- Stichprobenprüfung vorbereiten
- sichtbare Ausreißer schneller finden

Erfolgskriterium:

- ausgewählte Seiten können als Bild geprüft werden
- problematische Seiten werden schneller sichtbar

## v0.7 – DocumentModel

Status: begonnen

Ziele:

- Word-Absätze in ein internes Dokumentmodell übertragen – Basis umgesetzt
- Klassifikation, Sprecher, Regieanteile und schwierige Wörter getrennt speichern – Basis umgesetzt
- Formatter arbeitet gegen das Modell, nicht direkt gegen rohe Word-Absätze – ausstehend

Erfolgskriterium:

- Engine kann Analyse und Formatierung reproduzierbar durchführen
- spätere Exporte werden einfacher

## v0.8 – Plugin-System

Ziele:

- autorenspezifische Regeln ermöglichen
- `plugins/schiller.py` vorbereiten
- später Goethe, Shakespeare, Ibsen usw. möglich machen

Erfolgskriterium:

- Schiller-spezifische Schreibweisen können getrennt gepflegt werden

## v0.9 – Probenfassung

Ziele:

- vollständige Fassung von `Die Räuber` formatieren
- manuelle Prüffälle minimieren
- visuelle Kontrolle wichtiger Seiten
- finale QA

Erfolgskriterium:

- DOCX ist für Theaterproben verwendbar
- keine bekannten schweren Formatierungsfehler offen

## v1.0 – Stabile Theater-Engine

Ziele:

- stabile CLI
- dokumentierte Architektur
- reproduzierbare Formatierung
- Tests für alle Kernregeln
- saubere Ausgabeberichte

Erfolgskriterium:

- Projekt kann auch für andere Theaterstücke genutzt werden
- Änderungen laufen ausschließlich über GitHub, Tests und Reviews

## Arbeitsregel ab jetzt

Neue Features entstehen nicht mehr direkt als lose Chat-Ausgabe, sondern im Repository:

1. Issue oder klarer Auftrag
2. Codeänderung
3. Tests
4. Bericht
5. Review
6. Merge

So vermeiden wir, dass Word erneut heimlich zum Endgegner wird.
