# Path mapping

This page maps working-package paths to their locations in this repository and records every file whose bytes differ from its source. Absolute local paths are not published. Where a raw record contained one, the path prefix was replaced by `<PROJECT_ROOT>/`, and both SHA-256 values are listed so the redacted file can be matched to the original.

## Frozen files

The 88 public frozen files are byte-identical to the freeze of September 15, 2026. The exact original-to-new path of each file is in [../benchmark/freeze/frozen_path_map.json](../benchmark/freeze/frozen_path_map.json).

| Original frozen path | Repository path |
|---|---|
| `code/*` | `code/frozen_2026-09-15/*` |
| `inputs/W*.json` | `benchmark/cases/` |
| `references/W*.json` | `benchmark/answer-keys/` |
| `prompts/*_full_prompt.txt` | `benchmark/prompts/` |
| `protocol/control_profiles.json`, `protocol/output_schema.json` | `benchmark/controls/` |
| other `protocol/*` | `benchmark/protocol/` |
| `private/*` (4 files) | Withheld |

## Earlier repository layout (before 2026-09-18)

| Earlier path | Repository path |
|---|---|
| `methodology/experiment/frozen_2026-09-15/` | See above; the freeze manifests are in `benchmark/freeze/`, and its README is in `docs/provenance/frozen-snapshot-README_2026-09-17.md` |
| `methodology/development/` | `docs/provenance/case-development/` |
| `methodology/logs/` | `docs/provenance/development-logs/` |
| `methodology/artifact-manifest.json` | `docs/provenance/artifact-manifest_2026-09-13.json` (its paths use the earlier layout) |
| `results/timing/2026-09-17/` | `docs/provenance/timing_2026-09-17/` (the `COPY_MANIFEST.json` there is not published because it contains absolute paths) |
| `literature/policies/`, `literature/source-register.json` | Not published; replaced by `literature/institutional-sources.csv` |
| `PUBLIC_RELEASE_CHECKLIST.md`, `methodology/MIGRATION_STATUS.md`, pointer-only READMEs and `.gitkeep` placeholders | Not published (internal or empty) |

## Working packages

| Working package | Repository path |
|---|---|
| `21_EXPERIMENT_EXECUTION_PACKAGE` (frozen primary package) | `benchmark/`, `code/frozen_2026-09-15/`; the aggregate analysis is in `results/aggregate/`; `private/`, `scoring/`, `reviewers/` and `analysis/` are withheld |
| `22_RESEARCH_AUDIT_AND_RESULTS_READY_PACKAGE` | `code/supplement/`, `code/tests/`; addendum v2 is in `docs/deviations.md` |
| `23_AI_JUDGE_EXTENSION_PACKAGE` | `extensions/ai-judge-primary/` (without `private/`, `analysis/` or `code/`) |
| `24_DOCUMENT_EVIDENCE_EXTENSION_PACKAGE` | `extensions/document-evidence/` (without `source_originals/`, full-text attachments or blank observation templates) |
| `25_CLAUDE_MATCHED_SCORING_EXTENSION` | Not published (masked forms and identity key); aggregates are in `results/aggregate/claude_extension_ai_judge.csv` |
| `26_CLAUDE_AI_JUDGE_EXTENSION` | `extensions/ai-judge-claude/` (without `private/`) |

## Code copies and portability edits

No analysis logic was changed. Edited lines carry a comment dated 2026-09-18.

