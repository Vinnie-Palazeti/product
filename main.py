from components.options import *
from components.options import _option
from components.charts import *
from fasthtml.common import *
from fasthtml.svg import *
from datapulls import * 
import json
from db import *

# hetzer server
# nginx IP lockdown
# google auth
    # but google auth for specific users..


# create_and_populate_data(num_days=2000)

headers = [
    Meta(charset="UTF-8"),
    Meta(name="viewport", content="width=device-width, initial-scale=1.0, maximum-scale=1.0"),
    ## htmx
    Script(src="https://unpkg.com/htmx.org@next/dist/htmx.min.js"),
    ## echarts
    Script(src="https://assets.pyecharts.org/assets/v5/echarts.min.js"),
    ## daisy + tailwind js execute
    Link(href="https://cdn.jsdelivr.net/npm/daisyui@5", rel="stylesheet", type="text/css"),
    Script(src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"),
    
    # Script(src='https://colorjs.io/dist/color.js'),
    
    # local daisyui & tailwind
    # Link(rel="stylesheet", href="/static/css/output.css", type="text/css"),
    ## daisy themes
    Link(href='https://cdn.jsdelivr.net/npm/daisyui@5/themes.css', rel='stylesheet', type='text/css'),
    
    ## theme changer
    Script(src="https://cdn.jsdelivr.net/npm/theme-change@2.0.2/index.js"),
    
    Link(rel='preconnect', href='https://fonts.googleapis.com'),
    Link(rel='preconnect', href='https://fonts.gstatic.com', crossorigin=True),
    Link(href='https://fonts.googleapis.com/css2?family=Noto+Sans:ital,wght@0,100..900;1,100..900&display=swap', rel='stylesheet'),

    Style("""
        html {
            font-family: 'Noto Sans', sans-serif;
        }     
        th {
            font-weight: normal;
        }             
          

        .sidebar {
            width: 250px;
            transition: width 0.3s ease;
            height: 100vh;
            position: fixed;
            top: 0;
            left: 0;
        }
        .sidebar.collapsed {
            width: 80px;
        }
        .sidebar.collapsed .nav-text {
            display: none;
        }

        .main-content {
            margin-left: 250px;
            transition: margin-left 0.3s ease;
            width: calc(100% - 250px);
            max-width: 100%;
        }
        .main-content.expanded {
            margin-left: 80px;
            width: calc(100% - 80px);
        }
        
        /* Navbar logo positioning */
        .navbar-logo-container {
            margin-left: 250px;
            transition: margin-left 0.3s ease;
        }        
        
        /* Mobile responsive adjustments */
        @media (max-width: 768px) {
            .navbar-logo-container {
                margin-left: 0px !important;
                padding-left: 1rem;
            }
        }
        
        /* Container for content - prevent overflow */
        .content-container {
            width: 100%;
            overflow-x: auto;
        }
        
        /* Make sure images and charts stay within bounds */
        .content-container img,
        .content-container canvas,
        .content-container svg,
        .content-container.chart {
            max-width: 100%;
            height: auto;
        }
        
        @keyframes growBar {
            0% { transform: scaleX(0); }
            100% { transform: scaleX(1); }
        }

        .animate-grow-bar {
            animation: growBar 0.8s ease-out forwards;
            transform-origin: left; /* ensures it grows from the left */
        }      
        
        .no-left-padding,
        .no-left-padding * {
            padding-left: 0 !important;
        }  
        
        
              
    """)   
]

app, rt = fast_app(
    title='IndyStats',
    hdrs=headers, 
    default_hdrs=False, 
    live=True, 
    htmlkw={"data-theme": "light"} 
    
)

# app = FastHTML(title='Themes', hdrs=headers, default_hdrs=False, htmlkw={"data-theme": "light"} )
# rt = app.route

@rt("/{fname:path}.{ext:static}")
def get(fname: str, ext: str):
    return FileResponse(f"{fname}.{ext}")

def render_content(content: DashContent, hx_swap:str=None):
    ## get all data
    data = get_data(
        time_period=content.time,
        comparison_type=content.comparison,
        period_type=content.group,
        fields=content.fields,
    )
    ## summarize data
    totals = calculate_totals(results=data)
    ## get bar chart data.
    bar_data = get_bar_data(kpi=content.bar_kpi, dimension_list=None, time_period=content.time, comparison_type=content.comparison, period_type=content.group)
    ## format stat + line charts
    stat_charts = [stat_chart(name=f, timeseries=data, totals=totals, show_label=True if n==0 else False) for n, f in enumerate(content.fields)]
    ## format bar charts
    bar_charts = [bar_chart(dim=dim, data=bar_data, kpi=content.bar_kpi) for dim in list(KPI_DIMENSIONS.get(content.bar_kpi).keys())] ## using default dimensions
    return Div(cls="grid grid-cols-2 gap-4 items-start", id='stat-chart-container', hx_swap_oob=hx_swap)(
        Div(cls="grid grid-cols-3 gap-y-2", id='stat-chart-content')(*[c for c in stat_charts]),
        Div(cls="grid grid-cols-4 gap-y-30 gap-x-10", id='bar-chart-content')(*[c for c in bar_charts])
    )
    
## need to append the hidden value fields...
@rt("/append-metric")
def post(field:str, group:str, time:str, comparison:str, fields:list[str]):
    ## if the field is currently present in the hidden fields
    if field in fields[0]:
        return None
    ## if there is at least one field and there is a space present
    ## split the contents of the list    
    if len(fields) == 1 and ' ' in fields[0]:
        fields = fields[0].split(' ') + [field]
    # get data
    data = get_data(
        time_period=time,
        comparison_type=comparison,
        period_type=group,
        fields=[field],
    )
    totals = calculate_totals(results=data)
    return (stat_chart(name=field, timeseries=data, totals=totals, show_label=False), Input(type='hidden', name='fields', value=fields, id='fields-value', hx_swap_oob='outerHTML'))

## removes stat and line chart
@rt("/remove-metric")
def post(field:str, fields:list[str]):
    # format KPI button for OOB swap
    but = Template()(
        Li(A(field.replace('_', ' ').title(), 
             hx_swap_oob='outerHTML', 
             hx_post='/append-metric', hx_swap='beforeend', hx_target='#stat-chart-content', 
             hx_vals=dict(field=field),
             cls=f'm-1', id=f'metric-{field}-button', 
             onclick="if (!this.classList.contains('menu-active')) { this.classList.add('menu-active'); }",
             )
           )
    )
    # format current field values
    fields_values = [i for i in fields[0].split(' ') if i != field] 
    # return None, which swaps the stat line combo for nothing (i.e. removes it)
    # swap oob the button and current fields value
    return None, but, Input(type='hidden', name='fields', value=fields_values, id='fields-value', hx_swap_oob='outerHTML')

@rt("/options-input")
def post(content:DashContent, pressed:str):
    ## not sure why data class not list of strings.. turns it into a list of 1 concatenated string
    if len(content.fields) == 1 and ' ' in content.fields[0]:
        setattr(content,'fields', content.fields[0].split(' '))
    # return button option with updated pressed value and the hidden value 
    out = (
        _option(value=getattr(content, pressed), option_grp=pressed, anchor=OPTION_ANCHOR_MAP.get(pressed)), 
        Input(type='hidden', name=pressed, value=getattr(content, pressed), id=f'{pressed}-value', hx_swap_oob='outerHTML'),
    )
    # check to see if group has changed, i.e. went from day -> month
    if content.time not in TIME_GROUP_OPTIONS.get(content.group):
        updated_group=TIME_GROUP_OPTS_MAP.get(content.time) ## either Day Month Year
        setattr(content, 'group', updated_group) # update the group field
        ## return the group and the hidden input
        out += (
            _option(value=updated_group, option_grp='group', anchor=OPTION_ANCHOR_MAP.get(updated_group), hx_swap_oob='outerHTML'), 
            Input(type='hidden', name='group', value=content.group, id='group-value', hx_swap_oob='outerHTML')
        ) 
    # return the rendered content wth the new attributes
    out += (render_content(content=content, hx_swap='outerHTML'), )
    # return new formatted dates
    out += (Span(format_date_range(content.time), cls='text-primary', id='formatted-date-range', hx_swap_oob='outerHTML'), )
    return out

@rt("/bar-metric-select")
def post(content:DashContent, pressed:str):
    ## currently using default dimension_list
    bar_data = get_bar_data(kpi=pressed, dimension_list=None, time_period=content.time, comparison_type=content.comparison, period_type=content.group)
    bar_charts = [bar_chart(dim=dim, data=bar_data, kpi=pressed) for dim in KPI_DIMENSIONS.get(pressed)]
    return (
        bar_kpi_select(pressed, hx_swap_oob='outerHTML'),
        Div(cls="grid grid-cols-4 gap-y-30 gap-x-10", id='bar-chart-content')(*[c for c in bar_charts]),
        Input(type='hidden', name='bar_dims', value=list(KPI_DIMENSIONS.get(pressed).keys()), id='bar-dims-value', hx_swap_oob='outerHTML'),
        Input(type='hidden', name='bar_kpi', value=pressed, id='bar-kpi-value', hx_swap_oob='outerHTML'),
    )
    

def render_closer_look(field:str, time):
    data = get_data(
        time_period=time,
        comparison_type='No Comparison',
        period_type='Day',
        fields=[field],
    )
    dates = [i.get('date') for i in data.get('selected_period')]
    y = [i.get(field) for i in data.get('selected_period')]
    if 'comparison_period' in data:
        y = (
            y, # main data
            [i.get(field) for i in data.get('comparison_period')], # comparison
        )
    out = {'line':embed_line_chart(x=dates, y=y, show_label=True, label_pos='left')}
    
    ### GET FIELD/METRIC BREAKDOWNS HERE
    bar_data = get_bar_data(kpi=field, dimension_list=None, time_period=time, comparison_type='No Comparison', period_type='Day')
    
    # Add basic charts that work for all metrics
    if bar_data and bar_data.get('selected_period'):
        # Add grouped bar chart for metric breakdowns
        out.update({'grouped_bar': embed_grouped_bar_chart(bar_data, f"{field.replace('_', ' ').title()} Breakdown")})
        
        # Create stacked area chart data - split by first two dimensions
        dimensions = {}
        for item in bar_data.get('selected_period', []):
            dim = item['dimension']
            cat = item['category']
            val = item['total_value']
            
            if dim not in dimensions:
                dimensions[dim] = {}
            dimensions[dim][cat] = val
        
        if len(dimensions) >= 2:
            # Create time series data for stacked area (simulate daily breakdown)
            stacked_data = {}
            for dim_name, categories in list(dimensions.items())[:2]:  # Take first two dimensions
                for cat_name, total_val in categories.items():
                    series_name = f"{dim_name}: {cat_name}"
                    # Simulate daily values that sum to total
                    daily_vals = [total_val / len(dates) * (1 + 0.1 * (i % 7 - 3)) for i in range(len(dates))]
                    stacked_data[series_name] = daily_vals
            
            out.update({'stacked_area': embed_stacked_area_timeseries(dates, stacked_data, f"{field.replace('_', ' ').title()} Composition")})
        
        # Create calendar heatmap data - get full year's data
        year = int(dates[0].split('-')[0]) if dates else 2024
        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)
        year_data = get_data(
            time_period=TimeRange(start_date=year_start, end_date=year_end),
            comparison_type='No Comparison',
            period_type='Day',
            fields=[field],
        )
        if year_data and year_data.get('selected_period'):
            year_dates = [i.get('date') for i in year_data.get('selected_period')]
            year_values = [i.get(field) for i in year_data.get('selected_period')]
            calendar_data = [[date, val] for date, val in zip(year_dates, year_values)]
            out.update({'calendar': embed_calendar_heatmap(calendar_data, year, max(year_values), min(year_values))})
    
    # Add MMM experiments if available
    exps=get_experiments(field)
    if exps:
        exp_data = json.loads(exps[0]['data'])
        ## just take the first one
        out.update({'mmm_bar':channel_contribution_barchart(exp_data['channel_contribution_barchart'])})
        out.update({'mmm_grid':channel_contributions_forward_pass_grid(exp_data['channel_contribution_pass_forward_grid'])})
        out.update({'mmm_area':channel_contributions_over_time(exp_data['channel_contribution_over_time'])})
        out.update({'Experiments': [i.get('date') for i in exps]})
    
    return out

