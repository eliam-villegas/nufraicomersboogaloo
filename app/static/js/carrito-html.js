async function mostrarCarrito() {
    const response = await fetch('/api/carrito');
    const data = await response.json();
    renderizarCarrito(data.carrito);
    calcularSubtotal(data.carrito);
}

function renderizarCarrito(carrito) {
    const carritoContainer = document.getElementById("carritoContainer");
    carritoContainer.innerHTML = "";

    carrito.forEach(item => {
        const itemDiv = document.createElement("div");
        itemDiv.classList.add("carrito-item");

        const nombre = document.createElement("p");
        nombre.textContent = item.nombre;

        const precio = document.createElement("p");
        precio.textContent = `Precio: $${item.precio}`;

        const cantidad = document.createElement("input");
        cantidad.type = "number";
        cantidad.value = item.cantidad;
        cantidad.min = 1;
        cantidad.max = item.stock;
        cantidad.addEventListener("change", () => actualizarCantidad(item.producto_id, cantidad.value));

        const subtotal = document.createElement("p");
        subtotal.textContent = `Subtotal: $${(item.precio * item.cantidad).toFixed(2)}`;

        const botonEliminar = document.createElement("button");
        botonEliminar.textContent = "Eliminar";
        botonEliminar.onclick = () => eliminarDelCarrito(item.producto_id);

        itemDiv.append(nombre, precio, cantidad, subtotal, botonEliminar);
        carritoContainer.appendChild(itemDiv);
    });
}

function calcularSubtotal(carrito) {
    let total = 0;
    carrito.forEach(item => {
        total += item.precio * item.cantidad;
    });
    document.getElementById("subtotal").textContent = total.toFixed(2);
}

async function actualizarCantidad(productoId, nuevaCantidad) {
    await fetch('/api/carrito/actualizar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ producto_id: productoId, cantidad: parseInt(nuevaCantidad) })
    });
    mostrarCarrito(); // Actualizar el carrito después de cambiar la cantidad
}

async function eliminarDelCarrito(productoId) {
    await fetch('/api/carrito/eliminar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ producto_id: productoId })
    });
    mostrarCarrito(); // Actualizar el carrito después de eliminar
}

async function iniciarPago() {
    const subtotal = document.getElementById("subtotal").textContent;

    const response = await fetch("/iniciar_pago", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ amount: parseFloat(subtotal) })
    });

    const data = await response.json();
    if (data.url && data.token) {
        // Redirigir a Webpay Plus con el token
        const form = document.createElement("form");
        form.action = data.url;
        form.method = "POST";

        const tokenInput = document.createElement("input");
        tokenInput.name = "token_ws";
        tokenInput.value = data.token;
        form.appendChild(tokenInput);

        document.body.appendChild(form);
        form.submit();
    } else {
        alert("No se pudo iniciar el pago");
    }
}

window.onload = mostrarCarrito;
