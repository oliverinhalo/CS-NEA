let idleTime;
let idleLimit = 60000; // 60s idle
let idleActive = false;
let cards, currentIndex = 0;
let cycleInterval;

function resetTimer() {
    clearTimeout(idleTime);
    if (idleActive) {
        stopIdleCycle();
    }
    idleTime = setTimeout(startIdleCycle, idleLimit);
}

function startIdleCycle() {
    cards = document.querySelectorAll(".cards .card"); 
    if (cards.length === 0) return;

    idleActive = true;
    currentIndex = 0;

    let columns = 3; // number of columns in your grid

    cycleInterval = setInterval(() => {
        // Reset all cards
        cards.forEach(card => {
            card.style.transition = "transform 0.5s";
            card.style.transform = "scale(1)";
            card.style.zIndex = "1";
        });

        // Current card
        let card = cards[currentIndex];
        card.style.transition = "transform 0.5s";

        let col = currentIndex % columns; // column index
        console.log(col);

        let xShift = "0%";
        if (col === 0) {
            xShift = "50%";   // shift right
        } else if (col === 2) {
            xShift = "-50%";  // shift left
        }

        // Use backticks for template literals!
        card.style.transform = `scale(2) translateX(${xShift})`;
        card.style.zIndex = "10000";

        card.scrollIntoView({
            behavior: "smooth",
            block: "center",
            inline: "center"
        });

        // Next
        currentIndex = (currentIndex + 1) % cards.length;
    }, 5000); // 5 seconds ms
}

function stopIdleCycle() {
    idleActive = false;
    clearInterval(cycleInterval);
    // Reset
    document.querySelectorAll(".cards .card")
        .forEach(card => card.style.transform = "scale(1)");
}

// activity
window.onload = resetTimer;
window.onmousemove = resetTimer;
window.onclick = resetTimer;