@rt('/closer-look-experiment')
def post(metric:str, pressed:str):
    exps=get_experiments(metric)
    exp_data = json.loads([i for i in exps if i.get('date') == pressed][0]['data'])
    return (
        Div(id='closer-look-experiments', cls="grid grid-cols-2 gap-2 col-span-2")(  
            Div(cls='col-span-2')(
                option_closerlook(
                    value=Span(B(pressed)), 
                    hx_target='#closer-look-experiments', hx_post='/closer-look-experiment',
                    id='exp-drop', name='Display', options=[i.get('date') for i in exps])
            ),
            Div(cls='col-span-1 bg-base-100 p-4 rounded-lg shadow')(
                H3('Contribution Breakdown Over Time', cls='text-lg mb-4'),
                Div(cls='h-64')(channel_contribution_barchart(exp_data['channel_contribution_barchart']))
            ),
            Div(cls='col-span-1 bg-base-100 p-4 rounded-lg shadow')(
                H3('Component Decomposition', cls='text-lg mb-4'),
                Div(cls='h-64')(channel_contributions_forward_pass_grid(exp_data['channel_contribution_pass_forward_grid']))
            ),
            Div(cls='col-span-2 bg-base-100 p-4 rounded-lg shadow')(
                H3('Component Decomposition', cls='text-lg mb-4'),
                Div(cls='h-96')(channel_contributions_over_time(exp_data['channel_contribution_over_time']))
            )
        )        
    )

