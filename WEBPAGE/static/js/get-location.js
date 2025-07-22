function success(pos) {
  cwd = pos.coords;

  fetch("/check_location", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify({
      latitude: cwd.latitude,
      longitude: cwd.longitude,
    }),
  });
}

function error(err) {
  console.warn(`ERROR(${err.code}): ${err.message}`);
}


navigator.geolocation.watchPosition(success, error, {
  enableHighAccuracy: true,
  maximumAge: 0,
  timeout: 10000,
});