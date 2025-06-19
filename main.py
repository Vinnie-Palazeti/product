from components.options import *
from components.options import _option
from components.charts import *

from fasthtml.common import *
from fasthtml.svg import *
from datapulls import * 

# from db import *

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
    
    # Script(src='https://colorjs.io/dist/color.js'),
    
    # local daisyui & tailwind
    # Link(rel="stylesheet", href="/static/css/output.css", type="text/css"),
    ## daisy themes
    Link(href='https://cdn.jsdelivr.net/npm/daisyui@5/themes.css', rel='stylesheet', type='text/css'),
    
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
    """)   
]

app, rt = fast_app(hdrs=headers, default_hdrs=False, live=True, htmlkw={"data-theme": "light"} )
# app = FastHTML(title='Themes', hdrs=headers, default_hdrs=False)
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
    if not content.bar_dims:
        setattr(content,'bar_dims', list(KPI_DIMENSIONS.get(content.bar_kpi).keys()))
    ## get bar chart data.
    bar_data = get_bar_data(kpi=content.bar_kpi, dimension_list=content.bar_dims, time_period=content.time, comparison_type=content.comparison, period_type=content.group)
    ## format stat + line charts
    stat_charts = [stat_chart(name=f, timeseries=data, totals=totals, show_label=True if n==0 else False) for n, f in enumerate(content.fields)]
    ## format bar charts
    bar_charts = [bar_chart(dim=dim, data=bar_data, kpi=content.bar_kpi) for dim in content.bar_dims]
    return Div(cls="grid grid-cols-2 gap-4 items-start", id='stat-chart-container', hx_swap_oob=hx_swap)(
        Div(cls="grid grid-cols-3", id='stat-chart-content')(*[c for c in stat_charts]),
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

@rt("/")
def get():
    ## load defaults for user/session
    ## DashContent()
    content = DashContent()
    return Body(cls="min-h-screen")(
        sidebar(),
        top_navbar(),
        Script(src="/static/js/oklch-rgb.js"),
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
        Script(src="/static/js/collapse.js"),
        Script(src="/static/js/chart-color.js")
    )

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
    return out


@rt("/test")
def post(d: dict):
    print(d)
    print("hello")


serve(port=3001)