@rt('/closer-look-metric')
def post(start_date:date, end_date:date, pressed:str=None):
    charts = render_closer_look(field=pressed, time=TimeRange(start_date=start_date, end_date=end_date))
    
    # Create the main content div
    main_content = [
        Div(id='closer-look-line-chart', cls='col-span-2 bg-base-100 p-4 rounded-lg shadow')(
            Div(cls='h-96')(charts['line']), 
            Input(type='hidden', name='metric', value=pressed)
        )
    ]
    
    # Add basic charts section
    basic_charts = []
    if 'grouped_bar' in charts:
        basic_charts.append(
            Div(cls='col-span-1 bg-base-100 p-4 rounded-lg shadow')(
                H3('Metric Breakdown', cls='text-lg mb-4'),
                Div(cls='h-64')(charts['grouped_bar'])
            )
        )
    
    if 'stacked_area' in charts:
        basic_charts.append(
            Div(cls='col-span-1 bg-base-100 p-4 rounded-lg shadow')(
                H3('Composition Over Time', cls='text-lg mb-4'),
                Div(cls='h-64')(charts['stacked_area'])
            )
        )
    
    if 'calendar' in charts:
        basic_charts.append(
            Div(cls='col-span-2 bg-base-100 p-4 rounded-lg shadow')(
                H3('Calendar View', cls='text-lg mb-4'),
                Div(cls='h-96')(charts['calendar'])
            )
        )
    
    if basic_charts:
        main_content.append(
            Div(id='closer-look-basic-charts', cls="grid grid-cols-2 gap-2 col-span-2")(*basic_charts)
        )
    
    # Add MMM experiments section if available
    if 'Experiments' in charts:
        main_content.append(
            Div(id='closer-look-experiments', cls="grid grid-cols-2 gap-2 col-span-2")( 
                Div(cls='col-span-2')(
                    option_closerlook(
                        value=Span(B(charts.get('Experiments')[0])), 
                        hx_target='#closer-look-experiments', hx_post='/closer-look-experiment', 
                        id='exp-drop', name='Display', options=charts.get('Experiments'))
                ),
                Div(cls='col-span-1 bg-base-100 p-4 rounded-lg shadow')(
                    H3('MMM Contribution Breakdown', cls='text-lg mb-4'),
                    Div(cls='h-64')(charts['mmm_bar'])
                ),
                Div(cls='col-span-1 bg-base-100 p-4 rounded-lg shadow')(
                    H3('MMM Component Decomposition', cls='text-lg mb-4'),
                    Div(cls='h-64')(charts['mmm_grid'])
                ),
                Div(cls='col-span-2 bg-base-100 p-4 rounded-lg shadow')(
                    H3('MMM Contributions Over Time', cls='text-lg mb-4'),
                    Div(cls='h-96')(charts['mmm_area'])
                )
            )
        )
    
    out = (Div(id='closer-look-main-content', cls="grid grid-cols-2 gap-2 col-span-2")(*main_content),)
    out += (option_closerlook(value=Span(B(pressed.replace('_',' ').title())), option_grp='metrics', hx_post='/closer-look-metric', hx_target='#closer-look-main-content', hx_swap_oob='outerHTML'), )
    return out

