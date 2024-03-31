var priceSlider = document.getElementById('price-slider');
var inputLower = document.getElementById('input-lower');
var inputUpper = document.getElementById('input-upper');

noUiSlider.create(priceSlider, {
    start: [0, 100000],
    connect: true,
    range: {
        'min': 0,
        'max': 100000
    },
    format: {
        // Форматирование значения из ползунка в текстовый формат
        to: function (value) {
            return parseInt(value).toFixed(0);
        },
        // Форматирование значения из текстового поля обратно в формат числа
        from: function (value) {
            return parseInt(value);
        }
    }
});

// Обновление текстовых полей при изменении ползунков
priceSlider.noUiSlider.on('update', function (values, handle) {
    var value = values[handle];
    if (handle) {
        inputUpper.value = value;
    } else {
        inputLower.value = value;
    }
    window.vueApp.priceFilter(inputLower.value, inputUpper.value);
});

inputLower.addEventListener('change', function () {
    priceSlider.noUiSlider.set([this.value, null]);
    window.vueApp.priceFilter(this.value, inputUpper.value);
});

// Обработчик ввода в верхнее текстовое поле
inputUpper.addEventListener('change', function () {
    priceSlider.noUiSlider.set([null, this.value]);
    window.vueApp.priceFilter(inputLower.value, this.value);
});