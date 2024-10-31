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

// Función para llenar el formulario con los datos del producto seleccionado
async function llenarFormulario() {
    const dropdown = document.getElementById('productosDropdown');
    const id = dropdown.value;  // Obtener el _id del producto seleccionado

    // Obtener los datos actuales del producto
    try {
        const response = await fetch(`/api/producto/${id}`);
        const producto = await response.json();

        // Llenar el formulario con los datos actuales del producto
        document.getElementById('nombre').value = producto.nombre;
        document.getElementById('precio').value = producto.precio;
        document.getElementById('descripcion').value = producto.descripcion;
        document.getElementById('stock').value = producto.stock;
        document.getElementById('categoria').value = producto.categoria;
        document.getElementById('estado').value = producto.estado;

        // Mostrar la URL de la imagen en el campo y mostrar la imagen actual
        document.getElementById('imagenes').value = producto.imagenes[0]; // Mostrar la primera imagen
        document.getElementById('imagenActual').src = producto.imagenes[0]; // Mostrar la imagen actual
    } catch (error) {
        console.error('Error al llenar el formulario:', error);
    }
}

// Función para actualizar el producto cuando se envía el formulario
async function actualizarProducto(event) {
    event.preventDefault(); // Evitar recargar la página

    const dropdown = document.getElementById('productosDropdown');
    const id = dropdown.value;  // Obtener el _id del producto seleccionado

    const nuevoProducto = {
        _id: id,  // Enviar también el _id para que el backend sepa qué producto actualizar
        nombre: document.getElementById('nombre').value,
        precio: parseFloat(document.getElementById('precio').value),
        descripcion: document.getElementById('descripcion').value,
        stock: parseInt(document.getElementById('stock').value),
        categoria: document.getElementById('categoria').value,
        estado: document.getElementById('estado').value,
        imagenes: [document.getElementById('imagenes').value] // Actualizamos la imagen con el valor ingresado
    };

    try {
        await fetch('/actualizar_producto', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(nuevoProducto)
        });
        alert('Producto actualizado');
        obtenerProductosDropdown();  // Actualizar el dropdown después de editar
    } catch (error) {
        console.error('Error al actualizar el producto:', error);
    }
}
