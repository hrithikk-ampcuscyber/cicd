#!/usr/bin/env python3
"""Generate consolidated CI/CD pipeline report for audit and compliance."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path


def collect_artifacts(reports_dir: Path) -> list[dict[str, str | int]]:
    artifacts: list[dict[str, str | int]] = []
    if not reports_dir.exists():
        return artifacts

    for file_path in sorted(reports_dir.rglob("*")):
        if not file_path.is_file():
            continue
        suffix = file_path.suffix.lower()
        report_type = {
            ".sarif": "sarif",
            ".json": "json",
            ".xml": "xml",
            ".html": "html",
            ".md": "markdown",
            ".csv": "csv",
        }.get(suffix, "other")
        artifacts.append(
            {
                "path": str(file_path.relative_to(reports_dir)),
                "type": report_type,
                "size_bytes": file_path.stat().st_size,
            }
        )
    return artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate pipeline summary report")
    parser.add_argument("--reports-dir", default="reports")
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--environment", default="ci")
    parser.add_argument("--commit", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--ref", default="")
    parser.add_argument("--output", default="reports/pipeline-summary.json")
    args = parser.parse_args()

    reports_dir = Path(args.reports_dir)
    artifacts = collect_artifacts(reports_dir)

    summary = {
        "schema_version": "1.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "workflow": args.workflow,
        "environment": args.environment,
        "commit": args.commit,
        "run_id": args.run_id,
        "ref": args.ref,
        "artifacts": artifacts,
        "artifact_count": len(artifacts),
        "report_formats": sorted({str(a["type"]) for a in artifacts}),
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
