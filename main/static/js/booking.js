document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('bookingForm');
    const message = document.getElementById('formMessage');
    const dateInput = document.getElementById('date');

    const today = new Date().toISOString().split('T')[0];
    dateInput.setAttribute('min', today);

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        message.className = 'form-message';
        message.style.display = 'none';

        const data = {
            name: form.name.value.trim(),
            phone: form.phone.value.trim(),
            email: form.email.value.trim(),
            date: form.date.value,
            time: form.time.value,
            guests: parseInt(form.guests.value, 10),
            comment: form.comment.value.trim(),
        };

        try {
            const response = await fetch('http://127.0.0.1:8001/api/bookings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Ошибка при отправке');
            }

            message.textContent = 'Заявка отправлена! Мы свяжемся с вами для подтверждения.';
            message.className = 'form-message form-message--success';
            form.reset();
            dateInput.setAttribute('min', today);
        } catch (error) {
            message.textContent = typeof error.message === 'string'
                ? error.message
                : 'Не удалось отправить заявку. Убедитесь, что API-сервер запущен.';
            message.className = 'form-message form-message--error';
        }
    });
});
