// JavaScript personalizado para NBF Listados

/**
 * Confirmación simple para acciones peligrosas
 */
function confirmDelete(message = "¿Estás seguro de que deseas eliminar?") {
  return confirm(message);
}

/**
 * Copiar texto al portapapeles
 */
function copyToClipboard(text) {
  navigator.clipboard
    .writeText(text)
    .then(function () {
      showToast("Copiado al portapapeles", "success");
    })
    .catch(function (err) {
      console.error("Error al copiar: ", err);
    });
}

/**
 * Mostrar toast simple
 */
function showToast(message, type = "info") {
  const alertClasses = {
    success: "alert-success",
    danger: "alert-danger",
    warning: "alert-warning",
    info: "alert-info",
  };

  const alertDiv = document.createElement("div");
  alertDiv.className = `alert ${alertClasses[type] || alertClasses["info"]} alert-dismissible fade show`;
  alertDiv.setAttribute("role", "alert");
  alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

  const container = document.querySelector("main") || document.body;
  container.insertBefore(alertDiv, container.firstChild);

  // Auto-cerrar después de 5 segundos
  setTimeout(function () {
    alertDiv.remove();
  }, 5000);
}

/**
 * Formatear precio
 */
function formatPrice(price) {
  return parseFloat(price)
    .toFixed(2)
    .replace(/\d(?=(\d{3})+\.)/g, "$&,");
}

/**
 * Validación de formularios simple
 */
function validateForm(formId) {
  const form = document.getElementById(formId);
  if (!form) return false;

  let isValid = true;
  const requiredFields = form.querySelectorAll("[required]");

  requiredFields.forEach((field) => {
    if (!field.value.trim()) {
      field.classList.add("is-invalid");
      isValid = false;
    } else {
      field.classList.remove("is-invalid");
    }
  });

  return isValid;
}

/**
 * Inicializar comportamientos al cargar
 */
document.addEventListener("DOMContentLoaded", function () {
  // Bootstrap tooltips
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]'),
  );
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Añadir clase active al link actual en navbar
  const currentLocation = location.pathname;
  const menuItems = document.querySelectorAll("a.nav-link");
  menuItems.forEach((item) => {
    if (item.getAttribute("href") === currentLocation) {
      item.classList.add("active");
    }
  });
});

/**
 * Funciones de utilidad
 */
const utils = {
  // Obtener parámetro de URL
  getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
  },

  // Redirigir con retraso
  redirectAfterDelay(url, delay = 1500) {
    setTimeout(function () {
      window.location.href = url;
    }, delay);
  },

  // Animación de carga
  showLoading() {
    const loader = document.createElement("div");
    loader.className = "spinner-border text-primary";
    loader.setAttribute("role", "status");
    return loader;
  },
};

/**
 * Sistema de Filtros Avanzados
 * Maneja búsqueda rápida + filtros avanzados sin perder valores
 */
const FilterSystem = {
  searchTimeout: null,
  debounceDelay: 800, // ms

  /**
   * Inicializar el sistema de filtros
   */
  init() {
    const searchInput = document.querySelector('input[name="busqueda"]');

    if (searchInput) {
      // Debounce en la búsqueda
      searchInput.addEventListener("input", (e) => {
        this.debounceSearch(e.target);
      });

      // Enter para enviar inmediatamente
      searchInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
          clearTimeout(this.searchTimeout);
          e.target.closest("form").submit();
        }
      });
    }
  },

  /**
   * Búsqueda con debounce (espera 800ms después de escribir)
   */
  debounceSearch(input) {
    clearTimeout(this.searchTimeout);

    // Visual feedback
    input.parentElement.style.opacity = "0.7";

    this.searchTimeout = setTimeout(() => {
      input.parentElement.style.opacity = "1";
      // Auto-submit solo si hay texto
      if (input.value.trim().length > 0 && input.value.trim().length > 2) {
        input.closest("form").submit();
      }
    }, this.debounceDelay);
  },

  /**
   * Aplicar filtro y hacer submit preservando otros valores
   */
  applyFilter(filterName, filterValue) {
    const form = document.querySelector('form[method="GET"]');
    if (!form) return;

    const input = document.createElement("input");
    input.type = "hidden";
    input.name = filterName;
    input.value = filterValue;
    form.appendChild(input);
    form.submit();
  },

  /**
   * Limpiar todos los filtros
   */
  clearAllFilters() {
    window.location.href = window.location.pathname;
  },

  /**
   * Limpiar un filtro específico
   */
  clearFilter(filterName) {
    const form = document.querySelector('form[method="GET"]');
    if (!form) return;

    // Remover el filtro específico
    const select = form.querySelector(`select[name="${filterName}"]`);
    if (select) {
      select.value = "";
      form.submit();
    }
  },
};

// Inicializar filtros cuando el DOM está listo
document.addEventListener("DOMContentLoaded", function () {
  FilterSystem.init();
});
