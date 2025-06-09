// Menú reutilizable para todo el sitio
document.addEventListener('DOMContentLoaded', function() {
    var menuHTML = `
    <nav id="menu" class="main-nav" role="navigation">
        <ul class="main-menu">
            <li><a href="/" class="external">Inicio</a></li>
            <li><a href="/mision-vision/" class="external">Misión y Visión</a></li>
            <li><a href="/nosotros/" class="external">Nosotros</a></li>
            <li><a href="/docentes/" class="external">Docentes</a></li>
            <li><a href="#section-autoridades" class="scroll-to-section">Autoridades</a></li>
            <li><a href="#section-honor" class="scroll-to-section">Cuadro de Honor</a></li>
            <li><a href="#" data-bs-toggle="modal" data-bs-target="#loginModal">Login</a></li>
        </ul>
    </nav>`;

    // Insertar el menú después del botón del menú móvil
    var menuButton = document.querySelector('.menu-link');
    if (menuButton) {
        menuButton.insertAdjacentHTML('afterend', menuHTML);
    }

    // Manejar el clic en el botón del menú móvil
    var menuLink = document.querySelector('.menu-link');
    var menu = document.getElementById('menu');
    
    if (menuLink && menu) {
        menuLink.addEventListener('click', function(e) {
            e.preventDefault();
            menu.classList.toggle('active');
        });
    }

    // Cerrar el menú al hacer clic en un enlace
    var menuLinks = document.querySelectorAll('.main-menu a');
    menuLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            // Si el enlace es interno (no tiene clase 'external') y no es un enlace de sección
            if (this.getAttribute('href').startsWith('#')) {
                e.preventDefault();
                var targetId = this.getAttribute('href');
                var targetElement = document.querySelector(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({ behavior: 'smooth' });
                }
            }
            
            // Cerrar el menú móvil si está abierto
            if (menu.classList.contains('active')) {
                menu.classList.remove('active');
            }
        });
    });
});
