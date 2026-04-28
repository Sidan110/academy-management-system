document.addEventListener('DOMContentLoaded', () => {
    const confirmForms = document.querySelectorAll('.js-confirm');

    confirmForms.forEach((form) => {
        form.addEventListener('submit', (event) => {
            const ok = confirm('정말 실행하시겠습니까?');
            if (!ok) {
                event.preventDefault();
            }
        });
    });

    const messages = document.querySelectorAll('.message');

    if (messages.length > 0) {
        setTimeout(() => {
            messages.forEach((message) => {
                message.style.opacity = '0';
                message.style.transition = 'opacity 0.4s ease';
                setTimeout(() => message.remove(), 500);
            });
        }, 2500);
    }

    const statusInputs = document.querySelectorAll('.status-pill input');

    statusInputs.forEach((input) => {
        input.addEventListener('change', () => {
            const row = input.closest('.attendance-row');
            if (row) {
                row.setAttribute('data-status', input.value);
            }
        });
    });
});
