// Menú reutilizable para todo el sitio
document.addEventListener('DOMContentLoaded', function() {
    // Insertar el menú
    var menuHTML = `
    <nav id="menu" class="main-nav" role="navigation">
        <ul class="main-menu">
            <li><a href="/" class="external"><i class="fa fa-home"></i> Inicio</a></li>
            <li><a href="/mision-vision/" class="external"><i class="fa fa-bullseye"></i> Misión y Visión</a></li>
            <li><a href="/nosotros/" class="external"><i class="fa fa-users"></i> Nosotros</a></li>
            <li><a href="/docentes-nuevo/" class="external"><i class="fa fa-chalkboard-teacher"></i> Nuestros Docentes</a></li>
            <li><a href="/noticias/" class="scroll-to-section"><i class="fa fa-newspaper"></i> Noticias</a></li>
            <li><a href="#" class="login-link" data-bs-toggle="modal" data-bs-target="#loginModal"><i class="fa fa-sign-in-alt"></i> Login</a></li>
        </ul>
    </nav>`;

    // Insertar el menú después del botón del menú móvil
    var menuButton = document.querySelector('.menu-link');
    if (menuButton) {
        menuButton.insertAdjacentHTML('afterend', menuHTML);
    }

    // Elementos del menú
    var menuLink = document.querySelector('.menu-link');
    var menu = document.getElementById('menu');
    
    // Función para alternar el menú
    function toggleMenu(e) {
        if (e) e.preventDefault();
        
        menu.classList.toggle('active');
        
        // Cambiar el ícono del botón
        var icon = menuLink.querySelector('i');
        if (menu.classList.contains('active')) {
            icon.classList.remove('fa-bars');
            icon.classList.add('fa-times');
        } else {
            icon.classList.remove('fa-times');
            icon.classList.add('fa-bars');
        }
    }
    
    // Manejar clic en el botón del menú móvil
    if (menuLink && menu) {
        menuLink.addEventListener('click', toggleMenu);
    }
    
    // Cerrar menú al hacer clic fuera de él
    document.addEventListener('click', function(e) {
        if (menu && menu.classList.contains('active') && 
            !menu.contains(e.target) && 
            e.target !== menuLink && 
            !menuLink.contains(e.target)) {
            toggleMenu();
        }
    });

    // Cerrar menú al hacer clic en un enlace
    var menuLinks = document.querySelectorAll('.main-menu a');
    menuLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            // Si es un enlace de login, no hacer nada especial
            if (this.classList.contains('login-link')) {
                return;
            }
            
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
            if (menu && menu.classList.contains('active')) {
                toggleMenu();
            }
        });
    });
});
