# Audit `#A99 tools.tab` (deep-audit-core + docs-text-review)

Datum: 2026-03-23
Scope: kriticke skripty z planu (bez zasahu do vendor/externich knihoven)

## Prioritizovane nalezy (P1/P2/P3)

### P1 - Rizika se stabilitou, transakcemi a chovanim

1) `Python extension.extension/#A99 tools.tab/In development.panel/Change material.pushbutton/script.py`
- Problem: `Transaction` se startuje pred interakci s uzivatelem (`PickObject`, vyber parametru/materialu) a v `finally` se bezpodminecne `Commit()`.
- Dopad: i pri stornu/validacni chybe probehne commit prazdne transakce; navic je dlouho otevrena transakce behem UI flow.
- Doporuceni:
  - Presunout `Transaction.Start()` az po uspesnem ziskani vsech vstupu.
  - Pri chybe delat `RollBack()` (ne commit v `finally`).
  - Rozlisit `OperationCanceledException` (cancel) vs. skutecna chyba.
- Ocekavany prinos: predvidatelne transakcni chovani, mene side-effectu, lepsi UX.

2) `Python extension.extension/#A99 tools.tab/In development.panel/Rooms to floors.pushbutton/script.py`
- Problem: `create_floors(...)` predava `selected_floor_type_id`, ale `room_to_floor(...)` vola `Floor.Create(..., floor_type.Id, ...)`.
- Dopad: runtime chyba (`ElementId` nema `.Id`) skryta sirokym `except`, vysledkem tichy fail bez floor vystupu.
- Doporuceni:
  - Sjednotit kontrakt: predavat bud `FloorType`, nebo vsude `ElementId`; idealne typove konzistentne.
  - Odstranit tiche polykani vyjimek (`except: pass`) a logovat room `Id` + detail chyby.
- Ocekavany prinos: obnoveni funkcnosti tvorby podlah + jednodussi diagnostika.

3) `Python extension.extension/#A99 tools.tab/In development.panel/Rooms to floors.pushbutton/script.py`
- Problem: v `room_to_floor` se uvnitr kazde iterace otevira samostatna `Transaction`, i kdyz uz existuje `TransactionGroup`; warning swallower maze vsechny warningy bez filtru.
- Dopad: vysoka transakcni rezie, hure laditelne chovani, mozna ztrata dulezitych warningu.
- Doporuceni:
  - Jedna `Transaction` pro celou davku (nebo male chunky), ne per-room.
  - Failure preprocessor filtrovat jen zname benign warningy.
- Ocekavany prinos: vyssi vykon, lepsi kontrola chyb.

4) `Python extension.extension/#A99 tools.tab/In development.panel/Join elements.pushbutton/Join elements_script.py`
- Problem: pristup k `elem.BoundingBox[uidoc.ActiveView]` bez guardu; siroke `except` pri join operaci bez reportu.
- Dopad: `None` bounding box u casti prvku muze skoncit chybou; chyby joinu se ztraceji.
- Doporuceni:
  - Osetrit `None` bounding box pred konstrukci `Outline`.
  - Logovat pocet failu + duvod (alespon agregovane).
- Ocekavany prinos: mensi riziko padu, transparentni vysledek skriptu.

### P2 - Vykon, robustnost, maintainability

1) `.../Join elements_script.py`
- Problem: uvnitr smycky nad kazdym prvkem bezi novy `FilteredElementCollector(...).WherePasses(bbFilter).ToElements()`.
- Dopad: O(N^2) pattern + opakovane collectory, velky dopad na vykon u vetsich modelu.
- Doporuceni:
  - Predkolektovat kandidaty jednou na kategorii/pohled a delat vlastni prostorovy filtr.
  - Omezit testovane dvojice (napr. jen `elem.Id < other_elem.Id`) pro eliminaci duplicit.
- Ocekavany prinos: znatelne kratsi doba behu.

2) `.../Hide pointcloud.pushbutton/script.py`
- Problem: helpery jsou robustni, ale obsahuje hodne fallback vetvi s polykanym `except`; cast logiky je redundantni.
- Dopad: slozitejsi udrzba, horsi predikovatelnost pri edge-casech.
- Doporuceni:
  - Zjednodusit flow: jasne oddelit "detekce stavu" -> "akce" -> "verifikace".
  - Omezit broad `except` na konkretni API volani, zbytek nechat failnout s uzivatelskou hlaskou.
