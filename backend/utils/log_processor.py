import re
from typing import List, Tuple
from config import settings


# --- Noise patterns to strip ---
NOISE_PATTERNS = [
    r"^\s*$",                          # blank lines
    r"^\[INFO\].*Downloading.*$",      # maven download noise
    r"^\[INFO\].*Progress.*$",
    r"^\[INFO\].*Downloaded.*$",
    r"^Downloading:\s+https?://.*$",
    r"^\d+\s+KB/s.*$",
    r"^Progress\s*\(\d+/\d+\).*$",
]

# --- Error signal patterns ---
ERROR_PATTERNS = [
    r"(?i)(error|exception|failure|failed|fatal|critical)",
    r"(?i)(traceback|stack trace|caused by)",
    r"(?i)(build failed|compilation failed|test failed)",
    r"(?i)(exit code \d+|non-zero exit)",
    r"(?i)(permission denied|no such file|command not found)",
    r"(?i)(timeout|connection refused|unable to connect)",
    r"(?i)(out of memory|oom|killed)",
    r"(?i)(syntax error|import error|module not found)",
    r"(?i)(assertion.*failed|expected.*got)",
    r"(?i)(docker.*error|container.*failed)",
]

# --- Failure category keywords ---
CATEGORY_PATTERNS = {
    "build": [
        r"(?i)(compilation error|build failed|mvn.*failed|gradle.*failed)",
        r"(?i)(syntax error|import error|undefined.*reference|linker error)",
        r"(?i)(npm.*error|pip.*error|dependency.*error|module not found)",
        r"(?i)(makefile.*error|cmake.*error|ant.*failed)",
    ],
    "test": [
        r"(?i)(test.*failed|assertion.*error|junit|pytest|mocha|jest)",
        r"(?i)(expected.*but.*was|assertionerror|testcase.*failure)",
        r"(?i)(\d+\s+test.*failed|\d+\s+failures|tests.*failed)",
        r"(?i)(coverage.*failed|test suite.*failed)",
    ],
    "infrastructure": [
        r"(?i)(docker.*error|container.*failed|kubernetes.*error|k8s)",
        r"(?i)(connection refused|timeout|network.*error|dns.*error)",
        r"(?i)(permission denied|access denied|unauthorized|403|401)",
        r"(?i)(out of memory|disk.*full|no space left|resource.*limit)",
        r"(?i)(ssh.*failed|ssl.*error|certificate.*error)",
        r"(?i)(aws.*error|gcp.*error|azure.*error|cloud.*provider)",
    ],
}


def remove_noise(lines: List[str]) -> List[str]:
    """Remove irrelevant log lines."""
    clean = []
    for line in lines:
        if any(re.match(p, line) for p in NOISE_PATTERNS):
            continue
        clean.append(line)
    return clean


def extract_error_sections(lines: List[str], context_lines: int = 3) -> List[str]:
    """Extract lines with errors + surrounding context."""
    flagged = set()
    for i, line in enumerate(lines):
        if any(re.search(p, line) for p in ERROR_PATTERNS):
            for j in range(max(0, i - context_lines), min(len(lines), i + context_lines + 1)):
                flagged.add(j)

    if not flagged:
        # Return last portion of log as fallback
        return lines[-min(100, len(lines)):]

    return [lines[i] for i in sorted(flagged)]


def chunk_log(text: str, max_size: int = None) -> List[str]:
    """Split log text into meaningful chunks."""
    if max_size is None:
        max_size = settings.MAX_CHUNK_SIZE

    # Try to split on stage/step boundaries first
    stage_markers = re.split(
        r"(?m)(^={3,}|^-{3,}|^\[Stage\]|^\[Step\]|^STAGE:|^Step \d+)", text
    )

    chunks = []
    current = ""
    for part in stage_markers:
        if len(current) + len(part) <= max_size:
            current += part
        else:
            if current.strip():
                chunks.append(current.strip())
            current = part

    if current.strip():
        chunks.append(current.strip())

    if not chunks:
        # Fallback: split by character count
        for i in range(0, len(text), max_size):
            chunks.append(text[i:i + max_size])

    return chunks


def classify_failure(log_text: str) -> str:
    """Classify the failure into build / test / infrastructure."""
    scores = {cat: 0 for cat in CATEGORY_PATTERNS}
    for cat, patterns in CATEGORY_PATTERNS.items():
        for p in patterns:
            matches = re.findall(p, log_text)
            scores[cat] += len(matches)

    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else "build"


def preprocess_log(raw_log: str) -> Tuple[str, str]:
    """
    Full pipeline: clean → extract errors → classify.
    Returns (preprocessed_text, failure_category).
    """
    lines = raw_log.splitlines()
    lines = remove_noise(lines)
    error_lines = extract_error_sections(lines)
    preprocessed = "\n".join(error_lines)
    category = classify_failure(raw_log)
    return preprocessed, category