@rt('/closer-look-date')
def post(metric:str, start_date:date, end_date:date):
    charts = render_closer_look(field=metric, time=TimeRange(start_date=start_date, end_date=end_date))
    
    # Create the main content div (re-render everything except experiments)
    main_content = [
        Div(id='closer-look-line-chart', cls='col-span-2 bg-base-100 p-4 rounded-lg shadow')(
            Div(cls='h-96')(charts['line']), 
            Input(type='hidden', name='metric', value=metric)
        )
    ]
    
    # Add basic charts section
    basic_charts = []
    if 'grouped_bar' in charts:
        basic_charts.append(
            Div(cls='col-span-1 bg-base-100 p-4 rounded-lg shadow')(
                H3('Metric Breakdown', cls='text-lg mb-4'),
                Div(cls='h-64')(charts['grouped_bar'])
            )
        )
    
    if 'stacked_area' in charts:
        basic_charts.append(
            Div(cls='col-span-1 bg-base-100 p-4 rounded-lg shadow')(
                H3('Composition Over Time', cls='text-lg mb-4'),
                Div(cls='h-64')(charts['stacked_area'])
            )
        )
    
    if 'calendar' in charts:
        basic_charts.append(
            Div(cls='col-span-2 bg-base-100 p-4 rounded-lg shadow')(
                H3('Calendar View', cls='text-lg mb-4'),
                Div(cls='h-96')(charts['calendar'])
            )
        )
    
    if basic_charts:
        main_content.append(
            Div(id='closer-look-basic-charts', cls="grid grid-cols-2 gap-2 col-span-2")(*basic_charts)
        )
    
    # Keep existing experiments section if it exists (don't re-render)
    if 'Experiments' in charts:
        main_content.append(
            Div(id='closer-look-experiments', cls="grid grid-cols-2 gap-2 col-span-2")( 
                Div(cls='col-span-2')(
                    option_closerlook(
                        value=Span(B(charts.get('Experiments')[0])), 
                        hx_target='#closer-look-experiments', hx_post='/closer-look-experiment', 
                        id='exp-drop', name='Display', options=charts.get('Experiments'))
                ),
                Div(cls='col-span-1 bg-base-100 p-4 rounded-lg shadow')(
                    H3('MMM Contribution Breakdown', cls='text-lg mb-4'),
                    Div(cls='h-64')(charts['mmm_bar'])
                ),
                Div(cls='col-span-1 bg-base-100 p-4 rounded-lg shadow')(
                    H3('MMM Component Decomposition', cls='text-lg mb-4'),
                    Div(cls='h-64')(charts['mmm_grid'])
                ),
                Div(cls='col-span-2 bg-base-100 p-4 rounded-lg shadow')(
                    H3('MMM Contributions Over Time', cls='text-lg mb-4'),
                    Div(cls='h-96')(charts['mmm_area'])
                )
            )
        )
    
    return Div(id='closer-look-main-content', cls="grid grid-cols-2 gap-2 col-span-2")(*main_content)

