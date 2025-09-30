# Document Extractors

## Purpose
Document processing and text extraction tools for various document formats and file types.

## Role in System
The **document intelligence engine** that processes diverse document formats and extracts structured text content and metadata.

## What This Directory Contains
- **pdf-extractors/**: PDF text extraction, metadata extraction, and form processing
- **word-extractors/**: Microsoft Word document processing and content extraction
- **excel-extractors/**: Spreadsheet data extraction and analysis
- **powerpoint-extractors/**: Presentation content extraction and slide analysis
- **markdown-extractors/**: Markdown document processing and structure extraction
- **text-extractors/**: Plain text processing and analysis
- **ocr-extractors/**: Optical character recognition for image-based documents

## What This Directory Should NOT Contain
- **Web content processing** - belongs in web-extractors/
- **Code analysis** - belongs in code-extractors/
- **Media processing** - belongs in media-extractors/
- **AI-powered analysis** - belongs in claude-code-extractor/

## CLI Interface
```bash
# PDF extraction
document-extractors/pdf-extractors/extract-text.py --file /path/to/document.pdf --output /path/to/output
document-extractors/pdf-extractors/extract-metadata.py --file /path/to/document.pdf --output /path/to/output
document-extractors/pdf-extractors/extract-forms.py --file /path/to/document.pdf --output /path/to/output

# Word document extraction
document-extractors/word-extractors/extract-text.py --file /path/to/document.docx --output /path/to/output
document-extractors/word-extractors/extract-structure.py --file /path/to/document.docx --output /path/to/output
document-extractors/word-extractors/extract-styles.py --file /path/to/document.docx --output /path/to/output

# Excel extraction
document-extractors/excel-extractors/extract-data.py --file /path/to/spreadsheet.xlsx --output /path/to/output
document-extractors/excel-extractors/extract-sheets.py --file /path/to/spreadsheet.xlsx --output /path/to/output
document-extractors/excel-extractors/extract-formulas.py --file /path/to/spreadsheet.xlsx --output /path/to/output

# PowerPoint extraction
document-extractors/powerpoint-extractors/extract-text.py --file /path/to/presentation.pptx --output /path/to/output
document-extractors/powerpoint-extractors/extract-slides.py --file /path/to/presentation.pptx --output /path/to/output
document-extractors/powerpoint-extractors/extract-notes.py --file /path/to/presentation.pptx --output /path/to/output

# Markdown extraction
document-extractors/markdown-extractors/extract-content.py --file /path/to/document.md --output /path/to/output
document-extractors/markdown-extractors/extract-structure.py --file /path/to/document.md --output /path/to/output
document-extractors/markdown-extractors/extract-links.py --file /path/to/document.md --output /path/to/output

# Text extraction
document-extractors/text-extractors/extract-content.py --file /path/to/document.txt --output /path/to/output
document-extractors/text-extractors/analyze-structure.py --file /path/to/document.txt --output /path/to/output

# OCR extraction
document-extractors/ocr-extractors/extract-text.py --image /path/to/image.png --output /path/to/output
document-extractors/ocr-extractors/extract-from-pdf.py --file /path/to/scanned.pdf --output /path/to/output
```

## Dependencies and Relationships
- **Uses**: utilities/ for common functions, media-extractors/ for image processing
- **Provides**: Structured text content to core/rag-engine/ and claude-code-extractor/
- **Integrates with**: data-management/ for document storage and indexing
- **Serves**: Document processing and content analysis systems

## Implementation Guidelines
1. **Format-specific expertise** - deep understanding of each document format's structure
2. **Quality extraction** - preserve formatting, structure, and metadata where possible
3. **Error handling** - handle corrupted, protected, or malformed documents gracefully
4. **Performance optimization** - efficient processing of large documents and batches
5. **Metadata preservation** - extract and preserve document metadata and properties