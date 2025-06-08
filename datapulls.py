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
        
        # print(result["comparison_period"])
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




