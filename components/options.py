from fasthtml.common import *
from fasthtml.svg import *
from datapulls import *
from dataclasses import dataclass, field, asdict
from components.svg import *

### duplicated. bad
METRICS = ['users','gross_revenue', 'expenses','profit','new_users','returning_customers','impressions','traffic','buzz']
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

@dataclass
class DashContent:
    time: str='Last 14 Days'
    comparison: str='No Comparison'
    group: str='Day'
    fields: list[str] = field(default_factory=lambda: ['users','gross_revenue', 'expenses'])
    
def format_str(s):
    return s.replace('_',' ').title()

def metrics_select(options: Optional[List] = None):
    ops = [
            Li(
                A(
                format_str(m), 
                hx_post='/append-metric',
                hx_swap='beforeend',
                hx_target='#stat-chart-content',
                hx_vals=dict(field=m),
                cls=f'{"menu-active" if m in options else ""} m-1',
                id=f'metric-{m}-button',
                onclick="if (!this.classList.contains('menu-active')) { this.classList.add('menu-active'); }",
                )
            )
        for m in METRICS
    ]
    _metrics_dd = (
        Ul(cls='menu')(
            Li()(
                Button(("KPIs", plus), type="button", cls='btn btn-neutral btn-dash h-8', popovertarget=f'popover-metrics-1', style=f"anchor-name:--anchor-metrics-1"),
                Ul(popover=True, cls='dropdown menu bg-white w-52 shadow-xl', id=f'popover-metrics-1', style=f"position-anchor:--anchor-metrics-1")(*ops)            
            ),
        )
    )
    return _metrics_dd


def _format_option_value(v):
    return Span(B(v)) if not OPTIONS_MAP.get(v)=='group' else Span('Metrics By ', B(v)) ## only group has this extra formatting

## this below could be simplied so I am always just passing the value? something like that
def _option(value:str, option_grp:str, anchor:int, hx_swap_oob=False):
    
    options = OPTIONS_OPTIONS_MAP.get(option_grp)
    if len(options) >= 6:
        options = options[:3] + [Div(cls='divider my-0')] + options[3:]
        
    opts= [
        Li(A(o, 
             hx_post='/options-input', 
             hx_swap='outerHTML', 
             hx_target=f'#option-{option_grp}',
             hx_vals={OPTIONS_MAP.get(o):o, 'pressed':option_grp}
             )) 
        if isinstance(o, str) 
        else o 
        for o in options
    ]
    
    icon = OPTION_ICON_MAP.get(option_grp, None)
    _selected = Div(cls='flex flex-row gap-x-3 items-center')(Span(icon) if icon else None, _format_option_value(value), Span(arrow_down))
    _select_menu = (
        Ul(cls='menu menu-horizontal shrink-0')(
            Li()(
                Button(_selected, type='button', cls='btn h-8', popovertarget=f'popover-{anchor}', style=f"anchor-name:--anchor-{anchor}"),
                Ul(popover=True, cls='dropdown menu bg-white w-52 shadow-xl mt-1', id=f'popover-{anchor}', style=f"position-anchor:--anchor-{anchor}")(*opts)            
            ),
        )
    )
    return Fieldset(cls='fieldset', id=f'option-{option_grp}', hx_swap_oob=hx_swap_oob)(Legend(cls='fieldset-legend pb-0')(OPTION_LABEL_MAP.get(option_grp)), _select_menu)


## date range works...
## need comparison 
def options_bar(dates:str='Last 14 Days', comparison:str='No Comparison', group:str='Day'):
    
    t_select = _option(value=Span(B(dates)), option_grp='time', anchor=OPTION_ANCHOR_MAP.get('time'))
    c_select = _option(value=Span(B(comparison)), option_grp='comparison', anchor=OPTION_ANCHOR_MAP.get('comparison'))
    g_select = _option(value=Span('Metrics By ', B(group)), option_grp='group', anchor=OPTION_ANCHOR_MAP.get('group'))
    
    return (
        Div(cls='flex flex-row flex-nowrap gap-2 pb-5 shrink-0')(
            t_select,
            c_select,
            g_select
        )        
    )

