
document.addEventListener('DOMContentLoaded', () => {
    if (!window.chartRegistry) window.chartRegistry = [];

    // Listen for a click/change on any theme-controller input
    document.querySelectorAll('input.theme-controller')
            .forEach(input => input.addEventListener('change', recolorAll));
});

function cssOklchToRgb(cssVarName) {
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
    return `rgb(${rgb255[0]}, ${rgb255[1]}, ${rgb255[2]})`;
} 

function recolorAll() {    
    var rgbPrim = cssOklchToRgb('--color-primary');
    var rgbSec = cssOklchToRgb('--color-secondary');

    console.log(rgbPrim);
    console.log(rgbSec);

    window.chartRegistry.forEach(chart => {
        const newOption = {
            color: [rgbPrim, rgbSec], 
            series: chart.getOption().series.map((s, i) => ({
                ...s,
                lineStyle: { color: i === 0 ? rgbPrim : rgbSec },
                itemStyle: { color: i === 0 ? rgbPrim : rgbSec }
            }))
        };
        chart.setOption(newOption); 
    });
}


