#!/usr/bin/env python3
"""Extract the 17 authorised Life in the UK Test Web exam pages.

The script preserves the visible question and option wording while normalising
layout whitespace. It also records correct answers, explanations, categories,
audio URLs, source URLs, retrieval time, and a SHA-256 digest of each page.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = "https://lifeintheuktestweb.co.uk"
EXAM_PATHS = [
    "/british-citizenship-test-1/",
    "/british-citizenship-test-2/",
    "/british-citizenship-test-3/",
    "/british-citizenship-test-4/",
    "/british-citizenship-test-5/",
    "/british-citizenship-test-6/",
    "/british-citizenship-test-7/",
    "/british-citizenship-test-8/",
    "/british-citizenship-test-9/",
    "/british-naturalization-test-10/",
    "/audio-british-citizenship-test-11/",
    "/british-citizenship-test-practice-questions-12/",
    "/british-citizenship-test-13/",
    "/british-citizenship-test-14/",
    "/british-citizenship-test-15/",
    "/life-in-the-uk-exam-16/",
    "/exam-17/",
]


def clean_text(parts: list[str]) -> str:
    """Collapse HTML layout whitespace without altering visible wording."""
    return re.sub(r"\s+", " ", "".join(parts)).strip()


class ExamParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, set[str]]] = []
        self.categories: dict[str, str] = {}
        self.questions: list[dict] = []
        self.current_question: dict | None = None
        self.current_label: dict | None = None

    def _inside_class(self, class_name: str) -> bool:
        return any(class_name in classes for _, classes in self.stack)

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = {key: value or "" for key, value in attrs_list}
        classes = set(attrs.get("class", "").split())
        # Only div ancestry is needed for section detection. Tracking void
        # elements such as input/audio would corrupt the stack because they do
        # not receive matching end-tag callbacks.
        if tag == "div":
            self.stack.append((tag, classes))

        if tag == "div" and "question_button" in classes:
            question_id = attrs.get("data-id_question")
            category_id = attrs.get("data-category")
            if question_id and category_id:
                self.categories[question_id] = category_id

        if tag == "div" and "container_question" in classes:
            question_id = attrs.get("data-id_question", "")
            self.current_question = {
                "page_question_id": question_id,
                "category_id": self.categories.get(question_id),
                "question_parts": [],
                "options": [],
                "explanation_parts": [],
                "audio_url": None,
            }

        if self.current_question is None:
            return

        if tag == "label":
            self.current_label = {"answer_id": None, "parts": []}
        elif tag == "input" and self.current_label is not None:
            self.current_label["answer_id"] = attrs.get("data-id_answer")
            self.current_label["input_type"] = attrs.get("type")
        elif tag == "audio" and "audio_player" in classes:
            self.current_question["audio_url"] = attrs.get("src") or None

    def handle_endtag(self, tag: str) -> None:
        if tag == "label" and self.current_question is not None and self.current_label:
            self.current_question["options"].append(
                {
                    "id": self.current_label.get("answer_id"),
                    "text": clean_text(self.current_label["parts"]),
                }
            )
            self.current_label = None

        if tag == "div" and self.stack:
            _, classes = self.stack[-1]
            if "container_question" in classes and self.current_question is not None:
                question = self.current_question
                question["question"] = clean_text(question.pop("question_parts"))
                question["explanation"] = clean_text(question.pop("explanation_parts"))
                self.questions.append(question)
                self.current_question = None

        if tag == "div" and self.stack:
            self.stack.pop()

    def handle_data(self, data: str) -> None:
        if self.current_question is None:
            return
        if self.current_label is not None:
            self.current_label["parts"].append(data)
        elif self._inside_class("question"):
            self.current_question["question_parts"].append(data)
        elif self._inside_class("container_explication") and not self._inside_class(
            "container_response_correct_incorrect"
        ):
            self.current_question["explanation_parts"].append(data)


def fetch(url: str, attempts: int = 3) -> bytes:
    request = Request(
        url,
        headers={
            "User-Agent": "LifeInTheUKStudyImporter/1.0 (+authorised educational use)",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-GB,en;q=0.9",
        },
    )
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            with urlopen(request, timeout=30) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(attempt * 2)
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def extract_solution(html: str, url: str) -> dict[str, list[str]]:
    match = re.search(r"\bconst\s+solution\s*=\s*(\{.*?\})\s*(?:;|\n)", html, re.DOTALL)
    if not match:
        raise ValueError(f"No solution object found in {url}")
    raw_solution = json.loads(match.group(1))
    return {key: value.split(",") for key, value in raw_solution.items()}


def extract_exam(exam_number: int, url: str) -> dict:
    raw_html = fetch(url)
    html = raw_html.decode("utf-8", errors="strict")
    parser = ExamParser()
    parser.feed(html)
    solution = extract_solution(html, url)

    if len(parser.questions) != 24:
        raise ValueError(f"Exam {exam_number}: expected 24 questions, found {len(parser.questions)}")

    for index, question in enumerate(parser.questions, start=1):
        page_id = question["page_question_id"]
        correct_ids = solution.get(page_id)
        if not correct_ids:
            raise ValueError(f"Exam {exam_number}, question {index}: missing solution for {page_id}")
        option_ids = {option["id"] for option in question["options"]}
        if not set(correct_ids).issubset(option_ids):
            raise ValueError(
                f"Exam {exam_number}, question {index}: solution {correct_ids} not in {option_ids}"
            )
        question["id"] = f"exam-{exam_number:02d}-q{index:02d}"
        question["number"] = index
        question["type"] = "multiple" if len(correct_ids) > 1 else "single"
        question["correct_option_ids"] = correct_ids
        question["correct_answers"] = [
            option["text"] for option in question["options"] if option["id"] in correct_ids
        ]

    return {
        "exam_number": exam_number,
        "title": f"Exam {exam_number}",
        "source_url": url,
        "source_sha256": hashlib.sha256(raw_html).hexdigest(),
        "question_count": len(parser.questions),
        "questions": parser.questions,
    }


def duplicate_report(exams: list[dict]) -> list[dict]:
    by_question: dict[str, list[str]] = {}
    for exam in exams:
        for question in exam["questions"]:
            key = re.sub(r"\s+", " ", question["question"].strip().casefold())
            by_question.setdefault(key, []).append(question["id"])
    return [
        {"question": question, "ids": ids}
        for question, ids in by_question.items()
        if len(ids) > 1
    ]


def main() -> int:
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    retrieved_at = datetime.now(timezone.utc).isoformat()

    exams: list[dict] = []
    for exam_number, path in enumerate(EXAM_PATHS, start=1):
        url = f"{BASE_URL}{path}"
        print(f"Fetching Exam {exam_number}: {url}", file=sys.stderr)
        exams.append(extract_exam(exam_number, url))
        time.sleep(0.5)

    flat_questions = [question for exam in exams for question in exam["questions"]]
    output = {
        "dataset": "Life in the UK Test Web — Exams 1–17",
        "source_index": f"{BASE_URL}/exams-1-17/",
        "retrieved_at": retrieved_at,
        "authorisation_note": "Imported after the user confirmed permission to extract and use the 17 exams.",
        "exam_count": len(exams),
        "question_count": len(flat_questions),
        "exams": exams,
    }
    flat_output = {
        "dataset": output["dataset"],
        "source_index": output["source_index"],
        "retrieved_at": retrieved_at,
        "question_count": len(flat_questions),
        "questions": [
            {
                **question,
                "exam_number": exam["exam_number"],
                "source_url": exam["source_url"],
            }
            for exam in exams
            for question in exam["questions"]
        ],
    }

    (data_dir / "lifeintheuktestweb_exams_1_17.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (data_dir / "lifeintheuktestweb_questions.json").write_text(
        json.dumps(flat_output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    duplicates = duplicate_report(exams)
    (data_dir / "lifeintheuktestweb_duplicate_report.json").write_text(
        json.dumps(
            {
                "duplicate_group_count": len(duplicates),
                "duplicate_groups": duplicates,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "exam_count": len(exams),
                "question_count": len(flat_questions),
                "duplicate_group_count": len(duplicates),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
