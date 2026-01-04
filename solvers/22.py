from __future__ import annotations

from typing import List


def name_value(name: str) -> int:
    """Alphabetical value: A=1, ..., Z=26."""
    return sum((ord(c) - ord("A") + 1) for c in name)


def load_names() -> List[str]:
    # Common locations used by various problem runners
    candidates = [
        "names.txt",
        "0022_names.txt",
        "resources/documents/0022_names.txt",
        "resources/0022_names.txt",
    ]
    last_err: Exception | None = None

    for path in candidates:
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = f.read().strip()
            # File format: "MARY","PATRICIA",...
            parts = raw.split(",")
            return [p.strip().strip('"') for p in parts if p.strip()]
        except OSError as e:
            last_err = e

    raise FileNotFoundError(
        "Could not find names file. Tried: " + ", ".join(candidates)
    ) from last_err


def total_name_scores(names: List[str]) -> int:
    names_sorted = sorted(names)
    total = 0
    for i, nm in enumerate(names_sorted, start=1):
        total += i * name_value(nm)
    return total


def main() -> None:
    names = load_names()
    names_sorted = sorted(names)

    # Given example: COLIN is 938th and has score 49714 (in the provided dataset).
    colin_pos = names_sorted.index("COLIN") + 1
    colin_score = colin_pos * name_value("COLIN")
    assert colin_pos == 938
    assert colin_score == 49714

    ans = total_name_scores(names)


    print(ans)


if __name__ == "__main__":
    main()
