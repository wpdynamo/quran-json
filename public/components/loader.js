// Load header and footer components
async function loadComponents() {
    try {
        const headerPlaceholder = document.getElementById('header-placeholder');
        const footerPlaceholder = document.getElementById('footer-placeholder');
        
        if (!headerPlaceholder || !footerPlaceholder) {
            console.error('Placeholders not found');
            return;
        }
        
        // Load header
        const headerResponse = await fetch('/components/header.html');
        const headerHTML = await headerResponse.text();
        headerPlaceholder.innerHTML = headerHTML;
        
        // Load footer
        const footerResponse = await fetch('/components/footer.html');
        const footerHTML = await footerResponse.text();
        footerPlaceholder.innerHTML = footerHTML;
        
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
        if (currentPath === linkPath || (currentPath === '/' && linkPath === '/') || (currentPath.endsWith('/index.html') && linkPath === '/')) {
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
