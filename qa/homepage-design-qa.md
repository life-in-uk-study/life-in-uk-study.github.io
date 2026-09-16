# Homepage design QA

- Reference: user-selected iOS-style option 2 concept
- Viewport: 390 x 844 CSS pixels, DPR 1
- UI state: Chinese homepage without a saved exam result

## Full-view comparison

The implementation preserves the selected direction's compact iOS-style header, image-led hero, elevated quick-reference card, two-column exam grid, warm cream palette, deep green typography, red status treatment, gold accents, rounded material surfaces and concise mobile hierarchy.

## Findings

- The mobile hero was reduced to 20rem so the exam grid begins within the first viewport.
- Exam cards retain a 60px minimum touch target.
- A translucent text panel maintains contrast over the Union Jack photograph.
- Phone, tablet and desktop layouts were checked for clipping, overlap and horizontal overflow.

final result: passed
