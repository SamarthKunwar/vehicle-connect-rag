import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ERROR_CODE_PATTERN = re.compile(r"E-[A-Z]+-\d+")


def split_by_headings(text, heading_level=2):
    """Split markdown text into sections at each heading of the given level.
    Returns a list of (heading_title, section_body) tuples.
    """
    pattern = rf"^{'#' * heading_level} (.+)$"
    lines = text.splitlines()

    sections = []
    current_title = None
    current_lines = []

    for line in lines:
        match = re.match(pattern, line)
        if match:
            if current_title is not None:
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = match.group(1)
            current_lines = []
        else:
            current_lines.append(line)

    if current_title is not None:
        sections.append((current_title, "\n".join(current_lines).strip()))

    return sections


def extract_preamble(text, heading_level=2):
    """Return whatever text comes before the first heading of the given
    level -- e.g. a doc's title line and intro paragraph/table.
    """
    pattern = rf"^{'#' * heading_level} "
    preamble_lines = []
    for line in text.splitlines():
        if re.match(pattern, line):
            break
        preamble_lines.append(line)
    return "\n".join(preamble_lines).strip()


def chunk_document(text, source_file):
    """Split a doc into retrieval-ready chunks: one per level-2 section,
    further split into level-3 sub-sections where they exist (e.g. each
    error code under '## Error codes' becomes its own chunk).
    """
    module = source_file.stem.replace("_troubleshooting", "")
    chunks = []

    preamble = extract_preamble(text, heading_level=2)
    if preamble:
        title_match = re.match(r"^# (.+)$", preamble, re.MULTILINE)
        title = title_match.group(1) if title_match else "Introduction"
        body = re.sub(r"^# .+$", "", preamble, count=1, flags=re.MULTILINE).strip()
        if body:
            chunks.append(build_chunk(title, body, module, source_file))

    for section_title, section_body in split_by_headings(text, heading_level=2):
        sub_sections = split_by_headings(section_body, heading_level=3)

        if not sub_sections:
            # no ### sub-headings inside -> keep the whole ## section as one chunk
            chunks.append(build_chunk(section_title, section_body, module, source_file))
        else:
            for sub_title, sub_body in sub_sections:
                full_title = f"{section_title} — {sub_title}"
                chunks.append(build_chunk(full_title, sub_body, module, source_file))

    return chunks


def build_chunk(title, body, module, source_file):
    text = f"{title}\n\n{body}".strip()
    return {
        "text": text,
        "metadata": {
            "source_file": source_file.name,
            "module": module,
            "section_title": title,
            "error_codes": ",".join(sorted(set(ERROR_CODE_PATTERN.findall(text)))),
        },
    }


def chunk_all_docs(docs_dir=Path("data/docs")):
    all_chunks = []
    for path in sorted(docs_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        all_chunks.extend(chunk_document(text, path))
    return all_chunks


if __name__ == "__main__":
    chunks = chunk_all_docs()
    print(f"Produced {len(chunks)} chunks from all docs\n")
    for c in chunks:
        print(f"=== {c['metadata']['section_title']} ({c['metadata']['source_file']}) ===")
        print(f"error_codes: {c['metadata']['error_codes'] or '(none)'}")
        print(c["text"][:120].replace("\n", " ") + "...")
        print()
