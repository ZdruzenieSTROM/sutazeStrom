let setCountdown = () => {
    let now = new Date().getTime();
    let delta = new Date(countdownTime - now);
    if (delta <= 0) {
        delta = 0;
    }

    let hours = Math.floor((delta % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    let minutes = Math.floor((delta % (1000 * 60 * 60)) / (1000 * 60));
    let seconds = Math.floor((delta % (1000 * 60)) / 1000);
    document.getElementById("countdown").innerHTML = 
            `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

setInterval(() => {
    setCountdown();
}, 1000);