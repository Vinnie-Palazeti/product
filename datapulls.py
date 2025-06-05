import sqlite3
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass

### duplicated. bad
METRICS = ['users','gross_revenue', 'expenses','profit','new_users','returning_customers','impressions','traffic','buzz']

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

    if comparison_type:
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
    
def get_data(
    time_period: str,
    database_path: str='test_metrics.db',
    fields: Optional[List[str]] = ['users', 'gross_revenue', 'expenses'],
    comparison_type: Optional[str] = None,
    period_type: str = PeriodType.DAILY
) -> Dict[str, List[Tuple]]:
    
    valid_fields = set(sum([['date'], METRICS], []))

    if period_type == PeriodType.DAILY:
        default_fields = list(valid_fields)
    else:
        default_fields = list(valid_fields - {'date'})  # no 'date', month will be generated

    if fields is None:
        fields = default_fields
    
    else:
        invalid = set(fields) - valid_fields
        if invalid:
            raise ValueError(f"Invalid fields: {', '.join(invalid)}. Valid fields: {', '.join(valid_fields)}")
        if period_type == PeriodType.DAILY and 'date' not in fields:
            fields = ['date'] + fields

    date_ranges = get_comparison_dates(time_period, comparison_type, period_type)

    try:
        conn = sqlite3.connect(database_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        results = {}
        if period_type == PeriodType.DAILY:
            fields_str = ', '.join(fields)
            base_query = f"""
                SELECT {fields_str}
                FROM events
                WHERE date >= ? AND date <= ?
                ORDER BY date
            """
        else:  # MONTHLY
            agg_expressions = [f"SUM({field}) as {field}" for field in fields]
            agg_fields_str = ', '.join(agg_expressions)
            base_query = f"""
                SELECT 
                    strftime('%Y-%m', date) as date,
                    {agg_fields_str}
                FROM events
                WHERE date >= ? AND date <= ?
                GROUP BY strftime('%Y-%m', date)
                ORDER BY 1
            """

        for label, time_range in date_ranges.items():
            cursor.execute(base_query, (
                time_range.start_date.isoformat(),
                time_range.end_date.isoformat()
            ))
            results[label] = cursor.fetchall()
        return results

    except sqlite3.Error as e:
        raise Exception(f"Database error: {str(e)}")
    finally:
        if conn:
            conn.close()

def calculate_totals(
    results: Dict[str, List[Tuple]],
    fields: List[str]
    ) -> Dict[str, Dict[str, float]]:
    totals = {}
    for period, rows in results.items():
        summary = {}
        if not rows:
            totals[period] = {field: 0.0 for field in fields}
            continue
        for field in fields:
            values = [dict(row).get(field) for row in rows]
            if isinstance(values[0], str):
                continue
            summary[field] = sum(values)
        totals[period] = summary
    return totals



### Below I tried to infer the period from the date, but I have explicit options to select the grouping (the "GROUP" option)
## what I instead need to do is REACT to the selected options



## if last 90 days is select when we are on group, then the group should switch to DAY if it isn't already on day
### if last 3 months is selected, the group should SWITCH to month if it is not already on it!




# class PeriodType:
#     DAILY = "Day"
#     MONTHLY = "Month"

# class ComparisonType:
#     PREVIOUS_PERIOD = "Previous Period"
#     PREVIOUS_YEAR = "Previous Year"

# class TimeRange:
#     def __init__(self, start: date, end: date):
#         self.start = start
#         self.end = end

# def get_comparison_dates(
#     time_period: str,
#     comparison_type: Optional[str] = None
# ) -> Dict[str, TimeRange]:
    
#     daily_periods = {"Last 14 Days": 14, "Last 30 Days": 30, "Last 90 Days": 90}
#     monthly_periods = {
#         "Last Month": 1,
#         "Last 3 Months": 3,
#         "Last 6 Months": 6,
#         "Last 12 Months": 12,
#     }

#     today = datetime.now().date()

#     if time_period in daily_periods:
#         days = daily_periods[time_period]
#         end_date = today
#         start_date = end_date - timedelta(days=days)
#         period_type = PeriodType.DAILY
#     elif time_period in monthly_periods:
#         months = monthly_periods[time_period]
#         current_month_start = date(today.year, today.month, 1)
#         end_date = current_month_start - timedelta(days=1)
#         start_date = (current_month_start - relativedelta(months=months)).replace(day=1)
#         period_type = PeriodType.MONTHLY
#     else:
#         raise ValueError(f"Invalid time period: {time_period}")

#     selected_range = TimeRange(start_date, end_date)
#     result = {"selected_period": selected_range}

#     if comparison_type:
#         if comparison_type == ComparisonType.PREVIOUS_PERIOD:
#             comp_end = start_date - timedelta(days=1)
#             if period_type == PeriodType.DAILY:
#                 comp_start = comp_end - timedelta(days=days)
#             else:
#                 comp_start = (start_date - relativedelta(months=months)).replace(day=1)
#         elif comparison_type == ComparisonType.PREVIOUS_YEAR:
#             comp_start = start_date.replace(year=start_date.year - 1)
#             comp_end = end_date.replace(year=end_date.year - 1)
#         else:
#             raise ValueError("Invalid comparison type")

#         result["comparison_period"] = TimeRange(comp_start, comp_end)

#     return result


# def get_data(
#     time_period: str,
#     database_path: str = 'test_metrics.db',
#     fields: Optional[List[str]] = ['users', 'gross_revenue', 'expenses'],
#     comparison_type: Optional[str] = None
# ) -> Dict[str, List[Tuple]]:

#     daily_periods = {"Last 14 Days", "Last 30 Days", "Last 90 Days"}
#     monthly_periods = {"Last Month", "Last 3 Months", "Last 6 Months", "Last 12 Months"}

#     if time_period in daily_periods:
#         period_type = PeriodType.DAILY
#     elif time_period in monthly_periods:
#         period_type = PeriodType.MONTHLY
#     else:
#         raise ValueError(f"Invalid time period: {time_period}")

#     valid_fields = set(['date'] + METRICS)

#     # Adjust default fields based on period_type
#     if period_type == PeriodType.DAILY:
#         default_fields = list(valid_fields)
#     else:
#         default_fields = list(valid_fields - {'date'})  # 'date' will be replaced with 'month'

#     if fields is None:
#         fields = default_fields
#     else:
#         invalid = set(fields) - valid_fields
#         if invalid:
#             raise ValueError(f"Invalid fields: {', '.join(invalid)}. Valid fields: {', '.join(valid_fields)}")
#         if period_type == PeriodType.DAILY and 'date' not in fields:
#             fields = ['date'] + fields

#     date_ranges = get_comparison_dates(time_period, comparison_type)

#     try:
#         conn = sqlite3.connect(database_path)
#         conn.row_factory = sqlite3.Row
#         cursor = conn.cursor()
#         results = {}

#         if period_type == PeriodType.DAILY:
#             fields_str = ', '.join(fields)
#             base_query = f"""
#                 SELECT {fields_str}
#                 FROM events
#                 WHERE date >= ? AND date <= ?
#                 ORDER BY date
#             """
#         else:  # MONTHLY
#             agg_expressions = [f"SUM({field}) as {field}" for field in fields]
#             agg_fields_str = ', '.join(agg_expressions)
#             base_query = f"""
#                 SELECT 
#                     strftime('%Y-%m', date) as month,
#                     {agg_fields_str}
#                 FROM events
#                 WHERE date >= ? AND date <= ?
#                 GROUP BY strftime('%Y-%m', date)
#                 ORDER BY month
#             """

#         for label, time_range in date_ranges.items():
#             cursor.execute(base_query, (
#                 time_range.start.isoformat(),
#                 time_range.end.isoformat()
#             ))
#             results[label] = cursor.fetchall()

#         return results

#     except sqlite3.Error as e:
#         raise Exception(f"Database error: {str(e)}")
#     finally:
#         if conn:
#             conn.close()

