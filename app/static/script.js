// Función para obtener los productos del backend
async function obtenerProductos() {
    try {
        // Petición a la API para obtener los productos
        const response = await fetch("/api/productos");
        const data = await response.json();

        // Llamar a la función para mostrar los productos
        mostrarProductos(data.productos);
    } catch (error) {
        console.error("Error al obtener los productos:", error);
    }
}

// Función para mostrar los productos en el DOM
function mostrarProductos(productos) {
    const productosContainer = document.getElementById("productosContainer");

    productos.forEach(producto => {
        // Crear un div para cada producto
        const productoDiv = document.createElement("div");
        productoDiv.classList.add("producto");

        // Crear elementos HTML para mostrar la información del producto
        const nombre = document.createElement("h2");
        nombre.textContent = producto.nombre;

        const precio = document.createElement("p");
        precio.textContent = `Precio: $${producto.precio}`;

        const descripcion = document.createElement("p");
        descripcion.textContent = producto.descripcion;

        // Agregar imagen del producto (si existe)
        const imagen = document.createElement("img");
        if (producto.imagenes && producto.imagenes.length > 0) {
            imagen.src = producto.imagenes[0];
        } else {
            imagen.src = "https://via.placeholder.com/200"; // Imagen por defecto si no hay imagen
        }

        // Añadir los elementos al div del producto
        productoDiv.appendChild(nombre);
        productoDiv.appendChild(imagen);
        productoDiv.appendChild(precio);
        productoDiv.appendChild(descripcion);

        // Añadir el div del producto al contenedor principal
        productosContainer.appendChild(productoDiv);
    });
}

// Llamar a la función al cargar la página
window.onload = obtenerProductos;
