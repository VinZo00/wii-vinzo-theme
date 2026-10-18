---
name: wii-theme-vinzo
description: Modificare, ricostruire e installare il tema Wii "Material Dark – Mod by VinZo" (menu di sistema 4.3E, file .csm). Usare per qualsiasi richiesta su colori, sfondo, pulsanti, orologio, firma, nuove schermate del tema, oppure per analizzare archivi .ash/.arc/TPL/BRLYT del menu Wii.
---

# Tema Wii VinZo — guida operativa

Leggi anche `docs/CONVERSAZIONE.md` per la storia e le decisioni prese.

## Contesto fisso

- Console: Wii PAL, **System Menu 4.3E** (v514, file base `0000009a-v514.app`).
- Protezioni installate: **Priiloader** (RESET all'accensione), **BootMii come IOS** (no boot2),
  backup NAND verificato in `Documents\Wii\Wii_NAND_Backup_2026-10-18`.
- SD/USB sul PC = unità **D:**. Temi in `D:\themes\`, app in `D:\apps\` (csm-installer, usbloader_gx,
  Nintendont, priiloader, hackmii_installer, HBCtheme_Material_Dark).
- Installazione: Homebrew Channel → csm-installer → seleziona `.csm` → A → +.
- Tema di riferimento **funzionante** sulla console: `D:\themes\azurenight.csm` (usalo come
  confronto con `tools/compare_theme.py` e come ripiego in caso di problemi).
- L'utente parla **italiano**: rispondi sempre in italiano.

## Pipeline di build

`.\build.ps1` (da questa cartella):
1. `tools/extract_base.py` estrae il base app (archivio U8).
2. `ASH.exe` (ThemeMii, `Documents\Wii\ThemeMii`) decomprime `layout/common/*.ash` → `work/arc/*.ash.arc`.
3. `tools/build_vinzo.py` modifica materiali, UV e texture, ricomprime in **LZ77** (header `LZ77`+0x10,
   come ThemeMii/azurenight) e reinserisce gli archivi nel base → `.csm`.
4. `tools/verify_csm.py` ricarica tutto (TPL, BRLYT, BRLAN) e confronta la struttura col base.

Python: venv in `.venv` (pillow, numpy). Esegui sempre con `python -I`.

## Mappa del menu (scoperta analizzando i file)

- `chanSel.ash` → schermata principale.
  - `my_IplTop_a.brlyt`: `BaseMask0-4` (sfondo pieno 512x288, TEV `lerp(C0,C1,TEXC)`),
    `Picture_00-04` (stesso sfondo con maschera slot, stage1 `lerp(C0,C1,TEXC)` su texcoord 1),
    `Picture_05-09` e `board0-4` (barra inferiore), `Line*` (linea viola), `Edge*` (bordo barra),
    `Shade*` (ombra). Tutti usavano `my_TVSheet_b` (righe 608x8 ripetute 36 volte).
  - Lo **sfondo** = `my_TVSheet_b` sostituita col wallpaper + UV impostate a 0..1. Per i pannelli
    della barra si mette `c1 == c2` così il colore è costante e ignora la texture.
  - `my_Clock_a.brlyt`: cifre `my_Clock_a0..a9`, due punti `my_Clock_ab` (I4 48x48).
  - `my_IplTop_b.brlyt` `Ch0` = slot vuoti; `my_IplTop_d` `Cursur_a` = evidenziazione slot.
  - Attenzione: anche `my_TVMask_a.brlyt` ha un materiale `Picture_00` — non confonderlo.
- `cmnBtn.ash` → pulsanti in basso: `my_TopBtn_c`/`_b` (Wii), `_a` (posta; l'icona busta è
  `my_TopBtn_a0` sopra, materiale `BbsMark0`), `_d` calendario, `_e` nuovo messaggio,
  `my_ComBtn_a/_b` (+/−), `my_arw_a/_b` frecce pagina.
- `board.ash` → bacheca messaggi (`my_BackPic_a` è il suo sfondo, NON quello del menu).
- `chanTtl.ash` → schermata di anteprima del canale (pulsanti `BtnA*`/`BtnB*`, barra `Base0`).
- `cursor.ash` → cursori; `P1_Cat`/`P1_Def` colore giocatore 1 (non toccare le ombre `*S`).

Colori dei materiali BRLYT: `c1`/`c2`/`c3` a offset 0x14/0x1C/0x24 dal materiale (4×s16).
Con un solo texture e nessuno stage TEV custom il risultato è `lerp(c1, c2, texture)`.
Usa `tools/dump_tev.py` per vedere gli stage quando ci sono.

## Lezioni imparate dai test sulla TV

- **Texture con wrap REPEAT devono avere dimensioni potenza di 2** (GX). Una 512x288 ripetuta
  ha dato sfondo a strisce e slot bianchi (v2). Usa 512x256/512x512 e/o wrap clamp (0).
- **Quale set UV usa un pannello lo decide il TexCoordGen** del materiale (src 4 = TEX0,
  5 = TEX1), non l'ordine delle texture: `BaseMask*` e `Picture_0x` usano UV1 per lo sfondo.
- **Le animazioni RLMC sovrascrivono i colori dei materiali** (es. pulsante "Avvia" in
  `chanTtl`, target 4-6 = c1, 8-10 = c2). `build_vinzo.py` applica la stessa regola ai colori
  animati (`patch_anim_colors`); controlla sempre con `tools/dump_anim.py`.
- Nelle animazioni un canale può avere **una sola chiave** costante (es. G=190 in On/OffBtn):
  gli stati che si alternano devono avere lo stesso valore su quel canale, altrimenti escono colori
  misti (bordo lilla chiaro di "Avvia").
- `my_BackPic_a` (board.ash) è anche lo **sfondo della barra inferiore** nel menu principale (si vede
  sotto la curva): è lì che azurenight mette la sua foto. Modello: `assets/modello_barra_1920x1080.png`,
  immagine utente: `assets/barra.png`. Sfondo del menu: `FLAT_BG` in `build_vinzo.py`.
- `board.ash/my_BackPic_a` è lo sfondo della bacheca (UV 0..38 ripetute: va portato a 0..1).
- **Sfondo del menu = una copia per pagina, affiancate.** Sullo schermo 16:9 si vede ~9% finale
  dell'immagine sia a sinistra (pagina precedente) sia a destra: l'immagine deve essere continua
  tra i bordi e la firma va nell'ultimo 8% in alto. La griglia copre il resto: conta la luce
  nei margini e negli spazi tra le schede. Controlla con `tools/simulate_menu.py`.

- **Limite di memoria di `board.ash`:** 1.212.416 byte decompressi (v4/v7) funziona; 1.343.488 (v6,
  barra 1024x512 CMPR) → **schermo nero dopo la schermata avvertenze**. Tieni `my_BackPic_a` a
  512x512 CMPR o meno. Gli altri archivi hanno margini diversi: aumenta per piccoli passi.

## Regole di sicurezza (importanti)

- Non superare di molto gli aumenti di memoria di azurenight per archivio (riferimento:
  board +104 KB, chanSel +49 KB, ma sdButton +540 KB ha funzionato). Preferisci CMPR (4 bpp)
  o RGB565 per immagini grandi; RGB5A3 solo se serve trasparenza.
- Cambiare formato/dimensioni di una TPL è sicuro (azurenight lo fa), ma mantieni lo stesso
  file e lo stesso nome; non aggiungere né rimuovere file dagli archivi.
- Non modificare la lunghezza di BRLYT/BRLAN: solo patch di valori in place.
- Dopo ogni build esegui `verify_csm.py` e mostra all'utente le anteprime prima di installare.
- Ricorda sempre all'utente il ripristino: RESET → Priiloader → Homebrew Channel →
  csm-installer → `azurenight.csm` o `original_backup`.
- `base/` e `*.csm` contengono dati Nintendo: mai nel repository Git.

## Palette attuale

Accento `#E040FB` (224,64,251), accento scuro (150,40,170), barra (20,15,26)/(28,21,36),
schede (36,28,42), bianco (240,240,245), testo secondario (200,190,210).
Tutte definite in cima a `tools/build_vinzo.py`.

## Idee non ancora fatte

- Temi coordinati per dialoghi, impostazioni (`setupBtn`, `setupSel`, `dlgWdw`), menu SD
  (`sdChanSel`, `sdChanTtl`), schermata di avvio (`health.ash`).
- Esportare il tema anche come `.mym` (solo differenze) per condividerlo senza dati Nintendo.
- Tema coordinato per USB Loader GX (PNG + `.them`).
