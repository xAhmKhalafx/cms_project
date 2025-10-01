document.addEventListener("DOMContentLoaded", () => {
  const profileToggle = document.getElementById("profileToggle");
  const dropdownMenu = document.getElementById("dropdownMenu");

  if (profileToggle && dropdownMenu) {
    profileToggle.addEventListener("click", (event) => {
      event.stopPropagation(); // Prevents click from immediately closing the menu
      dropdownMenu.classList.toggle("visible");
    });

    // Close the dropdown when clicking anywhere else on the page
    document.addEventListener("click", (event) => {
      if (
        dropdownMenu.classList.contains("visible") &&
        !dropdownMenu.contains(event.target) &&
        event.target !== profileToggle
      ) {
        dropdownMenu.classList.remove("visible");
      }
    });
  }
});
