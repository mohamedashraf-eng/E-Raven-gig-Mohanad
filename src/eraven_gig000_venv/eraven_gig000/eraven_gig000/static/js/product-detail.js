// static/js/product-detail.js

function changeMainImage(imageUrl) {
    const mainImage = document.querySelector('.product-main-image');
    mainImage.src = imageUrl;
}

document.addEventListener('DOMContentLoaded', () => {
    const thumbnails = document.querySelectorAll('.thumbnail-image');
    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', (e) => {
            e.preventDefault();
            const imageUrl = thumbnail.getAttribute('src');
            changeMainImage(imageUrl);
        });
    });
});
