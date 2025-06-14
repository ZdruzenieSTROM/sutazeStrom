function autoScroll() {
    const tableContainer = document.getElementById("table-container")
    const scrollStep = tableContainer.clientHeight - 100;
    const pauseDuration = 15000;

    function scroll() {
        if (tableContainer.scrollTop + tableContainer.clientHeight >= tableContainer.scrollHeight) {
            location.reload(); // Refetches the results data and scrolls to the top as a side effect
        }
        
        tableContainer.scrollBy({top: scrollStep, behavior: 'smooth'});
        setTimeout(() => {
            scroll();
        }, pauseDuration);
    }

    setTimeout(() => {
        scroll();
    }, pauseDuration);
}