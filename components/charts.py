from fasthtml.common import *
from uuid import uuid4
from pyecharts.charts import Line, Grid, Bar, HeatMap
import pyecharts.options as opts
from pyecharts.commons.utils import JsCode
from components.relationships import UNIT_FIELDS
from components.svg import SVG_MAP
import numpy as np
from pyecharts.charts import Bar
from pyecharts import options as opts
import arviz as az
import pandas as pd


def channel_contribution_barchart(data):
    labels = data['labels']
    values = data['values']

    # dataframe = mmm.compute_mean_contributions_over_time(original_scale=True)
    # dataframe = mmm._process_decomposition_components(data=dataframe)
    
    # dataframe['percent'] = (dataframe['contribution'] / 100).round(2)
    # values = dataframe['contribution'].round(2).to_list()
    # labels = dataframe['component'].to_list()  
        
    c = (
        Bar()
        .add_xaxis(xaxis_data=labels)
        .add_yaxis(series_name="Channel Contribution", y_axis=values,label_opts=opts.LabelOpts(is_show=True,position='right'))
        .reversal_axis()
        .set_global_opts(legend_opts=opts.LegendOpts(is_show=False))
    )
    c = (
        Grid()
        .add(
            c,
            grid_opts=opts.GridOpts(
                pos_top="5%",
                pos_left="5%",
                pos_right="5%",
                pos_bottom="5%",
                is_contain_label=True
            )
        )
    ) 
    c = embed_chart(c)   
    return Div(c[1], id=c[0], cls='w-full h-full') 

def calculate_manual_ticks(min_val, max_val, num_ticks=5):
    """Calculate manual tick positions based on data range"""
    
    # Create evenly spaced tick positions
    tick_positions = np.linspace(min_val, max_val, num_ticks)
    
    # Round to nice numbers
    tick_positions = [round(tick) for tick in tick_positions]
    
    return tick_positions    

def format_tick(val):
    if val >= 10000:
        return f"{val // 1000}K"  # No decimals for 10K+
    elif val >= 1000:
        return f"{val / 1000:.1f}K".rstrip('0').rstrip('.')  # Decimals for 1K-10K
    return str(val)
    
def format_ticks(manual_ticks):
    ticks = '\n'.join([f"if (isClose(value, {i})) return '{format_tick(i)}';" for i in manual_ticks])    
    return JsCode(f"""
        function (value) {{
            const isClose = (a, b, tolerance = 1) => Math.abs(a - b) <= tolerance;
            {ticks}
            return '';
        }}
    """)   
        
def line_chart(x, y, show_label=False, label_pos='right', name=""):
    ## need to add x axis first.
    c = (
        Line()
        .add_xaxis(xaxis_data=x)
    )
    ## if received a tuple, that means there is two series
    ## a single list would be one series
    if isinstance(y, tuple):
        y_compare = y[-1] ## comparison period
        y=y[0] ## selected period
        ## format again (still getting weirdly rounded numbers?)
        y = [round(i,2) for i in y]
        y_compare = [round(i,2) for i in y_compare]
        ## get minimum and maximum for ticks
        min_=round(min(y + y_compare)*0.95)         
        max_=round(max(y + y_compare)*1.05)  
        manual_ticks = calculate_manual_ticks(min_,max_,4)    
        
        ## add comparion period to line chart
        c = (
            c
            .add_yaxis(
                series_name=name,
                y_axis=y,
                symbol="emptyCircle",
                is_symbol_show=False,
                label_opts=opts.LabelOpts(is_show=False)
            )
            .add_yaxis(
                series_name="comparison",
                y_axis=y_compare,
                symbol="emptyCircle",
                is_symbol_show=False,
                label_opts=opts.LabelOpts(is_show=False, color='rgb(68, 158, 255)'),
                linestyle_opts=opts.LineStyleOpts(color="rgb(68, 158, 255)"),
                itemstyle_opts=opts.ItemStyleOpts(color="rgb(68, 158, 255)")          
            )
        )
    else:
        y = [round(i,2) for i in y]
        min_=round(min(y)*0.98)         
        max_=round(max(y)*1.02)
        manual_ticks = calculate_manual_ticks(min_,max_,4)
        c = (
            c
            .add_yaxis(
                series_name="",
                y_axis=y,
                symbol="emptyCircle",
                is_symbol_show=False,
                label_opts=opts.LabelOpts(is_show=False)
            )       
            
        )       
        
    c = (
        c           
        .set_global_opts(
            legend_opts=opts.LegendOpts(is_show=False),  # hide legend 
            tooltip_opts=opts.TooltipOpts(
                    is_show=True, 
                    trigger="axis",
                    position='top',
                    textstyle_opts=opts.TextStyleOpts(color="#ffffff"),  # Text color
                    background_color="rgba(50, 50, 50, 0.7)"  # Background color
            ),                               
            xaxis_opts=opts.AxisOpts(
                position='top',
                type_="category",
                axispointer_opts=opts.AxisPointerOpts(is_show=True, type_="line"),
                axislabel_opts=opts.LabelOpts(formatter=JsCode("function(value, index){if (index === 0) {return '';} return value;}"), is_show=show_label),
                axisline_opts=opts.AxisLineOpts(is_show=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=0.90)),
            ),
            yaxis_opts=opts.AxisOpts(
                min_=min_,          
                max_=max_,   
                position=label_pos,
                type_="value",
                interval=round((max(manual_ticks) - min(manual_ticks)) / (len(manual_ticks) - 1)),
                axislabel_opts=opts.LabelOpts(is_show=True, formatter=format_ticks(manual_ticks)),                
                axisline_opts=opts.AxisLineOpts(is_show=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=0.90)),                
            )
        )
    )
    c = (
        Grid()
        .add(
            c,
            grid_opts=opts.GridOpts(
                pos_top="10%",
                pos_left="0%",
                pos_right="2%",
                pos_bottom="5%",            
                is_contain_label=True
            )
        )
    )    
    return c

