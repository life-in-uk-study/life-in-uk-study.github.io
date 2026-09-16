# Design QA — answer-aligned AI learning illustrations

- Browser-rendered answer state: `ai-visual-q01-browser.png`
- Batch samples: `ai-batch-01-contact.png`, `ai-batch-02-contact.png`, `ai-batch-03-sample.png`, `ai-batch-04-sample.png`
- State: Exam 1 question 1 answered correctly, Chinese interface

## Findings

- 397 unique 1200 × 900 WebP illustrations cover 401 question records; four exact duplicates reuse their canonical image.
- The illustrations use a consistent warm editorial style, contain no answer-card UI and remain visually specific to each question and correct answer.
- Five film questions retain real attributed posters; Big Ben and Saint Andrew retain their selected real photograph and museum painting.
- The Harry Potter question uses an original, generic British fantasy-film soundstage rather than protected characters, branding, costumes or exact sets.

## Interaction checks

- Before answering Exam 1 question 1, the answer column contains no image or answer-revealing alternative text.
- The question-specific image loads only after submission.
- The right column retains one image area followed by the continuous explanation and collapsed sources.

final result: passed