@rt("/closer-look")
def get(metric:str='users'):
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=30)
    charts = render_closer_look(field=metric, time=TimeRange(start_date=start_date, end_date=end_date))    
    
    # Create the main content
    main_content = [
        Div(id='closer-look-line-chart', cls='col-span-2 bg-base-100 p-4 rounded-lg shadow')(
            Div(cls='h-96')(charts['line']),
            Input(type='hidden', name='metric', value=metric),
        )
    ]
    
    # Add basic charts section
    basic_charts = []
    if 'grouped_bar' in charts:
        basic_charts.append(
            Div(cls='col-span-1 bg-base-100 p-4 rounded-lg shadow')(
                H3('Metric Breakdown', cls='text-lg mb-4'),
                Div(cls='h-64')(charts['grouped_bar'])
            )
        )
    
    if 'stacked_area' in charts:
        basic_charts.append(
            Div(cls='col-span-1 bg-base-100 p-4 rounded-lg shadow')(
                H3('Composition Over Time', cls='text-lg mb-4'),
                Div(cls='h-64')(charts['stacked_area'])
            )
        )
    
    if 'calendar' in charts:
        basic_charts.append(
            Div(cls='col-span-2 bg-base-100 p-4 rounded-lg shadow')(
                H3('Calendar View', cls='text-lg mb-4'),
                Div(cls='h-96')(charts['calendar'])
            )
        )
    
    if basic_charts:
        main_content.append(
            Div(id='closer-look-basic-charts', cls="grid grid-cols-2 gap-2 col-span-2")(*basic_charts)
        )
    
    # Add MMM experiments section if available
    if 'Experiments' in charts:
        main_content.append(
            Div(id='closer-look-experiments', cls="grid grid-cols-2 gap-2 col-span-2")(
                Div(cls='col-span-2')(
                    option_closerlook(
                        value=Span(B(charts.get('Experiments')[0])), 
                        hx_target='#closer-look-experiments', hx_post='/closer-look-experiment', 
                        id='exp-drop', name='Display', options=charts.get('Experiments'))
                ),
                Div(cls='col-span-1 bg-base-100 p-4 rounded-lg shadow')(
                    H3('MMM Contribution Breakdown', cls='text-lg mb-4'),
                    Div(cls='h-64')(charts['mmm_bar'])
                ),
                Div(cls='col-span-1 bg-base-100 p-4 rounded-lg shadow')(
                    H3('MMM Component Decomposition', cls='text-lg mb-4'),
                    Div(cls='h-64')(charts['mmm_grid'])
                ),
                Div(cls='col-span-2 bg-base-100 p-4 rounded-lg shadow')(
                    H3('MMM Contributions Over Time', cls='text-lg mb-4'),
                    Div(cls='h-96')(charts['mmm_area'])
                )
            )
        )
    
    return (
        Title('IndyStats'),
        Body(cls="min-h-screen")(
            sidebar(),
            top_navbar(),
            Script(src="/static/js/oklch-rgb.js"),
            ############ main ############
            Form()(
                Div(id='main-content-div' ,cls="main-content min-h-screen expanded p-5")(
                    Div(cls='grid grid-cols-2 gap-2')(     
                        Div(cls='flex flex-row flex-nowrap gap-2 pb-0 shrink-0')(
                            option_closerlook(
                                value=Span(B(metric.replace('_',' ').title())), option_grp='metrics',
                                hx_target='#closer-look-main-content', hx_swap='outerHTML', hx_post='/closer-look-metric'
                            ),
                            Fieldset(cls='fieldset')(
                                Legend(cls="fieldset-legend")('Start Date'),
                                Input(type='date', name='start_date', value=start_date, hx_post='/closer-look-date', hx_target='#closer-look-main-content', hx_swap='outerHTML', cls='input')
                            ),
                            Fieldset(cls='fieldset')(
                                Legend(cls="fieldset-legend")('End Date'),
                                Input(type='date', name='end_date', value=end_date, hx_post='/closer-look-date', hx_target='#closer-look-main-content', hx_swap='outerHTML', cls='input')
                            ),                            
                        ),
                        Div(id='closer-look-main-content', cls="grid grid-cols-2 gap-2 col-span-2")(*main_content)                       
                    ),
                )
            ),
        Script(src="/static/js/collapse.js"),
        Script(src="/static/js/chart-color.js")            
        )
    )    

