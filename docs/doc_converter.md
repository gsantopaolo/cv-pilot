## Usage Manual for `doc_converter.py`

This manual covers command-line options and examples for using the `doc_converter.py` tool, which leverages Docling (and optionally SmolDocling) to transform various document formats into Markdown, HTML, JSON, plain text, or Doctags.

---

### Command-Line Options

```bash
Usage: doc_converter.py SOURCE OUTPUT [OPTIONS]
```

| Option                  | Description                                                                         |
|-------------------------|-------------------------------------------------------------------------------------|
| `SOURCE`                | Path or URL to the source document (PDF, DOCX, MD, HTML, CSV, or image).            |
| `OUTPUT`                | Destination file path; extension selects export format (`.md`, `.html`, `.json`, `.txt`, `.doctags`). |
| `--format {md,html,json,text,doctags}` | Output format (default: `md`).                                         |
| `--ocr`                 | Run OCR on images and scanned PDFs.                                                  |
| `--table-structure`     | Recover and preserve table layouts in PDFs and other structured inputs.             |
| `--smol`                | Use SmolDocling VLM for unified OCR and layout extraction on PDFs.                  |
| `-h, --help`            | Show this help message and exit.                                                    |

---

### Parameter Details

- **`SOURCE`**: Supports local files or HTTP(S) URLs. Recognized formats:
  - **Documents**: PDF, DOCX, Markdown (`.md`), HTML (`.html`), CSV (`.csv`)
  - **Images**: PNG, JPEG, TIFF, BMP, WEBP

- **`OUTPUT`**: File name plus extension determines serializer:
  - `.md` → Markdown
  - `.html` → HTML
  - `.json` → JSON
  - `.txt` → Plain text (no markup)
  - `.doctags` → DocTags format (structured token sequence)

- **`--ocr`**: Forces optical character recognition on inputs with embedded images or scanned pages.
- **`--table-structure`**: Enables table-structure recovery when converting PDFs or images via Docling's layout pipeline.
- **`--smol`**: Activates the SmolDocling model for PDF OCR and layout instead of the default pipeline. Useful for unified end‑to‑end processing of complex page elements (text, tables, figures).

---

### Examples

1. **Basic PDF → Markdown**
   ```bash
   python3 doc_converter.py document.pdf document.md
   ```

2. **Enable OCR & table extraction**
   ```bash
   python3 doc_converter.py report.pdf report.md --ocr --table-structure
   ```

3. **Use SmolDocling for PDF**
   ```bash
   python3 doc_converter.py scanned.pdf output.md --smol
   ```

4. **Convert DOCX → JSON**
   ```bash
   python3 doc_converter.py slides.docx slides.json --format json
   ```

5. **Image → Plain Text with OCR**
   ```bash
   python3 doc_converter.py photo.png output.txt --format text --ocr
   ```

6. **HTML → DocTags**
   ```bash
   python3 doc_converter.py page.html page.doctags --format doctags
   ```

---

https://medium.com/@speaktoharisudhan/smoldocling-a-compact-vision-language-model-c54795474faf