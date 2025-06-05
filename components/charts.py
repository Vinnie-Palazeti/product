from fasthtml.common import *
from uuid import uuid4
from pyecharts.charts import Line, Grid
import pyecharts.options as opts
from pyecharts.commons.utils import JsCode
from pyecharts.charts import Calendar
from pyecharts.faker import Faker
from pyecharts.charts import Bar
import datetime
import random

area_color_js = (
    "new echarts.graphic.LinearGradient(0, 0, 0, 1, "
    "[{offset: 0, color: 'rgb(255, 158, 68)'}, {offset: 1, color: 'rgb(255, 70, 131)'}], false)"
)
2
find_color=JsCode("""
function colorFromTheme(cssVarName = '--color-primary') {
      const cssVal = getComputedStyle(document.documentElement).getPropertyValue(cssVarName).trim();
      const parsed = culori.parse(cssVal);
      const rgb = culori.formatRgb(parsed);
      console.log(`Converted ${cssVarName}:`, rgb); // e.g. "rgb(59, 130, 246)"
      return rgb;
    }
""")
### need to manually set tick bars..
## I could probably compute the primary color BEFORE I send it here.. using jscript from fasthml.. then pass it here

## also need to somehow make cerything the same character length...

## 100, 1000, 10000... etc
def line_chart(x, y, x_axis_label=True, line_color=None):

    c = (
        Line()
        .add_xaxis(xaxis_data=x)
        .add_yaxis(
            series_name="",
            y_axis=y,
            symbol="emptyCircle",
            is_symbol_show=False,
            label_opts=opts.LabelOpts(is_show=False, color='rgb(255, 158, 68)'),
            linestyle_opts=opts.LineStyleOpts(color="rgb(255, 158, 68)"),
            itemstyle_opts=opts.ItemStyleOpts(color="rgb(255, 158, 68)"),
                        
            # linestyle_opts=opts.LineStyleOpts(color='--color-accent'),
            # areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
            # areastyle_opts=opts.AreaStyleOpts(color=JsCode(area_color_js), opacity=0.3),
        )
        .set_global_opts(         
            tooltip_opts=opts.TooltipOpts(
                    is_show=True, 
                    trigger="axis",
                    position='top',
                    textstyle_opts=opts.TextStyleOpts(color="#ffffff"),  # Text color
                    background_color="rgba(50, 50, 50, 0.7)"  # Background color
                ),                               
            xaxis_opts=opts.AxisOpts(
                # formatter
                position='top',
                # is_inverse=True,
                type_="category",
                axispointer_opts=opts.AxisPointerOpts(is_show=True, type_="line"),
                # boundary_gap=False,
                axislabel_opts=opts.LabelOpts(
                    formatter=JsCode("function(value, index){if (index === 0) {return '';} return value;}"),
                    is_show=x_axis_label),
                axisline_opts=opts.AxisLineOpts(is_show=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=0.90)),
            ),
            yaxis_opts=opts.AxisOpts(
                # interval=30,
                position='right',
                # is_inverse=True,
                type_="value",
                # axispointer_opts=opts.AxisPointerOpts(is_show=True, type_="line"),
                axislabel_opts=opts.LabelOpts(is_show=True),
                axisline_opts=opts.AxisLineOpts(is_show=False),
                axistick_opts=opts.AxisTickOpts(is_show=False),
                splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(opacity=0.90)),                
            ),
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

def embed_chart(chart):
    # needs to be unique, but don't really need it after this
    chart_id = f'{uuid4()}' 
    chart_name = str(chart_id).replace("-","")
    options = chart if isinstance(chart,str) else chart.dump_options()
    chart_script = Script(f"""
        var chart_{chart_name} = echarts.init(document.getElementById('{chart_id}'), 'white', {{renderer: 'canvas'}});
        var option_{chart_name} = {options};
        chart_{chart_name}.setOption(option_{chart_name});
        
        // Add this chart to global registry
        if (!window.chartRegistry) {{
            window.chartRegistry = [];
        }}
        
        window.chartRegistry.push(chart_{chart_name});
        
        echarts.connect(window.chartRegistry);    
        
        window.addEventListener('resize', function() {{
            chart_{chart_name}.resize();
        }});         
    """)
    return chart_id, chart_script, chart_name

