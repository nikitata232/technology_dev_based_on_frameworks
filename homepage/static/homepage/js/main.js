// Небольшое клиентское поведение интерфейса КиноПлан.

// Текущий год в подвале страницы.
const yearElement = document.getElementById("current-year");

if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
}

// Кнопка «Скрыть отменённые» на странице графика съёмок.
const toggleButton = document.getElementById("toggle-cancelled");

if (toggleButton) {
    toggleButton.addEventListener("click", () => {
        const rows = document.querySelectorAll("tr.kp-cancelled");
        const hide = toggleButton.dataset.hidden !== "true";
        rows.forEach((row) => {
            row.hidden = hide;
        });
        toggleButton.dataset.hidden = String(hide);
        toggleButton.textContent = hide
            ? "Показать отменённые"
            : "Скрыть отменённые";
    });
}
