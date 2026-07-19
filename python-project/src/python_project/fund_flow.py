from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class FundStock:
    name: str
    code: str
    price: float
    change_percent: float
    net_inflow: float
    inflow_ratio: float
    signal: str


@dataclass(frozen=True)
class SectorFundFlow:
    id: str
    name: str
    description: str
    net_inflow: float
    main_inflow: float
    change_percent: float
    turnover: float
    stocks: list[FundStock]


SECTOR_FUND_FLOWS: list[SectorFundFlow] = [
    SectorFundFlow(
        id="robotics",
        name="机器人板块",
        description="工业机器人、减速器、智能制造方向",
        net_inflow=18.62,
        main_inflow=12.38,
        change_percent=2.84,
        turnover=286.4,
        stocks=[
            FundStock("拓普集团", "601689", 67.32, 4.18, 3.24, 10.6, "主力持续流入"),
            FundStock("绿的谐波", "688017", 118.45, 6.72, 2.58, 13.2, "放量突破"),
            FundStock("埃斯顿", "002747", 22.18, 3.11, 1.86, 8.4, "趋势增强"),
            FundStock("鸣志电器", "603728", 53.76, -1.28, -0.74, -3.1, "短线分歧"),
        ],
    ),
    SectorFundFlow(
        id="cpo",
        name="CPO板块",
        description="光模块、光通信、算力基础设施方向",
        net_inflow=26.91,
        main_inflow=19.47,
        change_percent=3.36,
        turnover=412.8,
        stocks=[
            FundStock("中际旭创", "300308", 183.65, 5.42, 5.66, 12.9, "强势流入"),
            FundStock("新易盛", "300502", 142.08, 4.96, 4.31, 11.7, "机构加仓"),
            FundStock("天孚通信", "300394", 96.52, 2.74, 2.19, 7.8, "量价配合"),
            FundStock("光迅科技", "002281", 41.26, -0.92, -0.68, -2.5, "资金回撤"),
        ],
    ),
    SectorFundFlow(
        id="semiconductor",
        name="半导体板块",
        description="设备、材料、先进封装方向",
        net_inflow=11.73,
        main_inflow=7.82,
        change_percent=1.58,
        turnover=368.9,
        stocks=[
            FundStock("北方华创", "002371", 337.18, 2.44, 2.88, 8.1, "稳步流入"),
            FundStock("中微公司", "688012", 168.36, 1.76, 1.72, 6.4, "震荡走强"),
            FundStock("长电科技", "600584", 36.92, 1.22, 1.14, 5.2, "温和吸筹"),
            FundStock("华海清科", "688120", 198.70, -0.84, -0.43, -1.9, "等待放量"),
        ],
    ),
]


def format_yi(value: float) -> str:
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}亿"


def format_percent(value: float) -> str:
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"


def get_sector_fund_flows() -> dict[str, Any]:
    sectors = []
    total_net_inflow = 0.0

    for sector in SECTOR_FUND_FLOWS:
        total_net_inflow += sector.net_inflow
        sector_data = asdict(sector)
        sector_data["net_inflow_text"] = format_yi(sector.net_inflow)
        sector_data["main_inflow_text"] = format_yi(sector.main_inflow)
        sector_data["change_percent_text"] = format_percent(sector.change_percent)
        sector_data["turnover_text"] = format_yi(sector.turnover)

        for stock in sector_data["stocks"]:
            stock["price_text"] = f"{stock['price']:.2f}"
            stock["change_percent_text"] = format_percent(stock["change_percent"])
            stock["net_inflow_text"] = format_yi(stock["net_inflow"])
            stock["inflow_ratio_text"] = format_percent(stock["inflow_ratio"])

        sectors.append(sector_data)

    hot_sector = max(SECTOR_FUND_FLOWS, key=lambda item: item.net_inflow)
    return {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total_net_inflow": total_net_inflow,
            "total_net_inflow_text": format_yi(total_net_inflow),
            "sector_count": len(SECTOR_FUND_FLOWS),
            "hot_sector": hot_sector.name,
            "hot_sector_net_inflow_text": format_yi(hot_sector.net_inflow),
        },
        "sectors": sectors,
    }
