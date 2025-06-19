from dataclasses import dataclass, field
from components.svg import *

@dataclass
class DashContent:
    time: str='Last 14 Days'
    comparison: str='No Comparison'
    group: str='Day'
    fields: list[str] = field(default_factory=lambda: ['users','revenue', 'expenses', 'profit'])
    bar_kpi: str = 'expenses'
    bar_dims: list[str] = field(default_factory=lambda: [])

KPI_DIMENSIONS = {
    'revenue': {
        'Sales Channel': ['in-store', 'online', 'delivery_app'],
        'Product Category': ['coffee', 'food', 'merchandise'],
        'Time of Day': ['morning', 'afternoon', 'evening'],
        'Day of Week': ['weekday', 'weekend'],
        'Customer Type': ['new', 'returning'],
        'Promotion Applied': ['none', 'discount', 'bogo']
    },
    'expenses': {
        'Expense Category': ['COGS', 'labor', 'rent', 'marketing'],
        'Department': ['kitchen', 'front_of_house', 'admin'],
        'Vendor': ['Supplier A', 'Supplier B', 'Supplier C'],
        'Location': ['Store 1', 'Store 2', 'Online'],
        'Period Unit': ['month', 'week'],
        'Cost Type': ['fixed', 'variable']
    },  
    'new_users': {
        'Acquisition Channel': ['Instagram', 'Google Ads', 'word_of_mouth'],
        'Signup Source': ['website', 'mobile_app', 'in_person'],
        'Device Type': ['mobile', 'desktop'],
        'Day of Week': ['weekday', 'weekend'],
        'Geo Region': ['North', 'South', 'East', 'West'],
        'Promo Used': ['coupon', 'none']
    },
    'returning_users': {
        'Time Since Last Visit': ['1_week', '1_month', '6_months'],
        'Visit Frequency': ['daily', 'weekly', 'monthly'],
        'Spend Tier': ['low', 'medium', 'high'],
        'Customer Segment': ['silver', 'gold', 'platinum'],
        'Preferred Product': ['coffee', 'pastries', 'cold_drinks'],
        'Period of Day': ['morning', 'afternoon', 'evening']
    },
    'buzz': {None: [None]},
    'traffic': {None: [None]},
    'impressions': {None: [None]},
    'users': {None: [None]},
    'profit': {None: [None]},
}

METRICS_W_DIMS = ['revenue', 'expenses','new_users','returning_users'] 

METRICS = ['users','revenue', 'expenses','profit','new_users','returning_users','impressions','traffic','buzz']
TIME_OPTS = ['Last 14 Days','Last 30 Days','Last 90 Days','Last 3 Months','Last 6 Months', 'Last 12 Months']
COMPARISON_OPTS = ['Previous Period','Previous Year','No Comparison']
GROUP_OPTS= ['Day','Month','Year']

LABEL_OPTION_MAP = {'Date Range': 'time', 'Comparison Period': 'comparison', 'Time Unit':'group'}
OPTION_LABEL_MAP = {'time':'Date Range','comparison':'Comparison Period','group':'Time Unit'}

OPTIONS_MAP = {
    **{val: 'time' for val in TIME_OPTS},
    **{val: 'comparison' for val in COMPARISON_OPTS},
    **{val: 'group' for val in GROUP_OPTS},
}
OPTIONS_OPTIONS_MAP = {'time':TIME_OPTS, 'comparison':COMPARISON_OPTS, 'group':GROUP_OPTS}

TIME_DAY_OPTS = ['Last 14 Days','Last 30 Days','Last 90 Days']
TIME_MONTH_OPTS = ['Last 3 Months','Last 6 Months', 'Last 12 Months']
TIME_YEAR_OPTS = ['Last 2 Years', 'Last 3 Years']

TIME_GROUP_OPTIONS = {v:k for v,k in zip(GROUP_OPTS, [TIME_DAY_OPTS,TIME_MONTH_OPTS,TIME_YEAR_OPTS])}

GROUP_TIME_OPTS_MAP = {
    **{'Day': val for val in TIME_DAY_OPTS},
    **{'Month': val for val in TIME_MONTH_OPTS},
    **{'Year': val for val in TIME_YEAR_OPTS}
}
TIME_GROUP_OPTS_MAP = {
    **{val:'Day' for val in TIME_DAY_OPTS},
    **{val:'Month' for val in TIME_MONTH_OPTS},
    **{val:'Year' for val in TIME_YEAR_OPTS}
}
OPTION_ANCHOR_MAP = {'time':1, 'comparison':2, 'group':3}
OPTION_ICON_MAP = {'time':calendar, 'comparison':compare}

UNIT_FIELDS = ['users', 'new_users', 'returning_users','impressions','traffic','buzz']