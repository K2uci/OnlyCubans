// base.js - JavaScript base para el módulo Content

document.addEventListener("DOMContentLoaded", function () {
  // Mobile menu functionality
  initMobileMenu();

  // Like functionality
  initLikeButtons();

  // Bookmark functionality
  initBookmarkButtons();

  // Comment functionality
  initCommentSystem();

  // Search functionality
  initSearch();

  // Notification system
  initNotifications();
});

// Mobile Menu
function initMobileMenu() {
  const mobileMenuBtn = document.getElementById("mobileMenuBtn");
  const contentSidebar = document.getElementById("contentSidebar");
  const mobileOverlay = document.getElementById("mobileOverlay");

  if (mobileMenuBtn && contentSidebar) {
    mobileMenuBtn.addEventListener("click", function () {
      contentSidebar.classList.toggle("active");
      mobileOverlay.classList.toggle("active");
    });

    mobileOverlay.addEventListener("click", function () {
      contentSidebar.classList.remove("active");
      mobileOverlay.classList.remove("active");
    });
  }
}

// Like System
function initLikeButtons() {
  document.addEventListener("click", function (e) {
    if (e.target.closest(".like-btn")) {
      const likeBtn = e.target.closest(".like-btn");
      const postId = likeBtn.dataset.postId;
      const isActive = likeBtn.classList.contains("active");

      likePost(likeBtn, postId, isActive);
    }
  });
}

function likePost(button, postId, isActive) {
  const url = isActive ? button.dataset.unlikeUrl : button.dataset.likeUrl;

  // Mostrar loading
  button.innerHTML = '<div class="loading-spinner"></div>';
  button.disabled = true;

  fetch(url, {
    method: "POST",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: new URLSearchParams({
      like_type: "like",
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Actualizar UI
        const likeCount = button.querySelector("span");
        if (likeCount) {
          likeCount.textContent = `Me gusta (${data.likes_count})`;
        }

        button.classList.toggle("active", data.liked);
        button.innerHTML = `<i class="fas fa-heart"></i><span>Me gusta (${data.likes_count})</span>`;
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showNotification("Error al procesar el like", "error");
    })
    .finally(() => {
      button.disabled = false;
    });
}

// Bookmark System
function initBookmarkButtons() {
  document.addEventListener("click", function (e) {
    if (e.target.closest(".bookmark-btn")) {
      const bookmarkBtn = e.target.closest(".bookmark-btn");
      const postId = bookmarkBtn.dataset.postId;

      toggleBookmark(bookmarkBtn, postId);
    }
  });
}

function toggleBookmark(button, postId) {
  const url = button.dataset.bookmarkUrl;

  button.innerHTML = '<div class="loading-spinner"></div>';
  button.disabled = true;

  fetch(url, {
    method: "POST",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": getCookie("csrftoken"),
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        button.classList.toggle("active", data.bookmarked);
        button.innerHTML = `<i class="fas fa-bookmark"></i><span>Guardar</span>`;
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showNotification("Error al guardar el post", "error");
    })
    .finally(() => {
      button.disabled = false;
    });
}

// Comment System
function initCommentSystem() {
  // Toggle comment section
  document.addEventListener("click", function (e) {
    if (e.target.closest(".comment-btn")) {
      const postId = e.target.closest(".comment-btn").dataset.postId;
      toggleComments(postId);
    }
  });

  // Reply functionality
  document.addEventListener("click", function (e) {
    if (e.target.closest(".reply-comment-btn")) {
      const commentId =
        e.target.closest(".reply-comment-btn").dataset.commentId;
      toggleReplyForm(commentId);
    }
  });
}

function toggleComments(postId) {
  const commentsSection = document.getElementById(`comments-${postId}`);
  if (!commentsSection) return;

  if (commentsSection.style.display === "none") {
    loadComments(postId);
    commentsSection.style.display = "block";
  } else {
    commentsSection.style.display = "none";
  }
}

function loadComments(postId) {
  const commentsSection = document.getElementById(`comments-${postId}`);
  const loadingElement = commentsSection.querySelector(".comments-loading");

  // Simular carga de comentarios (en producción, harías una petición AJAX)
  setTimeout(() => {
    loadingElement.style.display = "none";
    commentsSection.innerHTML = `
            <div class="comment-form">
                <textarea placeholder="Escribe tu comentario..." class="form-control"></textarea>
                <button class="btn btn-primary mt-2">Comentar</button>
            </div>
            <div class="comments-list">
                <!-- Los comentarios se cargarían aquí -->
            </div>
        `;
  }, 1000);
}

// Search Functionality
function initSearch() {
  const searchForm = document.querySelector(".search-form");
  if (searchForm) {
    searchForm.addEventListener("submit", function (e) {
      const searchInput = this.querySelector(".search-input");
      if (searchInput.value.trim() === "") {
        e.preventDefault();
        searchInput.focus();
      }
    });
  }
}

// Notification System
function initNotifications() {
  const notificationBtn = document.getElementById("notificationBtn");
  if (notificationBtn) {
    notificationBtn.addEventListener("click", function () {
      // Implementar lógica de notificaciones
      showNotification("Sistema de notificaciones en desarrollo", "info");
    });
  }
}

// Utility Functions
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function showNotification(message, type = "info") {
  // Crear notificación toast
  const notification = document.createElement("div");
  notification.className = `notification-toast notification-${type}`;
  notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;

  document.body.appendChild(notification);

  // Mostrar animación
  setTimeout(() => notification.classList.add("show"), 100);

  // Ocultar después de 3 segundos
  setTimeout(() => {
    notification.classList.remove("show");
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

function getNotificationIcon(type) {
  const icons = {
    success: "check-circle",
    error: "exclamation-circle",
    warning: "exclamation-triangle",
    info: "info-circle",
  };
  return icons[type] || "info-circle";
}

// Media Modal
function openMediaModal(mediaUrl, mediaType) {
  // Implementar modal para visualizar medios
  const modal = document.createElement("div");
  modal.className = "media-modal";
  modal.innerHTML = `
        <div class="modal-overlay">
            <div class="modal-content">
                <button class="modal-close">&times;</button>
                ${
                  mediaType === "image"
                    ? `<img src="${mediaUrl}" alt="Media">`
                    : `<video controls><source src="${mediaUrl}"></video>`
                }
            </div>
        </div>
    `;

  document.body.appendChild(modal);

  // Cerrar modal
  modal.querySelector(".modal-close").addEventListener("click", () => {
    modal.remove();
  });

  modal.querySelector(".modal-overlay").addEventListener("click", (e) => {
    if (e.target === modal.querySelector(".modal-overlay")) {
      modal.remove();
    }
  });
}

document.addEventListener("DOMContentLoaded", function () {
  const profileBtn = document.getElementById("profileBtn");
  const profileMenu = document.querySelector(".profile-menu");

  profileBtn.addEventListener("click", function (event) {
    event.stopPropagation();
    profileMenu.classList.toggle("show");
  });

  // Cerrar el menú si se hace clic fuera de él
  document.addEventListener("click", function () {
    profileMenu.classList.remove("show");
  });
});
