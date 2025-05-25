function agregarAlCarrito(productoId) {
    console.log("Agregando producto al carrito:", productoId); // Depuración
    fetch('/carrito', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ producto_id: productoId, cantidad: 1 }),
    })
    .then(response => response.json())
    .then(data => {
        console.log("Respuesta del servidor:", data); // Depuración
        if (data.success) {
            alert('Producto agregado al carrito');
        } else {
            alert('Error al agregar el producto al carrito');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}