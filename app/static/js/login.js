document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('login-form');
    const submitButton = document.getElementById('submit-btn');

    // Verificar si el submitButton existe en el DOM
    if (!submitButton) {
        console.error("El botón de submit no se encontró en el DOM.");
        return;  // Salir si no se encuentra el botón
    }

    form.addEventListener('submit', function (event) {
        event.preventDefault(); // Evita que el formulario se envíe de manera tradicional

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        if (!email || !password) {
            alert("Por favor, completa todos los campos.");
            return;
        }

        submitButton.disabled = true;
        submitButton.innerText = 'Iniciando sesión...';

        const data = {
            email: email,
            password: password
        };

        fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Inicio de sesión exitoso');
                // Guardar el token JWT en el localStorage
                localStorage.setItem('jwt_token', data.token);
                window.location.href = '/productos'; // Redirigir al dashboard o página principal
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Hubo un problema con la solicitud. Por favor, inténtalo de nuevo más tarde.');
        })
        .finally(() => {
            submitButton.disabled = false;
            submitButton.innerText = 'Iniciar sesión';
        });
    });
});
