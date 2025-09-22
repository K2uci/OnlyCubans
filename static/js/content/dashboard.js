// Age verification
document.addEventListener("DOMContentLoaded", function () {
  // Check if age is verified
  if (!localStorage.getItem("ageVerified")) {
    document.getElementById("age-verification").style.display = "flex";
  }

  // Confirm age
  document.getElementById("confirm-age").addEventListener("click", function () {
    localStorage.setItem("ageVerified", "true");
    document.getElementById("age-verification").style.display = "none";
  });

  // Deny age
  document.getElementById("deny-age").addEventListener("click", function () {
    window.location.href = "https://www.google.com";
  });

  // Like functionality
  const likeButtons = document.querySelectorAll(".like-btn");
  likeButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const postId = this.getAttribute("data-post-id");
      toggleLike(postId, this);
    });
  });

  // Comment toggle
  const commentButtons = document.querySelectorAll(".comment-btn");
  commentButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const postCard = this.closest(".post-card");
      const commentsSection = postCard.querySelector(".comments-section");

      if (commentsSection.style.display === "none") {
        commentsSection.style.display = "block";
      } else {
        commentsSection.style.display = "none";
      }
    });
  });

  // Load more posts
  const loadMoreBtn = document.querySelector(".load-more-btn");
  if (loadMoreBtn) {
    loadMoreBtn.addEventListener("click", function () {
      const page = this.getAttribute("data-page");
      loadMorePosts(page);
    });
  }
});

function toggleLike(postId, button) {
  // Simulate API call
  fetch(`/api/posts/${postId}/like/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        const likesCount = button
          .closest(".post-card")
          .querySelector(".likes-count");
        likesCount.textContent = `${data.likes_count} me gusta`;

        if (data.liked) {
          button.classList.add("liked");
          button.innerHTML = '<i class="icon-like"></i> Te gusta';
        } else {
          button.classList.remove("liked");
          button.innerHTML = '<i class="icon-like"></i> Me gusta';
        }
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

function loadMorePosts(page) {
  const loadMoreBtn = document.querySelector(".load-more-btn");
  loadMoreBtn.textContent = "Cargando...";
  loadMoreBtn.disabled = true;

  // Simulate API call
  fetch(`/api/posts/?page=${page}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.posts.length > 0) {
        appendPosts(data.posts);
        loadMoreBtn.setAttribute("data-page", parseInt(page) + 1);

        if (!data.has_next) {
          loadMoreBtn.style.display = "none";
        }
      } else {
        loadMoreBtn.style.display = "none";
      }

      loadMoreBtn.textContent = "Cargar más publicaciones";
      loadMoreBtn.disabled = false;
    })
    .catch((error) => {
      console.error("Error:", error);
      loadMoreBtn.textContent = "Cargar más publicaciones";
      loadMoreBtn.disabled = false;
    });
}

function appendPosts(posts) {
  const postsContainer = document.querySelector(".posts-container");

  posts.forEach((post) => {
    const postElement = createPostElement(post);
    postsContainer.appendChild(postElement);
  });
}

function createPostElement(post) {
  // This would create a post element based on the post data
  // Implementation would depend on your post structure
  const div = document.createElement("div");
  div.className = "card post-card";
  div.setAttribute("data-post-id", post.id);
  div.innerHTML = `
        <!-- Post HTML structure here -->
    `;
  return div;
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
