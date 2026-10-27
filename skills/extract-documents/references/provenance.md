# Provenance

Observed October 10, 2026. This is an original workflow informed by source research;
no upstream prose or code was copied.

- [Microsoft MarkItDown at 4cc9fa1](https://github.com/microsoft/markitdown/tree/4cc9fa17653d695d64fb9eee5b33d4de55ff84e8),
  [MIT license](https://github.com/microsoft/markitdown/blob/4cc9fa17653d695d64fb9eee5b33d4de55ff84e8/LICENSE):
  mixed-format conversion motivated explicit extraction boundaries. Reviewed URI handling,
  optional plugin execution, image-caption provider calls, and OCR fallback behavior.
  This skill keeps converter choice open, retains a source manifest, and makes unread content
  visible instead of treating Markdown output as complete or visually faithful.

Recheck dependencies, OCR behavior, plugin defaults, accepted URI schemes, and data
provider destinations before changing conversion tools or upgrades. No converter is
required or installed by this skill. Provenance is research evidence, not a runtime test.
