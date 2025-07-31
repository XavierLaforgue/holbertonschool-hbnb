const my_url = "http://localhost:5000/api/v1"

document.addEventListener('DOMContentLoaded', async () => {
  const token = await checkAuthentication();
  checkLogin();
  checkLogout();
  if (window.location.pathname.endsWith('place.html') || window.location.pathname === '/places' || window.location.pathname === '/place.html' || window.location.pathname.startsWith('/places/')) {
  /* Only show review form when authenticated */
    displayReviewForm(token);
  }
});

async function loginUser(email, password) {
  const response = await fetch(`${my_url}/auth/login`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email, password })
    }
  );
  if (response.ok) {
    const data = await response.json();
    document.cookie = `token=${data.access_token}; path=/`;
    window.location.href = '/';
  } else {
    const errorData = await response.json();
    if (errorData.error) {
      errorMsg = errorData.error;
      alert(`Login failed: ERROR ${response.status} ${response.statusText}: ${errorMsg}`);
    } else {
    alert(`Login failed: ERROR ${response.status} ${response.statusText}`);
    }
  }
}

function checkLogin() {
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      loginUser(event.target[0].value, event.target[1].value)
    });
  }
}

/* log out */

function logout() {
  document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
  // window.location.href = "login.html"; // Redirect to login page
}

function checkLogout() {
  const logoutBtn = document.getElementById('logout-link');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', logout);
  }
}

/* Check authentication */
async function isTokenValid(token) {
  const response = await fetch(`${my_url}/users/me`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  if (!response.ok) {
    return false;
  };
  return true;
}

async function checkAuthentication() {
  const token = getCookie('token');
  let validToken;
  if (token) {
    validToken = await isTokenValid(token);
  } else {
    validToken = false;
  }
  const loginLink = document.getElementById('login-link');
  const logoutLink = document.getElementById('logout-link');
  if (token == null || !validToken) { // if null or undefined
      loginLink.style.display = 'flex';
      logoutLink.style.display = 'none';
  } else {
    loginLink.style.display = 'none';
    logoutLink.style.display = 'flex';
    // Fetch places data if the user is authenticated
    // fetchPlaces(token);
  }
  /* Only fetch places if on index.html */
  if (window.location.pathname.endsWith('index.html') || window.location.pathname === '/' || window.location.pathname === '/index.html') {
    fetchPlaces(token);
  }
  return token;
}

function getCookie(name) {
  // Function to get a cookie value by its name
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) 
    return parts.pop().split(';').shift();
  return null;
}

async function fetchPlaces() {
  // Make a GET request to fetch places data
  const response = await fetch(`${my_url}/places`, {
  method: 'GET',
  });
  // Handle the response and pass the data to displayPlaces function
  if (response.ok) {
    const places = await response.json();
    displayPlaces(places);
  } else {
    const errorData = await response.json();
    if (errorData.error) {
      errorMsg = errorData.error;
      alert(`Retrieval of places failed: ERROR ${response.status} ${response.statusText}: ${errorMsg}`);
    } else {
      alert(`Retrieval of places failed: ERROR ${response.status} ${response.statusText}`)
    }
  }
}

async function getLocationInfo(lat, lon) {
  // If lat/lon are missing, not finite, or both are 0, return Unknown
  // location
  if (
    lat === undefined || lon === undefined ||
    lat === null || lon === null ||
    lat === '' || lon === '' ||
    !isFinite(Number(lat)) || !isFinite(Number(lon)) ||
    (Number(lat) === 0 && Number(lon) === 0)
  ) {
    return { city: 'Unknown', country: 'Unknown' };
  }
  const url = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lon}`;
  const response = await fetch(url);
  if (response.ok) {
    const data = await response.json();
    return {
      city: data.address.city || data.address.town || data.address.village || data.address.state || 'Unknown location',
      country: data.address.country || 'Unknown country'
    };
  }
  return { city: 'Unknown location', country: '' };
}

// function placeDetails(place) {
//   const placeSection = document.getElementById('place-details');
//   placeSection.innerHTML = `
//       <h2>${place.title}</h2>
//       <div id="place-info">
//         <div class="place-meta">
//             <span class="host"><b>Host:</b>${place.owner.first_name} ${place.owner.last_name}</span>
//             <br>
//             <span class="price"><b>Price:</b> ${place.price} €/night</span>
//         </div>
//         <section class="place-description">
//             <h3>Description</h3>
//             <p>${place.description}</p>
//         </section>
//         <section class="Amenities">
//             <h3>Features</h3>
//             <ul class="features-list">
//                 <li>WiFi</li>
//                 <li>Pool</li>
//                 <li>Air Conditioning</li>
//             </ul>
//         </section>
//       </div>
//     `;
//     window.location.href = `/places/${place.id}`;
// }

// async function fetchPlaceById(placeId) {
//   // Make a GET request to fetch places data
//   const response = await fetch(`${my_url}/places/${placeId}`, {
//   method: 'GET',
//   });
//   // Handle the response and pass the data to displayPlaces function
//   if (response.ok) {
//     const placeData = await response.json();
//     // placeDetails(placeData);
//   } else {
//     const errorData = await response.json();
//     if (errorData.error) {
//       errorMsg = errorData.error;
//       alert(`Retrieval of place details failed: ERROR ${response.status} ${response.statusText}: ${errorMsg}`);
//     } else {
//       alert(`Retrieval of place details failed: ERROR ${response.status} ${response.statusText}`)
//     }
//   }
// }

