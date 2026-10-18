---
name: wii-theme-vinzo
description: Modificare, ricostruire e installare il tema Wii "Material Dark – Mod by VinZo" (menu di sistema 4.3E, file .csm). Usare per qualsiasi richiesta su colori, sfondo, barra inferiore, pulsanti, orologio, firma, nuove schermate del tema, ripristino della console, oppure per analizzare archivi .ash/.arc/TPL/BRLYT/BRLAN del menu Wii.
---

# Tema Wii VinZo — guida operativa

Questo è **il tema su cui lavoriamo** (deciso dall'utente il 18/10/2026). Storia completa e
decisioni: `docs/CONVERSAZIONE.md`. Rispondi sempre in **italiano**.

## Stato attuale

- **Versione stabile: v7**, installata e confermata funzionante sulla TV ("è perfetto adesso").
  Commit/tag git `v7`. File: `build/vinzo_material_dark_v7_4.3E.csm` (copia sicura:
  `build/vinzo_material_dark_STABILE_4.3E.csm`) e `D:\themes\vinzo_material_dark_v7_4.3E.csm`.
- Contenuto v7:
  - Menu principale: sfondo **tinta piatta** `FLAT_BG = (16,12,22)`.
  - Barra inferiore + bacheca: immagine dell'utente `assets/barra.jpg` (1920x1080, onde viola in
    basso, "mod by VinZo" centrato in basso) → `my_BackPic_a` **512x512 CMPR**.
  - Barra scura con curva/linea viola, orologio sottile (Segoe UI Light), pulsanti circolari
    Wii/posta/calendario/matita/+/−, frecce viola, cursore P1 viola.
  - Schermata del canale: pulsanti "Menu Wii"/"Avvia" scuri con bordo viola, anche dopo il cambio
    canale (animazioni corrette).
- Ogni nuova modifica = **nuova versione numerata** (v8, v9…); non sovrascrivere la stabile finché
  l'utente non conferma sulla TV.

## Contesto fisso della console

