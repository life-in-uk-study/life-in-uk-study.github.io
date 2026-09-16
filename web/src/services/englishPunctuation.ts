const ASCII_PUNCTUATION: Readonly<Record<string, string>> = {
  "‘": "'",
  "’": "'",
  "“": '"',
  "”": '"',
  "–": "-",
  "—": "-",
};

export function normalizeEnglishPunctuation(text: string): string {
  return text.replace(/[‘’“”–—]/g, (character) => ASCII_PUNCTUATION[character]);
}
