function Panel() {
    if (document.getElementById("sidePanel").style.width === "0px") {
        document.getElementById("sidePanel").style.width = "300px";
    } else {
        document.getElementById("sidePanel").style.width = "0";
    }
}

function hideChangeImage() {
    document.getElementById("changeImageForm").style.display = "none";
}
function showChangeImage() {
    document.getElementById("changeImageForm").style.display = "block";
}

function showChangePassword() {
    document.getElementById("changePasswordForm").style.display = "block";
}

function hideChangePassword() {
    document.getElementById("changePasswordForm").style.display = "none";
}
