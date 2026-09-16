import { Typography } from "./Typography";
import { normalizeEnglishPunctuation } from "../services/englishPunctuation";

interface AnswerOptionProps {
  id: string;
  text: string;
  checked: boolean;
  disabled: boolean;
  multiple: boolean;
  state: "idle" | "correct" | "wrong";
  stateLabel?: string;
  onChange: () => void;
}

export function AnswerOption({ id, text, checked, disabled, multiple, state, stateLabel, onChange }: AnswerOptionProps) {
  return (
    <label className={`answer-option answer-option--${state}${checked ? " is-selected" : ""}`}>
      <input type={multiple ? "checkbox" : "radio"} name="answer" value={id} checked={checked} disabled={disabled} onChange={onChange} />
      <span className="answer-option__control" aria-hidden="true" />
      <Typography as="span" variant="heading">{normalizeEnglishPunctuation(text)}</Typography>
      {stateLabel ? <span className="visually-hidden">{stateLabel}</span> : null}
    </label>
  );
}