- Ocekavany prinos: lepsi citelnost, snazsi debug.

3) `.../Room Code.pushbutton/script.py` + `.../Test B.pushbutton/script.py`
- Problem: skript v `Test B` je obsahove totozny s produkcnim `Room Code` (duplicitni logika).
- Dopad: vysoky maintenance overhead, riziko divergence oprav.
- Doporuceni:
  - Vytahnout sdilenou logiku do spolecneho modulu v ramci extension a volat ji z obou vstupnich skriptu.
  - Nebo `Test B` jasne oznacit jako experimental a oddelit od produkce.
- Ocekavany prinos: jednotne opravy, mensi riziko regresi.

4) `.../Room Code.pushbutton/script.py`
- Problem: transakce je otevrena i behem celeho cteni/validace vsech rooms.
- Dopad: zbytecne dlouha otevrena transakce.
- Doporuceni:
  - Nechat predzpracovani mimo transakci a zapis delat v uzsi casti.
- Ocekavany prinos: mensi zamykani dokumentu, lepsi odezva.

### P3 - Komentare, texty, naming (docs-text-review)

1) Jazykova nekonzistence (CZ/EN mix)
- Stav: `__doc__` casto anglicky, `forms.alert` casto cesky; nekde i naming mix.
- Doporuceni: zvolit jednotny standard:
  - Uzivatelske hlasky: CZ.
  - Technicke komentare/docstringy: EN (nebo CZ), ale konzistentne napric skriptem.

2) Nekonzistentni naming promennych
- Priklady:
  - `types_ids` vs. beznejsi `type_ids`.
  - `List_curve_loop` (PascalCase) mezi snake_case.
  - `selected_floor_type_id` realne pouzivan jako "floor type object" v jine casti kodu.
- Doporuceni: striktni `snake_case`, id promenne koncit `_id`, objekty bez `_id`.

3) Komentare neodpovidaji realnemu chovani nebo jsou prehnane verbose
- Priklad: `Hide pointcloud` ma mnoho komentaru vysvetlujicich fallbacky, ktere jsou zcasti duplicitni k implementaci.
- Doporuceni: ponechat jen komentare popisujici "proc", ne "co" (to ma byt patrne z kodu).

4) Metadata bloky v hlavicce
- Stav: ruzne formaty (`Version`, `Date`, `How-to`, `To-Do`), casto neaktualni.
- Doporuceni: jednotna sablona hlavicky:
  - `__title__`, `__author__`, `__version__`, kratky `__doc__` (ucel + vstupy + vystupy + omezeni).
  - odstranit prazdne sekce typu `To-Do: -`.

## Konkretni navrh sjednoceni (minimum standard)

1) Error handling
- Zakaz `except: pass` bez logu.
- Povolit broad `except Exception as ex` pouze:
  - na hranici skriptu (top-level),
  - nebo kolem API callu s explicitnim kontextem.
- Vzdy logovat:
  - co selhalo,
  - element `Id` (pokud existuje),
  - dopad (skip/rollback/abort).

2) Transaction pattern
- Nikdy nedrzet transakci behem user input (`PickObject`, dialogy).
- Pattern:
  - Gather inputs (no transaction)
  - Validate inputs (no transaction)
  - Start transaction
  - Apply changes
  - Commit
  - On error: rollback + user-facing message

3) Texty a UX hlasky
- Uzivatelske texty pouze CZ, technicky presne, bez stack trace.
- Detailni chyba do logu/output (pokud relevantni), ne do kratke alert hlasky.

4) Naming
- `snake_case` vsude.
- `_id` jen pro `ElementId`, `_ids` pro kolekci `ElementId`.
- Nazev funkce ve tvaru sloveso + objekt (`collect_rooms`, `build_room_code`, `apply_material_to_types`).

## Quick wins (nizke naklady, vysoky prinos)

1) `Change material`: presun startu transakce az po vyberech + rollback pri chybe.
2) `Rooms to floors`: opravit nesoulad `FloorType` vs `ElementId`, odstranit tiche `except`.
3) `Join elements`: pridat guard na `BoundingBox` a agregovany report failu.
4) `Room Code`/`Test B`: odstranit duplicitu (shared modul nebo jasne oddeleni test/prod).

## Poznamka ke scope

- Audit i doporuceni jsou zamerne bez prime editace vendor/externich knihoven.