| Source (working package) | Repository path | Source SHA-256 | Edit | Repository SHA-256 |
|---|---|---|---|---|
| `22_RESEARCH_AUDIT_AND_RESULTS_READY_PACKAGE/06_code/analyze_supplement.py` | `code/supplement/analyze_supplement.py` | `f0eaef395f388a3c164c243d9862e8884e97ffc21eadc0bf282b4879f34b9d37` | None (byte-identical) | `f0eaef395f388a3c164c243d9862e8884e97ffc21eadc0bf282b4879f34b9d37` |
| `22_RESEARCH_AUDIT_AND_RESULTS_READY_PACKAGE/06_code/check_scoring_forms.py` | `code/supplement/check_scoring_forms.py` | `38e2839e85db4438c6208d468f454ebc7a0d4c97d51f0182768726f61b84e0f7` | None (byte-identical) | `38e2839e85db4438c6208d468f454ebc7a0d4c97d51f0182768726f61b84e0f7` |
| `22_RESEARCH_AUDIT_AND_RESULTS_READY_PACKAGE/06_code/sync_scoring_forms.py` | `code/supplement/sync_scoring_forms.py` | `73dba1eef839e99f517ff1babb9a19ace3951d98f27fca42744d1aa7a46ef24e` | None (byte-identical) | `73dba1eef839e99f517ff1babb9a19ace3951d98f27fca42744d1aa7a46ef24e` |
| `22_RESEARCH_AUDIT_AND_RESULTS_READY_PACKAGE/06_code/reviewer_agreement.py` | `code/supplement/reviewer_agreement.py` | `605f2953fcb1210b5ffd1cb96bbee3bdd522f20cd20de15373ee316f0ef4dc01` | None (byte-identical) | `605f2953fcb1210b5ffd1cb96bbee3bdd522f20cd20de15373ee316f0ef4dc01` |
| `22_RESEARCH_AUDIT_AND_RESULTS_READY_PACKAGE/06_code/extension_controls.py` | `code/supplement/extension_controls.py` | `4e8e0a4b591585ddcd845a6cae90d2cd186b12e5143e7640ecb4df7012feb204` | None (byte-identical) | `4e8e0a4b591585ddcd845a6cae90d2cd186b12e5143e7640ecb4df7012feb204` |
| `22_RESEARCH_AUDIT_AND_RESULTS_READY_PACKAGE/06_code/prepare_extension_scoring.py` | `code/supplement/prepare_extension_scoring.py` | `7b4a66fd3ceb9820e5d938b500905911acb2a1fe521f431f200639000d11edf6` | None (byte-identical) | `7b4a66fd3ceb9820e5d938b500905911acb2a1fe521f431f200639000d11edf6` |
| `22_RESEARCH_AUDIT_AND_RESULTS_READY_PACKAGE/06_code/ai_judge.py` | `code/supplement/ai_judge.py` | `3125047fe8a921a5fbaeafce7b706a964e8accead458275160c3c25b2dc2d96f` | None (byte-identical) | `3125047fe8a921a5fbaeafce7b706a964e8accead458275160c3c25b2dc2d96f` |
| `22_RESEARCH_AUDIT_AND_RESULTS_READY_PACKAGE/06_code/test_supplement.py` | `code/tests/test_supplement.py` | `27415a4bf8aab415b97f1280e707a202bce85924bdc6a1ec7537ebf075b6b0fa` | `HERE` now points to `code/supplement/` (one line) | `1190bebde4bcec1a9a499eff1e66b18e50746bda4d3c2ca29339ab844185677d` |
| `23_AI_JUDGE_EXTENSION_PACKAGE/code/test_process_outputs.py` | `code/tests/test_ai_judge_parser.py` | `c2fa9bf129d47a5b85d95cb9fdc88f000310e3b29bb48932afb7d210f087317b` | Renamed; adds `code/extensions/ai_judge/` to `sys.path` (one line) | `b84fea4cfa83bc6c71b23dcf6cb0d9beb41e00905dfb6ee27ddc6e58cd728b5b` |
| `23_AI_JUDGE_EXTENSION_PACKAGE/code/process_outputs.py` | `code/extensions/ai_judge/process_outputs.py` | `991bf48e7b7b6d47e6bc34ab1a47ded70ef81acba25d55302ae282d48cc21aa4` | None (byte-identical) | `991bf48e7b7b6d47e6bc34ab1a47ded70ef81acba25d55302ae282d48cc21aa4` |
| `24_DOCUMENT_EVIDENCE_EXTENSION_PACKAGE/code/run_api.py` | `code/extensions/document_evidence/run_api.py` | `c38eba3f7c8a06cadd9583cec4abe5e2e2a428a53010366a34b98e0753be1006` | Adds `--package` (default: parent folder, as before); uses it for the model folder and attachments | `cd1ffe56101e701e7f18b6054a392dcf6246290d35bf13472e6d233545f099da` |
| `24_DOCUMENT_EVIDENCE_EXTENSION_PACKAGE/code/process_outputs.py` | `code/extensions/document_evidence/process_outputs.py` | `3ccce8884a19cb9ca6ba693ac3b9b1f9252e092c7042eb9a9a27aef6cbaf6af8` | Adds `--package` (default: parent folder, as before) | `c4595dea41d70d3df8c978da7257427d03f5f40f016ea32fa25195a76c616932` |

