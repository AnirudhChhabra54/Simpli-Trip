"""
Add Data to RAG System - Easy Data Feeding Script
Supports: Text files, CSV, JSON, PDF, and direct text input

Features:
- Chunking of long text into ~900–1000 char chunks
- Batch ingestion when rag_service.add_documents is available
- PDF extraction via PyPDF2 with pdfplumber fallback
- Logging and error handling
- Interactive CLI mode + programmatic helper functions
"""
import sys
import logging
from pathlib import Path
from typing import List, Dict, Optional

# ensure project root is importable
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.rag_service import rag_service
import json
import csv

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def chunk_text(text: str, max_chars: int = 1000) -> List[str]:
    """Split text into reasonably-sized chunks ending on sentence/newline boundaries.

    Args:
        text: input text
        max_chars: approximate maximum characters per chunk
    Returns:
        list of text chunks
    """
    if not text:
        return []
    text = text.strip()
    if len(text) <= max_chars:
        return [text]
    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + max_chars, n)
        seg = text[start:end]
        # attempt to break on newline or sentence end within the segment
        brk = max(seg.rfind("\n"), seg.rfind(". "), seg.rfind("! "), seg.rfind("? "))
        if brk > max_chars // 4:
            cut = start + brk + 1
        else:
            cut = end
        chunk = text[start:cut].strip()
        if chunk:
            chunks.append(chunk)
        start = cut
    return chunks


def add_text_data(text: str, metadata: Dict = None):
    """
    Add plain text data to RAG

    Args:
        text: The text content
        metadata: Optional metadata (destination, category, etc.)
    Returns:
        list of doc ids or chunks (depends on rag_service implementation)
    """
    try:
        if metadata is None:
            metadata = {}

        chunks = chunk_text(text, max_chars=900)
        docs = []
        metas = []
        for i, chunk in enumerate(chunks):
            meta = metadata.copy()
            if len(chunks) > 1:
                meta['chunk_index'] = i
                meta['chunk_count'] = len(chunks)
            docs.append(chunk)
            metas.append(meta)

        # Prefer batch add if rag_service supports it
        if hasattr(rag_service, 'add_documents'):
            # expected signature: add_documents(documents: List[str], metadatas: List[dict])
            rag_service.add_documents(documents=docs, metadatas=metas)
            logger.info("✅ Added %d text chunks (batch) to RAG", len(docs))
            return docs
        else:
            doc_ids = []
            for d, m in zip(docs, metas):
                doc_id = rag_service.add_document(d, m)
                doc_ids.append(doc_id)
            logger.info("✅ Added %d text chunks to RAG (individual calls)", len(doc_ids))
            return doc_ids
    except Exception as e:
        logger.exception("Failed to add text data: %s", e)
        raise


