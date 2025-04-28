document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const loginError = document.getElementById('login-error');
    const signupError = document.getElementById('signup-error');

    // Обработка формы входа
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(loginForm);
        const data = Object.fromEntries(formData.entries());

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            if (response.status === 200) {
                window.location.href = '/collect';
            } else {
                const errorText = await response.text();
                loginError.textContent = errorText;
                loginError.style.display = 'block';
                loginError.classList.add('error-animation');
                setTimeout(() => {
                    loginError.classList.remove('error-animation');
                }, 500);
            }
        } catch (error) {
            loginError.textContent = 'Ошибка сети';
            loginError.style.display = 'block';
            loginError.classList.add('error-animation');
            setTimeout(() => {
                loginError.classList.remove('error-animation');
            }, 500);
        }
    });

    // Обработка формы регистрации
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(signupForm);
        const data = Object.fromEntries(formData.entries());

        // Проверка совпадения паролей на клиенте
        if (data.password !== data['confirm-password']) {
            signupError.textContent = 'Пароли не совпадают';
            signupError.style.display = 'block';
            signupError.classList.add('error-animation');
            setTimeout(() => {
                signupError.classList.remove('error-animation');
            }, 500);
            return;
        }

        try {
            const response = await fetch('/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ login: data.login, password: data.password }),
            });

            if (response.status === 200) {
                window.location.href = '/collect';
            } else {
                const errorText = await response.text();
                signupError.textContent = errorText;
                signupError.style.display = 'block';
                signupError.classList.add('error-animation');
                setTimeout(() => {
                    signupError.classList.remove('error-animation');
                }, 500);
            }
        } catch (error) {
            signupError.textContent = 'Ошибка сети';
            signupError.style.display = 'block';
            signupError.classList.add('error-animation');
            setTimeout(() => {
                signupError.classList.remove('error-animation');
            }, 500);
        }
    });
});