`code/verify_hashes.py`, `code/try_checks.py`, `code/supplement/export_public_tables.py` and `code/supplement/public_workbook_copy.py` are new in this release.

## Analysis workbook

`results/Analysis_Workbook_FINAL.xlsx` is a copy of `22_RESEARCH_AUDIT_AND_RESULTS_READY_PACKAGE/Analysis_Workbook_FINAL.xlsx` (source SHA-256 `732464e539da5b131c595b9f055d61da118c53b315cceba851f7c24f90422269`, saved 2026-09-18 16:07). The only change: four cells in the Timing sheet that held timing-item IDs now read "1 (ID withheld)".

## Redacted provenance files

These 30 raw prompt records from case development contained absolute local paths. The prefix of each path was replaced by `<PROJECT_ROOT>/`; nothing else changed. The originals are kept offline.

| File | Paths replaced | Original SHA-256 | Published SHA-256 |
|---|---|---|---|
| `docs/provenance/case-development/W1-01/W1-01_audit-prompt.txt` | 4 | `ad06391bc66d679af2f5951134e865a07a592149514379662d7fcbce6982001f` | `108faaf1a918c1e3ba5915232ce4a2af286ad260042cce428218d4ed4cd0161d` |
| `docs/provenance/case-development/W1-02/W1-02_audit-prompt.txt` | 4 | `d7d961b9d01058fd3ceddf0a5cb711b80f680b06021160e7d543aeb05fae8749` | `074b2748e976e67a3a3ee4ea62bff718bf9236e2392944f9128d9a16503500ea` |
| `docs/provenance/case-development/W1-03/W1-03_audit-prompt.txt` | 3 | `a304bd946e0cd224da521fd94ba6d221d72a782262ca7afef5143fee72c3a033` | `dfee6fcd7ec266b75db31ef6c5de62d6af0887f9347f1d3f7e13da693e69594c` |
| `docs/provenance/case-development/W1-04/W1-04_audit-prompt.txt` | 3 | `688b7998c8c67103cd065ad50ad0f40e03c12f6c086cc6dcef9bcf698578b5d7` | `369beba775e98fade78514c6c5721c7cff5ed6ed67ec0d1f77840ea35507459d` |
| `docs/provenance/case-development/W1-05/W1-05_audit-prompt.txt` | 4 | `15a63eda6ec53dd764587f58ce08151fd1057852408143337f8e4cffb780658b` | `702d7c9cfeb657ecdace4249de29d6e5f31efccb5f182892ea188073137ace23` |
| `docs/provenance/case-development/W1-06/W1-06_audit-prompt.txt` | 3 | `7dcdc437f9528f9bb1533af79bc2af26aa77ecc9ba2158e11a5964f4d68f5576` | `cb0a3b7ef7c588333addb3e8fa041988e2137e24de449ae0d364e8b13f2c3b08` |
| `docs/provenance/case-development/W1-07/W1-07_audit-prompt.txt` | 3 | `45208b2350f9e099da2e538a56ab4e656ee1039354fa527b6f3307835f563625` | `1e5ad0524c35ccd7951886f7d2289ac322ce20a02deb68654a62e2ecca9ef275` |
| `docs/provenance/case-development/W1-08/W1-08_audit-prompt.txt` | 3 | `c0675a8f5fbab1dc9123cc70a1c7f1220a1d1388ec691827d5108a837b812cef` | `7428d37274753ca5da0879ca113bcc08c092d64e55b4f1a52876ac1c8af9cb54` |
| `docs/provenance/case-development/W2-01/W2-01_audit-prompt.txt` | 3 | `b154f20b7e7c9616171e46beece20c2df81530c9466862f83e4f3651097f2bfd` | `51ec9838af99e38f4ebb0db5437fc6c9e57b64d95a5821ccd90b655a59dddadf` |
| `docs/provenance/case-development/W2-02/W2-02_audit-prompt.txt` | 3 | `5bb795e8e84732c0f0970ac3ca161811a7c5015582570efb9fb2a722dbd2cb90` | `9e72f24c664c21becb68556f0a8100037cf24da2d6cf6442d1b6955c00c87334` |
| `docs/provenance/case-development/W2-03/W2-03_audit-prompt.txt` | 3 | `89c495dcf8cdf277ac92a42226ac194b3db7d7c8bc136c2a07bfc61e3ee359bc` | `2d54d1d76e0fddf4af3ca8955fbf2211cffd409205768826b29a92814a3e3800` |
| `docs/provenance/case-development/W2-04/W2-04_audit-prompt.txt` | 3 | `9ea9c84764851f742cc970eae563253dbcd922fd1c64892315728ec95b794774` | `21ef6d4a9f9fac84507f60cc10ba6afa8ed293a8d0239be58e291b512d1d81e4` |
| `docs/provenance/case-development/W2-04/W2-04_revision-prompt.txt` | 1 | `0973c57a17f6bf766dd2c91acb78f3e2308cb8d93999dc931eb8b6d24dfb34b5` | `2b45977833e16d2ca9c578f9b8576c344150d62e5398102079274d7b4d2d6015` |
| `docs/provenance/case-development/W2-05/W2-05_audit-prompt.txt` | 3 | `1667ae2ebcc404cb4d9798034e43c23132deab0604119beabea793faf9c58236` | `98ccc18398d3bd559790378f2c1b52e9f212ae1ef5484640140498cfd473d230` |
| `docs/provenance/case-development/W2-06/W2-06_audit-prompt.txt` | 3 | `b3fe2fb28d4b39634624822ab820dc82acf0812df01e072072f642a8d415a556` | `c98b674962c91be7823cc24125be43fa16fad5ac6562fd1b7f7cbe96c184ba3f` |
| `docs/provenance/case-development/W2-07/W2-07_audit-prompt.txt` | 3 | `3ecc1b561035a177a2a84dc7941d7f0585890fe04e1db4b61f033d9220da6deb` | `abf8b824bbdf58a2ca83c5517a288fcf6aa46cf6ab3772eb80e7301e80663d03` |
| `docs/provenance/case-development/W2-08/W2-08_audit-prompt.txt` | 3 | `1a85eb4eafbe7915157c77fcd08e25ec2d25da5f107bde94a234add0c91c30f8` | `3b04121a354c79893412d97123b75c473834609ee41df964ef75fb9fa2b31a3c` |
| `docs/provenance/case-development/W2-08/W2-08_revision-prompt.txt` | 1 | `9fc5ce699269b6245f0ba9af3e0b3f9c3d4a2bf77525b4b498a14a37e8cc3ed7` | `10f020b4e073c6d17da3aeaaee9d5e133ae4de753423856bb401b47b0135595c` |
| `docs/provenance/case-development/W3-01/W3-01_audit-prompt.txt` | 3 | `b3e3b46e99a3cef551acc43aceb4768ce25bf9b4644bd10f9091038dfd711723` | `f0a17d43df51e66aee91be3de7174297ba34af3f89e81fc1ff0fa1fa2fe15a2d` |
| `docs/provenance/case-development/W3-01/W3-01_revision-prompt.txt` | 1 | `e4cbaf444edf56fac9d0ee81b1ad47cf8a0f0806b2899af49071d2f566f32eee` | `08406d41605ab569cab5a4ff3fdc687d980b3a7c6428d42fec29d3124c1fc5e6` |
| `docs/provenance/case-development/W3-02/W3-02_audit-prompt.txt` | 3 | `ebbd7b299f56fc933be02efe238a1ffdaf7089e9c9e30e2aa1eb2195b31a9d9a` | `cd9758e4a94cd73b5657d4b831e662c889a9de7bf91c35b7e5625cfe3f3dace7` |
| `docs/provenance/case-development/W3-03/W3-03_audit-prompt.txt` | 4 | `2e555e6a47a9188bde1ea8aeb7f2b07ee3ce3fbebe01cf60868ff7c59c38f482` | `7e82bfee0615e87a91661ba15d2e61f2957f42a04b2083d2dd2c34ba60ac7fa0` |
| `docs/provenance/case-development/W3-03/W3-03_revision-prompt.txt` | 1 | `35acbdcec4b6e3c3ac252e95ff18ebe75d2b06a85cbcc53a87e90661dc3fbf01` | `558063e807190fbba81ebd27e8710f9eeeabf1a65efbcf8748b7d56bed133391` |
| `docs/provenance/case-development/W3-04/W3-04_audit-prompt.txt` | 3 | `10b94009260386ed3b4dc7eb5420e63f3dda47ef051f55f317aa23ad8ccbdbd5` | `3cf25a78ea3cda929e7bf3265b43d858ef048503995c5065fdc43dfe17a49c9c` |
| `docs/provenance/case-development/W3-04/W3-04_revision-prompt.txt` | 1 | `fae6434ab94fb9ed05c98d5ad20c19d28341fbe1b2fd9c852f1cf7a4bbce9d60` | `e0c00c6304d40257c4201a0142d154f31c6d8a4a26ad398ce1d2f571547ded69` |
| `docs/provenance/case-development/W3-05/W3-05_audit-prompt.txt` | 3 | `7623c8d9f1ab30a3d4e2708e1ce5b914bb3c7a470049785018a2c162ad9960a1` | `3bb7b4c1c53e34985845d7a2c1862bec1e9defbaabdcf66e91c2c00ed1c842a7` |
| `docs/provenance/case-development/W3-06/W3-06_audit-prompt.txt` | 3 | `b0db489c1ad585e461bfb039879627630c343576ea23f72d7fc6282045da628b` | `af6136c9f5de8511d0e74c0cdd54227819e629ebd71a3952fbe030c0556b5de1` |
| `docs/provenance/case-development/W3-07/W3-07_audit-prompt.txt` | 3 | `f936e1bdcc7d1158d80a7c13bbdd71653b2e781cac82d2dba326df8bc65ca177` | `b11e5fb284cb9f13d4733282a315f1c39ff290a74783cc94f6bb7cd1ee983fdb` |
| `docs/provenance/case-development/W3-07/W3-07_revision-prompt.txt` | 1 | `f1d319872e675ef915826c29883aa6c7357dd474da0ca7eab3c60acbd4910e86` | `cd8690fb9d99b08047d8a703b5649654b6e832098e6229dc3d33b2e82fb0f55e` |
| `docs/provenance/case-development/W3-08/W3-08_audit-prompt.txt` | 3 | `4235c0eb899821d8b77575d66282b141ead4f6d20798bd35e142c29e19a9af7c` | `ae3c18d56d05ba0199c8a9e0c194c77961fd9f2d558cdbbdfc53789d12035035` |

