#!/usr/bin/env python3
"""
Local testing pipeline for LLM extraction.
Iterates over PDFs/TXTs, extracts text, runs LLM extraction, and provides a summary report.

Features:
- Rate limiting (sleep between requests)
- Token usage tracking
- Success/Failure summary
- JSON output saving

Usage:
    python scripts/test_llm_extraction.py --doc-type class_status_report --output-dir outputs_llm_extraction
"""

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Type

# Add app to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.logging import setup_logging
from app.infrastructure.llm.client import get_client
from app.infrastructure.llm.types import Message, CompletionRequest, JsonSchemaFormat
from app.definitions.document_types.class_status_report import ClassStatusReportDef
from app.definitions.document_types.protocols import DocumentTypeProtocol
from app.document_processors.factory import get_processor
from app.document_processors.protocols import SupportedMimeType

logger = logging.getLogger(__name__)

# Registry of available document types
DOC_TYPES: dict[str, Type[DocumentTypeProtocol]] = {
    "class_status_report": ClassStatusReportDef,
}

@dataclass
class ExtractionStats:
    total_files: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    successful_files: list[str] = field(default_factory=list)
    failed_files: list[str] = field(default_factory=list)

    @property
    def total_tokens(self) -> int:
        return self.total_prompt_tokens + self.total_completion_tokens

def load_text(file_path: Path) -> str:
    """Load text from a file (PDF or TXT) using document processors."""
    logger.info(f"Loading text from {file_path.name}")
    try:
        if file_path.suffix.lower() == ".pdf":
            processor = get_processor(SupportedMimeType.PDF)
            return processor.extract_text(file_path, SupportedMimeType.PDF)
        else:
            return file_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to extract text from {file_path}: {e}")
        return ""

def print_summary(stats: ExtractionStats):
    """Print a clean summary of the extraction run."""
    print("\n" + "="*50)
    print("EXTRACTION SUMMARY")
    print("="*50)
    print(f"Total Files Processed: {stats.total_files}")
    print(f"Successful:            {stats.success_count}")
    print(f"Failed:                {stats.failure_count}")
    print("-" * 50)
    print(f"Total Input Tokens:    {stats.total_prompt_tokens:,}")
    print(f"Total Output Tokens:   {stats.total_completion_tokens:,}")
    print(f"Total Tokens:          {stats.total_tokens:,}")
    print("="*50)
    
    if stats.failed_files:
        print("\nFailed Files:")
        for f in stats.failed_files:
            print(f" - {f}")
    print("\n")

def run_test(
    doc_type_name: str,
    data_dir: Path,
    output_dir: Path,
    model: str = "gpt-4o",
    delay: float = 1.5
):
    """Run extraction tests with rate limiting and stats."""
    
    if doc_type_name not in DOC_TYPES:
        logger.error(f"Unknown document type: {doc_type_name}")
        return

    # Initialize
    doc_def = DOC_TYPES[doc_type_name]()
    client = get_client("openai")
    stats = ExtractionStats()
    
    logger.info(f"=== Starting Extraction for {doc_type_name} ===")
    logger.info(f"Provider: {client.provider.info.name}")
    logger.info(f"Model: {model}")
    logger.info(f"Rate Limit Delay: {delay}s")
    
    # Check directories
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        return
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find files
    files = list(data_dir.glob("*.pdf")) + list(data_dir.glob("*.txt"))
    files.sort()
    
    if not files:
        logger.warning(f"No files found in {data_dir}")
        return

    stats.total_files = len(files)

    for i, file_path in enumerate(files, 1):
        logger.info(f"[{i}/{len(files)}] Processing {file_path.name}...")
        
        # 1. Extract Text
        text = load_text(file_path)
        if not text:
            logger.warning(f"Skipping empty text extraction for {file_path.name}")
            stats.failure_count += 1
            stats.failed_files.append(file_path.name)
            continue
            
        # 2. Run LLM Extraction
        try:
            start_time = time.perf_counter()
            
            # Prepare context & prompt
            prompt_context = doc_def.get_prompt_context()
            system_prompt = f"You are an expert data extraction AI for {prompt_context.get('document_name', doc_type_name)}. Extract structured data according to the schema."
            
            # Prepare JSON Schema
            schema_class = doc_def.target_schema
            json_schema = schema_class.model_json_schema()
            
            # Build Request manually to capture usage stats
            # (The high-level client.extract method swallows usage stats)
            request = CompletionRequest(
                messages=[
                    Message.system(system_prompt),
                    Message.user(text),
                ],
                model=model,
                json_schema=JsonSchemaFormat(
                    name=schema_class.__name__,
                    schema=json_schema,
                ),
            )
            
            # Call Provider
            response = client.provider.complete(request)
            
            # Validate output using Pydantic
            if not response.content:
                raise ValueError("Empty response from LLM")
                
            validated_model = schema_class.model_validate_json(response.content)
            result_json = validated_model.model_dump(mode="json", exclude_none=True)
            
            duration = time.perf_counter() - start_time
            
            # Update Stats
            stats.success_count += 1
            stats.successful_files.append(file_path.name)
            
            if response.usage:
                stats.total_prompt_tokens += response.usage.prompt_tokens
                stats.total_completion_tokens += response.usage.completion_tokens
                logger.info(f"Success ({duration:.2f}s) | Tokens: {response.usage.total_tokens}")
            else:
                logger.info(f"Success ({duration:.2f}s)")
            
            # 3. Save Output
            output_file = output_dir / f"{file_path.stem}.json"
            with open(output_file, "w") as f:
                json.dump(result_json, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"LLM Extraction failed for {file_path.name}: {e}")
            stats.failure_count += 1
            stats.failed_files.append(file_path.name)
        
        # Rate limit sleep
        if i < len(files):
            time.sleep(delay)

    # Report
    print_summary(stats)

if __name__ == "__main__":
    setup_logging()
    
    parser = argparse.ArgumentParser(description="LLM Extraction Pipeline Test")
    parser.add_argument("--doc-type", type=str, default="class_status_report", help="Document type to extract")
    parser.add_argument("--data-dir", type=str, default="tests/data/class_status_reports", help="Directory containing input files")
    parser.add_argument("--output-dir", type=str, default="outputs_llm_extraction", help="Directory for JSON outputs")
    parser.add_argument("--model", type=str, default="gpt-4o", help="LLM model to use")
    parser.add_argument("--delay", type=float, default=1.5, help="Seconds to wait between requests")
    
    args = parser.parse_args()
    
    run_test(
        doc_type_name=args.doc_type,
        data_dir=Path(args.data_dir),
        output_dir=Path(args.output_dir),
        model=args.model,
        delay=args.delay
    )