document.addEventListener("DOMContentLoaded", function () {
  // Tab functionality
  const tabLinks = document.querySelectorAll(".profile-nav a");
  tabLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      e.preventDefault();
      const tab = this.getAttribute("href");
      loadTab(tab);
    });
  });

  // Edit profile buttons
  const editButtons = document.querySelectorAll(
    ".edit-cover-btn, .edit-avatar-btn"
  );
  editButtons.forEach((button) => {
    button.addEventListener("click", function () {
      // Implementation for editing cover or avatar
      alert("Funcionalidad de edición en desarrollo");
    });
  });

  // Payout request
  const payoutRequestBtn = document.querySelector(".payout-request .btn");
  if (payoutRequestBtn) {
    payoutRequestBtn.addEventListener("click", function () {
      requestPayout();
    });
  }
});

function loadTab(tab) {
  // Simulate loading tab content
  fetch(tab)
    .then((response) => response.text())
    .then((html) => {
      document.querySelector(".profile-content").innerHTML = html;

      // Update active tab
      document.querySelectorAll(".profile-nav li").forEach((li) => {
        li.classList.remove("active");
      });

      document
        .querySelector(`.profile-nav a[href="${tab}"]`)
        .parentElement.classList.add("active");
    })
    .catch((error) => {
      console.error("Error loading tab:", error);
    });
}

function requestPayout() {
  if (confirm("¿Estás seguro de que quieres solicitar un pago?")) {
    fetch("/api/request-payout/", {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          alert("Solicitud de pago enviada correctamente");
          location.reload();
        } else {
          alert("Error: " + data.message);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("Error al procesar la solicitud");
      });
  }
}

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
