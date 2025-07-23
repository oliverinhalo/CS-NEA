function success(pos) {
  cwd = pos.coords;

  fetch("/check_location", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify({
      a: cwd.latitude,
      o: cwd.longitude,
    }),
  })
}

function error(err) {
  console.warn(`ERROR(${err.code}): ${err.message}`);
}

function getLocation() {
    navigator.geolocation.watchPosition(success, error, {
    enableHighAccuracy: true,
    timeout: 60000,
    });
}
getLocation();