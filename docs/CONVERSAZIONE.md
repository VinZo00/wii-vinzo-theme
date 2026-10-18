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
  In attesa di test sulla TV.

## 6. Decisioni e preferenze dell'utente

- Lingua: italiano.
- Stile: minimal, Material/Google, accento viola preso dal wallpaper.
- Firma visibile: "Mod by VinZo".
- Progetto in `Documents\Wii\wii-vinzo-theme`, repo `git@github.com:VinZo00/wii-vinzo-theme.git`;
  i file Nintendo (`base/`, `.csm`) restano fuori dal repo.
