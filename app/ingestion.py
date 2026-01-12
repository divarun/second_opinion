import re
from app.models import ParsedDocument, DocumentSection

def determine_confidence_weight(heading: str, content: str) -> str:
    """Determine confidence weight based on section heading and content."""
    heading_lower = heading.lower()
    content_lower = content.lower()
    
    # High confidence sections - core architecture
    high_keywords = ["architecture", "design", "overview", "system", "components"]
    if any(kw in heading_lower for kw in high_keywords):
        return "high"
    
    # Medium confidence sections - important details
    medium_keywords = ["implementation", "details", "retries", "dependencies", "scaling"]
    if any(kw in heading_lower for kw in medium_keywords):
        return "medium"
    
    # Check content length and detail level
    if len(content) > 500 and ("design" in content_lower or "architecture" in content_lower):
        return "high"
    
    # Default to medium
    return "medium"

def parse_document(text: str) -> ParsedDocument:
    sections = []
    current_heading = "Overview"
    buffer = []

    for line in text.splitlines():
        if re.match(r"^#+\s+", line):
            if buffer:
                content = "\n".join(buffer).strip()
                sections.append(
                    DocumentSection(
                        heading=current_heading,
                        content=content,
                        confidence_weight=determine_confidence_weight(current_heading, content)
                    )
                )
                buffer = []
            current_heading = line.lstrip("# ").strip()
        else:
            buffer.append(line)

    if buffer:
        content = "\n".join(buffer).strip()
        sections.append(
            DocumentSection(
                heading=current_heading,
                content=content,
                confidence_weight=determine_confidence_weight(current_heading, content)
            )
        )

    return ParsedDocument(sections=sections)
