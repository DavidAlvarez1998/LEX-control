#!/usr/bin/env python3
"""Idempotently append dark: variants to base slate/white utility classes.

Only matches tokens at a class boundary (after space/quote/backtick), so
variant-prefixed classes (hover:, focus:, etc.) and already-dark classes are
left untouched. Re-running is a no-op (negative lookahead guards each pair).
"""
import re
import sys

# light base class -> dark companion to append
MAP = [
    ("bg-white", "dark:bg-slate-900"),
    ("bg-slate-50", "dark:bg-slate-800"),
    ("bg-slate-100", "dark:bg-slate-800"),
    ("border-slate-200", "dark:border-slate-800"),
    ("border-slate-100", "dark:border-slate-800"),
    ("text-slate-800", "dark:text-slate-100"),
    ("text-slate-700", "dark:text-slate-200"),
    ("text-slate-600", "dark:text-slate-300"),
    ("text-slate-500", "dark:text-slate-400"),
    ("text-slate-400", "dark:text-slate-500"),
    # accent badges / status colors
    ("bg-emerald-50", "dark:bg-emerald-950/40"),
    ("bg-amber-50", "dark:bg-amber-950/40"),
    ("bg-indigo-50", "dark:bg-indigo-950/40"),
    ("bg-red-50", "dark:bg-red-950/40"),
    ("text-emerald-700", "dark:text-emerald-300"),
    ("text-emerald-600", "dark:text-emerald-400"),
    ("text-amber-700", "dark:text-amber-300"),
    ("text-indigo-700", "dark:text-indigo-300"),
    ("text-indigo-600", "dark:text-indigo-400"),
    ("text-red-700", "dark:text-red-300"),
    ("text-red-600", "dark:text-red-400"),
    ("text-rose-600", "dark:text-rose-400"),
]

def process(text: str) -> tuple[str, int]:
    total = 0
    for light, dark in MAP:
        pat = re.compile(
            r"(?<=[\s\"'`])" + re.escape(light) + r"\b(?!\s+" + re.escape(dark) + r")"
        )
        text, n = pat.subn(light + " " + dark, text)
        total += n
    return text, total

def main(paths):
    grand = 0
    for p in paths:
        with open(p, "r", encoding="utf-8") as f:
            src = f.read()
        out, n = process(src)
        if n:
            with open(p, "w", encoding="utf-8") as f:
                f.write(out)
        print(f"{n:4d}  {p}")
        grand += n
    print(f"---- total substitutions: {grand}")

if __name__ == "__main__":
    main(sys.argv[1:])
