# SH File Helper

**SH File Helper** is an offline Windows desktop tool for file conversion, OCR, and glossary generation.  
It is designed as a **self-contained, easy-to-install utility**, with no Python or external dependencies required at runtime.

This project was developed as a course / engineering project, with a focus on **software delivery, packaging, and robustness**, not just scripting.

---

## Features

### File Conversion
- PDF ↔ DOCX  
- PDF ↔ PPTX  
- Images → PDF  
- Multiple images → single PDF  

### OCR (Offline)
- Image OCR
- PDF OCR
- Powered by **bundled Tesseract**
- Supported languages (built-in):
  - English (`eng`)
  - Simplified Chinese (`chi_sim`)
  - Japanese (`jpn`)
  - Korean (`kor`)

### PPT Text Extraction
- Extract text from PowerPoint slides for convenient translation
- Supported languages (built-in):
  - English (`eng`)
  - Simplified Chinese (`chi_sim`)
  - Japanese (`jpn`)
  - Korean (`kor`)

### Glossary Generation
- Extract technical terms from text / OCR results
- Configurable:
  - Top-K terms
  - Co-occurrence window size
  - Minimum term length
- Output formats:
  - `.txt`
  - `.json`

### GUI
- Built with **PySide6 (Qt)**
- Drag & drop file input
- Task queue & status display
- No command line required for normal usage

---

## Download & Installation

### Windows (Recommended)
Go to the **Releases** page and download the installer:

**[Releases → SH File Helper v0.1.0 (Windows)](../../releases)**

**Installation steps:**
1. Download `SHFileHelper-Setup.exe`
2. Run the installer
3. Launch **SH File Helper** from Start Menu or Desktop

No Python installation required  
No external OCR installation required  
Works fully offline

---
## How to use
- Select input file
- Choose output path
- Give a output file name 

## Technical Overview

- **Language:** Python
- **GUI:** PySide6 (Qt 6)
- **OCR Engine:** Tesseract (bundled)
- **Packaging:** PyInstaller (onedir)
- **Installer:** Inno Setup
- **Platform:** Windows 10 / 11 (64-bit)

Tesseract binaries and language data are **bundled inside the application**, ensuring consistent behavior across different machines.
