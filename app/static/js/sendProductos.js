// Obtener el formulario
const form = document.getElementById('formProducto');

// Escuchar el evento de envío del formulario
form.addEventListener('submit', function(event) {
    event.preventDefault(); // Evita que la página se recargue

    // Obtener los datos del formulario
    const nombre = document.getElementById('nombre').value;
    const precio = document.getElementById('precio').value;
    const descripcion = document.getElementById('descripcion').value;
    const stock = document.getElementById('stock').value;
    const categoria = document.getElementById('categoria').value;
    const imagenes = document.getElementById('imagenes').value.split(','); // Convertir la cadena en array
    const estado = document.getElementById('estado').value;

    // Crear un objeto con los datos
    const producto = {
        nombre: nombre,
        precio: parseFloat(precio),
        descripcion: descripcion,
        stock: parseInt(stock),
        categoria: categoria,
        imagenes: imagenes.map(url => url.trim()), // Asegurarse de que cada URL esté limpia
        estado: estado
    };

    // Enviar los datos al backend usando Fetch
    fetch('/agregar_producto', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(producto)
    })
    .then(response => response.json())
    .then(data => {
        // Mostrar mensaje de éxito en la página
        const mensaje = document.getElementById('mensaje');
        mensaje.textContent = data.mensaje;
        mensaje.style.color = 'green';

        // Limpiar el formulario después de agregar el producto
        form.reset();
    })
    .catch(error => {
        // Mostrar mensaje de error en la página
        const mensaje = document.getElementById('mensaje');
        mensaje.textContent = 'Error al agregar el producto';
        mensaje.style.color = 'red';
        console.error('Error:', error);
    });
});
