document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".dropdown-checkbox").forEach(dropdown => {
        const btn = dropdown.querySelector(".dropdown-btn");
        const selectAll = dropdown.querySelector(".select-all");
        const checkboxes = dropdown.querySelectorAll(".item-checkbox");
        const form = dropdown.closest("form");

        // togle it
        btn.addEventListener("click", e => {
            dropdown.classList.toggle("active");
            e.stopPropagation();
        });

        // to many hours spent on closing the dropdown
        document.addEventListener("click", () => dropdown.classList.remove("active"));

        // all dont show all cheacked but is behind the scenes
        selectAll.addEventListener("change", () => {
            if (selectAll.checked) {
                checkboxes.forEach(cb => cb.checked = false);
                form.submit();
            }
        });

        // undo all if one is slected
        checkboxes.forEach(cb => {
            cb.addEventListener("change", () => {
                if (cb.checked) selectAll.checked = false;
                form.submit();
            });
        });
    });
});