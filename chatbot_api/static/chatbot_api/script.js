const chatHistory = document.getElementById('chat-history');
const chatForm = document.getElementById('chat-form');
const promptInput = document.getElementById('prompt-input');

// Weather and Spotify widgets
const weatherIcon = document.getElementById('weather-icon');
const weatherInfo = document.getElementById('weather-info');
const spotifyAlbumArt = document.getElementById('spotify-album-art');
const spotifyTrackInfo = document.getElementById('spotify-track-info');

// Google Calendar widget
const calendarEventsDiv = document.getElementById('calendar-events');

// Fetch initial data
updateWeather();
updateNowPlaying();
fetchCalendarEvents(); // Call on page load

// Add initial greeting
appendMessage('bot', 'Hello Kuldeep! What\'s up?'); // Added this line

// Refresh data every 30 seconds
setInterval(updateWeather, 30000);
setInterval(updateNowPlaying, 30000);
setInterval(fetchCalendarEvents, 60000); // Refresh calendar events every 60 seconds

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const prompt = promptInput.value;
    promptInput.value = '';

    appendMessage('user', prompt);

    const response = await fetch('/chat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ prompt: prompt }),
    });

    const data = await response.json();
    appendMessage('bot', data.response);
});

function appendMessage(sender, message) {
    const messageElement = document.createElement('div');
    messageElement.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    messageElement.innerText = message;
    chatHistory.appendChild(messageElement);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

async function updateWeather() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(async (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            // Updated URL
            const response = await fetch(`/api/weather/now/?lat=${lat}&lon=${lon}`);
            const data = await response.json();

            if (data.error) {
                weatherInfo.innerHTML = `<p>${data.error}</p>`;
                return;
            }

            weatherIcon.innerHTML = `<img src="http://openweathermap.org/img/wn/${data.icon}@2x.png" alt="Weather icon">`;
            weatherInfo.innerHTML = `
                <p>${data.location}</p>
                <p>${data.temperature_celsius}°C, ${data.condition}</p>
            `;
        }, (error) => {
            console.error("Error getting location:", error);
            // Fallback to default location if geolocation fails
            fetchDefaultWeather();
        });
    } else {
        console.log("Geolocation is not supported by this browser.");
        // Fallback to default location if geolocation is not supported
        fetchDefaultWeather();
    }
}

async function fetchDefaultWeather() {
    // Updated URL
    const response = await fetch('/api/weather/now/');
    const data = await response.json();

    if (data.error) {
        weatherInfo.innerHTML = `<p>${data.error}</p>`;
        return;
    }

    weatherIcon.innerHTML = `<img src="http://openweathermap.org/img/wn/${data.icon}@2x.png" alt="Weather icon">`;
    weatherInfo.innerHTML = `
        <p>${data.location}</p>
        <p>${data.temperature_celsius}°C, ${data.condition}</p>
    `;
}

async function updateNowPlaying() {
    // Updated URL
    const response = await fetch('/api/spotify/now-playing/');
    if (response.status === 204) {
        spotifyTrackInfo.innerHTML = `<p>Nothing playing on Spotify.</p>`;
        spotifyAlbumArt.innerHTML = '';
        return;
    }
    const data = await response.json();

    if (data.is_playing) {
        spotifyAlbumArt.innerHTML = `<img src="${data.album_art}" alt="Album art">`;
        spotifyTrackInfo.innerHTML = `
            <p><strong>${data.name}</strong></p>
            <p>${data.artist}</p>
        `;
    } else {
        spotifyTrackInfo.innerHTML = `<p>Nothing playing on Spotify.</p>`;
        spotifyAlbumArt.innerHTML = '';
    }
}

async function fetchCalendarEvents() {
    try {
        // Updated URL
        const response = await fetch('/api/google_calendar/events/');
        const data = await response.json();

        if (data.error) {
            calendarEventsDiv.innerHTML = `<p>Error fetching calendar events: ${data.error}</p>`;
            return;
        }

        if (data.events) {
            const eventsHtml = data.events.split('\n').map(event => `<p>${event}</p>`).join('');
            calendarEventsDiv.innerHTML = eventsHtml;
        } else {
            calendarEventsDiv.innerHTML = `<p>No upcoming events found.</p>`;
        }

    } catch (error) {
        console.error("Error fetching calendar events:", error);
        calendarEventsDiv.innerHTML = `<p>Error fetching calendar events.</p>`;
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
            }
    }
    return cookieValue;
}