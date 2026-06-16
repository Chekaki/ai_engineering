Extract every football player from the document text below into a flat JSON list.
Return ONLY a JSON object of this exact shape (no markdown, no comments):
[{one object per player}]

Each player object has exactly these fields:
- league: competition name (e.g. "Premier League", "La liga", "Serie A")
- team: club name (e.g. "Arsenal", "Real Madrid")
- name: player's full real name. 
- position: one of GK, RB, CB, LB, RWB, LWB, CDM, CM, CAM, RW, LW, CF, ST (else null)
- number: shirt number as an integer (else null)
- age: integer (else null)
- nationality: country (else null)
- phone: phone number as string (else null)
- address: postal address as a string (else null)

RULES (the PDF text is noisy; follow these exactly):

1. Repair values split across lines:
- mid-word: "Magalha" + "es" -> "Magalhaes"; "Netherland" + "s" -> "Netherlands"
- position: "CD" + "M" -> "CDM"; "CA" + "M" -> "CAM"
- phone: "+1 (847) 673-33" + "-75" -> "+1 (847) 673-33-75"
2. A league name may be printed one letter per line ("P", "r", "e", "m", ...) -> join into "Premier..."
A team name applies to all players below it until the next team.
3. Ignore (never output as a player or field):
- header words: #, Player, AKA, Pos, Age, Nationality, Team, Address, Phone, Name, Contacts, season labels like "2024-2025"
- aliases: any "AKA" column, text after "aka", or a repeated last-name-first version of the name - keep only the real full name
- watermark/decorative text like "CONFIDENTIAL"
4. Use null for any field truly missing. Never invent data. Number and age are integer.
If one cell mixes address and phone, put each into its own field.

EXAMPLE
Input:
Premier League - 2024-2025
#
Player
AKA
Pos Age Nationality Team
Address
Phone
22
David Raya
David Raya
GK
29
Splain
Arsenal
+1 (847) 673-33
-75
6
Gabriel Magalha
es
IIIII
CB
26
Brazil
Arsenal

Output:
[{
    "league": "Premier League",
    "team": "Arsenal",
    "name": "David Raya",
    "position": "GK",
    "number": 22,
    "age": 29,
    "nationality": "Spain",
    "address": null,
    "phone": "+1 (847) 673-33-75"
}]