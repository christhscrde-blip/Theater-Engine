# ENGINE_SPEC.md

Diese Spezifikation beschreibt die Theater-Engine. Sie ist verbindlich für Parser, Klassifikator, Formatter und Verifier.

## Ziel

Die Engine formatiert Theatertexte in DOCX-Dateien zuverlässig, nachvollziehbar und ohne sichtbare Textänderungen.

Die wichtigste Regel:

> Der sichtbare Textinhalt darf niemals verändert werden.

Formatierung ist erlaubt. Textänderung ist verboten.

## Grundpipeline

1. DOCX-Datei laden.
2. Sichtbaren Text hash-bilden.
3. Absätze extrahieren.
4. Absätze klassifizieren.
5. Analysebericht erzeugen.
6. Formatierung anhand einer Style-Konfiguration anwenden.
7. Sichtbaren Text erneut hash-bilden.
8. Hash vergleichen.
9. Nur bei identischem Hash gilt die Ausgabe als gültig.

## Absatztypen

### EMPTY

Leerer Absatz.

Erkennung:

- Absatztext ist nach `strip()` leer.

Formatierung:

- Keine inhaltliche Formatierung.
- Darf zur visuellen Struktur benutzt werden.

### PAGE_MARKER

Seitennummer im Manuskript.

Beispiele:

- `Seite 1`
- `Seite 12`

Erkennung:

- Muster: `Seite <Zahl>`

Formatierung:

- zentriert
- fett
- 14 pt
- Leerzeile oder Abstand davor

### ACT_HEADING

Aktüberschrift.

Beispiele:

- `Erster Akt`
- `Zweiter Akt.`

Erkennung:

- Ordinalzahl plus `Akt`

Formatierung:

- zentriert
- fett
- 18 pt
- Abstand davor und danach

### SCENE_HEADING

Szenenüberschrift.

Beispiele:

- `1. Szene`
- `Zweite Scene.`
- `Dritte Szene.`

Erkennung:

- Zahl plus `Szene`
- ausgeschriebene Ordnungszahl plus `Szene` oder `Scene`

Formatierung:

- zentriert
- fett
- 15 pt
- Abstand davor und danach

### LOCATION

Ortsangabe oder Szenenort.

Beispiele:

- `Saal im Moorischen Schloss.`
- `Schenke an den Grenzen von Sachsen.`
- `Des alten Moors Schlafzimmer.`

Erkennung:

- kurzer Absatz
- endet meist mit Punkt
- enthält typische Ortswörter wie `Saal`, `Zimmer`, `Schloss`, `Wald`, `Schenke`

Formatierung:

- zentriert
- kursiv
- 11 pt

### SPEAKER

Figurenname ohne Replik im selben Absatz.

Beispiele:

- `Franz.`
- `D. a. Moor.`
- `Amalia.`

Erkennung:

- Name ist in der Figurenliste oder Aliasliste bekannt
- endet mit Punkt oder Doppelpunkt
- enthält keine längere Replik nach dem Sprecherzeichen

Formatierung:

- kursiv
- anthrazit
- nicht fett
- Abstand davor zur besseren Lesbarkeit

### SPEAKER_WITH_STAGE

Figurenname mit Regie direkt am Sprecher.

Beispiele:

- `D. a. Moor (begierig).`
- `Franz (liest).`

Erkennung:

- erkannter Figurenname
- Klammerausdruck direkt am Sprecher
- keine längere Replik nach dem Sprecherzeichen

Formatierung:

- Figurenname: kursiv, anthrazit
- Regieanteil: kursiv, grau

### SPEAKER_WITH_REPLIQUE

Figurenname und Replik im selben Absatz.

Beispiele:

- `Franz. Keinen andern, Amalia – ...`
- `AMALIA. Karl!`
- `Franz …hinter der Bühne: Und ich dachte er hätte zwei.`

Erkennung:

- erkannter Figurenname
- nach Punkt oder Doppelpunkt folgt Repliktext

Formatierung:

- Sprecheranteil: kursiv, anthrazit
- Replikanteil: schwarz, normal
- Regieanteile innerhalb der Replik: grau, kursiv

Wichtig:

- Der Replikanteil darf nie komplett grau oder kursiv werden.

### REPLIQUE

Gesprochener Text einer Figur.

Erkennung:

- folgt nach einem Sprecher
- kein eigener Sprecher oder Überschrift

Formatierung:

- schwarz
- normal
- nicht kursiv
- gut lesbarer Zeilenabstand

### STAGE_DIRECTION

Regieanweisung als eigener Absatz.

Beispiele:

- `(Geht traurig ab.)`
- `(Sie gehen ab.)`

Erkennung:

- Absatz besteht überwiegend aus Klammerausdruck

Formatierung:

- grau
- kursiv
- optional eingerückt

### INLINE_STAGE

Regieanweisung innerhalb einer Replik.

Beispiele:

- `... (lacht) ...`
- `... (Zerreißt den Brief.) ...`

Erkennung:

- Klammerausdruck innerhalb eines Replikabsatzes

Formatierung:

- nur der Klammerausdruck wird grau und kursiv
- der restliche Repliktext bleibt schwarz und normal

