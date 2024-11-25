document.addEventListener("DOMContentLoaded", () => {
    if (!productoId || productoId.trim() === "") {
        console.error("ID del producto no disponible o inválido.");
        alert("No se pudo cargar el producto. ID no válido.");
        return;
    }

    cargarProducto(productoId);

    document.getElementById("formProducto").addEventListener("submit", (e) => {
        e.preventDefault();
        actualizarProducto(productoId);
    });

    document.getElementById("eliminarProducto").addEventListener("click", () => {
        eliminarProducto(productoId);
    });
});


// Función para cargar los datos del producto seleccionado
async function cargarProducto(id) {
    try {
        const response = await fetch(`/api/producto/${id}`);
        if (!response.ok) {
            throw new Error("Error al obtener el producto");
        }
        const producto = await response.json();

        // Llenar el formulario con los datos del producto
        document.getElementById("nombre").value = producto.nombre;
        document.getElementById("precio").value = producto.precio;
        document.getElementById("descripcion").value = producto.descripcion;
        document.getElementById("stock").value = producto.stock;
        document.getElementById("categoria").value = producto.categoria;
        document.getElementById("estado").value = producto.estado;

        // Mostrar la URL de la imagen en el campo y mostrar la imagen actual
        const imagenes = producto.imagenes || [];
        document.getElementById("imagenes").value = imagenes.join(", ");
        document.getElementById("imagenReferencia").src = imagenes[0] || "https://via.placeholder.com/150";

    } catch (error) {
        console.error("Error al cargar el producto:", error);
        alert("No se pudieron cargar los datos del producto.");
    }
}

// Función para actualizar los datos del producto
async function actualizarProducto(id) {
    const productoActualizado = {
        _id: id,
        nombre: document.getElementById("nombre").value,
        precio: parseFloat(document.getElementById("precio").value),
        descripcion: document.getElementById("descripcion").value,
        stock: parseInt(document.getElementById("stock").value),
        categoria: document.getElementById("categoria").value,
        estado: document.getElementById("estado").value,
        imagenes: document.getElementById("imagenes").value.split(",").map(img => img.trim())
    };

    try {
        const response = await fetch("/actualizar_producto", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(productoActualizado)
        });

        if (response.ok) {
            alert("Producto actualizado con éxito.");
        } else {
            throw new Error("Error al actualizar el producto.");
        }
    } catch (error) {
        console.error("Error al actualizar el producto:", error);
        alert("No se pudieron guardar los cambios.");
    }
}

// Función para eliminar el producto
async function eliminarProducto(id) {
    if (!confirm("¿Estás seguro de eliminar este producto?")) return;

    try {
        const response = await fetch("/eliminar_producto", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ _id: id })
        });

        if (response.ok) {
            alert("Producto eliminado con éxito.");
            window.location.href = "/inventario";
        } else {
            throw new Error("Error al eliminar el producto.");
        }
    } catch (error) {
        console.error("Error al eliminar el producto:", error);
        alert("No se pudo eliminar el producto.");
    }
}
