// Agregar un producto al carrito
async function agregarAlCarrito(productoId, cantidad = 1) {
    try {
        const response = await fetch('/api/carrito/agregar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ producto_id: productoId, cantidad: cantidad })
        });
        const data = await response.json();
        alert(data.mensaje);
    } catch (error) {
        console.error("Error al agregar al carrito:", error);
    }
}

// Obtener el carrito y mostrarlo en el DOM
async function mostrarCarrito() {
    try {
        const response = await fetch('/api/carrito');
        const carrito = await response.json();
        const carritoContainer = document.getElementById('carritoContainer');
        carritoContainer.innerHTML = '';

        carrito.forEach(item => {
            const productoDiv = document.createElement('div');
            productoDiv.textContent = `Producto ID: ${item.producto_id} | Cantidad: ${item.cantidad}`;
            carritoContainer.appendChild(productoDiv);
        });
    } catch (error) {
        console.error("Error al obtener el carrito:", error);
    }
}

// Eliminar un producto del carrito
async function eliminarDelCarrito(productoId) {
    try {
        const response = await fetch('/api/carrito/eliminar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ producto_id: productoId })
        });
        const data = await response.json();
        alert(data.mensaje);
        mostrarCarrito();
    } catch (error) {
        console.error("Error al eliminar del carrito:", error);
    }
}

// Llamar a mostrarCarrito al cargar la página
window.onload = mostrarCarrito;
