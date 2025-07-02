from components.options import *
from components.options import _option
from components.charts import *

from fasthtml.common import *
from fasthtml.svg import *
from datapulls import * 

from db import *


# create_and_populate_database("test_metrics.db", num_days = 2000)


# svg for delta
# different text for table?
# date picker? custom date?

# another page.. large timeseries metric in the middle.. 


# get an actual example up
# hetzer server
# nginx IP lockdown
# google auth
    # but google auth for specific users..





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

app, rt = fast_app(
    # title='IndyStats',
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
    # print(content)
    ## currently using default dimension_list
    bar_data = get_bar_data(kpi=pressed, dimension_list=None, time_period=content.time, comparison_type=content.comparison, period_type=content.group)
    bar_charts = [bar_chart(dim=dim, data=bar_data, kpi=pressed) for dim in KPI_DIMENSIONS.get(pressed)]
    return (
        bar_kpi_select(pressed, hx_swap_oob='outerHTML'),
        Div(cls="grid grid-cols-4 gap-y-30 gap-x-10", id='bar-chart-content')(*[c for c in bar_charts]),
        Input(type='hidden', name='bar_dims', value=list(KPI_DIMENSIONS.get(pressed).keys()), id='bar-dims-value', hx_swap_oob='outerHTML'),
        Input(type='hidden', name='bar_kpi', value=pressed, id='bar-kpi-value', hx_swap_oob='outerHTML'),
    )
    
    
def render_closer_look(content:DashContent):
    
    field='users'
    
    ## get all data
    data = get_data(
        time_period=content.time,
        comparison_type=content.comparison,
        period_type=content.group,
        fields=[field],
    )
    ## summarize data
    totals = calculate_totals(results=data)
    
    dates = [i.get('date') for i in data.get('selected_period')]
    y = [i.get(field) for i in data.get('selected_period')]
    if 'comparison_period' in data:
        y = (
            y, # main data
            [i.get(field) for i in data.get('comparison_period')], # comparison
        )
    c = embed_line_chart(x=dates, y=y, show_label=True, label_pos='left')    
    return c
    
### what do I need here?
## I need to lean into the MMM..
## Overall Time series that we have run experiments on.
## over the course of a year we are going to have demarkations for experiments
## vertical lines for changes or blackouts

## when we run the model or an experiment we need to save the results of the parameters
# datepicker start and end


## for 2 metrics
## for the first,
    # just copy straight up the MMM from pymc for one metric
    # then alter slightly for the second metric
    
## if they selected a closer look on a metic with no MMM, just post that 

## just mark experiements that occured
## then put contributions in 4x4 grid below.




    
## investigate impact of MMM on these
## https://www.pymc-marketing.io/en/stable/notebooks/mmm/mmm_example.html
## channel contribution graphs
# https://www.pymc-marketing.io/en/stable/notebooks/mmm/mmm_example.html#contribution-recovery


## ROAs
# https://www.pymc-marketing.io/en/stable/notebooks/mmm/mmm_example.html#roas



## so pymc 
@rt("/closer-look")
def get():
    content = DashContent()
    return (
        Title('IndyStats'),
        Body(cls="min-h-screen")(
            sidebar(),
            top_navbar(),
            Script(src="/static/js/oklch-rgb.js"),
            ############ main ############
            Form()(
                Div(cls="main-content min-h-screen expanded p-5")(
                    Div(cls='grid grid-cols-8')(
                        Div(cls='col-span-8 h-144 flex justify-center items-center')(render_closer_look(content)),
                        Div(cls='col-span-8 flex justify-center items-center')(Span('hi')), 
                        
                        # Div(cls='col-span-2 w-full pt-19')(
                        #     Div(cls='bg-base-100 border-base-300 collapse collapse-arrow border')( 
                        #         Input(type='checkbox', cls='peer'),
                        #         Div('Past Experiments', cls='collapse-title'),
                        #         Div('Click the "Sign Up" button in the top right corner and follow the registration process.', cls='collapse-content')
                        #     ),
                        #     Div(cls='bg-base-100 border-base-300 collapse collapse-arrow border')( 
                        #         Input(type='checkbox', cls='peer'),
                        #         Div('How do I create an account?', cls='collapse-title'),
                        #         Div('Click the "Sign Up" button in the top right corner and follow the registration process.', cls='collapse-content')
                        #     ),
                        #     Div(cls='bg-base-100 border-base-300 collapse collapse-arrow border')( 
                        #         Input(type='checkbox', cls='peer'),
                        #         Div('How do I create an account?', cls='collapse-title'),
                        #         Div('Click the "Sign Up" button in the top right corner and follow the registration process.', cls='collapse-content')
                        #     ) 
                        # )
                    ),
                    
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
            Div(cls="main-content min-h-screen expanded p-5")(
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
