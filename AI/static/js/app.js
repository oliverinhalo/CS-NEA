// Generic app JS used by templates

// small helper: POST JSON
async function postJson(url, obj) {
  const res = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(obj)
  });
  return res.json();
}

// When page loads, attach helpers to elements that exist
document.addEventListener('DOMContentLoaded', function(){

  // attach quick geolocation on pages that have the button (studentPage)
  const geoBtn = document.getElementById('btn-send-my-location');
  if (geoBtn) {
    geoBtn.addEventListener('click', function(){
      if (!navigator.geolocation) return alert('Geolocation not supported');
      geoBtn.disabled = true;
      navigator.geolocation.getCurrentPosition(async function(pos){
        try {
          const resp = await postJson('/check_location', { a: pos.coords.latitude, o: pos.coords.longitude });
          if (resp && resp.location) alert('Location matched: ' + resp.location);
          else alert('Location not recognised');
          window.location.reload();
        } catch (e) {
          console.error(e); alert('Network error');
        } finally { geoBtn.disabled = false; }
      }, function(err){ alert('GPS error: ' + err.message); geoBtn.disabled=false; });
    });
  }

  // Small helper for teacherTiles page to wire search (if present)
  const teacherFilterForm = document.getElementById('teacher-filter');
  if (teacherFilterForm) {
    teacherFilterForm.addEventListener('submit', function(e){
      e.preventDefault();
      const params = new URLSearchParams(new FormData(teacherFilterForm));
      window.location.search = params.toString();
    });
  }

});
