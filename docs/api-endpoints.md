# API Endpoints Documentation

This document describes all the HTTP endpoints available in the business metrics dashboard application.

## Overview

The application uses FastHTML with HTMX for dynamic updates. All endpoints return HTML fragments that are swapped into the DOM rather than JSON responses.

## Endpoints

### `GET /`
**Description**: Main dashboard page  
**Returns**: Complete HTML page with dashboard layout  
**Components**:
- Sidebar navigation
- Top navigation bar with theme switcher
- Main content area with metrics grid
- Default time period: Last 14 Days
- Default fields: users, gross_revenue, expenses

**Example Response**: Full HTML page with embedded charts and controls

---

### `POST /options-input`
**Description**: Updates dashboard options (time period, comparison, grouping)  
**Parameters**:
- `content: DashContent` - Dashboard configuration object
- `pressed: str` - Which option was changed ('time', 'comparison', or 'group')

**Request Body**:
```
time=Last 30 Days&comparison=Previous Period&group=Day&fields=users gross_revenue expenses&pressed=time
```

**Returns**: 
- Updated option UI component
- Hidden form input with new value
- Updated content grid with new data
- Additional group option update if time period requires different grouping

**Behavior**:
- Automatically adjusts grouping when time period changes (e.g., "Last 3 Months" switches to "Month" grouping)
- Refreshes all charts with new time range/comparison data

---

### `POST /remove-metric`
**Description**: Removes a metric from the dashboard  
**Parameters**:
- `field: str` - Name of the metric to remove
- `fields: list[str]` - Current list of active fields

**Request Body**:
```
field=expenses&fields=users gross_revenue expenses
```

**Returns**:
- `None` (removes the metric from grid)
- Button element to re-add the metric
- Updated hidden fields input

**Example**: Removing "expenses" metric will hide its chart and add an "Expenses" button to the metrics dropdown

---

### `POST /append-metric`
**Description**: Adds a metric to the dashboard  
**Parameters**:
- `field: str` - Name of the metric to add
- `group: str` - Current grouping (Day/Month/Year)
- `time: str` - Current time period
- `comparison: str` - Current comparison setting
- `fields: list[str]` - Current list of active fields

**Request Body**:
```
field=profit&group=Day&time=Last 14 Days&comparison=Previous Period&fields=users gross_revenue
```

**Returns**:
- New stat chart component for the added metric
- Updated hidden fields input with new field list

**Behavior**:
- Fetches data for the specific metric
- Creates new chart with same time settings as existing charts
- Adds to the end of the metrics grid

---

### `GET /{fname:path}.{ext:static}`
**Description**: Serves static files (CSS, JS, images)  
**Parameters**:
- `fname: str` - File path
- `ext: str` - File extension

**Returns**: Static file content

**Examples**:
- `/static/css/output.css` - Compiled Tailwind CSS
- `/collapse.js` - Sidebar collapse functionality

---

### `POST /test`
**Description**: Debug endpoint for testing form data  
**Parameters**:
- `d: dict` - Any form data

**Returns**: Prints form data to console (development only)

## Response Formats

### HTMX Responses
Most endpoints return HTML fragments with HTMX attributes:

- `hx-swap-oob="outerHTML"` - Replace element entirely
- `hx-target="#element-id"` - Target specific element for replacement
- `hx-swap="beforeend"` - Append to end of target element

### Hidden Form Inputs
Dashboard state is maintained through hidden form inputs:
- `#comparison-value` - Current comparison setting
- `#time-value` - Current time period  
- `#group-value` - Current grouping
- `#fields-value` - Space-separated list of active metrics

## Error Handling

The application includes basic error handling:
- Invalid time periods raise `ValueError`
- Database errors are caught and re-raised with context
- Missing fields are validated against `METRICS` list

## Data Flow

1. User interacts with UI (dropdown, button click)
2. HTMX sends POST request with current form state
3. Server processes request and queries database
4. Server returns HTML fragment with updated content
5. HTMX swaps content into DOM
6. Charts re-render with new data

## Authentication

Currently no authentication is implemented. All endpoints are publicly accessible.