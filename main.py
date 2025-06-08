from components.options import *
from components.options import _option
from components.charts import *
from components.misc import *
from components.svg import SVG_MAP, plus
from fasthtml.common import *
from fasthtml.svg import *
from datapulls import * 


# from db import create_and_populate_database
# create_and_populate_database("test_metrics.db", num_days = 2000)
    


## I think to handle the min width stuff I need to just format the grid columns




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
    
    # local daisyui & tailwind
    # Link(rel="stylesheet", href="/static/css/output.css", type="text/css"),
    ## daisy themes
    # Link(href='https://cdn.jsdelivr.net/npm/daisyui@5/themes.css', rel='stylesheet', type='text/css'),
    
    ## theme changer
    Script(src="https://cdn.jsdelivr.net/npm/theme-change@2.0.2/index.js"),

    Style("""

        body {
            background-color: var(--my-color);
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
    """),
]

app, rt = fast_app(hdrs=headers, default_hdrs=False, live=True)
# app = FastHTML(title='Themes', hdrs=headers, default_hdrs=False)
# rt = app.route

@rt("/{fname:path}.{ext:static}")
def get(fname: str, ext: str):
    return FileResponse(f"{fname}.{ext}")

METRICS = ['users','gross_revenue', 'expenses','profit','new_users','returning_customers','impressions','traffic','buzz']

## remove decimals if over 1k
def format_metric(value, dollar):
    if dollar:
        if value >= 1000:
            return f'${value:,.0f}'
        else:
            return f'${value:,.2f}'
    else:
        return f'{value:,.0f}'


def stat(name:str, value, dollar:bool = True, comparison=None):
    if comparison:
        pct_chng = (value - comparison) / value * 100
    return (
        ## h-[100px] could set the height based on position (1st being taller to make up for top labels) to make then more equal
        ## set the max height of the article to stop the stat + line chart from getting way to large 
        Article(cls="relative p-6 col-span-1 group bg-base-100 hover:bg-base-200 transition-colors duration-200 max-h-24", id=f'stat-{name}')(
            
            Div(cls="absolute top-1 right-1 text-base-600 opacity-0 group-hover:opacity-100 transition-opacity duration-1000")(              
                Div(cls='hover:bg-base-300 cursor-pointer transition-colors duration-200', 
                    hx_post='/remove-metric', hx_target=f'#metric-container-{name}', hx_swap='outerHTML', hx_vals=dict(field=name),
                    id=f'#stat-{name}-x')(
                        SVG_MAP.get("x")
                    )
            ),
            Div(cls="absolute top-1 right-7 text-base-600 opacity-0 group-hover:opacity-100 transition-opacity duration-1000")(
                Div(cls='hover:bg-base-300 cursor-pointer transition-colors duration-200')(
                    SVG_MAP.get("visit")
                )
            ),                     
            Div(cls="flex items-center justify-between")(
                Div()(
                    P(name.replace('_',' ').title(), cls="text-sm text-gray-500"),
                    P(format_metric(value, dollar), 
                    cls="text-2xl font-medium text-gray-900"),
                ),
                Span(cls="text-blue-600 mt-5")(SVG_MAP.get(name)),
            ),
            None if not comparison else 
            Div(cls=f"mt-1 flex gap-1 text-{'success' if pct_chng >=0 else 'error'}")(
                SVG_MAP.get('increase') if pct_chng >= 0  else SVG_MAP.get('decrease'),
                P(cls="flex gap-2 text-xs")(Span(f"{pct_chng:,.2f}%", cls="font-medium")),
            )
        )
    )
    
    

def stat_chart(name, dates, timeseries, totals, show_label):
    if isinstance(timeseries, tuple):
        
        y = (
            [round(i.get(name), 2) for i in timeseries[0]], # main data
            [round(i.get(name), 2) for i in timeseries[1]], # comparison
        )
    else:
        y = [i.get(name) for i in timeseries]

    c = embed_line_chart(x=dates, y=y, show_label=show_label)
    
    return (
        Div(id=f'metric-container-{name}', cls="contents")( ## this is a wrapper. display:contents -> element itself disappears and children styling  & layout is displayed
        stat(
            name=name, value=totals.get('selected_period').get(name), 
            dollar=name not in UNIT_FIELDS, 
            comparison=totals.get('comparison_period').get(name) if isinstance(y, tuple) else False
        ), 
        Div(c, cls="col-span-2", id=f'{name}-chart'))
    )
    
def render_content(content: DashContent, hx_swap:str=None):
    ## get all data
    data = get_data(
        content.time,
        comparison_type=content.comparison,
        period_type=content.group,
        fields=content.fields,
    )
    ## summarize data
    totals = calculate_totals(data, content.fields)
    ## transform to list[dict]
    timeseries = [dict(row) for row in data.get('selected_period')]
    # get dates for selected period
    dates = [i.get('date') for i in timeseries]
    if data.get('comparison_period'):
        timeseries = (timeseries, [dict(row) for row in data.get('comparison_period')])
    stat_charts = [stat_chart(f, dates, timeseries, totals, show_label=True if n==0 else False) for n, f in enumerate(content.fields)]
    
    return Div(cls="grid grid-cols-2 gap-4", id='stat-chart-container', hx_swap_oob=hx_swap)(
        Div(cls="grid grid-cols-3", id='stat-chart-content')(
            *[c for c in stat_charts]
        )
    )


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
    # calculate totals for period
    totals = calculate_totals(data, fields=[field])
    # get selected period data
    timeseries = [dict(row) for row in data.get('selected_period')]
    # get dates from period
    dates = [i.get('date') for i in timeseries]
    # if there is comparison data, get that
    if data.get('comparison_period'):
        # put selected and comparison in the same tuple
        timeseries = (timeseries, [dict(row) for row in data.get('comparison_period')])
    return (stat_chart(field, dates, timeseries, totals, show_label=False), Input(type='hidden', name='fields', value=fields, id='fields-value', hx_swap_oob='outerHTML'))

@rt("/")
def get():
    ## load defaults for user/session
    ## DashContent()
    content = DashContent()
    return Body(cls="min-h-screen")(
        sidebar(),
        top_navbar(),
        ############ main ############
        Form()(
            Div(cls="main-content min-h-screen expanded p-5")(
                options_bar(),
                metrics_select(content.fields),
                render_content(content),
            ),
            
            Input(type='hidden', name='comparison', value=content.comparison, id='comparison-value'),
            Input(type='hidden', name='time', value=content.time, id='time-value'),
            Input(type='hidden', name='group', value=content.group, id='group-value'),
            Input(type='hidden', name='fields', value=content.fields, id='fields-value'), # default fields
            
            
        ),
        Script(src="/collapse.js"),
    )

@rt("/options-input")
def post(content:DashContent, pressed:str):
    # print(asdict(content))
    # print(pressed)
    
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
    return out


@rt("/test")
def post(d: dict):
    print(d)
    print("hello")


serve(port=3001)