### UNCLASSIFIED

Nicht eindeutig erkannter Absatz.

Erkennung:

- keine sichere Regel passt

Formatierung:

- keine aggressive Formatierung
- im Bericht als manuell zu prüfen markieren

## Figuren-Aliase

Die Engine führt kanonische Figurennamen. Unterschiedliche Schreibweisen werden zusammengeführt.

Beispiele:

- `Franz`, `FRANZ`, `Franz von Moor` -> `Franz`
- `D. a. Moor`, `der alte Moor` -> `Der alte Moor`
- `Moor`, `Karl v. Moor`, `Karl von Moor` -> `Karl von Moor`
- `Amalia`, `AMALIA` -> `Amalia`

## Schwierige Wörter

Schwierige oder altertümliche Wörter können dezent markiert werden.

Regeln:

- Markierung darf den Text nicht ändern.
- Markierung muss dezent bleiben.
- Die Liste muss versioniert sein.
- Neue Wörter werden nur bewusst ergänzt.


## Internes DocumentModel

Das interne `DocumentModel` ist die stabile Übergabeschicht zwischen DOCX-Einlesung, Klassifikation und späterer Formatierung. Es speichert den sichtbaren Absatztext unverändert und ergänzt ausschließlich Metadaten.

Bestandteile:

- `DocumentModel`: Quelle, sichtbarer Texthash und geordnete Absätze.
- `DocumentParagraph`: Absatzindex, Originaltext, genau eine Klassifikation und verlustfreie Textsegmente.
- `TextSpan`: zusammenhängender Textbereich mit Rolle wie Sprecher, Replik, eigener Regie oder Inline-Regie.

Integritätsregeln:

- Die Verkettung aller `TextSpan.text`-Werte eines Absatzes muss exakt dem Absatztext entsprechen.
- Der aus allen Absatztexten rekonstruierte sichtbare Text muss zum gespeicherten SHA-256 passen.
- Unklare Absätze bleiben als `UNCLASSIFIED` beziehungsweise `needs_manual_review` erhalten und werden nicht geraten.
- Inline-Regie wird nur als Segment markiert; der sichtbare Text wird dabei nicht verändert.


## Style Engine

Die Style Engine trennt Formatierungsregeln vollständig vom Python-Code. Sie lädt YAML-Style-Dateien aus `styles/` und stellt typisierte Style-Objekte für Textsegmente bereit.

Pflichtfelder je vollständigem Style:

- `font_family`
- `font_size`
- `bold`
- `italic`
- `underline`
- `text_color`
- `highlight_color`
- `alignment`
- `left_indent`
- `right_indent`
- `first_line_indent`
- `spacing_before`
- `spacing_after`
- `line_spacing`

Regeln:

- `defaults` muss alle Pflichtfelder enthalten.
- Einzelne Span-Styles dürfen nur Abweichungen definieren und erben fehlende Werte aus `defaults`.
- Farben müssen hexadezimale Werte im Format `#RRGGBB` sein; `highlight_color` darf `null` sein.
- Erlaubte Ausrichtungen sind `left`, `center`, `right` und `justify`.
- Der Formatter darf keine hartcodierten Farben, Schriftgrößen oder Abstände enthalten.
- Die Style Engine verändert niemals sichtbaren Dokumenttext.


## FormattingPlan

Der `FormattingPlan` ist die rendererunabhängige Planungsschicht zwischen `DocumentModel` und späteren Ausgabe-Renderern. Er enthält keine DOCX-Schreiblogik.

Bestandteile:

- `FormattingPlan`: Quelle, sichtbarer Texthash, Style-Name und geordnete Absatzpläne.
- `ParagraphFormattingPlan`: Absatzindex, Absatztyp, Sprecher, Prüffallstatus und Formatierungsläufe.
- `FormattingRun`: Textsegment, `TextSpanType`, Sprecher, Flags und der zugehörige `TextStyle`.

Integritätsregeln:

- Die Verkettung aller `FormattingRun.text`-Werte eines Absatzes muss exakt den Absatztext rekonstruieren.
- Die Verkettung aller Absatzpläne muss denselben sichtbaren Text und denselben SHA-256 wie das `DocumentModel` ergeben.
- Ein Plan darf nur aus einem integren `DocumentModel` gebaut werden.
- Der Plan verändert niemals sichtbaren Dokumenttext und rendert noch keine Word-Formatierung.

## Qualitätsregeln

Ein Engine-Lauf ist nur erfolgreich, wenn:

- der sichtbare Texthash vor und nach der Formatierung identisch ist
- keine Replik komplett grau oder kursiv formatiert wurde
- Seitenmarker einheitlich formatiert sind
- unklare Absätze im Bericht auftauchen
- Tests grün sind

## Nicht-Ziele

Die Engine korrigiert keine Rechtschreibung, keine Grammatik und keine historische Schreibweise.

Auch offensichtliche Textfehler bleiben unverändert, solange der Nutzer keine explizite editorische Korrektur verlangt. Für Theaterproben ist Texttreue wichtiger als hübsche Eigenmächtigkeit.
