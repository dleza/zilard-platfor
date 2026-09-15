(function () {
  const root = document.documentElement;
  const contrastKey = 'dldms-high-contrast';

  function setContrast(enabled) {
    document.body.classList.toggle('high-contrast', enabled);
    localStorage.setItem(contrastKey, enabled ? '1' : '0');
  }

  function setSidebar(open) {
    document.body.classList.toggle('sidebar-open', open);
    document.querySelectorAll('[data-sidebar-toggle]').forEach((toggle) => {
      toggle.setAttribute('aria-expanded', String(open));
    });
  }

  if (localStorage.getItem(contrastKey) === '1') {
    window.addEventListener('DOMContentLoaded', () => setContrast(true));
  }

  document.addEventListener('click', (event) => {
    const contrastToggle = event.target.closest('[data-contrast-toggle]');
    if (contrastToggle) {
      setContrast(!document.body.classList.contains('high-contrast'));
    }

    const sidebarToggle = event.target.closest('[data-sidebar-toggle]');
    if (sidebarToggle) {
      setSidebar(!document.body.classList.contains('sidebar-open'));
    }

    if (event.target.closest('[data-sidebar-close]') || event.target.closest('.sidebar-nav a')) {
      setSidebar(false);
    }

    const menuToggle = event.target.closest('[data-mobile-menu-toggle]');
    if (menuToggle) {
      const menu = document.querySelector('[data-mobile-menu]');
      const expanded = menu && !menu.classList.contains('hidden');
      if (menu) {
        menu.classList.toggle('hidden', expanded);
        menuToggle.setAttribute('aria-expanded', String(!expanded));
      }
    }

    if (event.target.closest('[data-feedback-open]')) {
      openFeedback();
    }

    if (event.target.closest('[data-feedback-close]')) {
      closeFeedback();
    }

    if (event.target.closest('[data-capture-gps]')) {
      captureFakeGps(event.target.closest('form') || document);
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      setSidebar(false);
    }
  });

  function openFeedback() {
    const modal = document.querySelector('[data-feedback-modal]');
    const pageField = modal && modal.querySelector('input[name="page_url"]');
    if (pageField) {
      pageField.value = window.location.pathname + window.location.search;
    }
    if (modal) {
      modal.classList.remove('hidden');
      modal.classList.add('flex');
      const firstInput = modal.querySelector('input:not([type="hidden"]), textarea');
      if (firstInput) firstInput.focus();
    }
  }

  function closeFeedback() {
    const modal = document.querySelector('[data-feedback-modal]');
    if (modal) {
      modal.classList.add('hidden');
      modal.classList.remove('flex');
    }
  }

  function captureFakeGps(scope) {
    const provinceCenters = [
      [-15.4167, 28.2833],
      [-12.8058, 28.2132],
      [-13.6333, 32.6500],
      [-11.2000, 28.8833],
      [-16.8000, 26.9833],
      [-14.2333, 31.3167],
      [-12.1789, 26.4000],
      [-17.8500, 25.8667],
      [-13.1339, 27.8493]
    ];
    const center = provinceCenters[Math.floor(Math.random() * provinceCenters.length)];
    const lat = center[0] + (Math.random() - 0.5) * 1.2;
    const lng = center[1] + (Math.random() - 0.5) * 1.2;
    const latField = scope.querySelector('[data-gps-lat]');
    const lngField = scope.querySelector('[data-gps-lng]');
    if (latField && lngField) {
      latField.value = lat.toFixed(6);
      lngField.value = lng.toFixed(6);
      latField.dispatchEvent(new Event('input', { bubbles: true }));
      lngField.dispatchEvent(new Event('input', { bubbles: true }));
    }
  }

  function setupDrafts() {
    document.querySelectorAll('form[data-draft-form]').forEach((form) => {
      const key = `dldms-draft:${window.location.pathname}:${form.dataset.draftForm}`;
      const status = form.querySelector('[data-draft-status]');
      const saved = localStorage.getItem(key);
      if (saved) {
        try {
          const values = JSON.parse(saved);
          form.querySelectorAll('input, select, textarea').forEach((field) => {
            if (!field.name || field.type === 'file' || field.name === 'csrfmiddlewaretoken') return;
            if (!(field.name in values)) return;
            if (field.type === 'checkbox') {
              field.checked = values[field.name] === true;
            } else {
              field.value = values[field.name];
            }
          });
          if (status) status.textContent = 'Local draft restored.';
        } catch (error) {
          localStorage.removeItem(key);
        }
      }

      const save = () => {
        const values = {};
        form.querySelectorAll('input, select, textarea').forEach((field) => {
          if (!field.name || field.type === 'file' || field.name === 'csrfmiddlewaretoken') return;
          values[field.name] = field.type === 'checkbox' ? field.checked : field.value;
        });
        localStorage.setItem(key, JSON.stringify(values));
        if (status) status.textContent = 'Local draft saved.';
      };

      form.addEventListener('input', save);
      form.addEventListener('change', save);
      form.addEventListener('submit', () => localStorage.removeItem(key));
    });
  }

  function setupFilePreview() {
    document.querySelectorAll('input[type="file"]').forEach((input) => {
      input.addEventListener('change', () => {
        const preview = input.closest('form') && input.closest('form').querySelector('[data-file-preview]');
        if (!preview || !input.files || !input.files[0]) return;
        const file = input.files[0];
        preview.innerHTML = '';
        if (file.type.startsWith('image/')) {
          const image = document.createElement('img');
          image.alt = '';
          image.className = 'h-28 w-28 rounded-md object-cover';
          image.src = URL.createObjectURL(file);
          preview.appendChild(image);
        }
        const label = document.createElement('p');
        label.className = 'mt-2 text-sm text-slate-600';
        label.textContent = file.name;
        preview.appendChild(label);
      });
    });
  }

  function setupDistrictSelects() {
    document.querySelectorAll('[data-district-select]').forEach((districtSelect) => {
      if (districtSelect.dataset.districtSelectBound === 'true') return;
      districtSelect.dataset.districtSelectBound = 'true';

      const scope = districtSelect.closest('form') || document;
      const provinceSelect = scope.querySelector('[data-province-select]');
      if (!provinceSelect) return;

      const filterDistricts = () => {
        const province = provinceSelect.value;
        let selectedDistrictVisible = !districtSelect.value;

        districtSelect.querySelectorAll('optgroup').forEach((group) => {
          const visible = !province || group.label === province;
          group.hidden = !visible;
          group.disabled = !visible;
          group.querySelectorAll('option').forEach((option) => {
            option.hidden = !visible;
            option.disabled = !visible;
            if (visible && option.value === districtSelect.value) {
              selectedDistrictVisible = true;
            }
          });
        });

        if (!selectedDistrictVisible) {
          districtSelect.value = '';
        }
      };

      provinceSelect.addEventListener('change', filterDistricts);
      filterDistricts();
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    setupDrafts();
    setupDistrictSelects();
    setupFilePreview();
  });

  document.body.addEventListener('htmx:afterSwap', () => {
    setupDistrictSelects();
    setupFilePreview();
  });
})();
