import { useEffect, useState } from "react";
import { loadQuickReference, type QuickReferenceData } from "../services/quickReference";

interface QuickReferenceState {
  data: QuickReferenceData | null;
  error: boolean;
}

const INITIAL_STATE: QuickReferenceState = { data: null, error: false };

export function useQuickReference(): QuickReferenceState {
  const [state, setState] = useState<QuickReferenceState>(INITIAL_STATE);

  useEffect(() => {
    let active = true;
    loadQuickReference()
      .then((data) => active && setState({ data, error: false }))
      .catch(() => active && setState({ data: null, error: true }));
    return () => { active = false; };
  }, []);

  return state;
}
