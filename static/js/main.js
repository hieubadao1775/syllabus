/* ============================================
   NEU Syllabus Management System — JavaScript
   ============================================ */

// ---- Language Tab Switching (Public page) ----
function switchLang(lang) {
    document.querySelectorAll('.lang-tab').forEach(function(tab) {
        tab.classList.toggle('active', tab.dataset.lang === lang);
    });
    document.querySelectorAll('.lang-vi').forEach(function(el) {
        el.style.display = lang === 'vi' ? '' : 'none';
    });
    document.querySelectorAll('.lang-en').forEach(function(el) {
        el.style.display = lang === 'en' ? '' : 'none';
    });
}

// ---- Admin Tab Switching (VI/EN sub-tables) ----
function switchAdminTab(lang) {
    document.querySelectorAll('.admin-lang-tab').forEach(function(tab) {
        tab.classList.toggle('active', tab.dataset.lang === lang);
    });
    document.querySelectorAll('.tab-content').forEach(function(el) {
        el.classList.toggle('active', el.dataset.lang === lang);
    });
    // Update hidden language field in the add forms
    document.querySelectorAll('input[name="language"]').forEach(function(input) {
        input.value = lang.toUpperCase();
    });
}

// ---- AJAX Search Suggestions ----
(function() {
    var searchInput = document.getElementById('searchInput');
    var suggestions = document.getElementById('searchSuggestions');
    var debounceTimer = null;

    if (!searchInput || !suggestions) return;

    searchInput.addEventListener('input', function() {
        var q = this.value.trim();
        clearTimeout(debounceTimer);

        if (q.length < 2) {
            suggestions.classList.remove('active');
            suggestions.innerHTML = '';
            return;
        }

        debounceTimer = setTimeout(function() {
            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/search?q=' + encodeURIComponent(q));
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
            xhr.onload = function() {
                if (xhr.status === 200) {
                    var data = JSON.parse(xhr.responseText);
                    if (data.length === 0) {
                        suggestions.classList.remove('active');
                        suggestions.innerHTML = '';
                        return;
                    }
                    var html = '';
                    data.forEach(function(item) {
                        html += '<a class="suggestion-item" href="/syllabus/' +
                            encodeURIComponent(item.course_code) + '">' +
                            '<span class="code">' + escapeHtml(item.course_code) + '</span> — ' +
                            '<span class="title">' + escapeHtml(item.course_title_vi || item.course_title_en || '') + '</span>' +
                            '</a>';
                    });
                    suggestions.innerHTML = html;
                    suggestions.classList.add('active');
                }
            };
            xhr.send();
        }, 300);
    });

    // Close suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !suggestions.contains(e.target)) {
            suggestions.classList.remove('active');
        }
    });
})();

// ---- Edit Row Toggle ----
function toggleEditRow(itemId) {
    var row = document.getElementById('edit-row-' + itemId);
    if (row) {
        row.style.display = row.style.display === 'none' ? 'table-row' : 'none';
    }
}

// ---- Confirm Delete ----
function confirmDelete(form) {
    if (confirm('Bạn có chắc chắn muốn xóa?')) {
        form.submit();
    }
    return false;
}

// ---- Utility ----
function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
