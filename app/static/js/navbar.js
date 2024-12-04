// Abrir y cerrar el menú al hacer clic en el botón
document.querySelectorAll('.dropdown').forEach(dropdown => {
    dropdown.addEventListener('click', function(e) {
        // Prevenir que el clic en el dropdown cierre el menú
        e.stopPropagation();
        // Alternar la clase 'show' para mostrar u ocultar el menú
        this.classList.toggle('show');

        // Detectar la posición del menú
        const dropdownContent = this.querySelector('.dropdown-content');
        const rect = dropdownContent.getBoundingClientRect();  // Posición del menú

        // Obtener altura disponible de la pantalla
        const spaceBelow = window.innerHeight - rect.bottom; // Espacio debajo del menú
        const spaceAbove = rect.top;  // Espacio arriba del menú

        // Si el espacio debajo es insuficiente, mostrar el menú hacia arriba
        if (spaceBelow < rect.height && spaceAbove > rect.height) {
            dropdownContent.style.top = `auto`;
            dropdownContent.style.bottom = `${spaceAbove}px`; // Coloca el menú arriba
        } else {
            dropdownContent.style.top = `100%`; // Coloca el menú hacia abajo
            dropdownContent.style.bottom = `auto`;
        }
    });
});

// Detectar clic fuera del menú
document.body.addEventListener('click', function() {
    // Cerrar el menú si se hace clic fuera de él
    document.querySelectorAll('.dropdown').forEach(dropdown => {
        dropdown.classList.remove('show');
    });
});
