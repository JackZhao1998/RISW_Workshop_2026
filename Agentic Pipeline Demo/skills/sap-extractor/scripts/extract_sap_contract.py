#!/usr/bin/env python3
"""Extract a structured analysis contract from a markdown SAP excerpt."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "sap-analysis-contract-v1"
EXTRACTOR_VERSION = "sap-contract-extractor-0.1"


REQUIRED_SCALAR_FIELDS = [
    "study_id",
    "primary_endpoint",
    "parameter_code",
    "analysis_visit",
    "analysis_population",
    "population_filter",
    "treatment_variable",
    "outcome_variable",
    "baseline_covariate",
    "model",
    "formula",
    "contrast",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()


def split_sections(markdown: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current = "Document"
    sections[current] = []
    for line in markdown.splitlines():
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            current = heading.group(1).strip()
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def find_section(sections: dict[str, str], name: str) -> str:
    for section_name, text in sections.items():
        if section_name.lower() == name.lower():
            return text
    return ""


def evidence(text: str, fallback: str = "") -> str:
    cleaned = " ".join(line.strip() for line in text.splitlines() if line.strip())
    if not cleaned:
        cleaned = fallback
    return cleaned[:240]


def field(value: Any, section: str, evidence_text: str, status: str | None = None) -> dict[str, Any]:
    if status is None:
        if value in (None, "", [], {}):
            status = "NOT_FOUND"
        else:
            status = "FOUND"
    if value in (None, ""):
        value = "NOT_FOUND"
    return {
        "value": value,
        "source_section": section if status != "NOT_FOUND" else "NOT_FOUND",
        "evidence": evidence_text if status != "NOT_FOUND" else "",
        "status": status,
    }


def bullet_value(section_text: str, label: str) -> str | None:
    pattern = rf"^\s*-\s+{re.escape(label)}:\s*(.+?)\s*$"
    match = re.search(pattern, section_text, flags=re.MULTILINE)
    return match.group(1).strip() if match else None


def code_or_text_formula(section_text: str) -> str | None:
    code_match = re.search(r"```text\s*(.*?)\s*```", section_text, flags=re.DOTALL)
    if code_match:
        return code_match.group(1).strip()
    formula_match = re.search(r"\b([A-Za-z0-9_]+\s*=\s*.+)$", section_text, flags=re.MULTILINE)
    return formula_match.group(1).strip() if formula_match else None


def bullets_after_phrase(section_text: str, phrase: str) -> list[str]:
    idx = section_text.lower().find(phrase.lower())
    if idx < 0:
        return []
    tail = section_text[idx + len(phrase) :]
    values = []
    for line in tail.splitlines():
        if line.strip().startswith("- "):
            values.append(line.strip()[2:].strip("` "))
        elif values and line.strip():
            break
    return values


def all_bullets(section_text: str) -> list[str]:
    return [match.group(1).strip("` ") for match in re.finditer(r"^\s*-\s+(.+?)\s*$", section_text, re.MULTILINE)]


def extract_contract(sap_path: Path) -> dict[str, Any]:
    markdown = sap_path.read_text(encoding="utf-8")
    sections = split_sections(markdown)

    study = find_section(sections, "Study")
    estimand = find_section(sections, "Primary Estimand")
    endpoint = find_section(sections, "Primary Endpoint")
    population = find_section(sections, "Analysis Population")
    treatment = find_section(sections, "Treatment Variable")
    model = find_section(sections, "Primary Analysis Model")
    required_fields = find_section(sections, "Required Dataset Fields")
    missing = find_section(sections, "Missing Data Handling")
    readiness = find_section(sections, "Minimum Readiness Criteria")
    constraints = find_section(sections, "Reporting Constraints")

    study_id = bullet_value(study, "Study ID")
    title = bullet_value(study, "Title")
    endpoint_name = bullet_value(endpoint, "Endpoint name")
    parameter_code = bullet_value(endpoint, "Parameter code")
    analysis_visit = bullet_value(endpoint, "Analysis visit")
    outcome = bullet_value(endpoint, "Outcome variable")
    baseline = bullet_value(endpoint, "Baseline variable")
    formula = code_or_text_formula(model)

    population_rule = None
    if re.search(r"FASFL\s*=\s*\"Y\"", population):
        population_rule = 'FASFL == "Y"'

    treatment_var = "TRT01P" if "`TRT01P`" in treatment or "TRT01P" in treatment else None
    allowed_treatments = all_bullets(treatment)
    if allowed_treatments and any("Treatment group" in item for item in allowed_treatments):
        allowed_treatments = [item for item in allowed_treatments if "Treatment group" not in item]

    efficacy_vars = bullets_after_phrase(required_fields, "The efficacy dataset must include:")
    subject_vars = bullets_after_phrase(required_fields, "The subject-level dataset must include:")

    contract = {
        "study_id": field(study_id, "Study", f"- Study ID: {study_id}" if study_id else ""),
        "study_title": field(title, "Study", f"- Title: {title}" if title else ""),
        "primary_estimand": field(evidence(estimand), "Primary Estimand", evidence(estimand)),
        "primary_endpoint": field(endpoint_name, "Primary Endpoint", f"- Endpoint name: {endpoint_name}" if endpoint_name else ""),
        "parameter_code": field(parameter_code, "Primary Endpoint", f"- Parameter code: {parameter_code}" if parameter_code else ""),
        "analysis_visit": field(analysis_visit, "Primary Endpoint", f"- Analysis visit: {analysis_visit}" if analysis_visit else ""),
        "analysis_population": field("Full Analysis Set" if "Full Analysis Set" in population else None, "Analysis Population", evidence(population)),
        "population_filter": field(population_rule, "Analysis Population", evidence(population)),
        "treatment_variable": field(treatment_var, "Treatment Variable", evidence(treatment)),
        "allowed_treatments": field(allowed_treatments, "Treatment Variable", evidence(treatment)),
        "outcome_variable": field(outcome, "Primary Endpoint", f"- Outcome variable: {outcome}" if outcome else ""),
        "baseline_covariate": field(baseline, "Primary Endpoint", f"- Baseline variable: {baseline}" if baseline else ""),
        "model": field("ANCOVA" if "ANCOVA" in model else None, "Primary Analysis Model", evidence(model)),
        "formula": field(formula, "Primary Analysis Model", formula or ""),
        "contrast": field("ABC-201 minus Placebo" if "ABC-201 minus Placebo" in model else None, "Primary Analysis Model", evidence(model)),
        "missing_data_rule": field(evidence(missing), "Missing Data Handling", evidence(missing)),
        "required_datasets": field(["subject_level", "efficacy"], "Required Dataset Fields", evidence(required_fields)),
        "required_variables": field(
            {
                "efficacy": efficacy_vars,
                "subject_level": subject_vars,
            },
            "Required Dataset Fields",
            evidence(required_fields),
        ),
        "minimum_readiness_criteria": field(all_bullets(readiness), "Minimum Readiness Criteria", evidence(readiness)),
        "reporting_constraints": field(all_bullets(constraints), "Reporting Constraints", evidence(constraints)),
    }

    fields_requiring_review = [
        name
        for name in REQUIRED_SCALAR_FIELDS
        if contract[name]["status"] != "FOUND"
    ]
    if not efficacy_vars:
        fields_requiring_review.append("required_variables.efficacy")
    if not subject_vars:
        fields_requiring_review.append("required_variables.subject_level")

    extraction_status = "PASS" if not fields_requiring_review else "FAIL"

    return {
        "schema_version": SCHEMA_VERSION,
        "extraction_status": extraction_status,
        "fields_requiring_review": fields_requiring_review,
        "analysis_contract": contract,
        "extraction_metadata": {
            "sap_path": str(sap_path),
            "sap_sha256": sha256_file(sap_path),
            "extracted_at_utc": utc_now(),
            "extractor_version": EXTRACTOR_VERSION,
            "note": "Extraction only. No dataset readiness decision or ANCOVA execution was performed.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract SAP analysis contract JSON.")
    parser.add_argument("--sap", required=True, type=Path, help="Path to SAP markdown/text file.")
    parser.add_argument("--output", required=True, type=Path, help="Path to write JSON output.")
    args = parser.parse_args()

    result = extract_contract(args.sap.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"Wrote SAP contract JSON: {args.output}")
    print(f"Extraction status: {result['extraction_status']}")
    if result["fields_requiring_review"]:
        print("Fields requiring review:")
        for item in result["fields_requiring_review"]:
            print(f"- {item}")


if __name__ == "__main__":
    main()
