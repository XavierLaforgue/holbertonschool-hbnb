/* 
  User login
*/
const my_url = "http://localhost:5000/api/v1"

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
    window.location.href = 'index.html';
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

function checkAuthentication() {
  const token = getCookie('token');
  const loginLink = document.getElementById('login-link');
  const logoutLink = document.getElementById('logout-link');
  if (token == null) { // if null or undefined
      loginLink.style.display = 'block';
      logoutLink.style.display = 'none';
  } else {
    loginLink.style.display = 'none';
    logoutLink.style.display = 'block';
    // Fetch places data if the user is authenticated
    // fetchPlaces(token);
  }
  /* Only fetch places if on index.html */
  if (window.location.pathname.endsWith('index.html') || window.location.pathname === '/' || window.location.pathname === '/index.html') {
    fetchPlaces(token);
  }
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

function displayPlaces(places) {
    // Clear the current content of the places list
    // Iterate over the places data
    // For each place, create a div element and set its content
    // Append the created element to the places list
}

document.addEventListener('DOMContentLoaded', () => {
  checkAuthentication();
  checkLogin();
  checkLogout();
});
