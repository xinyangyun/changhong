from __future__ import annotations

import math
from datetime import datetime
from typing import Any


MONITORED_STOCKS = {
    "600519": {"name": "贵州茅台", "initial_price": 1482.50},
    "300308": {"name": "中际旭创", "initial_price": 183.65},
    "601689": {"name": "拓普集团", "initial_price": 67.32},
}


def get_t_monitor_quote(code: str = "600519") -> dict[str, Any]:
    normalized_code = "".join(character for character in code if character.isdigit())[:6]
    normalized_code = normalized_code or "600519"
    stock = MONITORED_STOCKS.get(
        normalized_code,
        {"name": "自选股", "initial_price": 25.00},
    )
    phase = datetime.now().timestamp() / 5
    initial_price = stock["initial_price"]
    average_price = initial_price * (1.02 + math.sin(phase / 6) * 0.0004)
    current_price = initial_price * (1.05 + math.sin(phase) * 0.0004)

    return {
        "stock": {"code": normalized_code, "name": stock["name"]},
        "current_price": round(current_price, 2),
        "initial_price": round(initial_price, 2),
        "average_price": round(average_price, 2),
        "change_percent": round((current_price / initial_price - 1) * 100, 2),
        "average_change_percent": round((average_price / initial_price - 1) * 100, 2),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "is_mock": True,
    }
