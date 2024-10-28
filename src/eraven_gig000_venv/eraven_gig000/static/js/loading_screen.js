// static/js/loading_screen.js

document.addEventListener("DOMContentLoaded", () => {
    const loadingScreen = document.getElementById('loading-screen');
    const loadingQuote = document.querySelector('.loading-quote');

    const quotes = [
        "Learning never exhausts the mind. – Leonardo da Vinci",
        "The beautiful thing about learning is that nobody can take it away from you. – B.B. King",
        "The expert in anything was once a beginner. – Helen Hayes",
        "You don’t have to be great to start, but you have to start to be great. – Zig Ziglar",
        "Success is the sum of small efforts, repeated day in and day out. – Robert Collier",
        "An investment in knowledge pays the best interest. – Benjamin Franklin",
        "The only limit to our realization of tomorrow is our doubts of today. – Franklin D. Roosevelt",
        "Success is no accident; it’s hard work, perseverance, learning, and sacrifice. – Pele",
        "Continuous improvement is better than delayed perfection. – Mark Twain",
        "The more I learn, the more I realize how much I don’t know. – Albert Einstein",
        "Mistakes are proof that you are trying. – Unknown",
        "Knowledge is power. Knowledge shared is power multiplied. – Robert Noyce",
        "Do not wait to strike till the iron is hot; make it hot by striking. – William Butler Yeats",
        "You are never too old to set another goal or to dream a new dream. – C.S. Lewis",
        "Believe in yourself and all that you are. Know there is something inside you that is greater than any obstacle. – Christian D. Larson",
        "Success usually comes to those who are too busy to be looking for it. – Henry David Thoreau",
        "Don’t let yesterday take up too much of today. – Will Rogers",
        "If you can dream it, you can achieve it. – Zig Ziglar",
        "Your limitation—it’s only your imagination. – Unknown",
        "The secret of getting ahead is getting started. – Mark Twain",
        "Set your goals high, and don’t stop till you get there. – Bo Jackson",
        "Self-education is, I firmly believe, the only kind of education there is. – Isaac Asimov",
        "The capacity to learn is a gift; the ability to learn is a skill; the willingness to learn is a choice. – Brian Herbert",
        "Don’t watch the clock; do what it does. Keep going. – Sam Levenson",
        "Learning is not attained by chance; it must be sought with ardor and diligence. – Abigail Adams",
        "Practice makes progress, not perfection. – Unknown",
        "A person who never made a mistake never tried anything new. – Albert Einstein",
        "Success is the ability to go from failure to failure without losing your enthusiasm. – Winston S. Churchill",
        "The future belongs to those who believe in the beauty of their dreams. – Eleanor Roosevelt",
        "Start where you are. Use what you have. Do what you can. – Arthur Ashe",
        "It’s not what you achieve, it’s what you overcome. That’s what defines your career. – Carlton Fisk",
        "Push yourself, because no one else is going to do it for you. – Unknown",
        "Strive for progress, not perfection. – Unknown",
        "Motivation gets you going, but discipline keeps you growing. – John C. Maxwell",
        "The journey of a thousand miles begins with one step. – Lao Tzu",
        "Success is walking from failure to failure with no loss of enthusiasm. – Winston S. Churchill",
        "If you’re not willing to learn, no one can help you. If you’re determined to learn, no one can stop you. – Zig Ziglar",
        "Knowledge has to be improved, challenged, and increased constantly, or it vanishes. – Peter Drucker",
        "Failure is success in progress. – Albert Einstein",
        "You don’t learn to walk by following rules. You learn by doing, and by falling over. – Richard Branson",
        "Education is the most powerful weapon which you can use to change the world. – Nelson Mandela",
        "Live as if you were to die tomorrow. Learn as if you were to live forever. – Mahatma Gandhi",
        "Formal education will make you a living; self-education will make you a fortune. – Jim Rohn",
        "Develop a passion for learning. If you do, you will never cease to grow. – Anthony J. D’Angelo",
        "Never stop learning, because life never stops teaching. – Unknown",
        "Be curious, not judgmental. – Walt Whitman",
        "Success doesn’t come from what you do occasionally, it comes from what you do consistently. – Marie Forleo",
        "Start each day with a positive thought and a grateful heart. – Roy T. Bennett",
        "The future depends on what you do today. – Mahatma Gandhi",
        "Small daily improvements over time lead to stunning results. – Robin Sharma",
        "Your mind is a powerful thing. When you fill it with positive thoughts, your life will start to change. – Unknown"
    ];

    // Set a random quote
    loadingQuote.textContent = quotes[Math.floor(Math.random() * quotes.length)];

    // Hide the loading screen after the page fully loads
    window.addEventListener("load", () => loadingScreen.classList.add("fade-out"));
});
