// Obtener todos los productos al cargar la página
window.onload = function() {
    obtenerProductosDropdown();
};

// Función para obtener los productos y llenar el dropdown
async function obtenerProductosDropdown() {
    try {
        const response = await fetch('/api/productos');
        const data = await response.json();
        llenarDropdown(data.productos);
    } catch (error) {
        console.error('Error al obtener los productos:', error);
    }
}

// Función para llenar el dropdown con los productos
function llenarDropdown(productos) {
    const dropdown = document.getElementById('productosDropdown');
    dropdown.innerHTML = ''; // Limpiar dropdown

    productos.forEach(producto => {
        const option = document.createElement('option');
        option.value = producto._id;  // Usamos el _id como valor oculto
        option.textContent = producto.nombre;
        dropdown.appendChild(option);
    });
}

// Función para eliminar el producto seleccionado del dropdown
async function eliminarProducto() {
    const dropdown = document.getElementById('productosDropdown');
    const id = dropdown.value;  // Obtener el _id del producto seleccionado

    if (confirm('¿Estás seguro de eliminar este producto?')) {
        try {
            const response = await fetch('/eliminar_producto', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({_id: id})
            });

            const data = await response.json();
            document.getElementById('mensaje').textContent = data.mensaje;

            obtenerProductosDropdown();  // Actualizar el dropdown después de eliminar
        } catch (error) {
            console.error('Error al eliminar el producto:', error);
            document.getElementById('mensaje').textContent = 'Error al eliminar el producto.';
        }
    }
}
