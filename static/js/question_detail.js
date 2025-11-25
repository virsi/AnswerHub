document.addEventListener('DOMContentLoaded', function() {
    function showMessage(message, type = 'success') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="alert-close" aria-label="Закрыть">×</button>
        `;

        let alertsContainer = document.getElementById('alerts-container');

        if (!alertsContainer) {
            alertsContainer = document.createElement('div');
            alertsContainer.id = 'alerts-container';
            alertsContainer.className = 'alerts-container';
            document.body.appendChild(alertsContainer);
        }

        alertsContainer.appendChild(alert);

        setTimeout(() => {
            alert.style.opacity = '1';
            alert.style.transform = 'translateY(0)';
        }, 10);

        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-20px)';
                setTimeout(() => alert.remove(), 300);
            }
        }, 5000);

        alert.querySelector('.alert-close').addEventListener('click', function() {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';
            setTimeout(() => alert.remove(), 300);
        });
    }

    // Удаление вопроса
    const deleteQuestionBtn = document.getElementById('deleteQuestionBtn');
    if (deleteQuestionBtn) {
        const questionModal = document.getElementById('deleteModal');
        const closeQuestionBtn = document.querySelector('.modal-close');
        const cancelQuestionBtn = document.querySelector('.modal-cancel');

        deleteQuestionBtn.addEventListener('click', function(e) {
            e.preventDefault();
            questionModal.style.display = 'block';
        });

        function closeQuestionModal() {
            questionModal.style.display = 'none';
        }

        if (closeQuestionBtn) {
            closeQuestionBtn.addEventListener('click', closeQuestionModal);
        }
        if (cancelQuestionBtn) {
            cancelQuestionBtn.addEventListener('click', closeQuestionModal);
        }

        window.addEventListener('click', function(e) {
            if (e.target === questionModal) {
                closeQuestionModal();
            }
        });
    }

    // Удаление ответов
    const deleteAnswerBtns = document.querySelectorAll('.delete-answer-btn');
    const answerModal = document.getElementById('deleteAnswerModal');
    const deleteAnswerForm = document.getElementById('deleteAnswerForm');
    const closeAnswerBtn = document.querySelector('.modal-close-answer');
    const cancelAnswerBtn = document.querySelector('.modal-cancel-answer');

    if (deleteAnswerBtns.length > 0 && answerModal) {
        deleteAnswerBtns.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const answerId = this.getAttribute('data-answer-id');
                const actionUrl = window.answerDeleteUrlTemplate.replace('0', answerId);
                deleteAnswerForm.action = actionUrl;
                answerModal.style.display = 'block';
            });
        });

        function closeAnswerModal() {
            answerModal.style.display = 'none';
        }

        if (closeAnswerBtn) {
            closeAnswerBtn.addEventListener('click', closeAnswerModal);
        }
        if (cancelAnswerBtn) {
            cancelAnswerBtn.addEventListener('click', closeAnswerModal);
        }

        window.addEventListener('click', function(e) {
            if (e.target === answerModal) {
                closeAnswerModal();
            }
        });
    }

    // AJAX голосование за ответы
    const answerVoteForms = document.querySelectorAll('.answer-card .vote-form');

    answerVoteForms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const url = this.action;
            const voteValue = this.getAttribute('data-vote-value');

            formData.append('value', voteValue);

            const voteCount = this.closest('.vote-buttons').querySelector('.vote-count');
            const allVoteBtns = this.closest('.vote-buttons').querySelectorAll('.vote-btn');

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (response.ok) {
                    const data = await response.json();

                    if (data.success) {
                        voteCount.textContent = data.votes;

                        // Сбрасываем все voted классы
                        allVoteBtns.forEach(btn => btn.classList.remove('voted'));

                        // Обновляем состояние кнопок в зависимости от голоса
                        if (data.voted === 1) {
                            allVoteBtns.forEach(btn => {
                                if (btn.classList.contains('vote-up')) {
                                    btn.classList.add('voted');
                                }
                            });
                        } else if (data.voted === -1) {
                            allVoteBtns.forEach(btn => {
                                if (btn.classList.contains('vote-down')) {
                                    btn.classList.add('voted');
                                }
                            });
                        }
                        // Если data.voted = 0, обе кнопки остаются без класса voted

                        showMessage('Голос учтен!', 'success');
                    } else {
                        showMessage(data.error || 'Ошибка при голосовании', 'error');
                    }
                } else {
                    showMessage('Ошибка сервера', 'error');
                }

            } catch (error) {
                showMessage('Ошибка сети', 'error');
            }
        });
    });


    // AJAX голосование за вопросы
    const questionVoteForms = document.querySelectorAll('.question-card .vote-form');

    questionVoteForms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const url = this.action;
            const voteValue = this.getAttribute('data-vote-value');

            formData.append('value', voteValue);

            const voteCount = this.closest('.vote-buttons').querySelector('.vote-count');
            const allVoteBtns = this.closest('.vote-buttons').querySelectorAll('.vote-btn');

            try {
                const response = await fetch(url, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                    }
                });

                if (response.ok) {
                    const data = await response.json();

                    if (data.success) {
                        voteCount.textContent = (data.new_votes ?? data.votes ?? 0);

                        // Сбрасываем все voted классы
                        allVoteBtns.forEach(btn => btn.classList.remove('voted'));

                        // Если голос снят (voted = 0), не добавляем класс voted
                        // Если пользователь проголосовал, добавляем класс voted соответствующей кнопке
                        if (data.voted === 1) {
                            allVoteBtns.forEach(btn => {
                                if (btn.classList.contains('vote-up')) {
                                    btn.classList.add('voted');
                                }
                            });
                        } else if (data.voted === -1) {
                            allVoteBtns.forEach(btn => {
                                if (btn.classList.contains('vote-down')) {
                                    btn.classList.add('voted');
                                }
                            });
                        }
                        // Если data.voted = 0, обе кнопки остаются без класса voted

                        showMessage('Голос учтен!', 'success');
                    } else {
                        showMessage(data.error || 'Ошибка при голосовании', 'error');
                    }
                } else {
                    showMessage('Ошибка сервера', 'error');
                }

            } catch (error) {
                showMessage('Ошибка сети', 'error');
            }
        });
    });
});


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Используем существующую систему уведомлений
function showNotification(message, type = 'success') {
    if (typeof window.showMessage === 'function') {
        window.showMessage(message, type);
        return;
    }
    let container = document.querySelector('.notification-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'notification-container';
        document.body.appendChild(container);
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
    }

    const note = document.createElement('div');
    note.className = `alert alert-${type}`;
    note.textContent = message;
    container.appendChild(note);
    setTimeout(() => note.classList.add('visible'), 50);
    setTimeout(() => {
        note.classList.remove('visible');
        setTimeout(() => note.remove(), 400);
    }, 3000);
}

// Основная логика
document.addEventListener('click', function (e) {
    const btn = e.target.closest('.mark-correct-btn');
    if (!btn) return;

    e.preventDefault();

    const form = btn.closest('form');
    if (!form) return;

    const url = form.action;
    const csrftoken = getCookie('csrftoken');

    fetch(url, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken,
            'Accept': 'application/json',
        },
        body: new FormData(form)
    })
    .then(res => res.json())
    .then(data => {
        if (!data.success) {
            showNotification('Ошибка: ' + (data.error || 'не удалось отметить ответ'), 'danger');
            return;
        }

        // --- 1️⃣ Снять флаг и вернуть кнопку у старого правильного ---
        if (data.prev_id) {
            const prevCard = document.querySelector(`#answer-${data.prev_id}`);
            if (prevCard) {
                prevCard.classList.remove('correct');
                const badge = prevCard.querySelector('.correct-badge');
                if (badge) badge.remove();

                // Вернуть кнопку
                const meta = prevCard.querySelector('.answer-meta');
                if (meta && !meta.querySelector('.mark-correct-btn')) {
                    const newForm = document.createElement('form');
                    newForm.method = 'post';
                    newForm.action = `/answers/${data.prev_id}/mark-correct/`;
                    newForm.className = 'correct-form';
                    newForm.innerHTML = `
                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrftoken}">
                        <button type="submit" class="btn btn-outline mark-correct-btn">
                            Отметить как правильный
                        </button>
                    `;
                    meta.prepend(newForm);
                }
            }
        }

        // --- 2️⃣ Добавить бейдж и убрать кнопку у нового правильного ---
        const newCard = document.querySelector(`#answer-${data.answer_id}`);
        if (newCard) {
            newCard.classList.add('correct');

            // Убираем все возможные формы отметки (даже если класс немного другой)
            const correctForms = newCard.querySelectorAll('form.correct-form, form.mark-correct-form');
            correctForms.forEach(formEl => formEl.remove());

            // Добавляем бейдж, если его нет
            const meta = newCard.querySelector('.answer-meta');
            if (meta && !meta.querySelector('.correct-badge')) {
                const badge = document.createElement('span');
                badge.className = 'correct-badge';
                badge.textContent = '✓ Правильный ответ';
                meta.prepend(badge);
            }
        }

        // --- 3️⃣ Уведомление ---
        showNotification('Ответ успешно отмечен как правильный!', 'success');
    })
    .catch(() => showNotification('Ошибка связи с сервером', 'danger'));
});


