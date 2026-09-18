# Evidence attachments

Only the **excerpt** files (`*_excerpt.txt`) are included here. They are the frozen `source_excerpt` of each case: short quotations of institutional rules, which remain under their owners' terms.

## Full-document text files (not redistributed)

The `*_full_text.txt` files were text renderings of whole institutional documents (handbooks and policies of up to 374 KB). The institutions' redistribution terms were not verified, so the files are not published. To recreate one:

1. Download the source from the URL in [../../../literature/institutional-sources.csv](../../../literature/institutional-sources.csv), and check its SHA-256 against `original_sha256` in [../protocol/SOURCE_MANIFEST.json](../protocol/SOURCE_MANIFEST.json).
2. Convert it as described in `conversion` for that case: `pdftotext -layout` across all pages, with page markers added. The Mapúa equation corrections are listed in [../protocol/TEXT_NORMALIZATION_RECORD.json](../protocol/TEXT_NORMALIZATION_RECORD.json).
3. Compare the result with `full_text_sha256`. A different tool version may give a different hash. If so, record that.
