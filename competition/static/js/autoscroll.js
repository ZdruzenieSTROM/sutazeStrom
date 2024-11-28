function autoScroll() {
    let scrollStep = 2;
    let pauseDuration = 4000;
    let isPaused = false;

    function scroll() {
        if (isPaused) return;

        window.scrollTo(0, window.scrollY + scrollStep);

        if (window.scrollY + window.innerHeight >= document.body.scrollHeight || window.scrollY <= 0) {
            scrollStep *= -1;

            isPaused = true;
                setTimeout(() => {
                isPaused = false;
                requestAnimationFrame(scroll);
            }, pauseDuration);
            return;
        }

        requestAnimationFrame(scroll);
    }

    scroll();
}