import type { ReactNode } from "react";
import { Typography } from "./Typography";

export function MessagePage({ title, icon }: { title: string; icon?: ReactNode }) {
  return <main className="message-page">{icon}<Typography as="h1" variant="title">{title}</Typography></main>;
}
