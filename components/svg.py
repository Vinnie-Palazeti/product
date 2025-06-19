from fasthtml.svg import *

money = Svg(xmlns="http://www.w3.org/2000/svg", fill="none",viewbox="0 0 24 24",stroke="currentColor",stroke_width="2",cls="size-8",)(Path(stroke_linecap="round",stroke_linejoin="round",d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"))

plus=Svg(
    Path(d='M5 12h14'),
    Path(d='M12 5v14'),
    cls='h-4 w-4',
    xmlns='http://www.w3.org/2000/svg',
    viewbox='0 0 24 24',
    fill='none',
    stroke='currentColor',
    stroke_width='2',
    stroke_linecap='round',
    stroke_linejoin='round'
)

cash = Svg(
    cls="inline-block h-8 w-8 stroke-current dark:text-white",
    aria_hidden="true",
    xmlns="http://www.w3.org/2000/svg",
    fill="none",
    viewBox="0 0 24 24",
)(
    Path(
        stroke="currentColor",
        stroke_linecap="round",
        stroke_linejoin="round",
        stroke_width="2",
        d="M8 7V6a1 1 0 0 1 1-1h11a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1h-1M3 18v-7a1 1 0 0 1 1-1h11a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1Zm8-3.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0Z",
    )
)

x = Svg(
    cls='block h-4 w-4 stroke-current dark:text-white', 
    xmlns='http://www.w3.org/2000/svg', viewbox='0 0 24 24', fill='none', stroke='currentColor', stroke_width='1', stroke_linecap='round', stroke_linejoin='round')(
    Path(d='M18 6 6 18'),
    Path(d='m6 6 12 12')
)

visit = Svg(
    cls='block h-4 w-4 stroke-current dark:text-white',
    xmlns='http://www.w3.org/2000/svg', viewbox='0 0 24 24', fill='none', stroke='currentColor', stroke_width='1', stroke_linecap='round', stroke_linejoin='round')(
    Path(d='M15 3h6v6'),
    Path(d='M10 14 21 3'),
    Path(d='M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6')
)
    
users = Svg(
    cls='block h-8 w-8 stroke-current',    
    xmlns='http://www.w3.org/2000/svg', viewbox='0 0 24 24', fill='none', stroke='currentColor', stroke_width='2', stroke_linecap='round', stroke_linejoin='round')(
    Path(d='M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2'),
    Path(d='M16 3.128a4 4 0 0 1 0 7.744'),
    Path(d='M22 21v-2a4 4 0 0 0-3-3.87'),
    Circle(cx='9', cy='7', r='4')
)


banknote_up = Svg(cls='inline-block h-8 w-8 stroke-current dark:text-white', xmlns='http://www.w3.org/2000/svg', width='24', height='24', viewbox='0 0 24 24', fill='none', stroke='currentColor', stroke_width='2', stroke_linecap='round', stroke_linejoin='round')(
    Path(d='M12 18H4a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5'),
    Path(d='M18 12h.01'),
    Path(d='M19 22v-6'),
    Path(d='m22 19-3-3-3 3'),
    Path(d='M6 12h.01'),
    Circle(cx='12', cy='12', r='2')
)


up_arrow = Svg(xmlns='http://www.w3.org/2000/svg', fill='none', viewbox='0 0 24 24', stroke='currentColor', cls='size-4')(
    Path(stroke_linecap='round', stroke_linejoin='round', stroke_width='2', d='M13 7h8m0 0v8m0-8l-8 8-4-4-6 6')
)

down_arrow = Svg(xmlns='http://www.w3.org/2000/svg', fill='none', viewbox='0 0 24 24', stroke='currentColor', cls='size-4')(
    Path(stroke_linecap='round', stroke_linejoin='round', stroke_width='2', d='M13 17h8m0 0V9m0 8l-8-8-4 4-6-6')
)

banknote_x = Svg(
    cls='inline-block h-8 w-8 stroke-current dark:text-white',
    
    xmlns='http://www.w3.org/2000/svg', width='24', height='24', viewbox='0 0 24 24', fill='none', stroke='currentColor', stroke_width='2', stroke_linecap='round', stroke_linejoin='round')(
    Path(d='M13 18H4a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5'),
    Path(d='m17 17 5 5'),
    Path(d='M18 12h.01'),
    Path(d='m22 17-5 5'),
    Path(d='M6 12h.01'),
    Circle(cx='12', cy='12', r='2')
)
    

compare = Svg(aria_hidden='true', xmlns='http://www.w3.org/2000/svg', width='24', height='24', fill='none', viewbox='0 0 24 24', cls='w-5 h-5 dark:text-white')(
    Path(stroke='currentColor', stroke_linecap='round', stroke_linejoin='round', stroke_width='2', d='M6 8v8m0-8a2 2 0 1 0 0-4 2 2 0 0 0 0 4Zm0 8a2 2 0 1 0 0 4 2 2 0 0 0 0-4Zm12 0a2 2 0 1 0 0 4 2 2 0 0 0 0-4Zm0 0V9a3 3 0 0 0-3-3h-3m1.5-2-2 2 2 2')
)

arrow_down = Svg(aria_hidden='true', xmlns='http://www.w3.org/2000/svg', width='24', height='24', fill='none', viewbox='0 0 24 24', cls='w-5 h-5 dark:text-white')(
    Path(stroke='currentColor', stroke_linecap='round', stroke_linejoin='round', stroke_width='2', d='m19 9-7 7-7-7')
)

calendar = Svg(
    cls='h-5 w-5',
    viewbox='0 0 24 24', fill='none', xmlns='http://www.w3.org/2000/svg')(
    Path(fill_rule='evenodd', clip_rule='evenodd', d='M4 9.5L20 9.5V11L4 11V9.5Z', fill='currentColor'),
    Rect(x='14.5', y='3.5', width='1.5', height='5', rx='0.5', fill='currentColor'),
    Rect(x='8', y='3.5', width='1.5', height='5', rx='0.5', fill='currentColor'),
    Path(fill_rule='evenodd', clip_rule='evenodd', d='M5 5.5C3.89543 5.5 3 6.39543 3 7.5V18.5C3 19.6046 3.89543 20.5 5 20.5H19C20.1046 20.5 21 19.6046 21 18.5V7.5C21 6.39543 20.1046 5.5 19 5.5H5ZM5.5 7C4.94772 7 4.5 7.44772 4.5 8V18C4.5 18.5523 4.94772 19 5.5 19H18.5C19.0523 19 19.5 18.5523 19.5 18V8C19.5 7.44772 19.0523 7 18.5 7H5.5Z', fill='currentColor'),
    Circle(cx='9.33329', cy='12.6667', r='0.666667', fill='currentColor'),
    Circle(cx='12', cy='12.6667', r='0.666667', fill='currentColor'),
    Circle(cx='14.6665', cy='12.6667', r='0.666667', fill='currentColor'),
    Circle(cx='17.3333', cy='12.6667', r='0.666667', fill='currentColor'),
    Circle(cx='6.66667', cy='14.9167', r='0.666667', fill='currentColor'),
    Circle(cx='9.33342', cy='14.9167', r='0.666667', fill='currentColor'),
    Circle(cx='11.9999', cy='14.9167', r='0.666667', fill='currentColor'),
    Circle(cx='14.6667', cy='14.9167', r='0.666667', fill='currentColor'),
    Circle(cx='17.3334', cy='14.9167', r='0.666667', fill='currentColor'),
    Circle(cx='6.66667', cy='17.1667', r='0.666667', fill='currentColor'),
    Circle(cx='9.33335', cy='17.1667', r='0.666667', fill='currentColor'),
    Circle(cx='12', cy='17.1667', r='0.666667', fill='currentColor'),
    Circle(cx='14.6667', cy='17.1667', r='0.666667', fill='currentColor')
)
    
home_svg = Svg(xmlns='http://www.w3.org/2000/svg', fill='none', viewbox='0 0 24 24',width='24', height='24', stroke='currentColor', cls='h-5 w-5')(
    Path(stroke_linecap='round', stroke_linejoin='round', stroke_width='2', d='M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6')
)

palette = Svg(
    cls='w-5 h-5 dark:text-white',
    xmlns='http://www.w3.org/2000/svg', width='24', height='24', viewbox='0 0 24 24', fill='none', stroke='currentColor', stroke_width='2', stroke_linecap='round', stroke_linejoin='round')(
    Circle(cx='13.5', cy='6.5', r='.5', fill='currentColor'),
    Circle(cx='17.5', cy='10.5', r='.5', fill='currentColor'),
    Circle(cx='8.5', cy='7.5', r='.5', fill='currentColor'),
    Circle(cx='6.5', cy='12.5', r='.5', fill='currentColor'),
    Path(d='M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z')
)   

buzz = Svg(
    cls='w-8 h-8 dark:text-white',
    xmlns='http://www.w3.org/2000/svg', viewbox='0 0 24 24', fill='none', stroke='currentColor', stroke_width='2', stroke_linecap='round', stroke_linejoin='round')(
    Path(d='m2 8 2 2-2 2 2 2-2 2'),
    Path(d='m22 8-2 2 2 2-2 2 2 2'),
    Rect(width='8', height='14', x='8', y='5', rx='1')
)
    
ret_user = Svg(
    cls='block w-8 h-8',    
    xmlns='http://www.w3.org/2000/svg', viewbox='0 0 24 24', fill='none', stroke='currentColor', stroke_width='2', stroke_linecap='round', stroke_linejoin='round')(
    Path(d='M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2'),
    Circle(cx='9', cy='7', r='4'),
    Polyline(points='16 11 18 13 22 9')
)
    
new_user = Svg(
    cls='block w-8 h-8 stroke-current', 
    xmlns='http://www.w3.org/2000/svg', width='24', height='24', viewbox='0 0 24 24', fill='none', stroke='currentColor', stroke_width='2', stroke_linecap='round', stroke_linejoin='round')(
    Path(d='M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2'),
    Circle(cx='9', cy='7', r='4'),
    Line(x1='19', x2='19', y1='8', y2='14', stroke='currentColor'),
    Line(x1='22', x2='16', y1='11', y2='11', stroke='currentColor')
)
    
traffic = Svg(
    cls='block w-8 h-8 stroke-current',
    xmlns='http://www.w3.org/2000/svg', width='24', height='24', viewbox='0 0 24 24', fill='none', stroke='currentColor', stroke_width='2', stroke_linecap='round', stroke_linejoin='round')(
    Path(d='m21 8-2 2-1.5-3.7A2 2 0 0 0 15.646 5H8.4a2 2 0 0 0-1.903 1.257L5 10 3 8'),
    Path(d='M7 14h.01'),
    Path(d='M17 14h.01'),
    Rect(width='18', height='8', x='3', y='10', rx='2'),
    Path(d='M5 18v2'),
    Path(d='M19 18v2')
)


SVG_MAP = {
    "users": users,
    "new_users":new_user,
    "buzz": buzz,    
    "expenses": banknote_x,
    "revenue": cash,
    "profit": money,
    'increase':up_arrow,
    'decrease':down_arrow,
    'x':x,
    'visit':visit,
    'returning_users':ret_user,
    'traffic':traffic
}