// === УДАЛЕНИЕ ОТВЕТА (через модальное окно) ===
document.addEventListener('click', function (e) {
    const deleteBtn = e.target.closest('.delete-answer-btn');
    if (!deleteBtn) return;

    e.preventDefault();
    const answerId = deleteBtn.dataset.answerId;
    const modal = document.querySelector('#deleteAnswerModal');
    const form = document.querySelector('#deleteAnswerForm');

    if (!modal || !form) return;

    // Устанавливаем action в форму
    const baseUrl = window.answerDeleteUrlTemplate;
    form.action = baseUrl.replace('/0/', `/${answerId}/`);

    // Показываем модалку (твой стиль)
    modal.style.display = 'block';
});

// Закрытие модалки
document.addEventListener('click', function (e) {
    if (e.target.matches('.modal-close-answer, .modal-cancel-answer')) {
        e.preventDefault();
        const modal = document.querySelector('#deleteAnswerModal');
        if (modal) modal.style.display = 'none';
    }
});

// Подтверждение удаления
document.querySelector('#deleteAnswerForm')?.addEventListener('submit', function (e) {
    e.preventDefault();
    const form = e.target;
    const url = form.action;
    const csrftoken = getCookie('csrftoken');

    fetch(url, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrftoken,
            'Accept': 'application/json',
        },
        body: new FormData(form)
    })
    .then(res => res.json())
    .then(data => {
        if (!data.success) {
            showNotification('Ошибка: ' + (data.error || 'не удалось удалить ответ'), 'danger');
            return;
        }

        // Удаляем карточку ответа из DOM
        const card = document.querySelector(`#answer-${data.answer_id}`);
        if (card) card.remove();

        // Обновляем счётчик ответов
        const header = document.querySelector('.answers-header h2');
        if (header && data.answers_count !== undefined) {
            header.textContent = `${data.answers_count} ответ${getWordEnding(data.answers_count)}`;
        }

        // Скрываем модалку
        const modal = document.querySelector('#deleteAnswerModal');
        if (modal) modal.style.display = 'none';

        showNotification('Ответ успешно удалён.', 'success');
    })
    .catch(() => showNotification('Ошибка соединения с сервером', 'danger'));
});

// Функция подбора правильного окончания для слова "ответ"
function getWordEnding(count) {
    const last = count % 10;
    const lastTwo = count % 100;
    if (lastTwo >= 11 && lastTwo <= 19) return 'ов';
    if (last === 1) return '';
    if (last >= 2 && last <= 4) return 'а';
    return 'ов';
}
