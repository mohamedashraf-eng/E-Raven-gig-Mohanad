// static/js/token_refresh.js

document.addEventListener('DOMContentLoaded', () => {
    const refreshInterval = (settings.SIMPLE_JWT.ACCESS_TOKEN_LIFETIME - 5 * 60) * 1000; // Refresh 5 minutes before expiry

    setInterval(() => {
        fetch('/api/v1/ums/refresh/', {
            method: 'POST',
            credentials: 'include', // Ensure cookies are sent
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        })
        .then(response => {
            if (response.status === 200) {
                console.log('Access token refreshed successfully.');
            } else {
                console.error('Failed to refresh access token.');
                // Optionally, redirect to sign-in page
            }
        })
        .catch(error => {
            console.error('Error during token refresh:', error);
        });
    }, refreshInterval);
});
