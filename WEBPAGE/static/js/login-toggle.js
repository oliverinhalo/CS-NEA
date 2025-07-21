function setEmailType(type) {
    const emailLabel = document.getElementById('emailLabel');
    const emailTypeInput = document.getElementById('emailType');
    const buttons = document.querySelectorAll('.toggle-buttons button');

    if (type === 'school') {
        emailLabel.textContent = 'School Email:';
        emailTypeInput.value = 'school';
        document.body.style.background = "linear-gradient(90deg, rgba(42, 123, 155, 1) 0%, rgba(87, 199, 133, 1) 50%, rgba(237, 221, 83, 1) 100%)";
    } else if (type === 'home') {
        emailLabel.textContent = 'Home Email:';
        emailTypeInput.value = 'home';
        document.body.style.background = "linear-gradient(270deg, rgba(42, 123, 155, 1) 0%, rgba(87, 199, 133, 1) 50%, rgba(237, 221, 83, 1) 100%)";
    }

    buttons.forEach(button => {
        if (button.textContent.toLowerCase().includes(type)) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
}