## Link-updated provenance summaries

These 49 Markdown summaries in `docs/provenance/case-development/` are editorial derivatives, not raw evidence. Their links to retained policy copies (`literature/policies/…`), which are no longer published, now point to `literature/institutional-sources.csv`, and the manifest link was updated. No wording by the researcher or reviewers was changed.

| File | SHA-256 before | SHA-256 after |
|---|---|---|
| `docs/provenance/case-development/README.md` | `8745f184f8bc8c39c9abe7c4634f13a5c99dd6417525e5cc71697fc09132dfa0` | `8b3162d3e38fbd512cf73784e78b7741e5b8102113abf57092eaffacd7ed46c5` |
| `docs/provenance/case-development/W1-01/README.md` | `e2e7833126cf80e278abb5ea6f2e4bf05cddac099f0a6e8f426834e6ce636248` | `9ad039eaaa2b4e48326ed420ecbd0e0a1670ef94cb6d65c660efb8525c48a2cf` |
| `docs/provenance/case-development/W1-01/W1-01_initial-review.md` | `41f7624287f4a32941c37b4091ebc9bae1b77ba8fda590718a4f131635257d6f` | `0cb379a905316d435b02fc20c140933417cf8fad92f564eabe67e3003cf0f345` |
| `docs/provenance/case-development/W1-02/README.md` | `fc4390adea35823f35df2f99b0fca98cee9b2a616966725e656f03dd308d6425` | `a91bab3717ff8d109d7942773ca2eed919bbc9d44b1eb4aa5441fbbd99b15205` |
| `docs/provenance/case-development/W1-02/W1-02_initial-review.md` | `211e0034f7123a302dad062c90d2a223c8d7126aa6ca3cffcd9592e76be7c509` | `b73abb5180f427c9e720fc76f05bb5e249d04dd1b729bebe0b9bdf49d12f9d0c` |
| `docs/provenance/case-development/W1-03/README.md` | `f46019ef3ac3a7cc66d766ee1c2cfc3f3945c866cb9ad4efd6e8016b21c6d401` | `48a0c2f68cbbcb08b05f75d1be4441f46fc941ad1ec131592b8e62676a4bd7a7` |
| `docs/provenance/case-development/W1-03/W1-03_initial-review.md` | `0510f9c5921b0be6a3017a2f1cc8826785710c181f93b8ff8e3ada020bb2e7a6` | `e76673451fcd995e2d37ee70046de3832060ec3e79336697b9e3809f2bd22ef1` |
| `docs/provenance/case-development/W1-04/README.md` | `51beeff6be16cbff3a6558c474cf12f3bd17586e47b35dcef336f5d6df083a1d` | `aa28901aa4d010eb46ccef45504887797db75c0afe723149430083d3ad63b4b5` |
| `docs/provenance/case-development/W1-04/W1-04_initial-review.md` | `73e061853d56eb901201d724678197ba49f206af4e2dbccf8dd9f9d86044d8d1` | `44dec5b3bda247414bde6ff5d8311cde48be7597ba4f4c6e93eb97a555987123` |
| `docs/provenance/case-development/W1-05/README.md` | `1c6a8e8bb596be17c9fa1f0554c427992fd7da0a8973cfaff8dc8822d8d8764c` | `6292d0d5479f72d8143e0691d8c2fa4468e09998b94367c31fc681fdd5fcb559` |
| `docs/provenance/case-development/W1-05/W1-05_initial-review.md` | `365a525284ce7149c9366fdc17e2978671c9db2e21c396ca0e274ab0a10ef3d0` | `499272afc80047db9d29b782e586262ceb22a4ffd580b525ca5cba2113909558` |
| `docs/provenance/case-development/W1-06/README.md` | `a1103f0d750cd83dfe7594e2b4f787bde9fa14702b4e9ca0c42567e0cd820f94` | `730470c22ecc435d77edb89327328af02038ed286e0aed72a335b501555a9d20` |
| `docs/provenance/case-development/W1-06/W1-06_initial-review.md` | `2c0d5c0396f6a966b6d656cd6983473aa29b5894891a0340417081f661ca5996` | `88c57e82dea654f9848554369f72fa19a90ccaf3eac9ed8be6255c80e870f282` |
| `docs/provenance/case-development/W1-07/README.md` | `ad524f6a4a250884678b225048991b8e8798517a22f93bf73793d38b2158d991` | `8a68f64b48c28a6a16709c8075f3a25279af175ff968cafbfdab9e8bc5f9472d` |
| `docs/provenance/case-development/W1-07/W1-07_initial-review.md` | `2766b21e674e08a803c35dd4d3c66416faf07fe227f8a177e8aee6a5e21ebfdc` | `de4f8e26226c82d8282cf10c44fae095602e578f6bf99a1f969dcd9278ef40aa` |
| `docs/provenance/case-development/W1-08/README.md` | `35d202bc9db84804ec71b584d25b379202154ff85d6ef13190fb85776f73aba1` | `4f6b552fbd4fbf57ee5cf4c3d5dff85b7dc71e279db9cb0c3caed419c9bcbd7d` |
| `docs/provenance/case-development/W1-08/W1-08_initial-review.md` | `fb14715cd326850f14cda34024137f8fc16ba6ba704c362ae69c65175169e0bd` | `843c069bf613aa24be43064da768b831375dec352b3eec073791a94d64e7d31d` |
| `docs/provenance/case-development/W2-01/README.md` | `a51bd6e71faaa4b36158459b4ec92a4b69b6bd68dff309dd1231347d8137ace4` | `88f420eea36e04efb59e597ef95908b272ad1025ab0e89012168aeffa13a2487` |
| `docs/provenance/case-development/W2-01/W2-01_initial-review.md` | `0018203c20dabf033363abc8cc7a0f1e5e3a38fce5014bda8b8475b9cbbf1cde` | `0fcff54d1253b5d0400781bb96c5d10906370d1937da2afb6ca073998c763bd3` |
| `docs/provenance/case-development/W2-02/README.md` | `d4c4a1f14579a535aa9f6402534f5c373b034468bbf1c404ee987d1920c9d551` | `49eab286d638f15f69e3b835a105e318628228341d311cf5a11f558d7833a266` |
| `docs/provenance/case-development/W2-02/W2-02_initial-review.md` | `1f97e8c17c49b3697896fc8b2afb2f6981b2cd9b809762228be79846e5a20290` | `ee88c55c9977088b92440cb98fb98e787cc47ec3fbabb832b4b17a3c7ba43d0d` |
| `docs/provenance/case-development/W2-03/README.md` | `2689bafb2f2973b49730247c9f22f6afc99d20b169b4bb480a5ab885b502318e` | `63e0c134f63b577480963450437063bf1216894ae07271a2b0cfc5fa3d90ce30` |
| `docs/provenance/case-development/W2-03/W2-03_initial-review.md` | `5584a2d62ec7a06d8133dd669bf3b882e36b354fef7558304c10face940cec9e` | `89c729ae7107db6751ea41aadf70feef55dd7e8203d5e970659a54ab348e6d1d` |
| `docs/provenance/case-development/W2-04/README.md` | `dcefe2ae02b186cf12be97371f1a466e158b129b3a1f8b2ec4a1af425d0a1510` | `61ab744cd0718016525c9b8b6f99041efa0582974ff55fb04bfd62b0dbeeb884` |
| `docs/provenance/case-development/W2-04/W2-04_initial-review.md` | `aa61018019258ecaf9fe497f09ffe577b669e233a0c9eb43977f9b47e12dec5a` | `40e6f29a8ef75590666474deac12223db4b2dd1d9fe94d1362c79f3f91ad4889` |
| `docs/provenance/case-development/W2-05/README.md` | `d5037d3052f36a165e56ec35e053dce7602abff3cfbaf8693c66fda9aa6cde59` | `16faf542d7d24f1eb4046e7eaadf4a6178545e207f9f5be4f4d4fdf93125abb6` |
| `docs/provenance/case-development/W2-05/W2-05_initial-review.md` | `b95422877b8e8e36bbb2f892c030d6de839bc7e9b4f5572dc0b78a2895b1cb2b` | `277e4b3f245bbbd0f0f9beeb52b709674cfddc896390be13a185125c12ad462d` |
| `docs/provenance/case-development/W2-06/README.md` | `a981dceaddd8695e33cfb5e17ca43e24459dde5ee2b1db2474b237b300e922c6` | `13debe5374102b3194347035dbc26dad25f1d7dae653e003c771cef25b79958d` |
| `docs/provenance/case-development/W2-06/W2-06_initial-review.md` | `b4e0dd6b72b587c624472ffecde45d6f7cf9b6adaf00cbef86080df1c12ef99d` | `12418dd1d3b1cf2442397edebf7a47fd2cfefbc429495450bd6c1c6a8fa4449b` |
| `docs/provenance/case-development/W2-07/README.md` | `b9e86a545bb92cac199cb85f51cdb0c935c3bbd05c92bff35624bcd847d3a816` | `f1624536889acfa30050371db6b5872859f1d937572a5e3afc75752b81889db6` |
| `docs/provenance/case-development/W2-07/W2-07_initial-review.md` | `1c4f8871727631a6bc0ebe2726a72ae705b797a8cc7028556e0e18b320e477f8` | `e572344930dd2e3b5185bfa29f16ec93c7e23320bcbd36ef69880d217cdd55d2` |
| `docs/provenance/case-development/W2-08/README.md` | `951e7945fd0727a15944fd71d80918bb5f07f3b55983467a4460df2071d06195` | `cbb25b505df12092c72c9e02b8a8b185b0b24e9edd174943b4340dd40adbd93d` |
| `docs/provenance/case-development/W2-08/W2-08_initial-review.md` | `203e4ad605549a1b5aba8565d7296be15695f07e7a0934ff2593308efacc0ae4` | `d3d03500253fc4532642d90da4fdad470324010aac2b5a92b3c66d8f1a065bbe` |
| `docs/provenance/case-development/W3-01/README.md` | `1387cc0030a3dd5353865377b35e21068058837543ed82c81f2c086508c7862b` | `0bf781ec555cdc6d74ceb31b674c75297bbc69396e3a44d330b4a57077b6c267` |
| `docs/provenance/case-development/W3-01/W3-01_initial-review.md` | `45fd10cd088dfc7448e9e331ffe011383fa81562d97980dc39d4f35ba8acfd73` | `391a2aa0ff0a7d0252996125d504573ff5d57d5d9c09b02e71a0b3b8ade07cec` |
| `docs/provenance/case-development/W3-02/README.md` | `cf509516305d9c6dc8134a52419e692325c776707f9207b2e6cf1e22e957be49` | `03e9c2063a27883a8b5a3498ef91480b96388f4c313042fbd6be63039959197a` |
| `docs/provenance/case-development/W3-02/W3-02_initial-review.md` | `d7a69e56ead460d97a00b811cffaf3636df4841f951eca8f796ebb33778012ca` | `b6fe8681c6c6f5fe11206e759cfc68d42462d86b528a741bf3dcac55f3d4afe0` |
| `docs/provenance/case-development/W3-03/README.md` | `81ef8409e3527416910b0b99e72545df524841d2b81631ed2f0725284947997f` | `32c75c40daae3ec240534f5ad191188c71db9fc56ce5374e8235c930f8c6b018` |
| `docs/provenance/case-development/W3-03/W3-03_initial-review.md` | `1c6d1a4742d4c199276aaa573e52a3b49b16bedfb61ef821abb3c3c350102798` | `484110247ffd62901de8e366f4a4adb543224cef517a2cfa66a8574622b13743` |
| `docs/provenance/case-development/W3-04/README.md` | `658b16ffd3d18a9cf8af9cfc3d67d1b496bcdbca740f1980d2c3a8a817e56f0a` | `2931a29827176edb6d0563b8e300959881e9630811c67958d8ff03dca2603d47` |
| `docs/provenance/case-development/W3-04/W3-04_initial-review.md` | `4d7e277bbbbd11a888efa817ee75b426dc54912bd6150f30ad5cb7d22de6d80d` | `d50b406b08ead915ea6d317cb7bdbede038e1163b90eeaf0409e22a589db0424` |
| `docs/provenance/case-development/W3-05/README.md` | `6cad39bf945bff619f1cc564a9f237cb67afceb2b51ac5764e7b4e0c38db9845` | `ce9187cf26ce01fa64e70b61c885f847c763cea480889445d120b70a4243323e` |
| `docs/provenance/case-development/W3-05/W3-05_initial-review.md` | `8b8eed1b9da4c3b6336355ad1c6d2829498b98d6b25c0de001e4fa15d22e2b79` | `92b256353e909fe72393dbe4340005b77dab96e61dcd51cb62aad055673cfd08` |
| `docs/provenance/case-development/W3-06/README.md` | `6933d5da09d10fa4b301935e9100902eda18f340119aa6cf1e72e462a07d6d20` | `831c50485c66cfb4ab1fb95789679c3a18b1f16ee36b61a462c4da169beeba87` |
| `docs/provenance/case-development/W3-06/W3-06_initial-review.md` | `a0735e1c31ea556db4d5898003a2fbf169b45e9bcd233b0ce11dd21d8a94523b` | `01e6809c0aa388f248fb69f4d6cc2e2c3de316bd69315bfda9d59de649bed542` |
| `docs/provenance/case-development/W3-07/README.md` | `5407bf2840bd527e9abd63d8c7e2746633ee74bb884899149137b64bc3724afd` | `b6c9fbcc9a8f4e841e792aa38ed46b47ace56078cda001f323e28ca15f297f71` |
| `docs/provenance/case-development/W3-07/W3-07_initial-review.md` | `f441965cd418e91024631ffb40803f7a1c2db44b4b5a6b9ad75b3bf247ed8e54` | `c3460735dadc9d23ef1d9b5dda04e577314458dd8d38bcd86206a1381af565f3` |
| `docs/provenance/case-development/W3-08/README.md` | `e212d4e2ba879f61c5628dc952f9d78abfd9bc465ffaf24d59a01a8bdbf1b0db` | `2f3cee238fc5dd4585d5d33b28380d68ed4452590c5d1ba648621b4d5ac1adec` |
| `docs/provenance/case-development/W3-08/W3-08_initial-review.md` | `5928585ba3658e59981b7290cf6075c750a0eca9913cfcf69af5a639dc6b4667` | `cecc2b7a2dea4b3473784a1c0d07449a2cdd8420701838930e6520f5876ba3cf` |
