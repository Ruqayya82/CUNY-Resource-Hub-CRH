// CUNY Resource Hub - JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap tooltips are used
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Search functionality with debouncing
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                // Auto-submit search form after user stops typing for 500ms
                const form = searchInput.closest('form');
                if (form) {
                    form.submit();
                }
            }, 500);
        });
    }

    // Filter functionality
    const filterSelects = document.querySelectorAll('select[name="campus"], select[name="category"]');
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            const form = select.closest('form');
            if (form) {
                form.submit();
            }
        });
    });

    // Resource card click tracking (for analytics)
    const resourceLinks = document.querySelectorAll('.card a[href*="resource"]');
    resourceLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Track resource clicks (could send to analytics service)
            console.log('Resource clicked:', this.href);
        });
    });

    // Loading state for forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<span class="loading"></span> Searching...';
                submitBtn.disabled = true;
            }
        });
    });

    // API integration example
    function loadResources() {
        fetch('/api/resources')
            .then(response => response.json())
            .then(data => {
                console.log('Resources loaded:', data);
                // Process data as needed
            })
            .catch(error => {
                console.error('Error loading resources:', error);
            });
    }

    // Load resources on page load if on index page
    if (window.location.pathname === '/') {
        loadResources();
    }

    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Keyboard navigation improvements
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[name="q"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
    });

    // Dynamic content loading for infinite scroll (if needed)
    let page = 1;
    const loadMoreBtn = document.getElementById('load-more');
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', function() {
            page++;
            fetch(`/api/resources?page=${page}`)
                .then(response => response.json())
                .then(data => {
                    // Append new resources to the page
                    console.log('Loading more resources:', data);
                });
        });
    }

    // Error handling for failed resource links
    const externalLinks = document.querySelectorAll('a[target="_blank"]');
    externalLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Check if link is still valid (basic check)
            fetch(this.href, { method: 'HEAD' })
                .then(response => {
                    if (!response.ok) {
                        alert('This resource link may be outdated. Please check the official CUNY website.');
                    }
                })
                .catch(() => {
                    // Link check failed, but allow navigation
                });
        });
    });
});
