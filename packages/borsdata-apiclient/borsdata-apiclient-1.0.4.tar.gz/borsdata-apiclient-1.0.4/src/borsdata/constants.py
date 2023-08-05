from enum import Enum


class ReportType(Enum):
    YEAR = "year"
    R12 = "r12"
    QUARTER = "quarter"


class PriceType(Enum):
    LOW = "low"
    MEAN = "mean"
    HIGH = "high"


class CalculationGroup(Enum):
    LAST = "last"
    WEEK1 = "1week"
    DAY1 = "1day"
    DAY3 = "3day"
    DAY5 = "5day"
    DAY7 = "7day"
    DAY10 = "10day"
    DAY20 = "20day"
    DAY30 = "30day"
    DAY50 = "50day"
    DAY70 = "70day"
    DAY100 = "100day"
    DAY200 = "200day"

    MONTH1 = "1month"
    MONTH3 = "3month"
    MONTH6 = "6month"

    YEAR1 = "1year"
    YEAR3 = "3year"
    YEAR5 = "5year"
    YEAR7 = "7year"
    YEAR10 = "10year"
    YEAR15 = "15year"

    MA20MA50 = "ma20ma50"
    MA20MA70 = "ma20ma70"
    MA50MA200 = "ma50ma200"
    MA5MA20 = "ma5ma20"


class Calculation(Enum):
    HIGH = "high "
    LATEST = "latest"
    LOW = "low"
    MEAN = "mean"
    SUM = "sum"
    CAGR = "cagr"
    DEFAULT = "default"
    RETURN = "return"
    GROWTH = "growth"
    DIFF = "diff"
    TREND = "trend"
    OVER = "over"
    UNDER = "under"
    RANK = "rank"
    POINT = "point"
    QUARTER = "quarter"
    STABIL = "stabil"
