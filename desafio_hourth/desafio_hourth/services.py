from datetime import datetime, timedelta
from itertools import groupby
from typing import List

import requests

from .consts import RAW_DATA_API


def convert_str_to_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")


def convert_date_to_str(date: datetime) -> str:
    return datetime.strftime(date, "%Y-%m-%d")


def date_range(start, end) -> List[str]:
    delta = end - start
    days = [convert_date_to_str(start + timedelta(days=i)) for i in range(delta.days + 1)]
    return days


def get_raw_data() -> List[dict]:
    data = requests.get(RAW_DATA_API).json()
    return data


def filter_data_by_date(data: List[dict], start_date: datetime, end_date: datetime) -> List[dict]:
    date_filtered = [item for item in data if start_date <= convert_str_to_date(item["consult_date"]) <= end_date]
    return date_filtered


def fill_dates_zero(dates: dict, list_group: List[dict], start_date: datetime, end_date: datetime):
    if start_date and end_date:
        min_date = start_date
        max_date = end_date
    else:
        min_date = min(list_group, key=lambda item: item["consult_date"])["consult_date"]
        min_date = convert_str_to_date(min_date)
        max_date = max(list_group, key=lambda item: item["consult_date"])["consult_date"]
        max_date = convert_str_to_date(max_date)

    dates_between = date_range(min_date, max_date)
    dates_zero = {date: 0 for date in dates_between if date not in dates}
    dates.update(dates_zero)


def data_group_by_product(data: List[dict], start_date: datetime, end_date: datetime) -> List[dict]:
    data_group = groupby(sorted(data, key=lambda item: item["product_url"]), key=lambda item: item["product_url"])
    result = []
    for key, group in data_group:
        list_group = list(group)

        dates = {item["consult_date"]: item["vendas_no_dia"] for item in list_group}

        fill_dates_zero(dates, list_group, start_date, end_date)

        total_sales = sum(dates[date] for date in dates)

        result.append({
            "product_url__image": list_group[0]["product_url__image"],
            "product_url": key,
            "product_url__created_at": list_group[0]["product_url__created_at"],
            "total_sales": total_sales,
            **dates
        })
    return result


def get_data_group_by_product(start_date: datetime = None, end_date: datetime = None) -> List[dict]:
    data = get_raw_data()
    if start_date and end_date:
        data = filter_data_by_date(data, start_date, end_date)

    return data_group_by_product(data, start_date=start_date, end_date=end_date)
