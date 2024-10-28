document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/v1/ums/token-lifetime/')
        .then(response => response.json())
        .then(data => {
            const accessTokenLifetime = data.access_token_lifetime * 1000;
            const refreshInterval = accessTokenLifetime - 5 * 60 * 1000; // Refresh 5 minutes before expiry

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
        })
        .catch(error => {
            console.error('Error fetching token lifetime:', error);
        });
});
