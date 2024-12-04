document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('registroForm');
    const submitButton = document.getElementById('submit-btn');

    form.addEventListener('submit', function (event) {
        event.preventDefault(); // Evita que el formulario se envíe de manera tradicional

        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const address = document.getElementById('address').value;

        if (!username || !email || !password || !address) {
            alert("Por favor, completa todos los campos.");
            return;
        }

        submitButton.disabled = true;
        submitButton.innerText = 'Registrando...';

        const data = {
            username: username,
            email: email,
            password: password,
            address: address
        };

        fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Registro exitoso');
                window.location.href = '/login'; // Redirigir al login
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
            submitButton.innerText = 'Registrarse';
        });
    });
});
