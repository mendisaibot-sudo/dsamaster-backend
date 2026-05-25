#!/usr/bin/env python3
"""Combine all content JSON files into a single all_content.json"""
import json
import re
from pathlib import Path

CONTENT_DIR = Path(__file__).parent.parent / "content_data"
OUT = CONTENT_DIR / "all_content.json"


def normalize_content(lesson):
    """Ensure lessons have content_json and exercises/code_examples fields."""
    lesson = dict(lesson)
    # Convert plain 'content' string to content_json if needed
    if "content_json" not in lesson and "content" in lesson and isinstance(lesson["content"], str):
        lesson["content_json"] = {
            "blocks": [{"type": "text", "text": lesson["content"]}]
        }
    # Ensure exercises and code_examples exist
    lesson.setdefault("exercises", [])
    lesson.setdefault("code_examples", [])
    # Ensure order_index
    lesson.setdefault("order_index", 0)
    return lesson


def load_03():
    path = CONTENT_DIR / "03_frameworks_dsa.json"
    with open(path) as f:
        data = json.load(f)
    for cat_slug, cat_data in data.items():
        if not isinstance(cat_data, dict):
            continue
        cat_data["topics"] = cat_data.get("topics", [])
        cat_data["lessons"] = [normalize_content(l) for l in cat_data.get("lessons", [])]
    return data


def load_master():
    path = CONTENT_DIR / "master_content.json"
    with open(path) as f:
        data = json.load(f)
    for cat_slug, cat_data in data.items():
        if not isinstance(cat_data, dict):
            continue
        cat_data["topics"] = cat_data.get("topics", [])
        cat_data["lessons"] = [normalize_content(l) for l in cat_data.get("lessons", [])]
    return data


def load_test():
    path = CONTENT_DIR / "test.json"
    with open(path) as f:
        d = json.load(f)
    result = {}
    categories = d.get("categories", [])
    topics = d.get("topics", [])
    lessons = [normalize_content(l) for l in d.get("lessons", [])]
    for cat in categories:
        cat_slug = cat["slug"]
        cat_topics = [t for t in topics if t.get("category_slug", cat_slug) == cat_slug]
        # fallback: infer from topic slug prefixes
        if not cat_topics:
            prefix = cat.get("slug_prefix", cat_slug)
            cat_topics = [t for t in topics if t["slug"].startswith(prefix)]
        cat_lessons = [l for l in lessons if l["topic_slug"] in {t["slug"] for t in cat_topics}]
        result[cat_slug] = {
            "category": cat,
            "topics": cat_topics,
            "lessons": cat_lessons,
        }
    return result


def load_01():
    path = CONTENT_DIR / "01_web_sql_python.json"
    with open(path) as f:
        d = json.load(f)
    result = {}
    categories = d.get("categories", [])
    topics = d.get("topics", [])
    lessons = [normalize_content(l) for l in d.get("lessons", [])]
    prefix_map = {
        "html": "html",
        "css": "css",
        "javascript": "js",
        "python": "python",
        "sql": "sql",
    }
    for cat in categories:
        cat_slug = cat["slug"]
        prefix = prefix_map.get(cat_slug, cat_slug)
        cat_topics = [t for t in topics if t["slug"].startswith(prefix + "-") or t["slug"] == prefix]
        cat_lessons = [l for l in lessons if l["topic_slug"] in {t["slug"] for t in cat_topics}]
        result[cat_slug] = {
            "category": cat,
            "topics": cat_topics,
            "lessons": cat_lessons,
        }
    return result


def merge(*datasets):
    merged = {}
    for ds in datasets:
        for cat_slug, cat_data in ds.items():
            if cat_slug not in merged:
                merged[cat_slug] = {
                    "category": dict(cat_data["category"]),
                    "topics": list(cat_data.get("topics", [])),
                    "lessons": list(cat_data.get("lessons", [])),
                }
            else:
                # Merge topics by slug
                existing_slugs = {t["slug"] for t in merged[cat_slug]["topics"]}
                for t in cat_data.get("topics", []):
                    if t["slug"] not in existing_slugs:
                        merged[cat_slug]["topics"].append(dict(t))
                        existing_slugs.add(t["slug"])
                # Merge lessons by slug
                existing_l_slugs = {l["slug"] for l in merged[cat_slug]["lessons"]}
                for l in cat_data.get("lessons", []):
                    if l["slug"] not in existing_l_slugs:
                        merged[cat_slug]["lessons"].append(dict(l))
                        existing_l_slugs.add(l["slug"])
    return merged


def deduplicate_topics_by_slug(topics):
    seen = set()
    out = []
    for t in topics:
        if t["slug"] not in seen:
            seen.add(t["slug"])
            out.append(dict(t))
    return out


def deduplicate_lessons_by_slug(lessons):
    seen = set()
    out = []
    for l in lessons:
        if l["slug"] not in seen:
            seen.add(l["slug"])
            out.append(dict(l))
    return out


def main():
    print("Combining content files...")
    ds03 = load_03()
    ds_master = load_master()
    ds_test = load_test()
    ds_01 = load_01()

    merged = merge(ds03, ds_master, ds_test, ds_01)

    # Deduplicate and order
    for cat_slug, cat_data in merged.items():
        cat_data["topics"] = deduplicate_topics_by_slug(cat_data["topics"])
        cat_data["lessons"] = deduplicate_lessons_by_slug(cat_data["lessons"])
        # Sort topics by order_index or name
        cat_data["topics"].sort(key=lambda t: t.get("order_index", 0) or t["slug"])
        # Sort lessons by order_index, then slug
        cat_data["lessons"].sort(key=lambda l: (l.get("order_index", 0), l["slug"]))

    with open(OUT, "w") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)

    total_cats = len(merged)
    total_topics = sum(len(c["topics"]) for c in merged.values())
    total_lessons = sum(len(c["lessons"]) for c in merged.values())
    print(f"Wrote {OUT}")
    print(f"  Categories: {total_cats}")
    print(f"  Topics: {total_topics}")
    print(f"  Lessons: {total_lessons}")


if __name__ == "__main__":
    main()
