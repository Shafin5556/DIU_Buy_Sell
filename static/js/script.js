function previewImage(event) {
  const imagePreviewContainer = document.getElementById(
    "imagePreviewContainer"
  );
  const imagePreview = document.getElementById("imagePreview");

  const file = event.target.files[0];
  const reader = new FileReader();

  reader.onload = function () {
    imagePreview.src = reader.result;
    imagePreviewContainer.style.display = "block";
  };

  if (file) {
    reader.readAsDataURL(file);
  } else {
    imagePreviewContainer.style.display = "none";
  }
}

//////////////////////////////profile////////////////////////////

function previewImage(event) {
  const reader = new FileReader();
  const imagePreview = document.getElementById("imagePreview");

  reader.onload = function () {
    imagePreview.src = reader.result;
  };

  if (event.target.files && event.target.files[0]) {
    reader.readAsDataURL(event.target.files[0]);
  }
}

///////////////buy//////////////////////

function submitComment(postId) {
  var form = event.target;
  var formData = new FormData(form);
  formData.append("post_id", postId);

  fetch("/comment/" + postId, {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      var commentsSection = document
        .getElementById("comments-" + postId)
        .querySelector(".comment-list");
      var newComment = document.createElement("div");
      newComment.classList.add("comment", "mb-2");
      newComment.innerHTML =
        "<p><strong>" +
        data.username +
        ":</strong> " +
        data.comment_text +
        "</p>";
      commentsSection.appendChild(newComment);
      form.reset();
    })
    .catch((error) => console.error("Error:", error));
  return false;
}

function loadMoreComments(postId) {
  var commentsSection = document
    .getElementById("comments-" + postId)
    .querySelector(".comment-list");

  fetch("/comments/" + postId)
    .then((response) => response.json())
    .then((data) => {
      if (data.comments) {
        commentsSection.innerHTML = "";
        data.comments.forEach((comment) => {
          var commentDiv = document.createElement("div");
          commentDiv.classList.add("comment", "mb-2");

          commentDiv.innerHTML = `
                <div class="d-flex align-items-center mb-2">
                    <!-- Placeholder for commenter's profile picture -->
                    <div class="rounded-circle" style="width: 40px; height: 40px; background-color: #ccc; display: flex; justify-content: center; align-items: center;">
                        <!-- Example of a placeholder icon, you can replace with any URL or use a letter from username -->
                        <span style="font-size: 20px; color: white;">${comment.username[0]}</span>
                    </div>
                    <p class="ml-3 mb-0"><strong>${comment.username}</strong></p>
                </div>
                <p>${comment.comment_text}</p> 
            `;
          commentsSection.appendChild(commentDiv);
        });

        document.querySelector(`#comments-${postId} button`).style.display =
          "none";
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

function addInterest(postId) {
  var btn = document.getElementById("interest-btn-" + postId);
  btn.disabled = true;
  btn.innerHTML = '<i class="fas fa-check"></i> Interested';

  fetch("/add_interest/" + postId, {
    method: "POST",
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        var interestCountElement = document.getElementById(
          "interest-count-" + postId
        );
        interestCountElement.textContent =
          "Interest: " + data.new_interest_count;
      } else {
        alert(data.message);
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

function openModal(postId) {
  var imageUrl = document.getElementById("product-image-" + postId).src;
  document.getElementById("fullScreenImage").src = imageUrl;
}

function zoomImage(event) {
  var img = event.target;
  img.style.transform = "scale(2)";
  img.style.transition = "transform 0.25s ease";
}

function resetZoom(event) {
  var img = event.target;
  img.style.transform = "scale(1)";
}
//////////////sell////////////////
function previewImage(event) {
    var input = event.target;
    var file = input.files[0];

    if (file) {
        var reader = new FileReader();

        reader.onload = function(e) {
     
            var previewContainer = document.getElementById('imagePreviewContainer');
            var imagePreview = document.getElementById('imagePreview');

            imagePreview.src = e.target.result;

  
            previewContainer.style.display = 'block';
        }

        reader.readAsDataURL(file);
    }
}