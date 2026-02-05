"""
GCS URI utilities for consistent path/URI construction across the codebase.
"""

from __future__ import annotations


def parse_gcs_uri(uri: str) -> tuple[str, str]:
    """
    Parse a GCS URI into bucket and path components.
    
    Args:
        uri: Full GCS URI (gs://bucket/path/to/object)
        
    Returns:
        Tuple of (bucket_name, object_path)
        
    Raises:
        ValueError: If URI is not a valid GCS URI
    """
    if not uri or not uri.startswith("gs://"):
        raise ValueError(f"Invalid GCS URI: {uri}")
    
    parts = uri[5:].split("/", 1)
    bucket = parts[0]
    path = parts[1] if len(parts) > 1 else ""
    
    return bucket, path


def build_gcs_uri(bucket: str, path: str) -> str:
    """
    Build a GCS URI from bucket and path components.
    
    Args:
        bucket: GCS bucket name
        path: Object path within the bucket
        
    Returns:
        Full GCS URI (gs://bucket/path)
    """
    # Remove leading slash from path if present
    path = path.lstrip("/")
    return f"gs://{bucket}/{path}"


def build_document_source_uri(
    bucket: str,
    org_id: str,
    document_id: str,
    file_id: str,
    filename: str = "source",
) -> str:
    """
    Build the GCS URI for a document file upload.
    
    Pattern: gs://{bucket}/org-uploads/{org_id}/documents/{document_id}/files/{file_id}/{filename}
    """
    path = f"org-uploads/{org_id}/documents/{document_id}/files/{file_id}/{filename}"
    return build_gcs_uri(bucket, path)


def build_parsing_result_uri(
    bucket: str,
    org_id: str,
    document_id: str,
    file_id: str,
    filename: str = "result.json",
) -> str:
    """
    Build the GCS URI for parsing job results.
    
    Pattern: gs://{bucket}/org-uploads-parsed/{org_id}/documents/{document_id}/files/{file_id}/{filename}
    """
    path = f"org-uploads-parsed/{org_id}/documents/{document_id}/files/{file_id}/{filename}"
    return build_gcs_uri(bucket, path)


def build_parsing_result_uri_from_source(
    source_uri: str,
    document_id: str,
    file_id: str,
    filename: str = "result.json",
) -> str:
    """
    Build the parsing result URI by extracting bucket from source URI.
    
    Args:
        source_uri: The source file's GCS URI
        document_id: Document ID
        file_id: Document file ID
        filename: Result filename (default: result.json)
        
    Returns:
        Full GCS URI for the parsing result
    """
    bucket, path = parse_gcs_uri(source_uri)
    
    # Extract org_id from source path (org-uploads/{org_id}/...)
    path_parts = path.split("/")
    if len(path_parts) >= 2 and path_parts[0] == "org-uploads":
        org_id = path_parts[1]
    else:
        raise ValueError(f"Cannot extract org_id from source path: {path}")
    
    return build_parsing_result_uri(bucket, org_id, document_id, file_id, filename)