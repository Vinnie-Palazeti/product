import sqlite3
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from components.relationships import KPI_DIMENSIONS


@dataclass
class TimeRange:
    start_date: date
    end_date: date

class ComparisonType:
    PREVIOUS_PERIOD = "Previous Period"
    PREVIOUS_YEAR = "Previous Year"

class PeriodType:
    DAILY = "Day"
    MONTHLY = "Month"

def get_comparison_dates(
    time_period: str,
    comparison_type: Optional[str] = None,
    period_type: str = PeriodType.DAILY
) -> Dict[str, TimeRange]:
    
    if period_type == PeriodType.DAILY:
        valid_periods = {"Last 14 Days": 14, "Last 30 Days": 30, "Last 90 Days": 90}
        days = valid_periods.get(time_period)
        if days is None:
            raise ValueError(f"Invalid time period: {time_period}")
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
    
    elif period_type == PeriodType.MONTHLY:
        valid_periods = {
            "Last 3 Months": 3,
            "Last 6 Months": 6,
            "Last 12 Months": 12,
        }
        months = valid_periods.get(time_period)
        if months is None:
            raise ValueError(f"Invalid monthly time period: {time_period}")
        today = datetime.now().date()
        current_month_start = date(today.year, today.month, 1)
        end_date = current_month_start - timedelta(days=1)
        start_date = (current_month_start - relativedelta(months=months)).replace(day=1)

    else:
        raise ValueError("Period type must be 'Day' or 'Month'")

    selected_range = TimeRange(start_date, end_date)
    result = {"selected_period": selected_range}

    if comparison_type != 'No Comparison':
        # print(comparison_type, start_date, end_date)
        if comparison_type == ComparisonType.PREVIOUS_PERIOD:
            comp_end = start_date - timedelta(days=1)
            if period_type == PeriodType.DAILY:
                comp_start = comp_end - timedelta(days=days)
            else:
                comp_start = (start_date - relativedelta(months=months)).replace(day=1)
        elif comparison_type == ComparisonType.PREVIOUS_YEAR:
            comp_start = start_date.replace(year=start_date.year - 1)
            comp_end = end_date.replace(year=end_date.year - 1)
        else:
            raise ValueError("Invalid comparison type")
        result["comparison_period"] = TimeRange(comp_start, comp_end)
    return result


