document.addEventListener('DOMContentLoaded', () => {
    // Function to fetch the access token lifetime
    const fetchTokenLifetime = () => {
        return fetch('/api/v1/ums/token-lifetime/', {
            credentials: 'include', // Ensure cookies are sent
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch token lifetime.');
            }
            return response.json();
        });
    };

    // Function to refresh the access token
    const refreshAccessToken = () => {
        return fetch('/api/v1/ums/refresh/', {
            method: 'POST',
            credentials: 'include', // Ensure cookies are sent
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({}) // Empty body as refresh token is in cookie
        })
        .then(response => {
            if (response.ok) {
                console.log('Access token refreshed successfully.');
                return response.json();
            } else {
                // Refresh failed; redirect to sign-in page
                console.error('Failed to refresh access token.');
                window.location.href = 'api/v1/pages/sign-in/'; // Adjust URL as needed
                throw new Error('Failed to refresh access token.');
            }
        })
        .catch(error => {
            console.error('Error during token refresh:', error);
        });
    };

    // Function to schedule the token refresh
    const scheduleTokenRefresh = (accessTokenLifetime) => {
        const refreshInterval = (accessTokenLifetime * 1000) - (5 * 60 * 1000); // 5 minutes before expiry

        setTimeout(() => {
            refreshAccessToken()
                .then(() => {
                    // Fetch the token lifetime again and reschedule the next refresh
                    fetchTokenLifetime()
                        .then(data => {
                            scheduleTokenRefresh(data.access_token_lifetime);
                        })
                        .catch(error => {
                            console.error('Error fetching token lifetime after refresh:', error);
                        });
                });
        }, refreshInterval);
    };

    // Initialize the token refresh mechanism
    const initializeTokenRefresh = () => {
        fetchTokenLifetime()
            .then(data => {
                scheduleTokenRefresh(data.access_token_lifetime);
            })
            .catch(error => {
                console.error('Error initializing token refresh:', error);
            });
    };

    // Start the token refresh process
    initializeTokenRefresh();
});
