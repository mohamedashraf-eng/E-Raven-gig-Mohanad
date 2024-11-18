// static/js/message_dismiss.js

document.addEventListener('DOMContentLoaded', () => {
    // Function to handle dismissal
    const dismissMessage = (message) => {
        message.style.animation = 'fadeOut 0.5s forwards';
        message.addEventListener('animationend', () => {
            message.remove();
        });
    };

    // Handle manual dismissal of messages
    const closeButtons = document.querySelectorAll('.close-btn');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const message = btn.parentElement;
            dismissMessage(message);
        });

        // Handle keyboard events for accessibility (Enter and Space keys)
        btn.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const message = btn.parentElement;
                dismissMessage(message);
            }
        });
    });

    // Handle automatic dismissal of messages after 5 seconds
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        setTimeout(() => {
            dismissMessage(message);
        }, 5000); // 5000 milliseconds = 5 seconds
    });
});
