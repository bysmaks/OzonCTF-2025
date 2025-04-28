const collectForm = document.getElementById('collect-form');
const collectError = document.getElementById('collect-error');
const logoutButton = document.querySelector('.logout-button');

collectForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(collectForm);
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch('/collect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (response.status === 200) {
            // Успешная отправка — обновляем страницу для актуализации счетчика и флага
            location.reload();
        } else {
            const errorText = await response.text();
            collectError.textContent = errorText.split("\n")[0];
            collectError.style.display = 'block';
            collectError.classList.add('error-animation');
            setTimeout(() => {
                collectError.classList.remove('error-animation');
            }, 500);
        }
    } catch (error) {
        collectError.textContent = 'Ошибка сети';
        collectError.style.display = 'block';
        collectError.classList.add('error-animation');
        setTimeout(() => {
            collectError.classList.remove('error-animation');
        }, 500);
    }
});

logoutButton.addEventListener('click', async () => {
    try {
        await fetch('/logout', {
            method: 'POST',
        });
        window.location.href = '/';
    } catch (error) {
        console.error('Ошибка при выходе:', error);
    }
});