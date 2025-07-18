function updateSearchHistory(query) {
  let history = JSON.parse(localStorage.getItem('searchHistory')) || [];

  // Remove if it already exists and re-add to front
  history = history.filter(q => q !== query);
  history.unshift(query);

  // Limit to 10
  if (history.length > 10) history = history.slice(0, 10);
  localStorage.setItem('searchHistory', JSON.stringify(history));

  renderDropdownHistory();
}

function renderDropdownHistory() {
  const input = document.getElementById('query');
  const dropdown = document.getElementById('historyDropdown');
  if (!input || !dropdown || document.activeElement !== input) return;

  const history = JSON.parse(localStorage.getItem('searchHistory')) || [];

  dropdown.innerHTML = '';
  if (history.length === 0) {
    dropdown.style.display = 'none';
    return;
  }

  dropdown.style.display = 'block';
  dropdown.style.left = `${input.offsetLeft}px`;
  dropdown.style.top = `${input.offsetTop + input.offsetHeight}px`;
  dropdown.style.width = `${input.offsetWidth}px`;

  history.forEach(q => {
    const item = document.createElement('div');
    item.className = 'history-item';
    item.style.position = 'relative';
    item.style.cursor = 'pointer';

    // Span to hold the query text
    const term = document.createElement('span');
    term.textContent = q;

    // "X" delete button
    const delBtn = document.createElement('span');
    delBtn.textContent = '🗙';
    delBtn.className = 'delete-btn';
    delBtn.style.position = 'absolute';
    delBtn.style.right = '8px';
    delBtn.style.cursor = 'pointer';
    delBtn.addEventListener('mousedown', e => {
      e.stopPropagation();
      removeSearchFromHistory(q);
      renderDropdownHistory();
    });

    item.addEventListener('mousedown', () => {
      input.value = q;
      dropdown.style.display = 'none';
      if (typeof handleSearchEvent === 'function') {
        handleSearchEvent(q);
      } else {
        window.location.href = `/search?q=${encodeURIComponent(q)}`;
      }
    });

    item.appendChild(term);
    item.appendChild(delBtn);
    dropdown.appendChild(item);
  });
}

function removeSearchFromHistory(query) {
  let history = JSON.parse(localStorage.getItem('searchHistory')) || [];
  history = history.filter(q => q !== query);
  localStorage.setItem('searchHistory', JSON.stringify(history));
  renderDropdownHistory();
}

document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById('query');
  if (input) {
    input.addEventListener('focus', renderDropdownHistory);
    input.addEventListener('input', renderDropdownHistory);
  }

  // Hide dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (
      !document.getElementById('query')?.contains(e.target) &&
      !document.getElementById('historyDropdown')?.contains(e.target)
    ) {
      const dropdown = document.getElementById('historyDropdown');
      if (dropdown) dropdown.style.display = 'none';
    }
  });

  // Delete entire search history
  const deleteBtn = document.getElementById("deleteHistory");
  if (deleteBtn) {
    deleteBtn.addEventListener("click", () => {
      localStorage.removeItem("searchHistory");
      renderDropdownHistory([]);  // Clear dropdown visually
    });
  }

  // Hide dropdown on form submission
  const form = document.getElementById("searchForm");
  if (form) {
    form.addEventListener("submit", () => {
      const dropdown = document.getElementById("historyDropdown");
      if (dropdown) dropdown.style.display = "none";
    });
  }
});
