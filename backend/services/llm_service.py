import json
import re
from typing import List, Dict, Any, Optional
from config import settings


SYSTEM_PROMPT = """You are an expert DevOps and CI/CD engineer specializing in failure analysis.
Analyze the provided CI/CD log and return a structured JSON response.

Your response MUST be valid JSON with exactly these keys:
{
  "summary": "2-3 sentence plain-English summary of what went wrong",
  "root_cause": "Single precise root cause statement",
  "suggested_fixes": ["fix1", "fix2", "fix3"],
  "confidence": 0.85
}

Rules:
- suggested_fixes must have 2-5 actionable items
- confidence is a float 0.0-1.0
- Be specific, not generic
- No markdown, no extra keys
"""

def _build_user_prompt(
    preprocessed_log: str,
    failure_category: str,
    similar_issues: List[Dict[str, Any]],
) -> str:
    context = ""
    if similar_issues:
        context = "\n\n--- SIMILAR PAST ISSUES (use for context) ---\n"
        for i, issue in enumerate(similar_issues, 1):
            meta = issue.get("metadata", {})
            context += f"\nIssue {i} (similarity={issue.get('similarity', 0):.2f}):\n"
            context += f"  Summary: {meta.get('summary', 'N/A')}\n"
            context += f"  Root Cause: {meta.get('root_cause', 'N/A')}\n"
            context += f"  Fix: {meta.get('fixes_preview', 'N/A')}\n"

    return f"""Failure Category: {failure_category.upper()}

CI/CD Log (preprocessed):
{preprocessed_log[:3000]}
{context}

Analyze this failure and return ONLY valid JSON as specified."""


def _mock_analysis(failure_category: str, log_snippet: str) -> Dict[str, Any]:
    """Return a deterministic mock response when no API key is configured."""
    templates = {
        "build": {
            "summary": "The build failed due to a compilation or dependency error detected in the CI pipeline. The build process could not complete successfully.",
            "root_cause": "Compilation failure caused by missing dependency or syntax error in source code.",
            "suggested_fixes": [
                "Run `mvn clean install -U` or `npm ci` to refresh dependencies",
                "Check for syntax errors in recently modified files",
                "Verify that all required build tools and correct versions are installed",
                "Review recent commits for breaking changes in build configuration",
            ],
        },
        "test": {
            "summary": "The test suite failed with one or more test cases reporting assertion errors or unexpected behavior. Test execution completed but reported failures.",
            "root_cause": "Unit or integration test failure due to assertion mismatch or environment-specific behavior.",
            "suggested_fixes": [
                "Review failing test output and fix the assertion logic",
                "Ensure test environment matches production configuration",
                "Run tests locally to reproduce and debug the failure",
                "Check for flaky tests and add retry logic if necessary",
            ],
        },
        "infrastructure": {
            "summary": "The pipeline failed due to an infrastructure or environment issue such as network timeout, permission denial, or resource exhaustion.",
            "root_cause": "Infrastructure failure caused by network connectivity, permissions, or resource limits.",
            "suggested_fixes": [
                "Check network connectivity and firewall rules for the CI runner",
                "Verify IAM roles and service account permissions",
                "Review resource limits (CPU/memory) and scale if needed",
                "Check cloud provider status page for active incidents",
            ],
        },
    }
    template = templates.get(failure_category, templates["build"])
    return {**template, "confidence": 0.72}


async def analyze_with_llm(
    preprocessed_log: str,
    failure_category: str,
    similar_issues: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Call OpenAI API or fall back to mock analysis."""

    if not settings.OPENAI_API_KEY:
        return _mock_analysis(failure_category, preprocessed_log)

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        response = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": _build_user_prompt(
                        preprocessed_log, failure_category, similar_issues
                    ),
                },
            ],
            temperature=0.2,
            max_tokens=800,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content
        result = json.loads(raw)

        # Normalise keys
        return {
            "summary": result.get("summary", "Analysis unavailable"),
            "root_cause": result.get("root_cause", "Unknown"),
            "suggested_fixes": result.get("suggested_fixes", []),
            "confidence": float(result.get("confidence", 0.8)),
        }

    except Exception as e:
        print(f"[LLM] OpenAI call failed ({e}), using mock.")
        return _mock_analysis(failure_category, preprocessed_log)