def channel_contributions_over_time(data):
    x = data['date']
    y_data = data['values']
    series_names = data['labels']
    c = embed_chart(area_chart(x, y_data, series_names), connect=False)
    return Div(c[1], id=c[0], cls='w-full h-full')
        

def area_chart(x, y_data, series_names):
    c = (
        Line()
        .add_xaxis(xaxis_data=x)
    )
    # Add each series as area
    for i, (name, data) in enumerate(zip(series_names, y_data)):
        c = c.add_yaxis(
            series_name=name,
            y_axis=data,
            stack="contributions",  # Stack all contributions
            areastyle_opts=opts.AreaStyleOpts(opacity=0.7),
            symbol="emptyCircle",
            is_symbol_show=False,
            label_opts=opts.LabelOpts(is_show=False)
        )
    c = (
        c.set_global_opts(
            tooltip_opts=opts.TooltipOpts(
                is_show=True,
                trigger="axis",
                position='top',
                textstyle_opts=opts.TextStyleOpts(color="#ffffff"),
                background_color="rgba(50, 50, 50, 0.7)"
            ),
            xaxis_opts=opts.AxisOpts(
                position='bottom',
                type_="category",
                axispointer_opts=opts.AxisPointerOpts(is_show=True, type_="line"),
                axislabel_opts=opts.LabelOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(is_show=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=0.90)),
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                axisline_opts=opts.AxisLineOpts(is_show=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=0.90)),
            ),
            legend_opts=opts.LegendOpts(is_show=True, pos_top="5%")
        )
    )
    
    c = (
        Grid()
        .add(
            c,
            grid_opts=opts.GridOpts(
                pos_top="5%",
                pos_left="5%",
                pos_right="5%",
                pos_bottom="5%",
                is_contain_label=True
            )
        )
    )
    return c


def channel_contributions_forward_pass_grid(data):
    line = Line().add_xaxis(data['x_axis'])
    for k,v in data.items():
        if k == 'x_axis':
            continue
        line = (
            line
            .add_yaxis(
                series_name=k,
                y_axis=v['values'],
                is_symbol_show=False,
                label_opts=opts.LabelOpts(is_show=False),
            )
            .add_yaxis(
                series_name=f"{k}-low",
                y_axis=v['lower'],
                is_symbol_show=False,
                linestyle_opts=opts.LineStyleOpts(opacity=0),
                stack=k,
                label_opts=opts.LabelOpts(is_show=False),
            )
            .add_yaxis(
                series_name=f"{k}-upper",
                y_axis=v['upper'],
                is_symbol_show=False,
                linestyle_opts=opts.LineStyleOpts(opacity=0),
                areastyle_opts=opts.AreaStyleOpts(opacity=0.2),
                stack=k,
                label_opts=opts.LabelOpts(is_show=False),
            )
        )
    line = line.add_yaxis(
        series_name="Current Spend",
        y_axis=[None] * len(data['x_axis']),
        is_symbol_show=False,
        label_opts=opts.LabelOpts(is_show=False),
        markline_opts=opts.MarkLineOpts(
            data=[opts.MarkLineItem(x='1.0')],
            symbol=["none", "none"], 
            linestyle_opts=opts.LineStyleOpts(type_="dotted", width=2),
        ),
    )   
    
    # print(data['x_axis'])     
        
    line=(
        line
        # .set_series_opts(markline_opts=opts.MarkLineOpts(data=[opts.MarkLineItem(x=1.0)], linestyle_opts=opts.LineStyleOpts(type_="dotted", width=2)))
        .set_global_opts(legend_opts=opts.LegendOpts(is_show=False), tooltip_opts=opts.TooltipOpts(trigger="axis", position="top"))
    )
    
    grid = (
        Grid()
        .add(
            line, 
            grid_opts=opts.GridOpts(
                pos_top="10%", 
                pos_left="5%", 
                pos_right="5%", 
                pos_bottom="10%", 
                is_contain_label=True
            )
        )
    )
    c = embed_chart(grid, connect=False)
    return Div(c[1], id=c[0], cls='w-full h-full')