@rt("/random")
def get():
    # Generate 10 random charts
    charts = [generate_random_chart() for _ in range(10)]
    
    return (
        Body(cls="min-h-screen bg-gray-50")(
            sidebar(),
            top_navbar(),
            Script(src="/static/js/oklch-rgb.js"),
            Div(id='main-content-div', cls="main-content min-h-screen expanded p-6")(
                # Bento-style grid layout
                Div(cls="grid grid-cols-4 grid-rows-4 gap-4 h-screen max-h-[1000px]")(
                    Div(cls="col-span-2 row-span-2 bg-white rounded-lg shadow-lg p-4")(Div(cls="h-full")(charts[0])),
                    Div(cls="col-span-1 row-span-2 bg-white rounded-lg shadow-lg p-4")(Div(cls="h-full")(charts[1])),
                    Div(cls="col-span-1 row-span-1 bg-white rounded-lg shadow-lg p-4")(Div(cls="h-full")(charts[2])),
                    Div(cls="col-span-1 row-span-1 bg-white rounded-lg shadow-lg p-4")(Div(cls="h-full")(charts[3])),
                    Div(cls="col-span-2 row-span-1 bg-white rounded-lg shadow-lg p-4")(Div(cls="h-full")(charts[4])),
                    
                    # Small chart (1x1)
                    Div(cls="col-span-1 row-span-1 bg-white rounded-lg shadow-lg p-4")(Div(cls="h-full")(charts[5])),
                    
                    # Small chart (1x1)
                    Div(cls="col-span-1 row-span-1 bg-white rounded-lg shadow-lg p-4")(
                        Div(cls="h-full")(charts[6])
                    ),
                    
                    # Medium wide chart (2x1)
                    Div(cls="col-span-2 row-span-1 bg-white rounded-lg shadow-lg p-4")(
                        Div(cls="h-full")(charts[7])
                    ),
                    
                    # Small chart (1x1)
                    Div(cls="col-span-1 row-span-1 bg-white rounded-lg shadow-lg p-4")(
                        Div(cls="h-full")(charts[8])
                    ),
                    
                    # Small chart (1x1)
                    Div(cls="col-span-1 row-span-1 bg-white rounded-lg shadow-lg p-4")(
                        Div(cls="h-full")(charts[9])
                    ),
                ),
                
                # Refresh button
                Div(cls="mt-8 text-center")(
                    A("🎲 Generate New Random Charts", 
                      href="/random", 
                      cls="inline-block bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 shadow-lg")
                )
            ),
            Script(src="/static/js/collapse.js"),
            Script(src="/static/js/chart-color.js")
        )
    )

