import type { ElementType, HTMLAttributes, ReactNode } from "react";

export type TypographyVariant = "brand" | "display" | "question" | "title" | "heading" | "body" | "label" | "utility";
interface TypographyProps extends HTMLAttributes<HTMLElement> {
  as?: ElementType;
  variant?: TypographyVariant;
  children: ReactNode;
}

export function Typography({ as: Component = "p", variant = "body", className = "", children, ...props }: TypographyProps) {
  return <Component className={`type type--${variant} ${className}`.trim()} {...props}>{children}</Component>;
}