def embed_line_chart(x, y, x_axis_label, cls='w-full h-full'): #
    c = embed_chart(line_chart(x,y, x_axis_label))
    return Div(c[1], id=c[0], cls=cls)

# def connect_charts(chart_names):
#     return Script(f"""\n echarts.connect([{",".join(['chart_'+i for i in chart_names])}])""")


def bar_row(n,v,p,s,top:bool=False):
    return (
        Tr(cls=f"h-4 group {'border-t border-gray-200' if top else ''}")(
            Td(colspan='2', cls='px-0 py-0 relative overflow-hidden')(
                Div(style=f'width: {s}%', cls='absolute inset-0 bg-secondary/80 z-0 h-full animate-grow-bar transition-transform duration-300 group-hover:scale-[1.02] group-hover:bg-secondary/70'),
                Div(cls='flex justify-between items-center px-4 py-0 relative z-10 h-full')(
                    Span(n),
                    Span(v, cls='text-right')
                )
            ),
            Td(p, cls='px-4 py-0 text-right text-red-500')
        )
    )  

def bar(metric:str, grp:str):
    data = [('Zoom', '$123.1K', '-13%', 60), ('Spotify', '$50.2K', '+15%', 18), ('Jira', '$44.8K', '-2%', 10), ('Asana', '$20.2K', '+10%', 8)]
    return (
        Table(cls='w-full text-sm text-left table-fixed border-collapse')(
            Thead()(
                Tr(
                    Th(f'{metric} by {grp}', cls='px-0 py-2 w-1/2'),
                    Th('#', cls='px-6 py-2 text-right w-1/3'),
                    Th('Δ%', cls='px-6 py-2 text-right w-1/6')
                )
            ),
            Tbody()(*[bar_row(n=row[0], v=row[1], p=row[2], s=row[3], top=1 if j==0 else None) for j,row in enumerate(data)])
        )
    )




import random
import datetime
from pyecharts import options as opts
from pyecharts.charts import Calendar

# Create the date list with lunar calendar data and solar terms
date_list = [
  ['2017-3-1', '初四'],
  ['2017-3-2', '初五'],
  ['2017-3-3', '初六'],
  ['2017-3-4', '初七'],
  ['2017-3-5', '初八', '驚蟄'],
  ['2017-3-6', '初九'],
  ['2017-3-7', '初十'],
  ['2017-3-8', '十一'],
  ['2017-3-9', '十二'],
  ['2017-3-10', '十三'],
  ['2017-3-11', '十四'],
  ['2017-3-12', '十五'],
  ['2017-3-13', '十六'],
  ['2017-3-14', '十七'],
  ['2017-3-15', '十八'],
  ['2017-3-16', '十九'],
  ['2017-3-17', '二十'],
  ['2017-3-18', '廿一'],
  ['2017-3-19', '廿二'],
  ['2017-3-20', '廿三', '春分'],
  ['2017-3-21', '廿四'],
  ['2017-3-22', '廿五'],
  ['2017-3-23', '廿六'],
  ['2017-3-24', '廿七'],
  ['2017-3-25', '廿八'],
  ['2017-3-26', '廿九'],
  ['2017-3-27', '三十'],
  ['2017-3-28', '三月'],
  ['2017-3-29', '初二'],
  ['2017-3-30', '初三'],
  ['2017-3-31', '初四']
]

# Prepare data in the format needed by pyecharts
heatmap_data = []
lunar_data = []
solar_term_data = []

# Process the date list to create the necessary data structures
for item in date_list:
    date_str = item[0]
    lunar_day = item[1]
    
    # Add random rainfall data for heatmap (as in the original)
    rainfall = random.random() * 300
    heatmap_data.append([date_str, rainfall])
    
    # Add lunar calendar day data
    lunar_data.append([date_str, lunar_day])
    
    # Add solar term data if present
    if len(item) > 2:
        solar_term_data.append([date_str, item[2]])

# # Create the calendar chart
# calendar = Calendar()

