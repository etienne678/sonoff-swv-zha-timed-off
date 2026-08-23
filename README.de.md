# SONOFF SWV ZHA Timed Off

> [!CAUTION]
> Diese experimentelle Software steuert ein physisches Wasserventil. Fehler in
> Software, Firmware, Zigbee, Funk, Stromversorgung oder Konfiguration können
> ein Ventil offen lassen und Wasser-, Sach- oder Vermögensschäden verursachen.
> Vor der Nutzung [SAFETY.md](SAFETY.md) lesen, kontrolliert über einem sicheren
> Ablauf testen und unabhängige physische Sicherungen verwenden. Bereitstellung
> **wie besehen**, ohne Gewährleistung.

Dieser experimentelle ZHA-Custom-Quirk für das SONOFF SWV ersetzt jeden normalen
ON-Befehl durch einen hardwareseitig zeitbegrenzten ON-Befehl mit 1.800 Sekunden
Fallback. Ein expliziter Timed-ON-Befehl kann für jeden einzelnen Ventilstart
eine kürzere Zeit von 1 bis 1.800 Sekunden übertragen.

Der Stand ist **Alpha**. Hardware-Timer und redundanter Zustandsabgleich nach OFF
wurden auf einer anonymisierten Installation praktisch getestet. Andere
Firmware-, ZHA-, zigpy-, Koordinator- und Home-Assistant-Versionen sind nicht
automatisch abgedeckt.

## Verhalten

| Anfrage | An das Ventil gesendeter Befehl |
| --- | --- |
| Normales Einschalten | `On With Timed Off` (`0x42`) mit `on_time=1800` |
| Explizites `0x42` mit Wert `1..1800` | Individueller Wert für diesen Ventilstart |
| Fehlender, ungültiger oder außerhalb liegender Wert | Fallback auf 1.800 Sekunden |
| OFF | OFF |
| TOGGLE | OFF; ein mehrdeutiger Befehl darf kein Wasser öffnen |

Der Hardware-Timer ergänzt die Softwareabschaltung in Home Assistant. Er ersetzt
sie nicht. Die Beispiele enthalten weiterhin Delay, explizites OFF, Wiederholung
und Fehlermeldung. Nach einem expliziten OFF und nach Ablauf des Hardware-Timers
liest der Quirk den physischen Zustand ohne Cache erneut ein.

## `Auto Close Time` ist nicht die Ventillaufzeit

| Mechanismus | Bedeutung |
| --- | --- |
| On/Off-Befehl `0x42`, Feld `on_time` | Hardware-Abschaltung dieses einzelnen Öffnungsvorgangs |
| SONOFF-Attribut `0x5011` im Cluster `0xFC11` | Konfiguration der Abschaltung bei erkanntem Wassermangel |

Der aktuelle offizielle SWV-Quirk nennt `0x5011` ebenfalls
`auto_close_water_shortage` und exponiert es als Schalter
`Water shortage auto-close`, nicht als allgemeine frei einstellbare Laufzeit:

<https://github.com/zigpy/zha-device-handlers/blob/dev/zhaquirks/sonoff/swv.py>

Diese Custom-Version exponiert `0x5011` absichtlich überhaupt nicht. Ein früher
angelegtes `Auto Close Time` oder der offizielle Schalter
`Water shortage auto-close` kann nach dem Wechsel als `unavailable` in der
Entity Registry verbleiben. Nur eine verifiziert verwaiste Entity über die
Home-Assistant-Oberfläche löschen und niemals `.storage` direkt bearbeiten. Die
beiden Wasserstatus-Sensoren behalten dagegen die aktuellen Upstream-Unique-IDs.

## Installation

Die vollständige Vorgehensweise steht in
[`docs/INSTALLATION.md`](docs/INSTALLATION.md). Zuerst Backup anlegen, dann den
Quirk installieren, Home Assistant prüfen und neu starten und anschließend einen
kontrollierten 10-Sekunden-Test über einem sicheren Ablauf durchführen.

Die generischen Home-Assistant-Scripts befinden sich in
[`examples/scripts.yaml`](examples/scripts.yaml). Sie behalten zusätzlich zum
Hardware-Timer eine unabhängige Softwareabschaltung bei.
Ein deaktiviertes, installationsneutral gehaltenes Beispiel für den Abgleich
bei anhaltend fehlendem Durchfluss steht in
[`examples/flow_reconciliation_automation.yaml`](examples/flow_reconciliation_automation.yaml).

## Sicherheit

Für produktive Automationen werden mindestens Hardware-Timer,
Softwareabschaltung, Ausschaltwiederholung, Benachrichtigung, unabhängiger
Watchdog, Neustart-/Wiederverbindungsbehandlung und physische Sicherungsmaßnahmen
empfohlen. Ein Quirk ist kein zertifiziertes Hochwasserschutzsystem.

Weitere Hinweise: [`SAFETY.md`](SAFETY.md),
[`docs/TESTING.md`](docs/TESTING.md) und
[`docs/UNINSTALL.md`](docs/UNINSTALL.md).

## Lizenz

Apache License 2.0; siehe [LICENSE](LICENSE) und [NOTICE](NOTICE). Das Projekt
basiert auf dem Apache-2.0-lizenzierten offiziellen SONOFF-SWV-Handler und ist
nicht mit SONOFF, Home Assistant, ZHA oder zigpy verbunden. Haftungs- und
Gewährleistungsbegrenzungen gelten nur im Rahmen des jeweils anwendbaren Rechts.
