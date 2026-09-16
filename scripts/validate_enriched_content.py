#!/usr/bin/env python3
"""Validate per-question explanations, authority sources, and learning visuals."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = ROOT / "data" / "enriched_exams"


def main() -> None:
    exam_data = [
        json.loads((DATASET_DIR / f"exam-{exam_number:02d}.json").read_text("utf-8"))
        for exam_number in range(1, 18)
    ]
    questions = [question for exam in exam_data for question in exam["questions"]]
    sources = {
        source_id: source
        for exam in exam_data
        for source_id, source in exam["authority_sources"].items()
    }
    assert all(exam["exam_number"] == index for index, exam in enumerate(exam_data, 1))
    assert all(exam["question_count"] == 24 == len(exam["questions"]) for exam in exam_data)
    assert len(questions) == 408
    assert len({question["id"] for question in questions}) == 408
    assert "official-handbook" in sources

    for question in questions:
        learning = question["learning"]
        assert learning["why_correct_en"].strip()
        assert learning["why_correct_zh"].strip()
        assert learning["answer_summary_zh"].strip()
        keywords = learning["keywords"]
        assert 1 <= len(keywords) <= 3, question["id"]
        assert all(keyword and keyword in question["question"] for keyword in keywords), question["id"]
        assert len(set(keywords)) == len(keywords), question["id"]
        source_ids = question["authoritative_source_ids"]
        assert "official-handbook" in source_ids
        assert all(source_id in sources for source_id in source_ids)
        assert all(sources[source_id]["url"].startswith("https://") for source_id in source_ids)
        visual = question["visual"]
        assert visual["display_after_answer"] is True
        assert visual["alt_zh"].strip()
        visual_path = ROOT / "public" / visual["src"].removeprefix("/")
        assert visual_path.exists(), visual_path
        if visual["kind"] == "ai_learning_illustration":
            assert visual_path.suffix == ".webp", visual_path
            assert visual_path.stat().st_size > 10_000, visual_path
            assert "AI学习插图" in visual["alt_zh"]
        elif visual["kind"] == "licensed_real_photo":
            assert visual_path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}, visual_path
            assert visual_path.stat().st_size > 10_000, visual_path
            assert visual["credit"].strip()
            assert visual["credit_url"].startswith("https://commons.wikimedia.org/")
        elif visual["kind"] == "original_location_map":
            assert visual_path.suffix == ".svg", visual_path
            assert visual["credit"].strip()
            assert visual["credit_url"].startswith("https://")
            svg = visual_path.read_text("utf-8")
            assert question["id"].upper() in svg
            assert all(answer in svg for answer in question["correct_answers"])
        else:
            svg = visual_path.read_text("utf-8")
            assert question["id"].upper() in svg
            assert all(answer in svg for answer in question["correct_answers"])

        film = question.get("film_connection")
        if film:
            assert film["relationship"] in {"direct", "background"}
            assert film["fun_fact_en"].strip() and film["fun_fact_zh"].strip()
            assert film["source_url"].startswith("https://www.bfi.org.uk/")
            assert film["poster_src"].startswith("/images/media/")
            assert film["poster_provider"] == "TMDB"
            assert film["poster_provider_url"].startswith("https://www.themoviedb.org/movie/")
            assert film["poster_credit_notice"] == "This product uses the TMDB API but is not endorsed or certified by TMDB."
            poster_path = ROOT / "public" / film["poster_src"].removeprefix("/")
            assert poster_path.exists(), poster_path

    first_question = next(q for q in questions if q["id"] == "exam-01-q01")
    assert first_question["learning"]["keywords"] == ["two"]

    assert all(
        len(question["learning"]["why_correct_zh"]) <= 500
        for question in questions
    ), "Chinese explanations must not exceed 500 characters"
    assert all(
        max(
            (
                len(paragraph)
                for paragraph in question["learning"]["why_correct_zh"].split("\n\n")
                if paragraph
            ),
            default=0,
        )
        <= 240
        for question in questions
    ), "Chinese explanation paragraphs must not exceed 240 characters"
    generic_zh_explanations = {"这个说法是正确的。", "这句话是真的。", "真的。"}
    generic_en_explanations = {
        "This statement is correct.",
        "This statement is true.",
        "This is true.",
        "True.",
    }
    assert not any(
        question["learning"]["why_correct_zh"].strip() in generic_zh_explanations
        for question in questions
    ), "Generic Chinese true/false explanations must be replaced with a reason"
    assert not any(
        question["learning"]["why_correct_en"].strip() in generic_en_explanations
        for question in questions
    ), "Generic English true/false explanations must be replaced with a reason"

    svg_count = len(list((ROOT / "public" / "images" / "questions").glob("*.svg")))
    assert svg_count == 408
    ai_visual_records = [q for q in questions if q["visual"]["kind"] == "ai_learning_illustration"]
    ai_visual_paths = {q["visual"]["src"] for q in ai_visual_records}
    assert ai_visual_records
    assert ai_visual_paths
    assert sum(q["visual"]["kind"] == "licensed_real_photo" for q in questions) == 4
    assert sum(q["visual"]["kind"] == "original_location_map" for q in questions) == 1
    assert len(list((ROOT / "public" / "images" / "ai").glob("*.webp"))) == 397
    print("PASS: 17 split exam datasets contain 24 questions each")
    print("PASS: 408 questions contain English and Chinese explanations")
    print("PASS: 408 questions reference the official handbook")
    print("PASS: all referenced authority records exist and use HTTPS")
    print(
        f"PASS: {len(ai_visual_records)} question records use "
        f"{len(ai_visual_paths)} answer-aligned AI learning illustrations"
    )
    print("PASS: licensed real photos include attribution and a source link")
    print("PASS: one geography question uses an original sourced location map")
    print("PASS: 408 original SVG fallback visuals remain available")
    print("PASS: 408 questions contain exact-source keyword highlights")
    print("PASS: film connections use real attributed posters, bilingual context, and BFI sources")
    print("PASS: all Chinese explanations are at most 500 characters with concise paragraphs")
    print("PASS: generic true/false explanations have been replaced with reasons")


if __name__ == "__main__":
    main()
