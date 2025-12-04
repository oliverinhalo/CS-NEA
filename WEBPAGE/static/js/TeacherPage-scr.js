function TileView() {
    var iframe = document.getElementById("teacher_tiles");
    var listView = document.getElementById("teacher_list");
    if (iframe.style.display === "none") {
        tileViewBtn.style.backgroundColor = "rgba(103, 209, 61, 0.94)";
        listViewBtn.style.backgroundColor = "rgba(254, 255, 195, 1)";
        iframe.style.display = "block";
        listView.style.display = "none";
    }
}

function ListView() {
    var iframe = document.getElementById("teacher_list");
    var tileView = document.getElementById("teacher_tiles");
    if (iframe.style.display === "none") {
        tileViewBtn.style.backgroundColor = "rgba(254, 255, 195, 1)";
        listViewBtn.style.backgroundColor = "rgba(103, 209, 61, 0.94)";
        iframe.style.display = "block";
        tileView.style.display = "none";
    }
}