# one thing to note here is the charts only have to be INTERNALLY consistent..
def embed_chart(chart, color = True, connect= True):
    # needs to be unique, but don't really need it after this
    chart_id = f'{uuid4()}' 
    chart_name = str(chart_id).replace("-","")
    options = chart if isinstance(chart,str) else chart.dump_options()
    chart_script = fr"""                          
        var chart_{chart_name} = echarts.init(document.getElementById('{chart_id}'), 'white', {{renderer: 'canvas'}});
        var option_{chart_name} = {options};
        chart_{chart_name}.setOption(option_{chart_name});
        
        // Add this chart to global registry
        if (!window.chartRegistry) {{
            window.chartRegistry = [];
        }}
        
        window.addEventListener('resize', function() {{
            chart_{chart_name}.resize();
        }});
        """
    if color:
        chart_script+=fr"""
        function cssOklchToRgb(cssVarName) {{
            // Step 1: Read OKLCH string from CSS variable
            const oklchStr = getComputedStyle(document.body).getPropertyValue(cssVarName).trim();

            // Step 2: Parse OKLCH string like: oklch(45% .24 277.023)
            const match = oklchStr.match(/oklch\(([\d.]+)%\s+([\d.]+)\s+([\d.]+)\)/);

            const [, lStr, cStr, hStr] = match;
            const l = parseFloat(lStr) / 100;
            const c = parseFloat(cStr);
            const h = parseFloat(hStr);

            // Step 3: Convert OKLCH to RGB (you must define this function somewhere)
            const rgb = oklch2rgb([l, c, h]);

            // Step 4: Clamp to [0, 1] and scale to [0, 255]
            const rgb255 = rgb.map(c => Math.round(Math.max(0, Math.min(1, c)) * 255));

            // Step 5: Format as CSS rgb() string
            return `rgb(${{rgb255[0]}}, ${{rgb255[1]}}, ${{rgb255[2]}})`;
        }} 
        
        var colors = [
            cssOklchToRgb('--color-primary'),
            cssOklchToRgb('--color-secondary'),
            cssOklchToRgb('--color-accent'),
            cssOklchToRgb('--color-info')
        ];
                
        // 1) grab the current option & series list
        const opt_{chart_name}  = chart_{chart_name}.getOption();
        const origSeries_{chart_name} = opt_{chart_name}.series;
        
        // 2) compute the list of unique base-names
        const baseNames_{chart_name} = Array.from(new Set(
            origSeries_{chart_name}.map(s => (s.name || '').replace(/-(low|upper)$/, ''))
        ));

        // 3) remap every series, lookup its base’s index, pick that color
        const newSeries_{chart_name} = origSeries_{chart_name}.map(s => {{
            const name     = s.name || '';
            const baseName = name.replace(/-(low|upper)$/, '');
            const idx      = baseNames_{chart_name}.indexOf(baseName);
            const color    = colors[idx % colors.length];

            return {{
                ...s,
                lineStyle: {{ ...(s.lineStyle || {{}}), color }},
                itemStyle: {{ ...(s.itemStyle || {{}}), color }}
            }};
        }});

        // 4) push it back into the chart
        chart_{chart_name}.setOption({{ series: newSeries_{chart_name} }});
        """
    if connect:
        chart_script+=fr"""
        window.chartRegistry.push(chart_{chart_name});
        echarts.connect(window.chartRegistry);             
        """
    return chart_id, Script(chart_script), chart_name

def embed_line_chart(x, y, show_label, label_pos='right', name="", cls='w-full h-full'): # flex justify-center items-center
    c = embed_chart(line_chart(x, y, show_label, label_pos, name))
    return Div(c[1], id=c[0], cls=cls)

