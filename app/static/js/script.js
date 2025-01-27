// Task Manager JavaScript

// Enable Bootstrap tooltips
document.addEventListener("DOMContentLoaded", function () {
  var tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
});

// Form validation
function validateForm() {
  "use strict";

  const forms = document.querySelectorAll(".needs-validation");

  Array.prototype.slice.call(forms).forEach(function (form) {
    form.addEventListener(
      "submit",
      function (event) {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add("was-validated");
      },
      false
    );
  });
}

// Delete confirmation
function confirmDelete(taskId) {
  if (confirm("Are you sure you want to delete this task?")) {
    document.getElementById("delete-form-" + taskId).submit();
  }
}

// Dynamic due date validation
function validateDueDate() {
  const dueDateInput = document.getElementById("due_date");
  if (dueDateInput) {
    dueDateInput.addEventListener("change", function () {
      const selectedDate = new Date(this.value);
      const today = new Date();

      if (selectedDate < today) {
        this.setCustomValidity("Due date cannot be in the past");
      } else {
        this.setCustomValidity("");
      }
    });
  }
}

// Task status updates
function updateTaskStatus(taskId, status) {
  const url = `/tasks/${taskId}/status`;
  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ status: status }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        location.reload();
      } else {
        alert("Failed to update task status");
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      alert("An error occurred while updating the task");
    });
}

// Initialize all components
document.addEventListener("DOMContentLoaded", function () {
  validateForm();
  validateDueDate();
});
