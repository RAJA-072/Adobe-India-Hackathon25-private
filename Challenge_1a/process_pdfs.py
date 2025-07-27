import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import fitz  # PyMuPDF - fast and efficient PDF processing
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFProcessor:
    """High-performance PDF processor for document structure extraction."""
    
    def __init__(self):
        # Font size thresholds for heading detection (optimized for performance)
        self.font_size_thresholds = {
            'h1': 16.0,
            'h2': 14.0, 
            'h3': 12.0,
            'h4': 11.0,
            'h5': 10.0,
            'h6': 9.0
        }
        
        # Common heading patterns for robust detection
        self.heading_patterns = [
            r'^\d+\.?\s+[A-Z][^.]*$',  # "1. Introduction" or "1 Introduction"
            r'^\d+\.\d+\.?\s+[A-Z][^.]*$',  # "1.1. Subsection" or "1.1 Subsection"
            r'^\d+\.\d+\.\d+\.?\s+[A-Z][^.]*$',  # "1.1.1. Sub-subsection"
            r'^[A-Z][A-Z\s]+$',  # "TABLE OF CONTENTS"
            r'^[A-Z][a-z\s]+$',  # "Introduction"
            r'^Chapter\s+\d+',  # "Chapter 1"
            r'^Section\s+\d+',  # "Section 1"
            r'^Appendix\s+[A-Z]',  # "Appendix A"
        ]
        
        # Compile patterns for performance
        self.compiled_patterns = [re.compile(pattern) for pattern in self.heading_patterns]

    def extract_title_from_metadata(self, doc: fitz.Document) -> Optional[str]:
        """Extract title from PDF metadata."""
        try:
            metadata = doc.metadata
            if metadata and metadata.get('title'):
                title = metadata['title'].strip()
                if title and len(title) > 1:
                    return title
        except Exception as e:
            logger.debug(f"Error extracting metadata title: {e}")
        return None

    def extract_title_from_first_page(self, doc: fitz.Document) -> Optional[str]:
        """Extract title from first page using heuristics."""
        try:
            if len(doc) == 0:
                return None
                
            first_page = doc[0]
            blocks = first_page.get_text("dict")["blocks"]
            
            # Look for the largest text in the first few blocks as potential title
            candidates = []
            
            for block in blocks[:15]:  # Check first 15 blocks for better coverage
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        max_size = 0
                        
                        for span in line["spans"]:
                            line_text += span["text"]
                            max_size = max(max_size, span["size"])
                        
                        line_text = line_text.strip()
                        
                        # Title criteria: large font, meaningful text, not too long
                        if (max_size > 0 and 
                            len(line_text) > 3 and 
                            len(line_text) < 300 and  # Increased length limit
                            not line_text.isdigit() and
                            not re.match(r'^page\s+\d+', line_text.lower()) and
                            not re.match(r'^\d+$', line_text.strip())):
                            
                            candidates.append((line_text, max_size))
            
            if candidates:
                # Sort by font size and return the largest
                candidates.sort(key=lambda x: x[1], reverse=True)
                return candidates[0][0]
                
        except Exception as e:
            logger.debug(f"Error extracting title from first page: {e}")
        
        return None

    def is_likely_heading(self, text: str, font_size: float, is_bold: bool, avg_font_size: float) -> bool:
        """Determine if text is likely a heading using multiple heuristics."""
        text = text.strip()
        
        # Basic filters
        if len(text) < 2 or len(text) > 200:
            return False
            
        # Font size criterion (most important)
        if font_size < avg_font_size * 1.1:  # At least 10% larger than average
            return False
            
        # Pattern matching
        for pattern in self.compiled_patterns:
            if pattern.match(text):
                return True
                
        # Bold text with reasonable size
        if is_bold and font_size >= avg_font_size * 1.2:
            return True
            
        # All caps (likely heading)
        if text.isupper() and len(text.split()) <= 10:
            return True
            
        return False

    def determine_heading_level(self, font_size: float, font_sizes: List[float]) -> str:
        """Determine heading level based on font size relative to document."""
        # Sort unique font sizes in descending order
        sorted_sizes = sorted(set(font_sizes), reverse=True)
        
        # Assign levels based on relative position
        for i, size in enumerate(sorted_sizes[:6]):  # Max 6 levels
            if font_size >= size:
                return f"H{i + 1}"
        
        return "H6"  # Default to H6 for smallest headings

    def extract_outline(self, doc: fitz.Document) -> List[Dict[str, Any]]:
        """Extract document outline with optimized performance."""
        outline = []
        font_sizes = []
        
        try:
            # First pass: collect all font sizes for relative sizing
            for page_num in range(len(doc)):
                page = doc[page_num]
                blocks = page.get_text("dict")["blocks"]
                
                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                font_sizes.append(span["size"])
            
            if not font_sizes:
                return outline
                
            avg_font_size = sum(font_sizes) / len(font_sizes)
            
            # Second pass: identify headings
            for page_num in range(len(doc)):
                page = doc[page_num]
                blocks = page.get_text("dict")["blocks"]
                
                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            line_text = ""
                            line_font_size = 0
                            is_bold = False
                            
                            # Combine spans in the same line
                            for span in line["spans"]:
                                line_text += span["text"]
                                line_font_size = max(line_font_size, span["size"])
                                if span["flags"] & 2**4:  # Bold flag
                                    is_bold = True
                            
                            line_text = line_text.strip()
                            
                            # Check if this is a heading
                            if self.is_likely_heading(line_text, line_font_size, is_bold, avg_font_size):
                                level = self.determine_heading_level(line_font_size, font_sizes)
                                
                                # Avoid duplicates
                                if not any(item["text"] == line_text and item["page"] == page_num + 1 
                                         for item in outline):
                                    outline.append({
                                        "level": level,
                                        "text": line_text,
                                        "page": page_num + 1
                                    })
        
        except Exception as e:
            logger.error(f"Error extracting outline: {e}")
        
        return outline

    def process_single_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """Process a single PDF and return structured data."""
        try:
            # Open PDF with PyMuPDF for optimal performance
            doc = fitz.open(str(pdf_path))
            
            # Extract title using multiple strategies
            title = (self.extract_title_from_metadata(doc) or 
                    self.extract_title_from_first_page(doc) or 
                    pdf_path.stem)  # Fallback to filename
            
            # Extract document outline
            outline = self.extract_outline(doc)
            
            # Close document to free memory
            doc.close()
            
            return {
                "title": title,
                "outline": outline
            }
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
            # Return minimal valid structure on error
            return {
                "title": pdf_path.stem,
                "outline": []
            }

def process_pdfs():
    """Main processing function optimized for hackathon constraints."""
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize processor
    processor = PDFProcessor()
    
    # Get all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Process each PDF
    for pdf_file in pdf_files:
        try:
            logger.info(f"Processing: {pdf_file.name}")
            
            # Process PDF and get structured data
            result = processor.process_single_pdf(pdf_file)
            
            # Create output JSON file
            output_file = output_dir / f"{pdf_file.stem}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Completed: {pdf_file.name} -> {output_file.name}")
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_file.name}: {e}")
            # Create minimal output on failure
            error_result = {
                "title": pdf_file.stem,
                "outline": []
            }
            output_file = output_dir / f"{pdf_file.stem}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(error_result, f, indent=4)

if __name__ == "__main__":
    logger.info("Starting PDF processing...")
    process_pdfs()
    logger.info("PDF processing completed!")