def sidebar():
    return (
            ## side bar
            Div(cls='sidebar bg-base-200 shadow-sm z-10 collapsed')(
                Div(cls='p-4 flex justify-between items-center')(
                    Span('Dashboard', cls='text-xl font-bold nav-text'),
                    Button(id='toggle-btn', cls='btn btn-circle btn-sm')(
                        Svg(xmlns='http://www.w3.org/2000/svg', fill='none', viewbox='0 0 24 24', stroke='currentColor', cls='h-6 w-6')(
                            Path(stroke_linecap='round', stroke_linejoin='round', stroke_width='2', d='M4 6h16M4 12h16M4 18h7')
                        )
                    )
                ),
                Ul(cls='menu p-4 pt-0')(
                    Li(
                        A(href='#', cls='flex items-center p-2 hover:bg-base-300 rounded-lg')(
                            home_svg,
                            Span('Home', cls='ml-3 nav-text')
                        )
                    ),
                    Li(
                        A(href='#', cls='flex items-center p-2 hover:bg-base-300 rounded-lg')(
                            Svg(xmlns='http://www.w3.org/2000/svg', fill='none', viewbox='0 0 24 24', stroke='currentColor', cls='h-5 w-5')(
                                Path(stroke_linecap='round', stroke_linejoin='round', stroke_width='2', d='M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z')
                            ),
                            Span('About', cls='ml-3 nav-text')
                        )
                    ),
                    Li(
                        A(href='#', cls='flex items-center p-2 hover:bg-base-300 rounded-lg')(
                            Svg(xmlns='http://www.w3.org/2000/svg', fill='none', viewbox='0 0 24 24', stroke='currentColor', cls='h-5 w-5')(
                                Path(stroke_linecap='round', stroke_linejoin='round', stroke_width='2', d='M12 6v6m0 0v6m0-6h6m-6 0H6')
                            ),
                            Span('Services', cls='ml-3 nav-text')
                        )
                    ),
                    Li(
                        A(href='#', cls='flex items-center p-2 hover:bg-base-300 rounded-lg')(
                            Svg(xmlns='http://www.w3.org/2000/svg', fill='none', viewbox='0 0 24 24', stroke='currentColor', cls='h-5 w-5')(
                                Path(stroke_linecap='round', stroke_linejoin='round', stroke_width='2', d='M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z')
                            ),
                            Span('Contact', cls='ml-3 nav-text')
                        )
                    ),
                    Li(
                        A(href='#', cls='flex items-center p-2 hover:bg-base-300 rounded-lg')(
                            Svg(xmlns='http://www.w3.org/2000/svg', fill='none', viewbox='0 0 24 24', stroke='currentColor', cls='h-5 w-5')(
                                Path(stroke_linecap='round', stroke_linejoin='round', stroke_width='2', d='M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z'),
                                Path(stroke_linecap='round', stroke_linejoin='round', stroke_width='2', d='M15 12a3 3 0 11-6 0 3 3 0 016 0z')
                            ),
                            Span('Settings', cls='ml-3 nav-text')
                        )
                    )
                )
            )        
    )   
    
   
    
def top_navbar():
    return Div(cls='navbar bg-base-100 shadow-sm w-full')(
        Div(cls='flex-1')(
            # A('MyApp', cls='btn btn-ghost normal-case text-xl')
        ),
        Div(cls='flex-none')(

            ## theme palette
            Div(cls='dropdown dropdown-end')(
                Label(tabindex='0', cls='btn btn-ghost btn-circle')(
                    Div(cls='indicator')(
                        palette,
                        Span('3', cls='badge badge-xs badge-primary indicator-item')
                    )
                ),
                Div(tabindex='0', cls='mt-3 card card-compact dropdown-content w-52 bg-base-100 shadow-lg')(
                    Div(cls='card-body')(
                        Input(type='radio', name='theme-buttons', aria_label='Default', value='default', cls='btn theme-controller join-item'),
                        Input(type='radio', name='theme-buttons', aria_label='Retro', value='retro', cls='btn theme-controller join-item'),
                        Input(type='radio', name='theme-buttons', aria_label='Cyberpunk', value='cyberpunk', cls='btn theme-controller join-item'),
                        Input(type='radio', name='theme-buttons', aria_label='Luxury', value='luxury', cls='btn theme-controller join-item'),
                        Input(type='radio', name='theme-buttons', aria_label='Bumblebee', value='bumblebee', cls='btn theme-controller join-item')
                    )
                )
            ),

            ## magnifying glass
            Button(cls='btn btn-ghost btn-circle')(
                Svg(xmlns='http://www.w3.org/2000/svg', fill='none', viewbox='0 0 24 24', stroke='currentColor', cls='h-5 w-5')(
                    Path(stroke_linecap='round', stroke_linejoin='round', stroke_width='2', d='M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z')
                )
            ),
            
            ### avatar
            Div(cls='dropdown dropdown-end')(
                Label(tabindex='0', cls='btn btn-ghost btn-circle avatar')(
                    Div(cls='w-10 rounded-full')(
                        Img(src='https://api.dicebear.com/9.x/big-smile/svg', alt='avatar')
                        
                    )
                ),
                Ul(tabindex='0', cls='menu menu-sm dropdown-content mt-3 p-2 shadow bg-base-100 rounded-box w-52')(
                    Li(
                        A('Profile')
                    ),
                    Li(
                        A('Settings')
                    ),
                    Li(
                        A('Logout')
                    )
                )
            )
        )
    )     