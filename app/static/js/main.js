// Small progressive enhancements. Every page also works without JavaScript.

// "+ Add another group" on the order form (allergy notes per guest group, FR-C3.2).
document.addEventListener("click", function (event) {
  if (event.target.id !== "add-note-row") return;
  var rows = document.getElementById("note-rows");
  var last = rows.querySelector(".note-row:last-child");
  var copy = last.cloneNode(true);
  copy.querySelectorAll("input").forEach(function (input) { input.value = ""; });
  rows.appendChild(copy);
  copy.querySelector("input").focus();
});

// Ask before removing a food item.
document.addEventListener("submit", function (event) {
  var message = event.target.getAttribute("data-confirm");
  if (message && !window.confirm(message)) event.preventDefault();
});
