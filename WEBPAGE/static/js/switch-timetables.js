function setActive(button) {
    document.querySelectorAll('.timeTable-View-button').forEach(btn => {
        btn.classList.remove('active');
    });
    button.classList.add('active');
}

function ShowList(button) {
    document.querySelector(".listView").style.display = "block";
    document.querySelector(".TimeTable").style.display = "none";
    setActive(button);
}

function ShowTraditional(button) {
    document.querySelector(".listView").style.display = "none";
    document.querySelector(".TimeTable").style.display = "block";
    setActive(button);
}