def add_text_file(file_path: str, metadata: Dict = None):
    """
    Add text file to RAG

    Args:
        file_path: Path to .txt file
        metadata: Optional metadata
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        if metadata is None:
            metadata = {'source': file_path}
        else:
            metadata = metadata.copy()
            metadata['source'] = file_path

        result = add_text_data(text, metadata)
        logger.info("✅ Added file: %s", file_path)
        return result
    except Exception as e:
        logger.exception("Failed to add text file %s: %s", file_path, e)
        raise


def add_csv_data(csv_path: str, text_column: str, metadata_columns: List[str] = None):
    """
    Add CSV data to RAG

    Args:
        csv_path: Path to CSV file
        text_column: Column name containing the text
        metadata_columns: List of columns to use as metadata
    Returns:
        number of doc chunks added
    """
    try:
        docs = []
        metas = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                text = row.get(text_column, '') or ''
                if not text:
                    continue

                metadata = {'source': csv_path}
                if metadata_columns:
                    for col in metadata_columns:
                        if col in row:
                            metadata[col] = row[col]

                # chunk the text and add each chunk as a separate doc with chunk metadata
                chunks = chunk_text(text, max_chars=900)
                for i, c in enumerate(chunks):
                    m = metadata.copy()
                    if len(chunks) > 1:
                        m['chunk_index'] = i
                        m['chunk_count'] = len(chunks)
                    docs.append(c)
                    metas.append(m)

        if not docs:
            logger.info("No documents found in CSV: %s", csv_path)
            return 0

        if hasattr(rag_service, 'add_documents'):
            rag_service.add_documents(documents=docs, metadatas=metas)
            logger.info("✅ Added %d documents from CSV (batch): %s", len(docs), csv_path)
            return len(docs)
        else:
            for d, m in zip(docs, metas):
                rag_service.add_document(d, m)
            logger.info("✅ Added %d documents from CSV (individual calls): %s", len(docs), csv_path)
            return len(docs)
    except Exception as e:
        logger.exception("Failed to add CSV data %s: %s", csv_path, e)
        raise


def add_json_data(json_path: str, text_field: str, metadata_fields: List[str] = None):
    """
    Add JSON data to RAG

    Args:
        json_path: Path to JSON file
        text_field: Field name containing the text
        metadata_fields: List of fields to use as metadata
    Returns:
        number of doc chunks added
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, dict):
            data = [data]

        docs = []
        metas = []
        for item in data:
            text = item.get(text_field, '') or ''
            if not text:
                continue

            metadata = {'source': json_path}
            if metadata_fields:
                for field in metadata_fields:
                    if field in item:
                        metadata[field] = item[field]

            chunks = chunk_text(text, max_chars=900)
            for i, c in enumerate(chunks):
                m = metadata.copy()
                if len(chunks) > 1:
                    m['chunk_index'] = i
                    m['chunk_count'] = len(chunks)
                docs.append(c)
                metas.append(m)

        if not docs:
            logger.info("No documents found in JSON: %s", json_path)
            return 0

        if hasattr(rag_service, 'add_documents'):
            rag_service.add_documents(documents=docs, metadatas=metas)
            logger.info("✅ Added %d documents from JSON (batch): %s", len(docs), json_path)
            return len(docs)
        else:
            for d, m in zip(docs, metas):
                rag_service.add_document(d, m)
            logger.info("✅ Added %d documents from JSON (individual calls): %s", len(docs), json_path)
            return len(docs)
    except Exception as e:
        logger.exception("Failed to add JSON data %s: %s", json_path, e)
        raise


def add_pdf_file(pdf_path: str, metadata: Dict = None):
    """
    Add PDF file to RAG

    Args:
        pdf_path: Path to PDF file
        metadata: Optional metadata
    """
    try:
        text = ""
        try:
            # Try PyPDF2 first
            import PyPDF2

            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    page_text = page.extract_text() or ''
                    text += page_text + "\n"
        except Exception:
            # fallback to pdfplumber for more robust extraction if available
            try:
                import pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    for p in pdf.pages:
                        page_text = p.extract_text() or ''
                        text += page_text + "\n"
            except Exception as e:
                logger.exception("PDF extraction failed with PyPDF2 and pdfplumber: %s", e)
                raise

        if metadata is None:
            metadata = {}
        metadata = metadata.copy()
        metadata['source'] = pdf_path
        metadata['type'] = 'pdf'

        result = add_text_data(text, metadata)
        logger.info("✅ Added PDF: %s", pdf_path)
        return result
    except ImportError as e:
        logger.error("PDF libraries not installed: %s", e)
        print("❌ PDF libraries missing. Install PyPDF2 or pdfplumber: pip install PyPDF2 pdfplumber")
        return None
    except Exception as e:
        logger.exception("Failed to add PDF %s: %s", pdf_path, e)
        raise


def add_travel_destination(
    destination: str,
    description: str,
    best_time: Optional[str] = None,
    attractions: Optional[List[str]] = None,
    tips: Optional[str] = None
):
    """
    Add travel destination information

    Args:
        destination: Destination name
        description: Description of the destination
        best_time: Best time to visit
        attractions: List of attractions
        tips: Travel tips
    """
    # Build comprehensive text
    text = f"Destination: {destination}\n\n"
    text += f"Description: {description}\n\n"

    if best_time:
        text += f"Best Time to Visit: {best_time}\n\n"

    if attractions:
        text += "Top Attractions:\n"
        for attraction in attractions:
            text += f"- {attraction}\n"
        text += "\n"

    if tips:
        text += f"Travel Tips: {tips}\n"

    metadata = {
        'destination': destination,
        'category': 'destination_guide',
        'type': 'travel_info'
    }

    result = add_text_data(text, metadata)
    logger.info("✅ Added destination: %s", destination)
    return result


