"""Refresh local Pal and item ID catalogs from Paldeck.

PalDefender's own documentation recommends paldeck.cc for ID lookup. The
downloaded catalogs are kept locally so the admin UI does not depend on the
website at runtime.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
HEADERS = {"User-Agent": "PalAdminPanel/1.0 catalog refresh"}
ITEMS_URL = "https://paldeck.cc/items"
PALS_URL = "https://paldeck.cc/pals"
ITEM_LOCALIZATION_URL = (
    "https://raw.githubusercontent.com/zaigie/palworld-server-tool/main/"
    "web/src/assets/items.json"
)
PAL_LOCALIZATION_URL = (
    "https://raw.githubusercontent.com/zaigie/palworld-server-tool/main/"
    "web/src/assets/pal.json"
)

ITEM_PATTERN = re.compile(
    r'\\"name\\":\\"([^"\\]*)\\",\\"description\\":.*?'
    r'\\"asset\\":\\"([^"\\]+)\\",\\"asset_image\\":\\"[^"\\]*\\",'
    r'\\"category\\":\\"([^"\\]*)\\".*?\\"legal_in_game\\":(true|false)',
    re.DOTALL,
)
PAL_PATTERN = re.compile(
    r'\\"name\\":\\"([^"\\]*)\\",\\"asset_name\\":\\"([^"\\]+)\\",'
    r'\\"dexkey\\":\\"([^"\\]+)\\".*?'
    r'\\"icon\\":\\"([^"\\]*)\\",\\"elements\\":(\{.*?\}),\\"stats\\"',
    re.DOTALL,
)


def fetch(url: str) -> str:
    request = Request(url, headers=HEADERS)
    with urlopen(request, timeout=45) as response:
        return response.read().decode("utf-8")


def main() -> None:
    item_localization = json.loads(fetch(ITEM_LOCALIZATION_URL))
    item_zh = {
        str(item.get("key", "")): str(item.get("name", ""))
        for item in item_localization.get("zh", [])
        if isinstance(item, dict)
    }
    pal_localization = json.loads(fetch(PAL_LOCALIZATION_URL))
    pal_zh = pal_localization.get("zh", {})
    if not isinstance(pal_zh, dict):
        pal_zh = {}

    item_html = fetch(ITEMS_URL)
    items_by_id: dict[str, dict[str, str]] = {}
    for name, item_id, category, legal in ITEM_PATTERN.findall(item_html):
        if legal == "true":
            items_by_id[item_id] = {
                "id": item_id,
                "name": name,
                "name_zh": item_zh.get(item_id, ""),
                "category": category,
            }

    pal_html = fetch(PALS_URL)
    pals_by_id: dict[str, dict[str, str]] = {}
    for name, pal_id, dex, _image, elements_blob in PAL_PATTERN.findall(pal_html):
        try:
            element_data = json.loads(elements_blob.replace(r'\"', '"'))
        except json.JSONDecodeError:
            element_data = {}
        elements = [
            str(value.get("name", ""))
            for value in element_data.values()
            if isinstance(value, dict) and value.get("name")
        ]
        pals_by_id[pal_id] = {
            "id": pal_id,
            "name": name,
            "name_zh": str(pal_zh.get(pal_id, "")),
            "dex": dex,
            "elements": elements,
        }

    if len(items_by_id) < 1000 or len(pals_by_id) < 200:
        raise RuntimeError(
            f"Catalog extraction returned too little data: items={len(items_by_id)}, pals={len(pals_by_id)}"
        )

    items = sorted(items_by_id.values(), key=lambda row: (row["category"], row["name"], row["id"]))
    pals = sorted(
        pals_by_id.values(),
        key=lambda row: (int(re.match(r"\d+", row["dex"]).group()), row["dex"], row["name"]),
    )
    DATA_DIR.mkdir(exist_ok=True)
    (DATA_DIR / "items.json").write_text(
        json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (DATA_DIR / "pals.json").write_text(
        json.dumps(pals, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    meta = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "items": len(items),
        "pals": len(pals),
        "sources": {
            "items": ITEMS_URL,
            "pals": PALS_URL,
            "item_localization": ITEM_LOCALIZATION_URL,
            "pal_localization": PAL_LOCALIZATION_URL,
        },
        "item_filter": "legal_in_game=true",
        "localized_items": sum(bool(item["name_zh"]) for item in items),
        "localized_pals": sum(bool(pal["name_zh"]) for pal in pals),
    }
    (DATA_DIR / "catalog_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"Catalogs updated: {len(items)} legal items "
        f"({sum(bool(item['name_zh']) for item in items)} Chinese names), "
        f"{len(pals)} pals ({sum(bool(pal['name_zh']) for pal in pals)} Chinese names)"
    )


if __name__ == "__main__":
    main()
