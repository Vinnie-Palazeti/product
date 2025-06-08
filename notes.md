## Notes


double click modal
sortablejs for charts within respective grid

update tick marks to be standard length.. 100 1.6K 50 (can I add a space?)
- should also help width

standard tooltip location? 

comparison values
group by month should switch..

`./tailwindcss -i static/css/input.css -o static/css/output.css --watch`



<!-- 
No longer needed on KPI buttons
    Button(..., hx_on__after_request="handleButtonClick(this)")
    ...
    Script("""
    function handleButtonClick(button) {
        
        // This is sufficient - no htmx.process() needed
        Array.from(button.attributes).forEach(attr => {
            if (attr.name.startsWith('hx-')) {
                button.removeAttribute(attr.name);
            }
        });
    }""")
 -->

 