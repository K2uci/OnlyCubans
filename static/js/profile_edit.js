// Configuración de edición de perfil
document.addEventListener("DOMContentLoaded", function () {
  // Navegación entre pestañas
  const navItems = document.querySelectorAll(".nav-item");
  const tabContents = document.querySelectorAll(".tab-content");

  navItems.forEach((item) => {
    item.addEventListener("click", function (e) {
      e.preventDefault();

      // Remover clase active de todos los items
      navItems.forEach((nav) => nav.classList.remove("active"));
      tabContents.forEach((content) => content.classList.remove("active"));

      // Agregar clase active al item clickeado
      this.classList.add("active");

      // Mostrar contenido correspondiente
      const tabId = this.getAttribute("data-tab");
      document.getElementById(tabId).classList.add("active");
    });
  });

  // Upload de imágenes
  const avatarInput = document.getElementById("id_profile_picture");
  const coverInput = document.getElementById("id_cover_photo");
  const avatarPreview = document.getElementById("avatar-preview");
  const coverPreview = document.getElementById("cover-preview");

  // Avatar upload
  document
    .querySelector(".avatar-overlay")
    .addEventListener("click", function () {
      avatarInput.click();
    });

  avatarInput.addEventListener("change", function (e) {
    if (e.target.files && e.target.files[0]) {
      const reader = new FileReader();
      reader.onload = function (e) {
        avatarPreview.src = e.target.result;
        // Aquí podrías agregar lógica de recorte
        openImageCropModal(e.target.result, "avatar");
      };
      reader.readAsDataURL(e.target.files[0]);
    }
  });

  // Cover upload
  document
    .querySelector(".cover-overlay")
    .addEventListener("click", function () {
      coverInput.click();
    });

  coverInput.addEventListener("change", function (e) {
    if (e.target.files && e.target.files[0]) {
      const reader = new FileReader();
      reader.onload = function (e) {
        coverPreview.src = e.target.result;
        openImageCropModal(e.target.result, "cover");
      };
      reader.readAsDataURL(e.target.files[0]);
    }
  });

  // Contador de caracteres para biografía
  const bioTextarea = document.getElementById("id_bio");
  const bioChars = document.getElementById("bio-chars");

  if (bioTextarea && bioChars) {
    bioChars.textContent = bioTextarea.value.length;

    bioTextarea.addEventListener("input", function () {
      bioChars.textContent = this.value.length;

      if (this.value.length > 450) {
        bioChars.style.color = "var(--warning-color)";
      } else if (this.value.length > 490) {
        bioChars.style.color = "var(--danger-color)";
      } else {
        bioChars.style.color = "var(--text-dark)";
      }
    });
  }

  // Selector de tema
  const themeOptions = document.querySelectorAll(".theme-option");
  themeOptions.forEach((option) => {
    option.addEventListener("click", function () {
      themeOptions.forEach((opt) => opt.classList.remove("active"));
      this.classList.add("active");

      const theme = this.getAttribute("data-theme");
      setTheme(theme);
    });
  });

  // Validación de formulario
  const form = document.querySelector(".profile-edit-form");
  form.addEventListener("submit", function (e) {
    if (!validateForm()) {
      e.preventDefault();
      showNotification(
        "Por favor corrige los errores en el formulario",
        "error"
      );
    }
  });

  // Validación en tiempo real
  const inputs = form.querySelectorAll("input[required], textarea[required]");
  inputs.forEach((input) => {
    input.addEventListener("blur", validateField);
    input.addEventListener("input", clearFieldError);
  });

  // Inicializar tema guardado
  const savedTheme = localStorage.getItem("theme") || "dark";
  setTheme(savedTheme);
});

// Funciones de utilidad
function validateForm() {
  let isValid = true;
  const inputs = document.querySelectorAll(
    "input[required], textarea[required]"
  );

  inputs.forEach((input) => {
    if (!validateField({ target: input })) {
      isValid = false;
    }
  });

  return isValid;
}

function validateField(e) {
  const field = e.target;
  const value = field.value.trim();
  let isValid = true;

  // Remover errores previos
  clearFieldError(field);

  // Validaciones específicas por tipo de campo
  switch (field.type) {
    case "email":
      if (!isValidEmail(value)) {
        showFieldError(field, "Por favor ingresa un email válido");
        isValid = false;
      }
      break;

    case "url":
      if (value && !isValidUrl(value)) {
        showFieldError(field, "Por favor ingresa una URL válida");
        isValid = false;
      }
      break;

    case "tel":
      if (value && !isValidPhone(value)) {
        showFieldError(field, "Por favor ingresa un número de teléfono válido");
        isValid = false;
      }
      break;

    default:
      if (field.required && !value) {
        showFieldError(field, "Este campo es obligatorio");
        isValid = false;
      }
  }

  // Validación de nombre de usuario
  if (field.name === "username") {
    if (value.length < 3) {
      showFieldError(
        field,
        "El nombre de usuario debe tener al menos 3 caracteres"
      );
      isValid = false;
    } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
      showFieldError(
        field,
        "El nombre de usuario solo puede contener letras, números y guiones bajos"
      );
      isValid = false;
    }
  }

  if (isValid) {
    field.classList.add("success");
  }

  return isValid;
}

function showFieldError(field, message) {
  field.classList.add("error");

  let errorElement = field.parentNode.querySelector(".error-message");
  if (!errorElement) {
    errorElement = document.createElement("div");
    errorElement.className = "error-message";
    field.parentNode.appendChild(errorElement);
  }

  errorElement.textContent = message;
}

function clearFieldError(e) {
  const field = e.target || e;
  field.classList.remove("error", "success");

  const errorElement = field.parentNode.querySelector(".error-message");
  if (errorElement) {
    errorElement.remove();
  }
}

function isValidEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

function isValidUrl(url) {
  try {
    new URL(url);
    return true;
  } catch (_) {
    return false;
  }
}

function isValidPhone(phone) {
  const re = /^\+?[\d\s\-\(\)]{10,}$/;
  return re.test(phone);
}

// function setTheme(theme) {
//     document.documentElement.setAttribute('data
