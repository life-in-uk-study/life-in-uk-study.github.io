#!/usr/bin/env python3
"""Validate generated Life in the UK exam data."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


def load(name: str) -> dict:
    return json.loads((DATA_DIR / name).read_text(encoding="utf-8"))


def main() -> None:
    grouped = load("lifeintheuktestweb_exams_1_17.json")
    flat = load("lifeintheuktestweb_questions.json")
    duplicate_report = load("lifeintheuktestweb_duplicate_report.json")

    exams = grouped["exams"]
    assert grouped["exam_count"] == 17 == len(exams)
    assert [exam["exam_number"] for exam in exams] == list(range(1, 18))
    assert all(exam["question_count"] == 24 for exam in exams)
    assert all(re.fullmatch(r"[0-9a-f]{64}", exam["source_sha256"]) for exam in exams)

    grouped_questions = [question for exam in exams for question in exam["questions"]]
    flat_questions = flat["questions"]
    assert grouped["question_count"] == 408 == len(grouped_questions)
    assert flat["question_count"] == 408 == len(flat_questions)
    assert len({question["id"] for question in grouped_questions}) == 408
    assert [question["id"] for question in grouped_questions] == [
        question["id"] for question in flat_questions
    ]

    for exam in exams:
        for expected_number, question in enumerate(exam["questions"], start=1):
            assert question["number"] == expected_number
            assert question["id"] == f"exam-{exam['exam_number']:02d}-q{expected_number:02d}"
            assert question["question"].strip()
            assert question["explanation"].strip()
            assert question["category_id"]
            assert len(question["options"]) in {2, 4}
            assert all(option["id"] and option["text"].strip() for option in question["options"])
            option_ids = [option["id"] for option in question["options"]]
            assert len(set(option_ids)) == len(option_ids)
            assert set(question["correct_option_ids"]).issubset(option_ids)
            expected_answers = [
                option["text"]
                for option in question["options"]
                if option["id"] in question["correct_option_ids"]
            ]
            assert question["correct_answers"] == expected_answers
            assert question["type"] == (
                "multiple" if len(question["correct_option_ids"]) > 1 else "single"
            )

    by_text: dict[str, list[str]] = {}
    for question in grouped_questions:
        key = re.sub(r"\s+", " ", question["question"].strip().casefold())
        by_text.setdefault(key, []).append(question["id"])
    expected_duplicates = [
        {"question": text, "ids": ids} for text, ids in by_text.items() if len(ids) > 1
    ]
    assert duplicate_report["duplicate_group_count"] == len(expected_duplicates)
    assert duplicate_report["duplicate_groups"] == expected_duplicates

    print("PASS: 17 exams")
    print("PASS: 24 questions per exam")
    print("PASS: 408 total questions with unique IDs")
    print("PASS: all questions have options, solutions, explanations, and categories")
    print(f"PASS: duplicate report contains {len(expected_duplicates)} exact-text groups")


if __name__ == "__main__":
    main()
