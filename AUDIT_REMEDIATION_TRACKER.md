# Audit remediation tracker

Permanent follow-up for [`AUDIT_GLOBAL_V1.3.2.md`](AUDIT_GLOBAL_V1.3.2.md).
Update this file in the same change set as every future audit-related fix.

Allowed statuses: `TODO`, `IN PROGRESS`, `DONE`, `DONE WITH RESERVATION`,
`DEFERRED`, `NOT APPLICABLE`.

Current scope: **Phase A — rapid security hardening closed; v1.4.0 prepared
locally**. No tag or remote publication was created. No GUI redesign, parser
refactor or frame-lifecycle redesign was performed.

## Phase A closure / v1.4.0 local preparation

- Inno Setup 6.7.1 was found outside `PATH` and compiled the installer
  successfully. The resulting setup reports file/product version `1.4.0`.
- The release manifest and checksum were regenerated from that setup. The
  manifest records a clean exact local commit. This build is not yet tied to an
  immutable tag or remote publication.
- Python compilation, embedded ExifTool, PNG prompt extraction (including a
  MiniMax fixture), AI Info payload, FFmpeg 8.1.2 and MP4-to-PNG extraction
  were revalidated locally. Console
  suppression received static validation; no Explorer interactive visual test
  was run.
- The validation residue directories `.ffmpeg_update_8_1_2`,
  `.validation_ffmpeg` and `.validation_manifest_2` have no active associated
  process. Their deletion was attempted with exact absolute paths but blocked
  before execution by the host command policy. They remain a local-workspace
  cleanup item, not an application defect.

## Roadmap coverage

| Phase | Scope | Status | Reserve / reste à faire | Validation |
|---|---|---|---|---|
| 0 — Freeze and safety net | Release line, corpus, exact release gate | DEFERRED | Requires test corpus, CI/release authority and a future release decision. | Audit read; no release state changed. |
| A — Rapid security hardening | SEC-01, DEP-01, SEC-03, partial FRM-04, PRIV-01, partial REL-03 | DONE WITH RESERVATION | Explorer GUI validation, broader codec/Cancel corpus, lock redesign, signing and CI remain deferred. Host policy also blocked removal of three validation-residue directories. | Targeted checks re-run; Inno 6.7.1 build, setup version/hash and manifest consistency verified locally. |
| 1 — Blocking low/medium-surface fixes | Remaining ExifTool bound, parser, config, installer and Explorer fixes | DEFERRED | Explicitly out of Phase A. | Not run. |
| 2 — Frame integrity and supervision | Staging, GUI/process supervisor, Job Object, stderr, progress | DEFERRED | Explicitly out of Phase A; only the immediate lock cleanup is fixed. | Not run. |
| 3 — Modern ComfyUI compatibility | GraphContext, bounded resolver, adapters, provenance | DEFERRED | Explicitly out of Phase A. | Not run. |
| 4 — GUI, installation and maintenance | Renderer decision, DPI, clipboard, installer strategy, centralization | DEFERRED | Explicitly out of Phase A, except PRIV-01 log cleanup and REL-03 minimal manifest. | Not run. |

## Findings

