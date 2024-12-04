document.addEventListener("DOMContentLoaded", () => {
    cargarProductos(1); // Cargar productos en la primera página
});

// Cargar productos con paginación
async function cargarProductos(pagina) {
    const response = await fetch(`/api/productos?page=${pagina}`);
    const data = await response.json();
    renderizarTabla(data.productos);
    renderizarPaginacion(data.totalPaginas, pagina);
}

// Renderizar la tabla con los productos
function renderizarTabla(productos) {
    const tbody = document.querySelector("#productosTabla tbody");
    tbody.innerHTML = ""; // Limpiar contenido previo

    productos.forEach(producto => {
        const fila = document.createElement("tr");

        const imagen = document.createElement("td");
        const img = document.createElement("img");
        img.src = producto.imagenes[0] || "https://via.placeholder.com/50";
        imagen.appendChild(img);

        const nombre = document.createElement("td");
        const enlace = document.createElement("a");
        enlace.href = `/inventario/detalle_producto/${producto._id}`; // Actualiza el enlace
        enlace.textContent = producto.nombre;
        nombre.appendChild(enlace);

        const precio = document.createElement("td");
        precio.textContent = `$${producto.precio}`;

        const stock = document.createElement("td");
        stock.textContent = producto.stock;

        fila.append(imagen, nombre, precio, stock);
        tbody.appendChild(fila);
    });
}

// Renderizar controles de paginación
function renderizarPaginacion(totalPaginas, paginaActual) {
    const paginacion = document.getElementById("paginacion");
    paginacion.innerHTML = ""; // Limpiar contenido previo

    for (let i = 1; i <= totalPaginas; i++) {
        const boton = document.createElement("button");
        boton.textContent = i;
        boton.disabled = i === paginaActual;
        boton.addEventListener("click", () => cargarProductos(i));
        paginacion.appendChild(boton);
    }
}