- Wii PAL, **System Menu 4.3E** (v514, base `base/0000009a-v514.app`, anche in
  `D:\themes\original_backup\`).
- Protezioni: **Priiloader** installato nella NAND (Block Disc/Online Updates), **BootMii come IOS**
  (no boot2), backup NAND verificato in `Documents\Wii\Wii_NAND_Backup_2026-10-18`.
- Unità **D:** = SD/USB della Wii quando è collegata al PC (spesso è nella Wii: controlla con
  `Test-Path D:\` prima di copiare). `D:\themes\` contiene `azurenight.csm` (ripiego sicuro),
  `azurenight.mym`, `original_backup\`, la versione corrente. `D:\apps\`: csm-installer,
  usbloader_gx (tema azurenight in `theme\`), Nintendont.
- Installazione: Homebrew Channel → csm-installer → seleziona `.csm` → A → +.

## Ripristino (da ricordare sempre all'utente prima di un test)

Se dopo l'installazione il menu non parte (schermo nero, blocco):
1. Wii spenta (se bloccata: POWER sulla console tenuto ~5 s).
2. **Tieni premuto RESET**, poi premi POWER, e continua a tenere RESET ~5 s → menu Priiloader.
3. Wiimote (frecce, A) o controller GameCube → **Homebrew Channel** → csm-installer →
   `azurenight.csm` o il `.csm` stabile → A → +.
Spiegalo passo passo: l'utente ha avuto dubbi sull'ordine RESET/POWER.

## Pipeline di build

`.\build.ps1 -Out "$PWD\build\vinzo_material_dark_vN_4.3E.csm"` (da questa cartella):
1. `tools/extract_base.py` estrae il base app (archivio U8).
2. `ASH.exe` (ThemeMii, `Documents\Wii\ThemeMii`) decomprime `layout/common/*.ash` → `work/arc/*.ash.arc`.
3. `tools/build_vinzo.py` modifica materiali, UV, wrap, colori animati e texture, ricomprime in
   **LZ77** (header `LZ77`+0x10, come ThemeMii/azurenight) e reinserisce gli archivi → `.csm`.
4. `tools/verify_csm.py` ricarica tutto (TPL, BRLYT, BRLAN) e confronta la struttura col base.

Controlla nel log le dimensioni decompresse di ogni archivio (vedi limiti sotto).
Python: venv `.venv` (pillow, numpy), sempre `python -I`.
Anteprime/strumenti: `work/preview/`, `tools/simulate_menu.py`, `tools/dump_layout.py`,
`tools/dump_tev.py`, `tools/dump_anim.py`, `tools/inspect_tex_mapping.py`, `tools/compare_theme.py`.
Modello per l'immagine della barra: `assets/modello_barra_1920x1080.png` (`tools/make_bar_template.py`).

## Dove si cambia cosa (`tools/build_vinzo.py`)

- Palette in cima: `ACCENT (224,64,251)`, `ACCENT_DARK (150,40,170)`, `ACCENT_OFF (110,64,120)`,
  `BAR (20,15,26)/(28,21,36)`, `SLOT`, `CARD (36,28,42)`, `WHITE (240,240,245)`, `MUTED (200,190,210)`.
- `FLAT_BG`: colore dello sfondo del menu (mettere `None` per tornare all'immagine `menu_bg_tex`).
- `BAR_IMAGE` (`assets/barra.jpg`) e `BAR_TEX (512,512)`: immagine della barra/bacheca.
- Regole per archivio: `chansel_rule`, `cmnbtn_rule`, `board_rule`, `cursor_rule`, `chanttl_rule`;
  texture: `chansel_tex` (cifre orologio), `cmnbtn_tex` (pulsanti), `board_tex`; layout: `*_lyt`.

## Mappa del menu

- `chanSel.ash` → schermata principale.
  - `my_IplTop_a.brlyt`: `BaseMask0-4` (sfondo pieno per pagina) e `Picture_00-04` (sfondo con
    maschera slot), `Picture_05-09`/`board0-4` (barra), `Line*` (linea viola), `Edge*` (bordo barra),
    `Shade*` (ombra). Tutti usano `my_TVSheet_b` (righe 608x8). Con `c1 == c2` il colore è piatto.
  - `my_Clock_a.brlyt`: cifre `my_Clock_a0..a9`, due punti `my_Clock_ab` (I4 48x48).
  - `my_IplTop_b` `Ch0` = slot vuoti; `my_IplTop_d` `Cursur_a` = evidenziazione slot.
  - Anche `my_TVMask_a.brlyt` ha un materiale `Picture_00`: non confonderlo.
- `board.ash` → `my_IplTop_c.brlyt` `TopBack_a/b/c` con `my_BackPic_a`: **sfondo della barra
  inferiore del menu (visibile sotto la curva) e sfondo intero della bacheca**. Data = `T_Day_*`.
- `cmnBtn.ash` → pulsanti: `my_TopBtn_c`/`_b` (Wii), `_a` (posta; busta `my_TopBtn_a0`, materiale
  `BbsMark0`), `_d` calendario, `_e` nuovo messaggio, `my_ComBtn_a/_b` (+/−), `my_arw_a/_b` frecce.
- `chanTtl.ash` → schermata del canale: `BtnA*`/`BtnB*` (pillole), `*_Shade` (bordo), `*_Ac`
  (evidenziazione), `T_BtnA/B` (testo), `Base0` (barra).
- `cursor.ash` → `P1_Cat`/`P1_Def` colore giocatore 1 (non le ombre `*S`).

BRLYT: colori materiale `c1`/`c2`/`c3` a offset 0x14/0x1C/0x24 (4×s16); senza stage TEV custom il
risultato è `lerp(c1, c2, texture)`. TexCoordGen src 4 = UV0, 5 = UV1.

## Lezioni imparate dai test sulla TV (non ripetere questi errori)

- **Limite di memoria di `board.ash`: 1.212.416 byte decompressi funziona (v4, v7); 1.343.488 (v6,
  barra 1024x512) → SCHERMO NERO** dopo la schermata avvertenze. Tieni `my_BackPic_a` ≤ 512x512
  CMPR. Per gli altri archivi aumenta per piccoli passi e annota qui ogni limite trovato.
- Texture con wrap REPEAT → dimensioni **potenza di 2** (512x288 ripetuta = strisce, v2).
- Il set UV di un pannello lo decide il TexCoordGen, non l'ordine delle texture.
- `my_BackPic_a` aveva UV 0..38 ripetute: portate a 0..1 con wrap clamp.
- Le animazioni RLMC (target 4-6 = c1, 8-10 = c2) sovrascrivono i colori: `patch_anim_colors`
  applica le stesse regole. Un canale con **una sola chiave** resta fisso per tutta l'animazione:
  gli stati alternati devono avere lo stesso valore su quel canale (bordo "Avvia" lilla, v4/v5).
- Lo sfondo del menu è una copia per pagina, affiancate: un'immagine lì si vede solo ai margini e
  tra le schede, con cuciture. L'utente ha preferito la **tinta piatta**.
- Un "glitch" visto una volta dopo un riavvio era l'HDMI, non il tema.

## Regole di sicurezza

- Cambiare formato/dimensioni di una TPL è ok; non aggiungere/rimuovere file dagli archivi; non
  cambiare la lunghezza di BRLYT/BRLAN (solo patch in place).
- Dopo ogni build: `verify_csm.py`, anteprime all'utente, poi copia su `D:\themes` (togliendo le
  versioni di prova vecchie, mai `azurenight.csm` né `original_backup`).
- `base/` e `*.csm` contengono dati Nintendo: mai nel repository Git.
- Dopo ogni test confermato: aggiorna questa skill, `docs/CONVERSAZIONE.md`, commit + push.

## Idee non ancora fatte

- Temi coordinati per impostazioni (`setupBtn`, `setupSel`), dialoghi (`dlgWdw`), menu SD
  (`sdChanSel`, `sdChanTtl`), schermata di avvio (`health.ash`).
- Esportare anche come `.mym` (solo differenze) per condividerlo senza dati Nintendo.
- Tema coordinato per USB Loader GX (PNG + `.them`).