def format_results(
    rows: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Given flat KPI‐rows like
      {'date':'2025-06-01','kpi':'revenue','total_value':120000.3}, …
    Pivot them into one dict per date, then return a list sorted by date:
      [
        {'date':'2025-06-01','revenue':120000.3, 'expenses':…},
        {'date':'2025-06-02', …},
        …
      ]
    """
    # Step 1: aggregate into a dict of date → {kpi: value}
    by_date: Dict[str, Dict[str, float]] = {}
    for r in rows:
        date = r['date']
        by_date.setdefault(date, {})[r['kpi']] = r['total_value']

    # Step 2: build a sorted list of dicts
    formatted: List[Dict[str, Any]] = []
    for date in sorted(by_date):  # ISO dates sort correctly as strings
        entry = {'date': date}
        entry.update(by_date[date])
        formatted.append(entry)
    return formatted

def get_data(
    fields: List[str],
    time_period: str,
    database_path: str = 'test_metrics.db',
    comparison_type: Optional[str] = None,
    period_type: PeriodType = PeriodType.DAILY,
    dimension_list: Optional[List[str]] = None
) -> Dict[str, List[sqlite3.Row]]:
    """
    Fetch summed KPI values by day or month, grouped by KPI.

    Args:
      fields:        list of KPI names (e.g. ['revenue','expenses'])
      time_period:     a period string to pass into get_comparison_dates
      comparison_type: optional comparison (e.g. 'vs_last_year')
      period_type:     DAILY or MONTHLY
      dimension_list:  optional list of dimension names to filter on

    Returns:
      A dict mapping each comparison‐range label to a list of sqlite3.Row, each row with:
        • date (or period)
        • kpi
        • total_value
    """
    # 1. compute the date windows
    date_ranges = get_comparison_dates(time_period, comparison_type, period_type)

    # 2. choose date vs. month expressions
    if period_type == PeriodType.DAILY:
        date_expr = "date"
        grp_date = "date"
        ord_date = "date"
    else:
        date_expr = "strftime('%Y-%m', date) AS period"
        grp_date = "period"
        ord_date = "period"

    # 3. build SQL with KPI‐IN and optional dimension filter
    kpi_ph = ", ".join("?" for _ in fields)
    sql = f"""
    SELECT
      {date_expr},
      kpi,
      SUM(value) AS total_value
    FROM events
    WHERE
      kpi IN ({kpi_ph})
      AND date BETWEEN ? AND ?
    """

    params_extra: List[str] = []
    if dimension_list:
        dim_ph = ", ".join("?" for _ in dimension_list)
        sql += f"  AND dimension IN ({dim_ph})\n"
        params_extra = dimension_list

    sql += f"""
    GROUP BY
      {grp_date},
      kpi
    ORDER BY
      {ord_date},
      kpi
    """

    # 4. execute one query per comparison window
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    results: Dict[str, List[sqlite3.Row]] = {}

    try:
        for label, rng in date_ranges.items():
            params = (
                fields
                + [rng.start_date.isoformat(), rng.end_date.isoformat()]
                + params_extra
            )
            cur.execute(sql, params)
            out = cur.fetchall()
            results[label] = format_results(out)
        return results
    finally:
        conn.close()
        
        
       

def get_bar_data(
    kpi: str,
    dimension_list: List[str],
    time_period: str,
    database_path: str = 'test_metrics.db',
    comparison_type: Optional[str] = None,
    period_type: PeriodType = PeriodType.DAILY
) -> Dict[str, List[sqlite3.Row]]:
    """
    Returns total KPI values for each (dimension, category) over the given time window.

    Args:
      kpi:             the single KPI to filter on (e.g. 'revenue')
      dimension_list:  list of dimension names to include (e.g. ['Sales Channel', 'Time of Day'])
      time_period:     period string for get_comparison_dates
      comparison_type: optional comparison (e.g. 'vs_last_year')
      period_type:     DAILY or MONTHLY

    Returns:
      A dict mapping each comparison‐range label to a list of sqlite3.Row, each row with:
        • dimension
        • category
        • total_value
    """
    if not dimension_list:
        dimension_list = list(KPI_DIMENSIONS.get(kpi).keys())
    # compute the date windows
    date_ranges = get_comparison_dates(time_period, comparison_type, period_type)
    # prepare SQL placeholders for dimensions
    dim_ph = ", ".join("?" for _ in dimension_list)

    sql = f"""
        SELECT
            dimension,
            category,
            SUM(value) AS total_value,
            SUM(SUM(value)) OVER (PARTITION BY dimension) AS dimension_total            
        FROM events
        WHERE
            kpi = ?
            AND dimension IN ({dim_ph})
            AND date BETWEEN ? AND ?
        GROUP BY
            dimension,
            category
        ORDER BY
            dimension,
            total_value DESC
    """

    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    results: Dict[str, List[sqlite3.Row]] = {}

    try:
        for label, rng in date_ranges.items():
            params = (
                [kpi]
                + dimension_list
                + [rng.start_date.isoformat(), rng.end_date.isoformat()]
            )
            cur.execute(sql, params)
            out=cur.fetchall()
            results[label]=[dict(i) for i in out]
        return results

    except sqlite3.Error as e:
        raise RuntimeError(f"Database error: {e}")
    finally:
        conn.close()
        
def calculate_totals(
    results: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, Dict[str, float]]:
    """
    Given:
      results = {
        "current": [
          {'date':'2025-06-01','expenses':49778.47,'revenue':82555.97,'profit':32777.5},
          {'date':'2025-06-02','expenses':55073.74,'revenue':83259.84,'profit':28186.1},
          …
        ],
        "previous": [ … ]
      }
    Returns:
      {
        "current":  {'expenses': 104852.21, 'revenue': 165815.81, 'profit': 60963.6, …},
        "previous": { … }
      }
    """
    totals: Dict[str, Dict[str, float]] = {}

    for period, rows in results.items():
        acc: Dict[str, float] = {}
        for row in rows:
            for key, val in row.items():
                if key == "date":
                    continue
                # assume any non-date field is numeric
                acc[key] = acc.get(key, 0.0) + val
        totals[period] = acc
    return totals