// Скрипт для закрытия алертов
function initAlertClose() {
    document.querySelectorAll('.alert-close').forEach(button => {
        button.addEventListener('click', function() {
            this.closest('.alert').style.display = 'none';
        });
    });
}

// Инициализация при загрузке документа
document.addEventListener('DOMContentLoaded', function() {
    initAlertClose();
});