@rt("/")
def get():
    ## load defaults for user/session
    ## DashContent()
    content = DashContent()
    return (Title('IndyStats'),
            Body(cls="min-h-screen")(
        sidebar(),
        top_navbar(),
        Script(src="/static/js/oklch-rgb.js"),
        ############ main ############
        Form()(
            Div(id='main-content-div', cls="main-content min-h-screen expanded p-5")(
                options_bar(),
                Div(cls="grid grid-cols-2", id='metrics-select-container')(
                    Div(cls='flex flex-row gap-x-3 items-center')(
                        metrics_select(content.fields),
                        Span(format_date_range(content.time),cls='text-primary hover:bg-base-200 transition-colors duration-200 p-2 rounded-lg', id='formatted-date-range')
                    ), 
                    bar_kpi_select(content.bar_kpi)),
                render_content(content),
            ),
            Input(type='hidden', name='comparison', value=content.comparison, id='comparison-value'),
            Input(type='hidden', name='time', value=content.time, id='time-value'),
            Input(type='hidden', name='group', value=content.group, id='group-value'),
            Input(type='hidden', name='fields', value=content.fields, id='fields-value'),
            Input(type='hidden', name='bar_dims', value=content.bar_dims, id='bar-dims-value'),
            Input(type='hidden', name='bar_kpi', value=content.bar_kpi, id='bar-kpi-value'),
        ),
        Script(src="/static/js/collapse.js"),
        Script(src="/static/js/chart-color.js")
    ))

@rt("/test")
def post(d: dict):
    print(d)
    print("hello")


serve(port=3001)
