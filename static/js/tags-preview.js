function initTagsPreview() {
    const tagsInput = document.getElementById('id_tags_input');
    const tagsPreview = document.getElementById('tags-preview');

    if (tagsInput && tagsPreview) {
        function updateTagsPreview() {
            const tags = tagsInput.value.split(',').map(tag => tag.trim()).filter(tag => tag);
            tagsPreview.innerHTML = tags.map(tag => {
                const span = document.createElement('span');
                span.className = 'tag';
                span.textContent = tag;
                return span.outerHTML;
            }).join('');
        }

        tagsInput.addEventListener('input', updateTagsPreview);
        // Инициализируем предпросмотр при загрузке страницы
        updateTagsPreview();
    }
}

// Инициализация при загрузке документа
document.addEventListener('DOMContentLoaded', function() {
    initTagsPreview();
});
