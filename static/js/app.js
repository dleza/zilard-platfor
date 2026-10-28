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
      captureGps(event.target.closest('[data-capture-gps]'), event.target.closest('form') || document);
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

  // Approximate province centres and the distance (km) within which a location is plausible.
  const PROVINCE_AREAS = {
    'Central': [-14.2, 27.9, 300],
    'Copperbelt': [-13.0, 28.3, 200],
    'Eastern': [-13.7, 32.2, 300],
    'Luapula': [-11.1, 29.0, 260],
    'Lusaka': [-15.4, 28.3, 150],
    'Muchinga': [-11.8, 31.6, 320],
    'Northern': [-10.3, 31.0, 320],
    'North-Western': [-12.8, 25.5, 420],
    'Southern': [-16.8, 26.8, 320],
    'Western': [-15.5, 23.5, 380]
  };

  function distanceKm(lat1, lng1, lat2, lng2) {
    const toRad = (d) => (d * Math.PI) / 180;
    const dLat = toRad(lat2 - lat1);
    const dLng = toRad(lng2 - lng1);
    const a = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) ** 2;
    return 6371 * 2 * Math.asin(Math.sqrt(a));
  }

  function gpsStatusWriter(button) {
    let el = button.parentElement && button.parentElement.querySelector('[data-gps-status]');
    if (!el) {
      el = document.createElement('p');
      el.setAttribute('data-gps-status', 'true');
      el.setAttribute('aria-live', 'polite');
      el.className = 'mt-2 text-sm text-slate-700';
      button.insertAdjacentElement('afterend', el);
    }
    return function (message, isWarning) {
      el.textContent = message;
      el.style.color = isWarning ? '#b45309' : '';
    };
  }

  function captureGps(button, scope) {
    const latField = scope.querySelector('[data-gps-lat]');
    const lngField = scope.querySelector('[data-gps-lng]');
    if (!button || !latField || !lngField) return;
    const say = gpsStatusWriter(button);
    if (!('geolocation' in navigator)) {
      say('This browser cannot capture a location. Type the latitude and longitude instead.', true);
      return;
    }
    button.disabled = true;
    say('Getting your location. Please allow location access if asked...');
    navigator.geolocation.getCurrentPosition(
      function (position) {
        button.disabled = false;
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        latField.value = lat.toFixed(6);
        lngField.value = lng.toFixed(6);
        latField.dispatchEvent(new Event('input', { bubbles: true }));
        lngField.dispatchEvent(new Event('input', { bubbles: true }));

        let message = 'Location captured (accuracy about ' + Math.round(position.coords.accuracy) + ' m).';
        let warn = false;
        if (position.coords.accuracy > 1000) {
          message += ' Accuracy is low. Computers often give a rough location, so use a phone or type the coordinates.';
          warn = true;
        }
        const provinceSelect = scope.querySelector('[data-province-select]');
        const area = provinceSelect && PROVINCE_AREAS[provinceSelect.value];
        if (area) {
          const away = distanceKm(lat, lng, area[0], area[1]);
          if (away > area[2]) {
            message += ' Warning: this is about ' + Math.round(away) + ' km from ' + provinceSelect.value +
              ' Province. Check it is the worker\'s location, or correct the coordinates.';
            warn = true;
          }
        }
        say(message, warn);
      },
      function (error) {
        button.disabled = false;
        const reasons = {
          1: 'Location access was denied. Allow location for this site in the browser, or type the coordinates.',
          2: 'The location could not be determined. Try again or type the coordinates.',
          3: 'Getting the location took too long. Try again or type the coordinates.'
        };
        say(reasons[error.code] || 'Could not capture the location. Type the coordinates instead.', true);
      },
      { enableHighAccuracy: true, timeout: 20000, maximumAge: 0 }
    );
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
