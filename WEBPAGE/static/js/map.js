navigator.geolocation.getCurrentPosition(function(pos) {;
    let lat = pos.coords.latitude;
    let lng = pos.coords.longitude;
    let to = window.FLASK_DATA.lesson_location;
    let iframe = document.getElementById("mapFrame");
    iframe.src = `https://www.google.com/maps?saddr=${lat},${lng}&daddr=${to}&dirflg=w&output=embed`; // if change rember ` instead of " or '
});
