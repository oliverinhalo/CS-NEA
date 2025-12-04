function setEmailType(type) {
    const emailLabel = document.getElementById('emailLabel');
    const emailTypeInput = document.getElementById('emailType');
    const buttons = document.querySelectorAll('.toggle-buttons button');

    if (type === 'school') {
        emailLabel.textContent = 'School Email:';
        emailTypeInput.value = 'school';
        document.body.style.background = "radial-gradient(circle, #edabd1, #d099c7, #b188bd, #9179b2, #6e6aa5, #5b72ae, #4279b5, #1880b8, #009fcf, #00bee0, #24ddeb, #5ffbf1)";
    } else if (type === 'home') {
        emailLabel.textContent = 'Home Email:';
        emailTypeInput.value = 'home';
        document.body.style.background = "radial-gradient(circle, #5ffbf1, #24ddeb, #00bee0, #009fcf, #1880b8, #5b72ae, #4279b5, #6e6aa5, #9179b2, #b188bd, #b188bd, #d099c7, #edabd1)";
    }

    buttons.forEach(button => {
        if (button.textContent.toLowerCase().includes(type)) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
}
