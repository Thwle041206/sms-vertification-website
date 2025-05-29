document.addEventListener('DOMContentLoaded', function () {
  const togglePassword = document.getElementById('togglePassword');
  const passwordInput = document.getElementById('passwordInput');

  if (togglePassword && passwordInput) {
    togglePassword.addEventListener('click', function () {
      const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      passwordInput.setAttribute('type', type);

      // Toggle icon src
      if (type === 'text') {
        togglePassword.src = 'eye-on0.svg';
      } else {
        togglePassword.src = 'eye-off0.svg';
      }
    });
  }

  // New code for Show all toggle
  function toggleShowAll(event) {
    const showAllDiv = event.currentTarget;
    const targetId = showAllDiv.getAttribute('data-target');
    let container = showAllDiv.closest('.services-container');
    const listDiv = document.getElementById(targetId);
    
    if (!listDiv) return;
    if (!container) {
      // fallback for country section where container is not inside .services-container
      container = listDiv;
    }

    // Toggle expanded class on show-all button and list only (remove container toggle)
    showAllDiv.classList.toggle('expanded');
    listDiv.classList.toggle('expanded');
    
    // Rotate arrow icon
    const arrow = showAllDiv.querySelector('.vector6');
    if (arrow) {
      arrow.style.transform = showAllDiv.classList.contains('expanded') ? 'rotate(180deg)' : '';
    }
  }

  const showAllServices = document.getElementById('show-all-services');
  const showAllCountry = document.getElementById('show-all-country');

  if (showAllServices) {
    showAllServices.addEventListener('click', toggleShowAll);
  }
  if (showAllCountry) {
    showAllCountry.addEventListener('click', toggleShowAll);
  }

  // Sorting functionality for services and countries
  const serviceSortDropdown = document.querySelector('.service-sort-dropdown');
  const countrySortDropdown = document.querySelector('.country-sort-dropdown');
  const allServicesContainer = document.getElementById('all-services');
  const allCountryContainer = document.getElementById('all-country');

  function parseNumberOfNumbers(serviceElem) {
    const numbersElem = serviceElem.querySelector('._21-267-numbers');
    if (!numbersElem) return 0;
    const text = numbersElem.textContent || '';
    const match = text.match(/(\d+)/);
    return match ? parseInt(match[1], 10) : 0;
  }

  function parsePrice(serviceElem) {
    const priceElem = serviceElem.querySelector('.from-1-90');
    if (!priceElem) return Number.MAX_VALUE;
    const text = priceElem.textContent || '';
    const match = text.match(/\$([\d\.]+)/);
    return match ? parseFloat(match[1]) : Number.MAX_VALUE;
  }

  function parseSuccessRate(serviceElem) {
    const successElem = serviceElem.querySelector('.already-use-43-435');
    if (!successElem) return 0;
    const text = successElem.textContent || '';
    const match = text.match(/([\d\.]+)%/);
    return match ? parseFloat(match[1]) : 0;
  }

  function parseName(elem, selector) {
    const nameElem = elem.querySelector(selector);
    if (!nameElem) return '';
    return nameElem.textContent.trim().toLowerCase();
  }

  function sortServices(criteria) {
    if (!allServicesContainer) return;
    const services = Array.from(allServicesContainer.querySelectorAll('.service'));
    services.sort((a, b) => {
      switch (criteria) {
        case 'number_of_numbers':
          return parseNumberOfNumbers(b) - parseNumberOfNumbers(a);
        case 'price':
          return parsePrice(a) - parsePrice(b);
        case 'success_rate':
          return parseSuccessRate(b) - parseSuccessRate(a);
        case 'name':
          return parseName(a, '.vietnam').localeCompare(parseName(b, '.vietnam'));
        default:
          return 0;
      }
    });
    // Re-append in sorted order
    services.forEach(service => allServicesContainer.appendChild(service));
  }

  function parseAvailableServices(countryElem) {
    const availElem = countryElem.querySelector('.available-services-count');
    if (!availElem) return 0;
    const text = availElem.textContent || '';
    const match = text.match(/(\d+)/);
    return match ? parseInt(match[1], 10) : 0;
  }

  function sortCountries(criteria) {
    if (!allCountryContainer) return;
    const countries = Array.from(allCountryContainer.querySelectorAll('.service'));
    countries.sort((a, b) => {
      switch (criteria) {
        case 'name_country':
          return parseName(a, '.countryName').localeCompare(parseName(b, '.countryName'));
        case 'available_services':
          return parseAvailableServices(b) - parseAvailableServices(a);
        default:
          return 0;
      }
    });
    // Re-append in sorted order
    countries.forEach(country => allCountryContainer.appendChild(country));
  }

  if (serviceSortDropdown) {
    serviceSortDropdown.addEventListener('change', function () {
      sortServices(this.value);
    });
  }

  if (countrySortDropdown) {
    countrySortDropdown.addEventListener('change', function () {
      sortCountries(this.value);
    });
  }
});

