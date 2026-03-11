// Load header and footer components
async function loadComponents() {
    try {
        // Load header
        const headerResponse = await fetch('/components/header.html');
        const headerHTML = await headerResponse.text();
        document.getElementById('header-placeholder').innerHTML = headerHTML;
        
        // Load footer
        const footerResponse = await fetch('/components/footer.html');
        const footerHTML = await footerResponse.text();
        document.getElementById('footer-placeholder').innerHTML = footerHTML;
        
        // Set active nav link based on current page
        setActiveNavLink();
    } catch (error) {
        console.error('Error loading components:', error);
    }
}

function setActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (currentPath === linkPath || (currentPath === '/' && linkPath === '/')) {
            link.classList.add('active');
        }
    });
}

// Load components when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadComponents);
} else {
    loadComponents();
}
