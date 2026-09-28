import html
import re

from flask import Flask, jsonify, request


app = Flask(__name__)


# Start headings are ordered by preference.
# The parser uses the first preferred heading it finds, not merely the first
# occurrence of words such as "requirements" anywhere in the document.
START_HEADERS = [
    "what you will do",
    "what you'll do",
    "what you’ll do",
    "what you will be doing",
    "what you'll be doing",
    "what you’ll be doing",
    "responsibilities",
    "your responsibilities",
    "role responsibilities",
    "the role",
    "what you will need",
    "what you'll need",
    "what you’ll need",
    "what we are looking for",
    "what we're looking for",
    "what we’re looking for",
    "minimum qualifications",
    "required qualifications",
    "preferred qualifications",
    "qualifications",
    "requirements",
    "must have",
]

# These identify content that normally appears after the useful job sections.
END_HEADERS = [
    "additional information",
    "compensation",
    "salary",
    "salary range",
    "pay range",
    "benefits",
    "equal opportunity",
    "equal employment opportunity",
    "eeo statement",
    "about the company",
    "about us",
    "company overview",
    "privacy policy",
    "applicant privacy",
    "legal notice",
    "accommodations",
    "interested in working with us",
    "similar jobs",
    "set alert for similar jobs",
    "put your best foot forward",
    "see how you compare",
    "exclusive job seeker insights",
    "about the company",
]

# If one of these headings appears after the starting heading, it remains part
# of the useful content. For example, "What You Will Need" should not terminate
# a block beginning with "What You Will Do."
RELATED_JOB_HEADERS = {
    "what you will do",
    "what you'll do",
    "what you’ll do",
    "what you will be doing",
    "what you'll be doing",
    "what you’ll be doing",
    "responsibilities",
    "your responsibilities",
    "role responsibilities",
    "what you will need",
    "what you'll need",
    "what you’ll need",
    "what we are looking for",
    "what we're looking for",
    "what we’re looking for",
    "minimum qualifications",
    "required qualifications",
    "preferred qualifications",
    "qualifications",
    "requirements",
    "must have",
}


def normalize_heading(value):
    """Normalizes a possible heading for reliable comparison."""
    value = html.unescape(value)
    value = value.replace("’", "'")
    value = re.sub(r"\s+", " ", value)
    value = value.strip(" \t\r\n:-–—|")
    return value.casefold()


def html_to_readable_text(raw_text):
    """
    Removes HTML while preserving meaningful line boundaries.

    Converting <br>, list items, paragraphs, and headings to newlines is
    important because section detection depends on headings occupying their
    own lines.
    """
    text = raw_text or ""

    # Convert common block boundaries into newlines before removing tags.
    text = re.sub(
        r"(?i)<\s*br\s*/?\s*>",
        "\n",
        text,
    )

    text = re.sub(
        r"(?i)</?\s*(p|div|section|article|header|footer|h[1-6]|ul|ol)\b[^>]*>",
        "\n",
        text,
    )

    # Preserve list-item boundaries and add a simple bullet for readability.
    text = re.sub(
        r"(?i)<\s*li\b[^>]*>",
        "\n- ",
        text,
    )
    text = re.sub(
        r"(?i)</\s*li\s*>",
        "\n",
        text,
    )

    # Strip all remaining HTML tags.
    text = re.sub(r"<[^>]+>", "", text)

    # Decode entities such as &amp;, &#39;, and &nbsp;.
    text = html.unescape(text)
    text = text.replace("\xa0", " ")

    # Normalize spacing without destroying line boundaries.
    cleaned_lines = []

    for line in text.splitlines():
        line = re.sub(r"[ \t]+", " ", line).strip()

        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def find_heading_lines(lines, allowed_headers):
    """
    Returns heading matches as dictionaries.

    Exact line matching prevents prose such as
    "requirements listed here" from being treated as a header.
    """
    normalized_allowed = {
        normalize_heading(header): header
        for header in allowed_headers
    }

    matches = []

    for index, line in enumerate(lines):
        normalized_line = normalize_heading(line)

        if normalized_line in normalized_allowed:
            matches.append(
                {
                    "line_index": index,
                    "heading": line.strip(),
                    "normalized_heading": normalized_line,
                }
            )

    return matches


def choose_start_heading(lines):
    """
    Chooses the most useful available heading according to START_HEADERS.

    For example, "What You Will Do" is preferred over a later
    "Qualifications" heading.
    """
    matches = find_heading_lines(lines, START_HEADERS)

    if not matches:
        return None

    priority = {
        normalize_heading(header): rank
        for rank, header in enumerate(START_HEADERS)
    }

    return min(
        matches,
        key=lambda match: (
            priority.get(match["normalized_heading"], len(priority)),
            match["line_index"],
        ),
    )


def choose_end_index(lines, start_index):
    """
    Finds the first boilerplate heading after the selected job section.

    Related job headings such as "What You Will Need" remain included.
    """
    normalized_end_headers = {
        normalize_heading(header)
        for header in END_HEADERS
    }

    for index in range(start_index + 1, len(lines)):
        normalized_line = normalize_heading(lines[index])

        if normalized_line in normalized_end_headers:
            return index

    return len(lines)


def extract_relevant_section(raw_text):
    """Extracts the useful responsibilities and qualifications block."""
    cleaned_text = html_to_readable_text(raw_text)
    lines = cleaned_text.splitlines()

    start_match = choose_start_heading(lines)

    if not start_match:
        return {
            "has_content": False,
            "source": "full_text_fallback",
            "matched_heading": None,
            "content": cleaned_text,
        }

    start_index = start_match["line_index"]
    end_index = choose_end_index(lines, start_index)

    content = "\n".join(lines[start_index:end_index]).strip()

    return {
        "has_content": bool(content),
        "source": "automatic_section_detection",
        "matched_heading": start_match["heading"],
        "content": content,
    }


@app.route("/process", methods=["POST"])
def snip_job_description():
    data = request.get_json(silent=True) or {}

    raw_text = str(data.get("text", "") or "").strip()
    manual_section = str(data.get("manual_section", "") or "").strip()

    # Manual text always wins. This lets users paste only the relevant section
    # if a posting has unusual formatting that automatic detection cannot read.
    if manual_section:
        cleaned_manual_section = html_to_readable_text(manual_section)

        return jsonify(
            {
                "has_content": bool(cleaned_manual_section),
                "source": "manual_section",
                "matched_heading": None,
                "requirements_section_only": cleaned_manual_section,
            }
        )

    if not raw_text:
        return (
            jsonify(
                {
                    "has_content": False,
                    "source": "empty_input",
                    "matched_heading": None,
                    "requirements_section_only": "",
                    "error": (
                        "Provide either 'text' for automatic extraction or "
                        "'manual_section' for a manually selected section."
                    ),
                }
            ),
            400,
        )

    result = extract_relevant_section(raw_text)

    print(
        "[SECTION PARSER] "
        f"source={result['source']}, "
        f"heading={result['matched_heading']!r}, "
        f"characters={len(result['content'])}"
    )

    return jsonify(
        {
            "has_content": result["has_content"],
            "source": result["source"],
            "matched_heading": result["matched_heading"],
            # Preserve your existing response key so the main app does not
            # need to change immediately.
            "requirements_section_only": result["content"],
        }
    )


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5002,
        debug=True,
    )