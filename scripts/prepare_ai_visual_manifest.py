#!/usr/bin/env python3
"""Build prompts for missing post-answer AI learning illustrations."""

from __future__ import annotations

import json
from pathlib import Path

from enrich_question_content import NON_AI_VISUAL_IDS, film_connection_for, visual_content_key


ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = ROOT / "data" / "enriched_exams"
OUTPUT = ROOT / "data" / "ai_visual_manifest.json"
AI_IMAGE_DIR = ROOT / "public" / "images" / "ai"


PROMPT_OVERRIDES = {
    "exam-01-q17": """Use case: scientific-educational
Asset type: post-answer learning visual for a mobile-first Life in the UK exam website
Primary request: Create a realistic, clean studio photograph of a fictional British poll card lying flat on a warm cream desk, shown fully and clearly. It must look like an election information card but must not copy a real voter's data or claim official endorsement.
Subject: one landscape-format white paper poll card with restrained black typography and simple rule lines
Composition/framing: landscape 4:3 overall image; top-down view; the card fills most of the frame with a small natural shadow; all four card edges visible
Lighting/mood: soft daylight, calm, factual, documentary
Color palette: warm cream background, white card, black and dark green type, one muted red accent
Text (verbatim): "SAMPLE — NOT VALID"; "POLL CARD"; "UK PARLIAMENTARY GENERAL ELECTION"; "Polling day: Thursday 4 July"; "Polling hours: 7am to 10pm"; "Your polling station: Community Hall, 10 Sample Road"; "Elector: Alex Example"; "Address: 25 Sample Street"; "Elector number: AB-123-4"; "You do not need to take this card with you to vote."
Constraints: exact English punctuation; fictional sample data only; no ballot choices, candidates, political-party names, logos, government crest, QR code, handwriting, hands or people; no watermark other than the exact SAMPLE — NOT VALID label; no extra text; readable at medium web size; visually distinguish it from a ballot paper""",
    "exam-15-q04": """Use case: scientific-educational
Asset type: post-answer learning visual for a Life in the UK exam website
Primary request: Create a neutral educational editorial illustration that helps a learner remember that the correct answer to a question about a highly successful UK-produced fantasy film franchise is Harry Potter, without reproducing protected characters or branding.
Scene/backdrop: a British film studio soundstage during production of an original, generic fantasy-school movie
Subject: film cameras, lighting rigs, a clapperboard with no writing, an original stone hall set, practical candle effects, an old travel trunk, round reading spectacles resting on a production table, and a generic broom-shaped prop; no people required
Style/medium: warm contemporary editorial illustration with realistic production details, tactile paper and gouache texture
Composition/framing: landscape 4:3, coherent behind-the-scenes film-production scene, readable at medium web size
Lighting/mood: warm studio lighting, imaginative but documentary-like
Color palette: deep British green, warm cream, muted brick red, restrained gold
Constraints: no written words, no letters, no numbers, no logos, no watermark, no franchise title, no house crest, no recognisable copyrighted character, costume, face, wand design, creature, or exact set recreation; make all fantasy props original and generic; no answer-card UI"""
}


def prompt_for(question: dict) -> str:
    if question["id"] in PROMPT_OVERRIDES:
        return PROMPT_OVERRIDES[question["id"]]
    answers = "; ".join(question["correct_answers"])
    category = question.get("category_name", "Life in the UK")
    return f"""Use case: scientific-educational
Asset type: post-answer learning visual for a mobile-first Life in the UK exam website
Primary request: Create a polished educational editorial illustration based on this exam question and its correct answer.
Question: {question['question']}
Correct answer: {answers}
Topic: {category}
Scene/backdrop: choose one clear, historically and geographically appropriate British setting that makes the correct answer memorable
Subject: visually communicate the correct answer through people, objects, architecture, landscape or a map as appropriate; keep factual details plausible
Style/medium: warm contemporary editorial illustration, realistic proportions, tactile paper and gouache texture, sophisticated educational publishing quality
Composition/framing: landscape 4:3, one coherent focal scene, readable at medium web size
Lighting/mood: natural, calm, engaging and respectful
Color palette: deep British green, warm cream, muted brick red, restrained golden accents to harmonise with an existing cream-and-green learning website
Constraints: no written words, no letters, no numbers, no logos, no watermark, no check marks, no answer-card UI, no official endorsement; image appears only after answer submission
Avoid: decorative imagery unrelated to the question, inaccurate flags, modern objects in historical scenes, caricatures of real people"""


def main() -> None:
    questions = [
        question
        for exam_number in range(1, 18)
        for question in json.loads(
            (DATASET_DIR / f"exam-{exam_number:02d}.json").read_text("utf-8")
        )["questions"]
    ]
    seen: dict[str, str] = {}
    items = []

    for question in questions:
        key = visual_content_key(question)
        canonical_id = seen.setdefault(key, question["id"])
        if canonical_id != question["id"]:
            continue
        if canonical_id in NON_AI_VISUAL_IDS or film_connection_for(question) is not None:
            continue
        target = AI_IMAGE_DIR / f"{canonical_id}.webp"
        items.append(
            {
                "id": canonical_id,
                "question": question["question"],
                "correct_answers": question["correct_answers"],
                "category_name": question.get("category_name"),
                "prompt": prompt_for(question),
                "target": str(target.relative_to(ROOT)),
                "status": "generated" if target.exists() else "pending",
            }
        )

    OUTPUT.write_text(
        json.dumps(
            {
                "total": len(items),
                "generated": sum(item["status"] == "generated" for item in items),
                "pending": sum(item["status"] == "pending" for item in items),
                "items": items,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"total": len(items), "output": str(OUTPUT)}))


if __name__ == "__main__":
    main()