def embed_area_chart(x, y_data, series_names, colors=None, cls='w-full h-full'):
    c = embed_chart(area_chart(x, y_data, series_names, colors))
    return Div(c[1], id=c[0], cls=cls)

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
                A(cls='hover:bg-base-300 cursor-pointer transition-colors duration-200', href=f"/closer-look?metric={name}")(
                    SVG_MAP.get("visit")
                )
            ),                     
            Div(cls="flex items-center justify-between")(
                Div()(
                    P(name.replace('_',' ').title(), cls="text-sm text-base-content"),
                    P(format_metric(value, dollar), 
                    cls="text-2xl font-medium text-primary"),
                ),
                Span(cls="text-secondary mt-5")(SVG_MAP.get(name)), # removed the numbers
            ),
            None if not comparison else 
            Div(cls=f"mt-1 flex gap-1 text-{'success' if pct_chng >=0 else 'error'}")(
                SVG_MAP.get('increase') if pct_chng >= 0  else SVG_MAP.get('decrease'),
                P(cls="flex gap-2 text-xs")(Span(f"{pct_chng:,.2f}%", cls="font-medium")),
            )
        )
    )

def stat_chart(name, timeseries, totals, show_label):    
    dates = [i.get('date') for i in timeseries.get('selected_period')]
    y = [i.get(name) for i in timeseries.get('selected_period')]
    if 'comparison_period' in timeseries:
        y = (
            y, # main data
            [i.get(name) for i in timeseries.get('comparison_period')], # comparison
        )
    c = embed_line_chart(x=dates, y=y, show_label=show_label, name=name)
    return (
        Div(id=f'metric-container-{name}', cls="contents")( ## this is a wrapper. display:contents -> element itself disappears and children styling  & layout is displayed
        stat(
            name=name, value=totals.get('selected_period').get(name), 
            dollar=name not in UNIT_FIELDS, 
            comparison=totals.get('comparison_period').get(name) if isinstance(y, tuple) else False ## this should still work
        ), 
        Div(c, cls="col-span-2", id=f'{name}-chart'))
    )
    
def bar_row(name, value, perc_change, perc_width, top:bool=False):
    if perc_change:
        fmt_change = f'{perc_change:,.0f}%'
        text = f"text-{'success' if perc_change>0 else 'error'}"
    else:
        fmt_change='-'
        text=None
    return (
        Tr(cls=f"h-4 group {'border-t border-primary-200' if top else ''}")(
            Td(colspan='2', cls='px-0 py-0 relative overflow-hidden')(
                Div(style=f'width: {perc_width}%', cls='absolute inset-0 bg-primary/20 z-0 h-full animate-grow-bar transition-transform duration-300 group-hover:scale-[1.10] group-hover:bg-primary/20'),
                Div(cls='flex justify-between items-center px-4 py-0 relative z-10 h-full')(
                    Span(name, cls='text-base-content'),
                    Span(value, cls='text-right text-base-content')
                )
            ),
            Td(fmt_change, cls=f'px-4 py-0 text-right {text}')
        )
    )
    
def pivot_by_category(rows, dim):
    return {
        row['category']: {k: v for k, v in row.items() if k != 'category'}
        for row in rows
        if row.get('dimension') == dim
    }

def bar_chart(data, kpi:str=None, dim:str=None):
    chart_data=pivot_by_category(rows=data.get('selected_period'), dim=dim)
    if 'comparison_period' in data:
        comp_data = pivot_by_category(rows=data.get('comparison_period'), dim=dim)
        for cat in chart_data.keys():
            current_val = chart_data.get(cat).get('total_value')
            comp_val = comp_data.get(cat).get('total_value')
            pct_change = ((current_val - comp_val) / current_val) * 100
            chart_data[cat].update({'perc_change': pct_change})
    return (
        Div(cls='col-span-2')(
            Table(cls='w-full text-sm text-left table-fixed border-collapse')(
                Thead()(
                    Tr(
                        Th(f'{dim}', cls='text-base-content px-0 py-2 w-1/2'),
                        Th('#', cls='px-6 py-2 text-right w-1/3'),
                        Th('Δ%', cls='px-6 py-2 text-right w-1/6')
                    )
                ),
                Tbody()(*[bar_row(name=nm, 
                                  value=format_metric(value=row.get('total_value'), dollar=kpi not in UNIT_FIELDS), 
                                  perc_change=row.get('perc_change'),
                                  perc_width=round((row.get('total_value')/row.get('dimension_total'))*100), 
                                  top=1 if j==0 else None) 
                          for j,(nm, row) in enumerate(chart_data.items())])
            )
        )
    )
    