// function btnPlaceListener(article) {
//   // Add an event listener to the buttons
//   const btn = article.querySelector('.details-button');
//   btn.addEventListener('click', event => {
//     event.preventDefault();
//     const placeId = btn.getAttribute('details-place-id');
    // window.location.href = `/places/${placeId}`;
    // fetchPlaceById(placeId);
    // fetch(`${my_url}/places/${placeId}`)
    // .then(response => {
    //   response.json();
    //   console.log(response);
    // })
    // .then(data => {
    //   placeDetails(data);
    //   window.location.href = '/place'; // Redirect after fetch
    // }).catch(error => {
    //   alert(`Place details retrieval failed: ERROR ${error.status} ${error.statusText}`);
    // });
//   })
// }

function displayPlaces(places) {
  // Clear the current content of the places list
  const placesList = document.getElementById('places-list');
  placesList.innerHTML = '';
  // Iterate over the places data
  places.forEach((place, idx) => {
    // (async () => {
    // For each place, create a div element and set its content
    const article = document.createElement('article');
    article.className = 'place-card';
    article.setAttribute('place-price', place.price);
    article.style.animationDelay = `${idx * 0.05}s`; // Staggered delay
    // Always get city and country from lat/lon (handles invalid/missing too)
    // let location = await getLocationInfo(place.latitude,
    // place.longitude);
    const locationSpanId = `location-${place.id}`;
    article.innerHTML = `
      <h2>${place.title}</h2>
      <section class="place-meta">
          <p>Price per night: ${place.price} €
          <br>
          Host: ${place.owner.first_name} ${place.owner.last_name}
          <br>
          Location: <span id="${locationSpanId}">Loading...</span></p>
      </section>
      <section class="place-description">
          <p>${place.description ? place.description : ""}</p>
      </section>
      <a href="/places/${place.id}" class="details-button" details-place-id="${place.id}">View details</a>
    `;
    // ${typeof placeUrl !== 'undefined' ? placeUrl : '/place'}" 
    // Append the created element to the places list
    placesList.appendChild(article);
    // btnPlaceListener(article);
    // Fetch location asynchronously and update the span
    getLocationInfo(place.latitude, place.longitude).then(location => {
      const locationSpan = document.getElementById(locationSpanId);
      if (locationSpan) {
        locationSpan.textContent = `${location.city}, ${location.country}`;
      }
    });
    // })()
  });
}

const priceFilter = document.getElementById('price-filter');
if (priceFilter) {
  priceFilter.addEventListener('change', (event) => {
    // Get the selected price value
    const maxPrice = event.target.value;
    // Iterate over the places and show/hide them based on the selected price
    const placeCards = document.querySelectorAll('.place-card');
    placeCards.forEach(card => {
      if (maxPrice === "null" || maxPrice === "") {
        card.style.display = 'flex';
      } else {
        const price = parseFloat(card.getAttribute('place-price'));
        if (price > maxPrice) {
          card.style.display = 'none';
        } else {
          card.style.display = 'flex';
        }
      }
    });
  });
}

async function submitReview(token, text, rating, place_id) {
  if (!(await isTokenValid(token))) {
    alert('Token is no longer valid');
    window.location.href = '/login';
  }
  const response = await fetch(`${my_url}/reviews/`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
    },
    credentials: 'include',
    body: JSON.stringify({ text, rating, place_id })
    }
  );
  if (response.ok) {
    const data = await response.json();
    alert('Review submitted successfully');
    window.location.reload();
  } else {
    const errorData = await response.json();
    console.log(errorData);
    if (errorData.error) {
      errorMsg = errorData.error;
      alert(`Review submission failed: ERROR ${response.status} ${response.statusText}: ${errorMsg}`);
    } else if (errorData.msg) {
      errorMsg = errorData.msg;
      alert(`Review submission failed: ERROR ${response.status} ${response.statusText}: ${errorMsg}`);
    } else {
      alert(`Review submission failed: ERROR ${response.status} ${response.statusText}`);
    }
  }
}

function displayReviewForm(token) {
  const addReviewSection = document.getElementById('add-review');
  if (addReviewSection && token) {
    addReviewSection.style.display = 'block';
    const addReviewForm = document.getElementById('review-form');
    addReviewForm.addEventListener('submit', async (event) => {
      event.preventDefault();
      const reviewText = addReviewForm.querySelector("#review-text").value;
      const rating = parseFloat(addReviewForm.querySelector("#rating").value);
      const place_id = addReviewForm.getAttribute("data-place-id");
      submitReview(token, reviewText, rating, place_id);
    })
  } else {
    addReviewSection.style.display = 'none';
    console.log('did\'nt find review form or token');
  }
}

// function displayReviewForm(token) {
//   const addReviewForm = document.getElementById('add-review');
//   if (addReviewForm && token) {
//     addReviewForm.style.display = 'block';
//     const rating = addReviewForm.querySelector("#rating");
//     if (rating) {
//       rating.addEventListener('change', (event) => {
//         const givenRating = event.target.value;
//         console.log(givenRating);
//       })
//     }
//     const ReviewText = addReviewForm.querySelector("#review-text");
//     if (ReviewText) {
//       ReviewText.addEventListener('input', (event) => {
//         const givenReviewText = event.target.value;
//         console.log(givenReviewText);
//       })
//     }
//     const submitButton = addReviewForm.querySelector("#submit-review-btn");
//     if (submitButton) {
//       const place_id = submitButton.getAttribute("data-place-id");
//       submitButton.addEventListener('click', async (event) => {
//         event.preventDefault();
//         const reviewText = addReviewForm.querySelector("#review-text").value;
//         const rating = addReviewForm.querySelector("#rating").value;
//         submitReview(token, reviewText, rating, place_id);
//       })
//     }
//   } else {
//     addReviewForm.style.display = 'none';
//     console.log('did\'nt find review form or token');
//   }
// }

