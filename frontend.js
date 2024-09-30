import React, { useState, useEffect } from 'react';

function Catalogo() {
  const [productos, setProductos] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/productos/')
      .then(response => response.json())
      .then(data => setProductos(data));
  }, []);

  return (
    <div>
      <h1>Catálogo de Productos</h1>
      <ul>
        {productos.map(producto => (
          <li key={producto.nombre}>
            <h2>{producto.nombre}</h2>
            <p>{producto.descripcion}</p>
            <p>Precio: ${producto.precio}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Catalogo;
