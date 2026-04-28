(function () {
    // Use camelCase for standard JS methods
    const quantityContainer = document.querySelector(".quantity");
    const minusBtn = quantityContainer.querySelector(".minus");
    const plusBtn = quantityContainer.querySelector(".plus");
    const inputBox = quantityContainer.querySelector(".input-box");

    updateButtonStates();

    quantityContainer.addEventListener("click", handleButtonClick);
    inputBox.addEventListener("input", handleQuantityChange);

    function updateButtonStates() {
        const value = parseInt(inputBox.value);
        const max = parseInt(inputBox.max) || Infinity; // Fallback if no max is set
        minusBtn.disabled = value <= 1;
        plusBtn.disabled = value >= max;
    }

    function handleButtonClick(event) {
        if (event.target.classList.contains("minus")) {
            decreaseValue();
        } else if (event.target.classList.contains("plus")) {
            increaseValue();
        }
    }

    function decreaseValue() {
        let value = parseInt(inputBox.value);
        value = isNaN(value) ? 1 : Math.max(value - 1, 1);
        inputBox.value = value;
        updateButtonStates();
        handleQuantityChange();
    }

    // Fixed the "fuction" typo here
    function increaseValue() {
        let value = parseInt(inputBox.value);
        const max = parseInt(inputBox.max) || Infinity;
        value = isNaN(value) ? 1 : Math.min(value + 1, max);
        inputBox.value = value;
        updateButtonStates();
        handleQuantityChange();
    }

    function handleQuantityChange() {
        let value = parseInt(inputBox.value);
        if (isNaN(value) || value < 1) value = 1;

        // Ensure the input doesn't exceed max manually
        const max = parseInt(inputBox.max);
        if (max && value > max) value = max;

        inputBox.value = value;
        updateButtonStates();
        console.log("Quantity changed:", value);
    }
})();
