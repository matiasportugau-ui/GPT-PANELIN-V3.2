"""Handler for the catalog_search MCP tool.

Searches shopify_catalog_v1.json for products by name, category, or keyword.
Returns lightweight results (id, title, handle, type, vendor, tags).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

KB_ROOT = Path(__file__).resolve().parent.parent.parent
CATALOG_FILE = KB_ROOT / "shopify_catalog_v1.json"

_catalog_data: list[dict[str, Any]] | None = None


def _load_catalog() -> list[dict[str, Any]]:
    global _catalog_data
    if _catalog_data is None:
        with open(CATALOG_FILE, encoding="utf-8") as f:
            raw = json.load(f)
        _catalog_data = raw if isinstance(raw, list) else raw.get("products", [])
    return _catalog_data


def _normalize(text: str) -> str:
    return text.lower().strip()


CATEGORY_MAP = {
    "techo": ["techo", "roof", "isoroof", "isodec", "cubierta"],
    "pared": ["pared", "wall", "isowall", "isopanel"],
    "camara": ["camara", "frio", "isofrig", "frigorifico"],
    "accesorio": ["accesorio", "accessory", "fijacion", "tornillo", "cumbrera", "babeta"],
}


def _to_contract_result(product: dict[str, Any]) -> dict[str, Any]:
    """Transform a product record to the v1 contract result format."""
    product_id = product.get("id")
    # Convert numeric IDs to strings as per contract
    if isinstance(product_id, (int, float)):
        product_id = str(int(product_id))
    elif product_id is None:
        product_id = ""
    else:
        product_id = str(product_id)
    
    name = product.get("title", "")
    
    # Map product_type or tags to category
    ptype = _normalize(product.get("product_type", ""))
    tags = _normalize(str(product.get("tags", "")))
    searchable = f"{ptype} {tags}"
    
    category = "unknown"
    for cat, keywords in CATEGORY_MAP.items():
        if any(kw in searchable for kw in keywords):
            category = cat
            break
    
    # Build URL from handle if available
    handle = product.get("handle", "")
    url = f"https://bromyros.com/products/{handle}" if handle else ""
    
    result = {
        "product_id": product_id,
        "name": name,
        "category": category
    }
    
    if url:
        result["url"] = url
    
    # Note: score would require actual relevance calculation, omitting for now
    
    return result


async def handle_catalog_search(arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute catalog_search tool and return results in v1 contract format."""
    query = arguments.get("query", "")
    category = arguments.get("category", "all")
    limit = arguments.get("limit", 5)

    # Validate query
    if not query:
        return {
            "ok": False,
            "contract_version": "v1",
            "error": {
                "code": "QUERY_TOO_SHORT",
                "message": "Query parameter is required"
            }
        }
    
    if len(query) < 2:
        return {
            "ok": False,
            "contract_version": "v1",
            "error": {
                "code": "QUERY_TOO_SHORT",
                "message": f"Query must be at least 2 characters long (received: {len(query)})",
                "details": {"query": query, "length": len(query)}
            }
        }
    
    if len(query) > 120:
        return {
            "ok": False,
            "contract_version": "v1",
            "error": {
                "code": "QUERY_TOO_SHORT",
                "message": f"Query must be at most 120 characters long (received: {len(query)})",
                "details": {"query": query[:50] + "...", "length": len(query)}
            }
        }
    
    # Validate category
    valid_categories = ["techo", "pared", "camara", "accesorio", "all"]
    if category not in valid_categories:
        return {
            "ok": False,
            "contract_version": "v1",
            "error": {
                "code": "INVALID_CATEGORY",
                "message": f"Invalid category '{category}'. Must be one of: {', '.join(valid_categories)}",
                "details": {"received": category, "valid_options": valid_categories}
            }
        }
    
    # Validate limit
    if not isinstance(limit, int) or limit < 1 or limit > 30:
        return {
            "ok": False,
            "contract_version": "v1",
            "error": {
                "code": "INVALID_CATEGORY",
                "message": f"Limit must be an integer between 1 and 30 (received: {limit})",
                "details": {"received": limit, "min": 1, "max": 30}
            }
        }

    try:
        catalog = _load_catalog()
        norm_query = _normalize(query)

        # Determine category keywords
        category_keywords: list[str] = []
        if category != "all" and category in CATEGORY_MAP:
            category_keywords = CATEGORY_MAP[category]

        results: list[dict[str, Any]] = []
        for product in catalog:
            title = _normalize(product.get("title", ""))
            ptype = _normalize(product.get("product_type", ""))
            tags = _normalize(str(product.get("tags", "")))
            handle = _normalize(product.get("handle", ""))
            searchable = f"{title} {ptype} {tags} {handle}"

            if norm_query not in searchable:
                continue

            if category_keywords:
                if not any(kw in searchable for kw in category_keywords):
                    continue

            results.append(_to_contract_result(product))
            if len(results) >= limit:
                break

        return {
            "ok": True,
            "contract_version": "v1",
            "results": results
        }
    
    except FileNotFoundError:
        return {
            "ok": False,
            "contract_version": "v1",
            "error": {
                "code": "CATALOG_UNAVAILABLE",
                "message": "Catalog file not found",
                "details": {"file": str(CATALOG_FILE)}
            }
        }
    except Exception as e:
        return {
            "ok": False,
            "contract_version": "v1",
            "error": {
                "code": "INTERNAL_ERROR",
                "message": f"Internal error during catalog search: {str(e)}",
                "details": {"exception_type": type(e).__name__}
            }
        }