| Phase | ID | Sujet | Priorité | Statut | Réserve / reste à faire | Validation |
|---|---|---|---|---|---|---|
| 0 | REL-01 | Tag/release v1.3.2 non reproductible | HAUTE | DEFERRED | Publier une version future depuis un commit/tag immuable exact. | Aucun état Git/release distant modifié. |
| 0 | REL-02 | Absence de corpus et de gate automatisé | HAUTE | DEFERRED | Construire les fixtures et le gate avant les refactors. | Aucun test projet existant trouvé. |
| A / 0 | REL-03 | Traçabilité supply-chain/release | MOYENNE | DONE WITH RESERVATION | Authenticode, SBOM, CI, tag immuable et publication vérifiée restent à faire. | Setup v1.4.0 compilé depuis un commit local propre; checksum et manifest régénérés; hash setup/sidecar/manifest concordants. |
| A / 1 | SEC-01 | Texte variable dans `powershell.exe -Command` pour les dialogues | HAUTE | DONE WITH RESERVATION | Validation interactive de MessageBoxW (session Explorer) à faire sur Windows 10/11. | Les deux helpers appellent `MessageBoxW`; inspection ciblée confirme l'absence de subprocess dans ces helpers; build Inno réussi. |
| 1 | SEC-02 | Limite ExifTool après allocation | HAUTE | DEFERRED | Lecture bornée concurrente stdout/stderr et kill/reap. | Non traité, par périmètre. |
| A / 1 | DEP-01 | FFmpeg antérieur aux correctifs 8.1.2 | HAUTE | DONE WITH RESERVATION | Corpus codecs CFR/VFR/corrompu et progression/Cancel réels restent à rejouer. | Archive Gyan SHA-256 vérifiée; `ffmpeg.exe` SHA-256 vérifié; version 8.1.2; extraction MP4 de validation par `frame_extractor.launch_ffmpeg()` en 2 PNG; setup v1.4.0 compilé. |
| A | SEC-03 | Config ExifTool, fin d'options, chemins système et CWD | MOYENNE | DONE | Les temporaires réouverts et autres durcissements conditionnels restent hors Phase A. | Commande contrôlée: `-config ""` avant options, `--` avant média; ExifTool réel sur PNG; chemins System32 et CWD vérifiés par test ciblé; build Inno réussi. |
| 1 / 3 | PAR-01 | `inputs` ComfyUI liste/dict | HAUTE | DEFERRED | Normaliser les représentations avec fixtures. | Non traité, par périmètre. |
| 3 | PAR-02 | Liens/UI/reroutes/workflow moderne | HAUTE | DEFERRED | GraphContext et résolveur borné. | Non traité, par périmètre. |
| 1 / 3 | PAR-03 | Indices KSampler faux | HAUTE | DEFERRED | Mapping canonique testé. | Non traité, par périmètre. |
| 1 / 3 | PAR-04 | Polarité des prompts par titre/ordre JSON | HAUTE | DEFERRED | Traversée depuis le sampler final. | Non traité, par périmètre. |
| 1 / 3 | PAR-05 | Divergence fast/full | HAUTE | DEFERRED | Algorithme et priorité unifiés. | Non traité, par périmètre. |
| 1 / 3 | PAR-06 | Multi-sampler/seed hybride | HAUTE | DEFERRED | Sélection d'un pass unique; seed 0. | Non traité, par périmètre. |
| 3 | PAR-07 | Workflows modernes/branche finale | HAUTE | DEFERRED | Adaptateurs explicites et provenance. | Non traité, par périmètre. |
| 3 | PAR-08 | Cycles, budgets et confiance des données | MOYENNE | DEFERRED | Validation structurelle, `visited`, budgets. | Non traité, par périmètre. |
| 3 | META-01 | Provenance groupes Exif/règles textuelles | MOYENNE | DEFERRED | Sortie groupée et règles par tag. | Non traité, par périmètre. |
| 2 | PERF-01 | Second appel ExifTool | MOYENNE | DEFERRED | Réutiliser un snapshot sans changer la sémantique. | Non traité, par périmètre. |
| 2 | FRM-01 | Nettoyage frames destructif/non transactionnel | HAUTE | DEFERRED | Staging, manifeste, publication atomique, reparse-point checks. | Non traité, par périmètre. |
| 2 | FRM-02 | GUI de progression cachée/supervision inversée | HAUTE | DEFERRED | Profils GUI/console séparés et supervision unique. | Non traité, par périmètre. |
| 2 | FRM-03 | Timeout et processus enfants | HAUTE | DEFERRED | Watchdog, kill/wait et Job Object. | Non traité, par périmètre. |
| A / 2 | FRM-04 | Lock persistant et chemins avant `finally` | HAUTE | DONE WITH RESERVATION | Verrou OS, validation PID/instance et SMB restent à concevoir/tester. | Test simulé: échec `os.write` ne laisse aucun lock; échec avant lancement libère le lock. |
| 2 | FRM-05 | Code FFmpeg/stderr/capacité non visibles | HAUTE | DEFERRED | Stderr borné, statut UI, espace disque, message unique. | Non traité, par périmètre. |
| 2 | FRM-06 | Progression coûteuse/VFR | MOYENNE | DEFERRED | `ffmpeg -progress`, bornes numériques et UI marquee. | Non traité, par périmètre. |
| 4 | GUI-01 | Tkinter annoncé mais absent | HAUTE | DEFERRED | Décider/implémenter le contrat renderer. | Non traité, par périmètre. |
| 4 | GUI-02 | GUI hostile: preview/cartes non bornées | MOYENNE | DEFERRED | Plafonds de rendu et d'affichage. | Non traité, par périmètre. |
| 4 | GUI-03 | DPI/parité/version renderer | MOYENNE | DEFERRED | Schéma de vue commun et tests DPI. | Non traité, par périmètre. |
| 4 | GUI-04 | Clipboard Unicode | MOYENNE | DEFERRED | `CF_UNICODETEXT` Win32 et relecture exacte. | Non traité; le fallback PowerShell fixe n'interprète pas le texte stdin. |
| A / 4 | PRIV-01 | Logs de succès contenant des chemins privés | MOYENNE | DONE WITH RESERVATION | Rotation/redaction plus fine et test réel d'uninstall VM restent à faire. | Les écritures de succès ont été retirées; seuls les échecs diagnostiques persistent; règle de suppression ajoutée à l'installateur et compilée avec Inno 6.7.1. |
| 1 / 4 | INS-01 | Config ANSI lue UTF-8 | HAUTE | DEFERRED | Écriture UTF-8 atomique. | Non traité, par périmètre. |
| 1 / 4 | INS-02 | Update/Modify écrase config | HAUTE | DEFERRED | Préserver/charger la config existante. | Non traité, par périmètre. |
| 4 | INS-03 | Données utilisateur du compte élevé | HAUTE | DEFERRED | Choisir stratégie per-user/all-users. | Non traité, par périmètre. |
| 1 / 4 | INS-04 | Downgrade silencieux | HAUTE | DEFERRED | Comparaison explicite et blocage/confirmation. | Non traité, par périmètre. |
| 1 / 4 | CTX-01 | Sélection multiple Explorer | HAUTE | DEFERRED | Déclarer `MultiSelectModel=Single`. | Non traité, par périmètre. |
| 4 | INS-05 | BAT context-menu legacy cassés | MOYENNE | DEFERRED | Retirer ou générer/tester le chemin legacy. | Non traité, par périmètre. |
| 4 | INS-06 | Modification des menus non transactionnelle | MOYENNE | DEFERRED | Reporter la suppression et ajouter rollback. | Non traité, par périmètre. |
| 1 / 4 | INS-07 | Contrat Windows x64 absent | HAUTE | DEFERRED | Déclarer/supporter l'architecture après validation VM. | Non traité, par périmètre. |
| 1 | ROB-01 | Erreurs critiques silencieuses | HAUTE | DEFERRED | Résultat structuré et couche de notification unique. | Non traité, par périmètre. |
| 2 | ROB-02 | Config invalide/imports couplés | MOYENNE | DEFERRED | Distinguer absent/invalide et isoler imports. | Non traité, par périmètre. |
| 3 | ARC-01 | Représentations ComfyUI dupliquées | MOYENNE | DEFERRED | GraphContext et SamplerPass canoniques. | Non traité, par périmètre. |
| 4 | ARC-02 | Frontières Windows/politiques dupliquées | MOYENNE | DEFERRED | Centralisation plus large après stabilisation. | Un helper minimal `windows_runtime.py` est introduit seulement pour les besoins Phase A. |
| 4 | MNT-01 | Mise à jour ExifTool | MOYENNE | DEFERRED | Examiner changelog/fixtures avant changement. | Non traité, par périmètre. |
| 4 | MNT-02 | Maintenance Python embarqué | FAIBLE | DEFERRED | Planifier après validation des composants. | Non traité, par périmètre. |
| 4 | MNT-03 | Preview vidéo/multistream | FAIBLE/MOYENNE | DEFERRED | Définir le contrat avec fixtures. | Non traité, par périmètre. |
| 4 | MNT-04 | Interprétation ManualSigmas | FAIBLE | DEFERRED | Clarifier par fixtures officielles. | Non traité, par périmètre. |
| 4 | MNT-05 | MinVersion Windows | MOYENNE | DEFERRED | Déclarer après validation VM 10/11. | Non traité, par périmètre. |
| 4 | MNT-06 | Signature des dépendances | MOYENNE | DEFERRED | Vérifier provenance figée et signer le setup. | Non traité, par périmètre. |

## Protections à préserver

Les protections validées par l'audit restent hors suivi correctif: appels
`subprocess` sans shell, chemins absolus des outils embarqués, `-nostdin`,
whitelist FFmpeg, `-fps_mode passthrough`, temporaires privés aléatoires,
runtime Python isolé et absence d'updater réseau. Elles ne doivent pas être
retirées dans les phases suivantes sans validation dédiée.
