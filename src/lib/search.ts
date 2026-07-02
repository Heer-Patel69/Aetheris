import Fuse from "fuse.js";
import { rfcs } from "@/data/rfcs";
import { specs } from "@/data/specs";
import { skills } from "@/data/skills";
import { docs } from "@/data/docs";

export interface SearchResult {
  id: string;
  title: string;
  type: "RFC" | "SPEC" | "Skill" | "Doc";
  href: string;
  description: string;
}

const items: SearchResult[] = [
  ...rfcs.map(r => ({ id: r.id, title: r.title, type: "RFC" as const, href: `/rfc-explorer`, description: r.purpose })),
  ...specs.map(s => ({ id: s.id, title: s.title, type: "SPEC" as const, href: `/spec-explorer`, description: s.purpose })),
  ...skills.map(sk => ({ id: sk.id, title: sk.name, type: "Skill" as const, href: `/skills-marketplace`, description: sk.description })),
  ...docs.map(d => ({ id: d.slug, title: d.title, type: "Doc" as const, href: `/docs`, description: d.content.substring(0, 100) }))
];

const fuse = new Fuse(items, {
  keys: ["id", "title", "description"],
  threshold: 0.3
});

export function searchAll(query: string): SearchResult[] {
  if (!query) return [];
  return fuse.search(query).map(r => r.item);
}
