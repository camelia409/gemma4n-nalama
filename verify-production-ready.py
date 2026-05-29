#!/usr/bin/env python3
"""
Production Readiness Verification Script

Checks that all components are in place for production deployment.
Exit code: 0 if all checks pass, 1 if any check fails.
"""

import sys
import json
from pathlib import Path


def check(condition, message):
    """Print status and track result."""
    status = "[OK]" if condition else "[ERROR]"
    print(f"{status} {message}")
    return condition


def main():
    issues = []

    print("=" * 60)
    print("PRODUCTION READINESS VERIFICATION")
    print("=" * 60)
    print()

    # 1. Backend files
    print("1. Backend Files")
    print("-" * 40)

    backend_py = Path("nalam/backend.py").exists()
    issues.append(not check(backend_py, "nalam/backend.py exists"))

    requirements = Path("nalam/requirements.txt").exists()
    issues.append(not check(requirements, "nalam/requirements.txt exists"))

    # Verify requirements include RAG dependencies
    if requirements:
        reqs_content = Path("nalam/requirements.txt").read_text()
        has_faiss = "faiss-cpu" in reqs_content or "faiss" in reqs_content
        has_google_genai = "google-generativeai" in reqs_content

        issues.append(not check(has_faiss, "  - Contains faiss-cpu"))
        issues.append(not check(has_google_genai, "  - Contains google-generativeai"))

    render_yaml = Path("render.yaml").exists()
    issues.append(not check(render_yaml, "render.yaml exists (Render deployment)"))

    if render_yaml:
        render_content = Path("render.yaml").read_text()
        correct_cmd = "backend:app" in render_content
        issues.append(not check(correct_cmd, "  - startCommand points to backend:app"))

    print()

    # 2. Frontend files
    print("2. Frontend Files")
    print("-" * 40)

    package_json = Path("nalam/package.json").exists()
    issues.append(not check(package_json, "nalam/package.json exists"))

    vercel_json = Path("vercel.json").exists()
    issues.append(not check(vercel_json, "vercel.json exists (Vercel deployment)"))

    print()

    # 3. Knowledge base files
    print("3. Knowledge Base")
    print("-" * 40)

    # Knowledge base is in parent directory
    raw_dir = Path("../knowledge_base/raw")
    kb_files = sorted(raw_dir.glob("*.md")) if raw_dir.exists() else []

    expected_files = [
        "01-hbnc-visit-schedule-and-danger-signs.md",
        "02-nutrition-and-diet-recommendations.md",
        "03-infection-signs-and-home-care.md",
        "04-followup-schedule.md",
        "05-visit-report-template.md",
    ]

    for fname in expected_files:
        exists = (raw_dir / fname).exists()
        issues.append(not check(exists, f"  - {fname}"))

    embeddings_dir = Path("../knowledge_base/embeddings")
    issues.append(not check(embeddings_dir.exists(), "knowledge_base/embeddings/ exists"))

    if embeddings_dir.exists():
        index_file = embeddings_dir / "faiss_index.bin"
        metadata_file = embeddings_dir / "chunks_metadata.json"

        has_index = index_file.exists()
        has_metadata = metadata_file.exists()

        issues.append(not check(has_index, "  - faiss_index.bin exists"))
        issues.append(not check(has_metadata, "  - chunks_metadata.json exists"))

        # Verify metadata structure
        if has_metadata:
            try:
                with open(metadata_file, encoding='utf-8') as f:
                    metadata = json.load(f)

                has_chunks = "chunks" in metadata
                has_model = "embedding_model" in metadata
                has_dim = "embedding_dimension" in metadata

                issues.append(not check(has_chunks, "    - Contains chunks data"))
                issues.append(not check(has_model, "    - Contains embedding_model"))
                issues.append(not check(has_dim, "    - Contains embedding_dimension"))

                if has_chunks:
                    chunk_count = len(metadata.get("chunks", []))
                    has_content = chunk_count > 0
                    issues.append(not check(has_content, f"    - Contains {chunk_count} chunks"))

                    # Check that chunks reference new kebab-case filenames
                    sample_sources = set()
                    for chunk in metadata.get("chunks", [])[:10]:
                        sample_sources.add(chunk.get("source", ""))

                    uses_kebab_case = all("-" in src for src in sample_sources if src)
                    if uses_kebab_case:
                        check(True, "    - Chunk metadata uses kebab-case filenames")
                    else:
                        check(False, "    - Chunk metadata uses kebab-case filenames")
                        issues.append(True)

            except Exception as e:
                check(False, f"  - Error reading metadata: {e}")
                issues.append(True)

    retriever_py = Path("../knowledge_base/retriever.py").exists()
    issues.append(not check(retriever_py, "knowledge_base/retriever.py (RAG retriever)"))

    print()

    # 4. Evaluation files
    print("4. Evaluation & Testing")
    print("-" * 40)

    evaluate_py = Path("eval/evaluate.py").exists()
    issues.append(not check(evaluate_py, "eval/evaluate.py (test runner)"))

    eval_set = Path("eval/eval-set.json").exists()
    issues.append(not check(eval_set, "eval/eval-set.json (test cases)"))

    print()

    # 5. Documentation
    print("5. Documentation")
    print("-" * 40)

    api_contract = Path("API_CONTRACT.md").exists()
    issues.append(not check(api_contract, "API_CONTRACT.md (API specification)"))

    main_readme = Path("README.md").exists()
    issues.append(not check(main_readme, "README.md (project overview)"))

    deployment_checklist = Path("DEPLOYMENT_CHECKLIST.md").exists()
    issues.append(not check(deployment_checklist, "DEPLOYMENT_CHECKLIST.md"))

    logging_schema = Path("docs/logging-schema.md").exists()
    issues.append(not check(logging_schema, "docs/logging-schema.md"))

    kb_readme = Path("../knowledge_base/README.md").exists()
    issues.append(not check(kb_readme, "knowledge_base/README.md"))

    print()

    # 6. No stale filenames
    print("6. File Naming Verification")
    print("-" * 40)

    stale_patterns = [
        "mock_backend",
        "run_eval",
        "test_mock",
        "patch_notebook",
        "payload_assess_danger",
        "eval_set.json",
    ]

    found_stale = False
    for pattern in stale_patterns:
        matches = list(Path(".").rglob(f"*{pattern}*"))
        if matches and not any(str(m).startswith(".git") for m in matches):
            check(False, f"Found stale filename pattern: {pattern}")
            issues.append(True)
            found_stale = True

    if not found_stale:
        check(True, "No stale filenames found (all properly renamed)")

    print()
    print("=" * 60)

    if any(issues):
        print("RESULT: ISSUES FOUND - not production ready")
        print(f"Failed checks: {sum(issues)}")
        return 1
    else:
        print("RESULT: ALL CHECKS PASSED - production ready!")
        print()
        print("Next steps:")
        print("  1. Set GOOGLE_API_KEY in Render dashboard")
        print("  2. Push code to GitHub")
        print("  3. Deploy backend to Render: https://dashboard.render.com")
        print("  4. Deploy frontend to Vercel: https://vercel.com/new")
        print("  5. Add VITE_API_URL env var in Vercel (Render API URL)")
        print("  6. Run: python eval/evaluate.py --base-url <deployed-api-url>")
        return 0


if __name__ == "__main__":
    sys.exit(main())
