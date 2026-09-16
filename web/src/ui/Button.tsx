import type { ButtonHTMLAttributes, ReactNode } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  tone?: "primary" | "secondary";
  children: ReactNode;
}

export function Button({ tone = "primary", className = "", children, ...props }: ButtonProps) {
  return <button className={`button button--${tone} ${className}`.trim()} {...props}>{children}</button>;
}