# # Add heatmap data series for rainfall
# calendar.add(
#     series_name="降雨量",
#     yaxis_data=heatmap_data,
#     calendar_opts=opts.CalendarOpts(
#         pos_left="center",
#         pos_top="middle",
#         range_="2017-03",  # Show only March 2017 as in original
#         cell_size=["50", "50"],
#         orient="vertical",
#         yearlabel_opts=opts.CalendarYearLabelOpts(is_show=False),
#         daylabel_opts=opts.CalendarDayLabelOpts(
#             first_day=1,  # Monday as first day
#             name_map="cn"  # Chinese day names
#         ),
#         monthlabel_opts=opts.CalendarMonthLabelOpts(is_show=False)
#     )
# )



# # Add scatter series for lunar calendar days
# calendar.add(
#     series_name="",
#     yaxis_data=lunar_data,
#     type_="scatter",
#     symbol_size=0,  # Invisible scatter points
#     label_opts=opts.LabelOpts(
#         is_show=True,
#         position="inside",
#         color="#000"
#     ),
#     is_silent=True
# )

# # Add scatter series for solar terms
# calendar.add(
#     series_name="",
#     yaxis_data=solar_term_data,
#     type_="scatter",
#     symbol_size=0,  # Invisible scatter points
#     label_opts=opts.LabelOpts(
#         is_show=True,
#         position="inside",
#         font_size=14,
#         font_weight="bold",
#         color="#a00"
#     ),
#     is_silent=True
# )

# # Set global options
# calendar.set_global_opts(
#     visualmap_opts=opts.VisualMapOpts(
#         is_show=False,
#         max_=300,
#         min_=0,
#         range_color=["#e0ffff", "#006edd"],
#         orient="horizontal",
#         pos_left="center",
#         pos_bottom=20,
#         range_opacity=0.3
#     ),
# )

# Create the calendar chart
calendar = Calendar()

# Add heatmap data series for rainfall
calendar.add(
    series_name="降雨量",
    yaxis_data=heatmap_data,
    type_="effectScatter",  # Changed from heatmap to effectScatter
    symbol_size=JsCode("""
        function(val) {
            return val[1] / 40;
        }
    """),
    effect_opts=opts.EffectOpts(
        is_show=True,
        brush_type="fill",
        scale=3.5,
        period=4,
    ),
    calendar_opts=opts.CalendarOpts(
        pos_left="center",
        pos_top="middle",
        range_="2017-03",  # Show only March 2017 as in original
        cell_size=["50", "50"],
        orient="vertical",
        yearlabel_opts=opts.CalendarYearLabelOpts(is_show=False),
        daylabel_opts=opts.CalendarDayLabelOpts(
            first_day=1,  # Monday as first day
            name_map="en"  # Chinese day names
        ),
        monthlabel_opts=opts.CalendarMonthLabelOpts(is_show=False)
    )
)

# Add scatter series for lunar calendar days
calendar.add(
    series_name="",
    yaxis_data=lunar_data,
    type_="scatter",
    symbol_size=0,  # Invisible scatter points
    label_opts=opts.LabelOpts(
        is_show=True,
        position="inside",
        color="#000"
    ),
    is_silent=True
)

# Add scatter series for solar terms
calendar.add(
    series_name="",
    yaxis_data=solar_term_data,
    type_="scatter",
    symbol_size=0,  # Invisible scatter points
    label_opts=opts.LabelOpts(
        is_show=True,
        position="inside",
        font_size=14,
        font_weight="bold",
        color="#a00"
    ),
    is_silent=True
)

# Set global options
calendar.set_global_opts(
    visualmap_opts=opts.VisualMapOpts(
        is_show=False,
        max_=100,
        min_=0,
        range_color=["#e0ffff", "#006edd"],
        orient="horizontal",
        pos_left="center",
        pos_bottom=20,
        range_opacity=0.3
    ),
)


def calendar_chart():
    return calendar



