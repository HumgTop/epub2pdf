# EPUB to PDF Converter

English | [中文](README.md)

A simple and easy-to-use Python tool for batch converting EPUB format e-books to PDF format.

## Features

- 🔄 **Batch Conversion**: Automatically processes all EPUB files in the `source_book` directory
- 📁 **Preserve Directory Structure**: Converted PDF files maintain the original directory structure in the `output_book` directory
- ⚡ **Smart Skip**: Automatically detects already converted files to avoid duplicate conversion
- 🖼️ **Image Support**: Automatically extracts images from EPUB and embeds them completely in PDF
- 📖 **Format Preservation**: Maintains the original book's format and layout as much as possible
- 📄 **Page Numbers**: Automatically adds page numbers
- 🎨 **Chinese Optimization**: Optimized for Chinese text display

## Usage

> **💡 Tip**: The startup script automatically handles all dependency installation!

### Method 1: Using Startup Script (Recommended)

**macOS/Linux:**
```bash
./run.sh
```

The startup script will automatically:
- Check and install Python dependencies
- Create and activate virtual environment
- Create necessary directory structure
- Run the conversion program

> **⚠️ Windows Users Note**: You need to install GTK+ for Windows first: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer, then use Method 2 for manual execution

### Method 2: Manual Execution (For Advanced Users)

<details>
<summary>Click to expand manual installation steps</summary>

1. **Create Virtual Environment:**
   ```bash
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   
   # Windows
   python -m venv venv
   venv\Scripts\activate.bat
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Conversion:**
   ```bash
   python epub2pdf.py
   ```

</details>

### Prepare EPUB Files

Place the EPUB files to be converted in the `source_book` directory. Subdirectory structures are supported, for example:

```
source_book/
├── novels/
│   ├── three_body.epub
│   └── wandering_earth.epub
├── tech_books/
│   ├── python_programming.epub
│   └── algorithms.epub
└── others/
    └── history_book.epub
```

### View Results

After conversion is complete, PDF files will be saved in the `output_book` directory, maintaining the same structure as the source directory:

```
output_book/
├── novels/
│   ├── three_body.pdf
│   └── wandering_earth.pdf
├── tech_books/
│   ├── python_programming.pdf
│   └── algorithms.pdf
└── others/
    └── history_book.pdf
```

## Advanced Usage

### Custom Source and Output Directories

```python
from epub2pdf import EPUBtoPDFConverter

# Custom directories
converter = EPUBtoPDFConverter(
    source_dir="my_epub_books",
    output_dir="my_pdf_books"
)
converter.convert_all()
```

### Convert Single File

```python
from pathlib import Path
from epub2pdf import EPUBtoPDFConverter

converter = EPUBtoPDFConverter()
epub_file = Path("source_book/example.epub")
converter.convert_epub_to_pdf(epub_file)
```

## Technical Details

### Dependencies

- **ebooklib**: For reading and parsing EPUB files
- **weasyprint**: For converting HTML to PDF
- **Pillow**: Image processing support
- **lxml**: XML parsing support

### Conversion Process

1. Scan all EPUB files in the source directory
2. Check if target PDF already exists and is up to date
3. Parse EPUB file, extract chapter content and image resources
4. Convert images to base64 encoding and embed in HTML
5. Generate formatted HTML content
6. Use WeasyPrint to convert HTML to PDF
7. Save PDF to output directory

### PDF Format Features

- Uses SimSun font, suitable for Chinese reading
- 12pt font size, 1.6x line spacing
- 2cm margins
- Automatic page numbers
- Preserves original book title and author information
- Images automatically fit page width and are centered
- Complete preservation of all image content from EPUB

## FAQ

### Q: Why is the conversion slow?
A: EPUB to PDF conversion is a computationally intensive operation, especially for books with many images. This is normal behavior.

### Q: What to do if dependency installation fails?
A: If the `run.sh` script fails to install dependencies, possible causes and solutions:
- **macOS**: May need to install system dependencies first: `brew install cairo pango gdk-pixbuf libffi`
- **Ubuntu/Debian**: Need to install: `sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info`
- **Windows**: Need to install GTK+ for Windows first

### Q: What to do if some EPUB files fail to convert?
A: Check the error messages in the log output. Common causes include:
- Corrupted EPUB files
- Unsupported formats
- Missing required fonts

### Q: How to adjust PDF formatting?
A: Modify the CSS styles section in `epub2pdf.py` to adjust fonts, font sizes, line spacing, etc.

### Q: Which EPUB versions are supported?
A: Supports EPUB 2.0 and EPUB 3.0 formats.

## License

MIT License

## Contributing

Issues and Pull Requests are welcome!
