function Panel() {
    if (document.getElementById("sidePanel").style.width === "0px") {
        document.getElementById("sidePanel").style.width = "300px";
    } else {
        document.getElementById("sidePanel").style.width = "0";
    }
}
