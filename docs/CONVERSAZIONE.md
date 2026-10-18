# Riassunto della conversazione (18/10/2026)

Riassunto compatto di come è stata preparata la Wii e di come è nato il tema VinZo.

## 1. Situazione iniziale

- SD/USB su **D:** con Homebrew Channel già installato (HackMii v1.2 il 07/10/2025), USB Loader GX,
  Nintendont. Log `D:\installer.log`: BootMii installabile **solo come IOS**.
- Scaricato `azurenight_themepack.zip` (tema USB Loader GX + `.mym` per il menu Wii).

## 2. Tema USB Loader GX

- Copiati `azurenight.them` + cartella `azurenight` in `D:\apps\usbloader_gx\theme\`
  (percorso da `GXGlobal.cfg`: `theme_path = sd:/apps/usbloader_gx/theme/`).
- Attivazione: USB Loader GX → Impostazioni → Tema.

## 3. Preparazione per i temi del menu Wii

1. Versione verificata: **4.3E**.
2. **csm-installer 1.5** (OSCWii) in `D:\apps\csm-installer\`; scaricato il menu originale →
   `D:\themes\original_backup\0000009a-v514.app` (v514 = 4.3E).
3. csm-installer chiedeva Priiloader → installato **Priiloader 0.10.0** (+ Block Disc/Online Updates).
4. **BootMii come IOS** installato tramite HackMii Installer copiato in `D:\apps\hackmii_installer\`;
   "Prepare an SD card" fatto.
5. **Backup NAND** con BootMii (alcuni bad block, normale), verificato (553.649.152 byte, keys
   coincidenti) e copiato in `Documents\Wii\Wii_NAND_Backup_2026-10-18`.
6. ThemeMii MOD (da wii.hacks.guide) usato per convertire `azurenight.mym` → `azurenight.csm`
   (servito .NET 3.5). **azurenight installato e funzionante.**

## 4. Extra

- Tema HBC **Material Dark v1.4** copiato in `D:\apps\HBCtheme_Material_Dark\` (si installa
  aprendolo dall'Homebrew Channel). Influisce solo sull'HBC.
- Spiegati: forwarder/canali (YAWM ModMii Edition), aggiornamento HBC (già 1.1.2), cartelle
  eliminabili (hackmii_installer, priiloader, Material Dark dopo l'installazione, nand.bin su D:).
- Raccolte temi: Wii Theme Team Creations (GBAtemp), Google Drive dei temi, GBAtemp Other Files.

## 5. Tema "Material Dark – Mod by VinZo"

- Mockup approvato: sfondo = `Pictures\background.jpg` (viola fluido), schede scure, barra
  scura con linea viola, orologio sottile, pulsanti circolari con anello viola, firma "Mod by VinZo".
- Scritti strumenti propri (U8, TPL codec incl. CMPR, BRLYT, BRLAN, LZ77) e analizzato il menu.
  azurenight usato come riferimento sicuro (quali file/formati cambiare, limiti di memoria).
- **v1**: sfondo messo per errore in `board.ash` (`my_BackPic_a` = bacheca messaggi) → sullo
  schermo principale non si vedevano né sfondo né firma; schermata del canale non tematizzata.
  Un "glitch" visto dopo un riavvio era dovuto all'HDMI, non al tema.
- **v2** (attuale): sfondo e firma su `chanSel.ash/my_TVSheet_b` con UV corrette; tematizzata la
  schermata del canale (`chanTtl.ash`). File: `D:\themes\vinzo_material_dark_v2_4.3E.csm`.
- Test v2 (foto in Download, 18/10 02:40): sfondo a strisce e slot bianchi nel menu, bacheca con
  sfondo ripetuto a strisce verticali, pulsante "Avvia" ancora bianco. Cause: texture 512x288 non
  potenza di 2 usata con wrap REPEAT, set UV sbagliato su `BaseMask`, UV 0..38 nella bacheca,
  colori dei pulsanti reimpostati dalle animazioni RLMC.
- **v3**: texture 512x256 (menu) e 512x512 CMPR (bacheca) con wrap clamp e UV 0..1, colori animati
  corretti.
- Test v3: sfondo disegnato bene, ma ogni pagina ha la sua copia affiancata → a sinistra si vede la
  fine dell'immagine della pagina precedente ("VinZo" tagliato) e la griglia copre quasi tutto.
- **v4**: sfondo dedicato (`menu_bg_tex`) continuo tra bordo destro e sinistro, onde più luminose,
  firma su due righe nell'ultimo 8% a destra, in alto (si vede intera in entrambi gli angoli).
  Simulazione: `preview/simulazione_menu.png` (`tools/simulate_menu.py`, geometria dalle foto).
  File: `D:\themes\vinzo_material_dark_v4_4.3E.csm`.
- Test v4: "va meglio" ma l'effetto non piace. Decisione: **sfondo menu a tinta piatta** (16,12,22) e
  immagine personalizzata per la barra inferiore (`my_BackPic_a`, la stessa tecnica di azurenight, che
  usa una foto notturna 544x408). L'utente la crea 1920x1080 seguendo `assets/modello_barra_1920x1080.png`
  e la salva come `assets/barra.png` (la build la usa se esiste). Azurenight sconsigliato come base
  (azzurro, bassa risoluzione, non nostro).
- Bug: dopo il cambio canale il bordo di "Avvia" diventava lilla chiaro. Causa: animazione On/OffBtn
  grigio→blu con canale G a chiave singola (190). Fix: stato spento = (110,64,120), stesso G dell'accento.
- **v5**: tinta piatta + fix pulsanti. File: `D:\themes\vinzo_material_dark_v5_4.3E.csm`.
- **v6**: immagine della barra creata dall'utente (`assets/barra.jpg`, onde viola in basso + "mod by VinZo"
  centrato), texture 1024x512 CMPR (firma leggibile, board +248 KB). File:
  `D:\themes\vinzo_material_dark_v6_4.3E.csm`.
- Test v6: **schermo nero** dopo la schermata avvertenze. Causa più probabile: board.ash troppo grande
  (1.34 MB contro 1.21 MB della v4 funzionante). Ripristino: RESET → Priiloader → HBC → csm-installer.
- **v7**: barra 512x512 CMPR (stessa dimensione della v4). Firma più morbida: meglio ingrandirla nell'immagine.
- Ripristino dallo schermo nero riuscito con Priiloader (tenere RESET prima di accendere, Wiimote ok).
- **v7 installata: "è perfetto adesso".** Diventa la versione stabile (tag git `v7`); d'ora in poi si
  lavora su questo tema, con nuove versioni numerate a partire dalla v8.
- **v8**: nuova immagine della barra dell'utente (`modello_barra_new.jpg` → `assets/barra.jpg`, onde
  viola solo in basso; la vecchia è `assets/barra_v7.jpg`). board.ash identico alla v7 (1.212.416 byte).
  Su D: ci sono sia la v7 (stabile) sia la v8 (da provare).

## 7. Temi coordinati per Homebrew Channel e USB Loader GX

- Richiesta: temi simili a VinZo per USB Loader GX e per la lista dell'Homebrew Channel.
- HBC: tema disegnato da zero (`tools/hbc_theme.py`), schede scure, selezione con bordo/barra viola,
  frecce circolari, pulsanti a pillola, sfondo = immagine della barra. App `HBCtheme_VinZo`.
- GX: ricolorazione automatica di azurenight (`tools/gx_theme.py`), 36 pannelli scuriti, 90 icone
  ricolorate, 55 immagini lasciate com'erano, `.them` convertito (msgid + msgstr).
- Comando unico: `.\build_extras.ps1`. Copiati su D: (accanto a azurenight e a Material Dark).
- Ritorno all'aspetto originale dell'HBC: solo cancellando i dati di salvataggio dell'HBC da
  Gestione dati (hackmii.com, 2010); tra temi si passa aprendo l'app del tema.

- Test GX v1 (foto 11:02/11:03): testi neri, griglia con riquadri bianchi, pulsanti troppo grossi.
  Causa: nel `.them` avevo cambiato i `msgid`, che sono le chiavi → il loader usava i predefiniti.
- **GX v2**: base = tema predefinito ufficiale di USB Loader GX (scelta dell'utente al posto di azurenight),
  colori solo nei `msgstr`, pulsanti ridisegnati più piccoli, nessun font personalizzato. Su D:.

- Test GX v2 (foto 11:14): pannelli scuri ma testi neri illeggibili, disposizione diversa dal
  predefinito. Cause: (1) l'archivio master di GitHub è un ramo vecchio, la versione installata è
  4.0 r1283 con immagini/posizioni diverse; (2) molti testi del loader sono neri nel codice.
  Richiesta dell'utente: "parti dal predefinito e applica i colori e gli sfondi".
- **GX v3**: predefinito r1283 + azzurri → viola + sfondo predefinito ricolorato (foglio scuro, barra
  scura con le onde e "mod by VinZo", linea viola) + orologio bianco. Pannelli chiari invariati. Su D:.

## 9. Altre app installate su D: (18/10/2026)

- **ftpsrv 1.2.2** (ITotalJustice, GitHub, `wii.zip`) → `D:\apps\ftpsrv` + `D:\config\ftpsrv\config.ini`
  (utente `vinzo`, password solo sulla SD, NON nel repo; porta 21).
- **Homebrew Browser 0.3.9e** = app dell'Open Shop Channel → `D:\apps\homebrew_browser` (alternativa
  se instabile: LibreShop).
- **WiiXplorer** e **SaveGame Manager GX** (da Open Shop Channel) → `D:\apps\wiixplorer`,
  `D:\apps\SaveGame_Manager_GX`.
- **CTGP-R v1.03**: requisiti ufficiali (chadsoft.co.uk) = disco originale di Mario Kart Wii + SD ≥ 768 MB;
  download solo da Mega (manuale). Le ISO/USB loader non sono indicate come supportate.

## 10. Mario Kart Wii: tutto sbloccato (18/10/2026)

- CTGP-R scartato: le versioni attuali richiedono il disco originale; i metodi "senza disco"
  (video YouTube) usano ISO complete della vecchia 1.02 scaricate da terzi → non fatto.
- Salvataggi estratti con SaveGame Manager GX (Device default → `D:\savegames\<titleID>\`), backup
  completo sul PC in `Documents\Wii\Salvataggi_backup_2026-10-18`.
- `tools/mkw_unlock.py`: byte di sblocco 0x30–0x37 = FF nelle 4 licenze + CRC-32 a 0x27FFC
  (verificato sull'originale). Trofei/stelle GP non toccati. Originale anche in `D:\savegames_originale_MKW`.
- **Testato: funziona** — ogni profilo ha tutto sbloccato.

## 8. Forwarder di USB Loader GX

- WAD ufficiale dal README di wiidev/usbloadergx: `USBLoaderGX_forwarder[UNEO].wad` → `D:\wad\`.
- WAD manager: **YAWM ModMii Edition 1.0.1** (OSCWii) → `D:\apps\yawmME\`.
- Dopo l'installazione: in USB Loader GX → Impostazioni loader → "Ritorna a" = UNEO.

## 6. Decisioni e preferenze dell'utente

- Lingua: italiano.
- Stile: minimal, Material/Google, accento viola preso dal wallpaper.
- Firma visibile: "Mod by VinZo".
- Progetto in `Documents\Wii\wii-vinzo-theme`, repo `git@github.com:VinZo00/wii-vinzo-theme.git`;
  i file Nintendo (`base/`, `.csm`) restano fuori dal repo.
