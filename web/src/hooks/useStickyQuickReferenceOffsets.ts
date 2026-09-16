import { useLayoutEffect, type RefObject } from "react";

export function useStickyQuickReferenceOffsets(
  pageRef: RefObject<HTMLElement | null>,
  refreshKey: string,
) {
  useLayoutEffect(() => {
    const page = pageRef.current;
    if (!page) return;

    const appHeader = document.querySelector<HTMLElement>(".app-header");
    const titleOne = page.querySelector<HTMLElement>(".quick-reference-section__heading");
    const titleTwo = [...page.querySelectorAll<HTMLElement>(".quick-reference-subsection__title")]
      .find((element) => !element.closest("[hidden]"));

    const updateOffsets = () => {
      const measurements = [
        ["--quick-reference-header-height", appHeader],
        ["--quick-reference-title-one-height", titleOne],
        ["--quick-reference-title-two-height", titleTwo],
      ] as const;
      measurements.forEach(([property, element]) => {
        const height = element?.getBoundingClientRect().height ?? 0;
        if (height > 0) page.style.setProperty(property, `${height}px`);
      });
    };

    updateOffsets();
    if (typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(updateOffsets);
    [appHeader, titleOne, titleTwo].forEach((element) => element && observer.observe(element));
    return () => observer.disconnect();
  }, [pageRef, refreshKey]);
}
