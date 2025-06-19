document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('toggle-btn');
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    // Initialize chart registry if it doesn't exist
    if (!window.chartRegistry) {
        window.chartRegistry = [];
    }
    
    // Function to resize all charts
    function resizeAllCharts() {
        // Short delay to allow DOM to update
        setTimeout(function() {
            if (window.chartRegistry && window.chartRegistry.length > 0) {
                window.chartRegistry.forEach(function(chart) {
                    if (chart && typeof chart.resize === 'function') {
                        chart.resize();
                    }
                });
            }
        }, 300);
    }
    
    // Check if we're on mobile based on viewport width
    const isMobile = () => window.innerWidth <= 768;
    
    // Only add event listeners if elements exist
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            if (!isMobile()) {
                sidebar.classList.toggle('collapsed');
                mainContent.classList.toggle('expanded');
            } else {
                sidebar.classList.toggle('mobile-visible');
            }
            
            resizeAllCharts();
        });
    }
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            sidebar.classList.toggle('mobile-visible');
            resizeAllCharts();
        });
    }
    
    // Rest of your code...
    // (Add similar null checks for sidebar and mainContent if needed)
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (sidebar && mainContent) {
            if (isMobile()) {
                sidebar.classList.remove('collapsed');
                mainContent.classList.remove('expanded');
                if (!sidebar.classList.contains('mobile-visible')) {
                    sidebar.classList.add('transform', 'translateX(-100%)');
                }
            } else {
                sidebar.classList.remove('mobile-visible');
                sidebar.style.transform = '';
            }
        }
        
        resizeAllCharts();
    });
    
    // Close sidebar when clicking outside on mobile
    if (sidebar && mobileMenuBtn) {
        document.addEventListener('click', function(event) {
            if (isMobile() && 
                sidebar.classList.contains('mobile-visible') && 
                !sidebar.contains(event.target) && 
                event.target !== mobileMenuBtn) {
                sidebar.classList.remove('mobile-visible');
                
                resizeAllCharts();
            }
        });
    }
    
    // Initial setup
    if (isMobile() && sidebar && mainContent) {
        sidebar.classList.remove('collapsed');
        mainContent.classList.remove('expanded');
    }
});