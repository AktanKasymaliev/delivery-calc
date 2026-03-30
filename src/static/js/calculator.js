document.addEventListener("DOMContentLoaded", function () {
    var API_BASE = "/calculator/api";

    var fromCitySelect = document.getElementById("from-city");
    var toCitySelect = document.getElementById("to-city");
    var weightInput = document.getElementById("weight");
    var volumeInput = document.getElementById("volume");
    var form = document.getElementById("calculator-form");
    var errorMessage = document.getElementById("error-message");
    var resultSection = document.getElementById("result-section");
    var calculateBtn = document.getElementById("calculate-btn");

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove("hidden");
        resultSection.classList.add("hidden");
    }

    function hideError() {
        errorMessage.classList.add("hidden");
    }

    function showResult(data) {
        hideError();
        document.getElementById("result-total").textContent =
            formatPrice(data.total_price, data.currency);
        document.getElementById("result-price-per-kg").textContent =
            formatPrice(data.price_per_kg, data.currency) + " / кг";
        document.getElementById("result-delivery-time").textContent =
            data.delivery_time_from + "\u2013" + data.delivery_time_to + " дней";
        resultSection.classList.remove("hidden");
    }

    function formatPrice(value, currency) {
        var num = parseFloat(value);
        var symbols = { USD: "$", EUR: "\u20AC", RUB: "\u20BD", KGS: "сом" };
        var symbol = symbols[currency] || currency;
        return num.toLocaleString("ru-RU", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " " + symbol;
    }

    function validateForm() {
        if (!fromCitySelect.value) {
            showError("Выберите город отправки");
            return false;
        }
        if (!toCitySelect.value) {
            showError("Выберите город доставки");
            return false;
        }
        if (fromCitySelect.value === toCitySelect.value) {
            showError("Город отправки и доставки не могут совпадать");
            return false;
        }
        var weight = parseFloat(weightInput.value);
        if (!weight || weight <= 0) {
            showError("Введите вес");
            return false;
        }
        var volume = parseFloat(volumeInput.value);
        if (!volume || volume <= 0) {
            showError("Введите объём");
            return false;
        }
        return true;
    }

    function loadCities() {
        fetch(API_BASE + "/cities/")
            .then(function (response) { return response.json(); })
            .then(function (result) {
                if (!result.success) return;
                var cities = result.data;
                var optionsHtml = '<option value="">Выберите город</option>';
                cities.forEach(function (city) {
                    optionsHtml +=
                        '<option value="' + city.id + '">' +
                        city.name + ", " + city.country +
                        "</option>";
                });
                fromCitySelect.innerHTML = optionsHtml;
                toCitySelect.innerHTML = optionsHtml;
            })
            .catch(function () {
                showError("Не удалось загрузить список городов");
            });
    }

    function submitCalculation() {
        if (!validateForm()) return;

        hideError();
        calculateBtn.disabled = true;
        calculateBtn.textContent = "Расчёт...";

        var payload = {
            from_city_id: parseInt(fromCitySelect.value, 10),
            to_city_id: parseInt(toCitySelect.value, 10),
            weight: parseFloat(weightInput.value),
            volume: parseFloat(volumeInput.value),
        };

        fetch(API_BASE + "/calculate/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        })
            .then(function (response) { return response.json(); })
            .then(function (result) {
                if (result.success) {
                    showResult(result.data);
                } else {
                    showError(result.message);
                }
            })
            .catch(function () {
                showError("Ошибка сети. Попробуйте позже");
            })
            .finally(function () {
                calculateBtn.disabled = false;
                calculateBtn.textContent = "Рассчитать";
            });
    }

    form.addEventListener("submit", function (e) {
        e.preventDefault();
        submitCalculation();
    });

    loadCities();
});