def add_bulk_destinations(destinations_data: List[Dict]):
    """
    Add multiple destinations at once

    Args:
        destinations_data: List of destination dicts
    """
    for dest in destinations_data:
        add_travel_destination(
            destination=dest.get('name'),
            description=dest.get('description'),
            best_time=dest.get('best_time'),
            attractions=dest.get('attractions'),
            tips=dest.get('tips')
        )


def interactive_add():
    """Interactive mode to add data"""
    print("\n" + "=" * 60)
    print("RAG Data Feeder - Interactive Mode")
    print("=" * 60)

    print("\nWhat type of data do you want to add?")
    print("1. Plain text")
    print("2. Text file (.txt)")
    print("3. CSV file")
    print("4. JSON file")
    print("5. PDF file")
    print("6. Travel destination info")
    print("7. Exit")

    choice = input("\nEnter choice (1-7): ").strip()

    if choice == '1':
        print("\nEnter your text (press Ctrl+D or Ctrl+Z when done):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass

        text = '\n'.join(lines)
        destination = input("\nDestination name (optional): ").strip()
        category = input("Category (optional): ").strip()

        metadata = {}
        if destination:
            metadata['destination'] = destination
        if category:
            metadata['category'] = category

        add_text_data(text, metadata)

    elif choice == '2':
        file_path = input("\nEnter file path: ").strip()
        add_text_file(file_path)

    elif choice == '3':
        file_path = input("\nEnter CSV file path: ").strip()
        text_column = input("Text column name: ").strip()
        metadata_cols = input("Metadata columns (comma-separated, optional): ").strip()

        meta_cols = [c.strip() for c in metadata_cols.split(',')] if metadata_cols else None
        add_csv_data(file_path, text_column, meta_cols)

    elif choice == '4':
        file_path = input("\nEnter JSON file path: ").strip()
        text_field = input("Text field name: ").strip()
        metadata_fields = input("Metadata fields (comma-separated, optional): ").strip()

        meta_fields = [f.strip() for f in metadata_fields.split(',')] if metadata_fields else None
        add_json_data(file_path, text_field, meta_fields)

    elif choice == '5':
        file_path = input("\nEnter PDF file path: ").strip()
        add_pdf_file(file_path)

    elif choice == '6':
        destination = input("\nDestination name: ").strip()
        description = input("Description: ").strip()
        best_time = input("Best time to visit (optional): ").strip()
        attractions = input("Attractions (comma-separated, optional): ").strip()
        tips = input("Travel tips (optional): ").strip()

        attractions_list = [a.strip() for a in attractions.split(',')] if attractions else None

        add_travel_destination(
            destination=destination,
            description=description,
            best_time=best_time or None,
            attractions=attractions_list,
            tips=tips or None
        )

    elif choice == '7':
        print("\nGoodbye!")
        return False

    return True


def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("SimpliTrip RAG Data Feeder")
    print("=" * 60)

    print("\nCurrent RAG collection stats:")
    stats = {}
    try:
        stats = rag_service.get_collection_stats()
    except Exception as e:
        logger.warning("Could not fetch collection stats from rag_service: %s", e)
    print(f"  Total documents: {stats.get('count', 0) if isinstance(stats, dict) else stats}")

    # Sanity check rag_service capabilities
    required_methods = ['add_document', 'get_collection_stats', 'search']
    for m in required_methods:
        if not hasattr(rag_service, m):
            logger.warning("rag_service does not expose expected method: %s. Please verify implementation.", m)
    if hasattr(rag_service, 'add_documents'):
        logger.info("rag_service supports batch ingestion (add_documents). Using batch mode where possible.")

    # Check if running in interactive mode
    if len(sys.argv) == 1:
        # Interactive mode
        while interactive_add():
            cont = input("\nAdd more data? (y/n): ").strip().lower()
            if cont != 'y':
                break
    else:
        # Command line mode
        print("\nUsage examples:")
        print("  python add_data_to_rag.py                    # Interactive mode")
        print("  python -c 'from add_data_to_rag import *; add_text_file(\"data.txt\")'")
        print("  python -c 'from add_data_to_rag import *; add_csv_data(\"data.csv\", \"description\")'")

    print("\n✅ Done!")
    print(f"\nFinal collection stats:")
    try:
        stats = rag_service.get_collection_stats()
    except Exception as e:
        logger.warning("Could not fetch collection stats from rag_service: %s", e)
        stats = {}
    print(f"  Total documents: {stats.get('count', 0) if isinstance(stats, dict) else stats}")


if __name__ == "__main__":
    main()
