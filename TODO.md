# PDF Toolkit - TODO

> Sidst opdateret: 15. februar 2026

---

## Fase 6: Test & Distribution

- [ ] Unit tests for core moduler
  - [ ] `test_merger.py` - merge to PDFs, bevar sideantal
  - [ ] `test_splitter.py` - split modes, page ranges
  - [ ] `test_compressor.py` - komprimeringsniveauer
  - [ ] `test_ocr.py` - dansk tekst, tekstlag
  - [ ] `test_encryption.py` - kryptér/dekryptér
  - [ ] `test_page_ops.py` - rotér, fjern sider
- [ ] PyInstaller build setup (`build.spec`)
- [ ] Test på ren Windows installation
- [ ] Bundled Tesseract OCR (eller installationsvejledning)
- [ ] Poppler DLLs til pdf2image
- [ ] Valgfrit: Inno Setup installer

## Backlog / Nice-to-have

- [ ] Auto-detect orientering (rotate-feature)
- [ ] Bookmark-sammenfletning ved merge
- [ ] Batch-processing mode
- [ ] Dark/Light theme toggle
- [ ] Keyboard shortcuts oversigt
- [ ] Opdater README.md (afspejl alle implementerede features)
- [ ] API-dokumentation fra docstrings
