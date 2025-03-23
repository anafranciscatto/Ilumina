function togglePassword() {
    const passwordInput = document.getElementById('senha');
    const toggleIcon = document.getElementById('toggle-password');
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        toggleIcon.src = '/static/img/olho-cruzado.png';
    } else {
        passwordInput.type = 'password';
        toggleIcon.src = '/static/img/olho.png';
    }
}