# def bar_chart():
#     return """{
#     grid: {
#         top: 50,            // space for headers
#         bottom: 0,
#         left: 0,
#         right: 90,          // extra space for Growth column
#         containLabel: false
#     },
#     tooltip: { show: false },
#     legend: { show: false },
#     xAxis: {
#         type: "value",
#         show: false,
#         max: 630230
#     },
#     yAxis: [
#         {
#             type: "category",
#             data: ["Brazil", "Indonesia", "USA", "India", "China", "World"],
#             position: "left",
#             axisLabel: { color: "#000", inside: true },
#             axisTick: { show: false },
#             axisLine: { show: false }
#         },
#         {
#             type: "category",
#             data: [18203, 23489, 29034, 104970, 131744, 630230],
#             position: "right",
#             axisLabel: { color: "#000" },
#             axisTick: { show: false },
#             axisLine: { show: false }
#         },
#         {
#             type: "category",
#             data: ["+2%", "+3%", "+1%", "+4%", "+5%", "+6%"],
#             position: "right",
#             offset: 50, // shift further right
#             axisLabel: {
#                 color: "#000",
#                 align: "left",
#                 fontWeight: "normal"
#             },
#             axisTick: { show: false },
#             axisLine: { show: false }
#         }
#     ],
#     series: [
#         {
#             name: "Population",
#             type: "bar",
#             data: [18203, 23489, 29034, 104970, 131744, 630230],
#             barCategoryGap: "0%",
#             barGap: "0%",
#             itemStyle: {
#                 color: {
#                     type: "linear",
#                     x: 0,
#                     y: 0,
#                     x2: 1,
#                     y2: 0,
#                     colorStops: [
#                         { offset: 0, color: "#008D8E" },
#                         { offset: 1, color: "#24C1C3" }
#                     ]
#                 },
#                 borderRadius: 4
#             }
#         },
#         {
            
#             type: "bar",
#             data: [0, 0, 0, 0, 0, 0],
#             yAxisIndex: 2, // third y-axis
#             xAxisIndex: 0,
#             barWidth: 1,
#             itemStyle: { color: "transparent" },
#             label: {
#                 show: true,
#                 position: "right",
#                 formatter: (params) => {
#                     const growth = ["+2%", "+3%", "+1%", "+4%", "+5%", "+6%"];
#                     return growth[params.dataIndex];
#                 },
#                 color: "#000",
#                 fontSize: 12
#             }
#         }
#     ],
#     graphic: [
#         {
#             type: "text",
#             left: 10,
#             top: 10,
#             style: {
#                 text: "Country",
#                 fontSize: 14,
#                 fill: "#000",
#                 fontWeight: "bold"
#             }
#         },
#         {
#             type: "text",
#             right: 80,
#             top: 10,
#             style: {
#                 text: "#",
#                 fontSize: 14,
#                 fill: "#000",
#                 fontWeight: "bold"
#             }
#         },
#         {
#             type: "text",
#             right: 20,
#             top: 10,
#             style: {
#                 text: "Growth",
#                 fontSize: 14,
#                 fill: "#000",
#                 fontWeight: "bold"
#             }
#         }
#     ]
# }

#     """


# def embed_bar_chart(cls='w-full h-full'):
#     c=embed_chart(bar_chart())
#     return Div(c[1], id=c[0], cls=cls), c[2]  







# def calendar_chart():
#     begin = datetime.date(2017, 1, 1)
#     end = datetime.date(2017, 1, 31)
#     data = [
#         [str(begin + datetime.timedelta(days=i)), random.randint(1000, 25000)]
#         for i in range((end - begin).days + 1)
#     ]
    
#     print(data)

#     c = (
#         Calendar()
#         .add(
#             "",
#             data,
#             calendar_opts=opts.CalendarOpts(
#                 range_="2017-01",
#                 daylabel_opts=opts.CalendarDayLabelOpts(),
#                 monthlabel_opts=opts.CalendarMonthLabelOpts(),
#             ),
#         )
#         .set_global_opts(
#             # title_opts=opts.TitleOpts(title="Calendar-2017年微信步数情况(中文 Label)"),
#             visualmap_opts=opts.VisualMapOpts(
#                 max_=20000,
#                 min_=500,
#                 orient="horizontal",
#                 is_piecewise=True,
#                 pos_top="230px",
#                 pos_left="100px",
#             ),
#         )
#     )
    
#     c = (
#         Grid()
#         .add(
#             c,
#             grid_opts=opts.GridOpts(
#                 pos_top="10%",
#                 pos_left="0%",
#                 pos_right="2%",
#                 pos_bottom="5%",            
#                 is_contain_label=True
#             )
#         )
#     )      
#     return c
    
def embed_calendar_chart(cls='w-full h-full'):
    c=embed_chart(calendar_chart())
    return Div(c[1], id=c[0], cls=cls), c[2]  



