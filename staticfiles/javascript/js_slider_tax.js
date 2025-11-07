const sliderOne = document.getElementById('slider-1-tax');
const sliderTwo = document.getElementById('slider-2-tax');
const sliderThree = document.getElementById('slider-3-tax');
const sliderBackground = document.getElementById('background-tax');


let sliderOneOptions = {
    slider: sliderOne,
    background: "linear-gradient(342.11deg, #000000 7.36%, rgba(40, 21, 21, 0) 57.67%), url('../static/img/Ready-stock/WEBP version/hero-banner_2.jpg')"
};
let sliderTwoOptions = {
    slider: sliderTwo,
    background: "linear-gradient(342.11deg, #000000 7.36%, rgba(40, 21, 21, 0) 57.67%), url('../static/img/Ready-stock/WEBP version/hero-banner_3.webp')"
};
let sliderThreeOptions = {
    slider: sliderThree,
    background: "linear-gradient(342.11deg, #000000 7.36%, rgba(40, 21, 21, 0) 57.67%), url('../static/img/Ready-stock/WEBP version/hero-banner_4.webp')"
};


const prevButtonTax = document.querySelector('#prev-button-tax');
const nextButtonTax = document.querySelector('#next-button-tax');

let currentSlider = sliderOne;

prevButtonTax.addEventListener('click', prevHandler);
nextButtonTax.addEventListener('click', nextHandler);


function prevHandler() {

    if (currentSlider === sliderOne) {
        sliderOne.style.display = 'none';
        sliderThree.style.display = 'flex';
        sliderBackground.style.backgroundImage = sliderThreeOptions.background;
        currentSlider = sliderThree;
    } else {
        if (currentSlider === sliderThree) {
            sliderThree.style.display = 'none';
            sliderTwo.style.display = 'flex';
            sliderBackground.style.backgroundImage = sliderTwoOptions.background;
            currentSlider = sliderTwo;
        } else {
            if (currentSlider === sliderTwo) {
                sliderTwo.style.display = 'none';
                sliderOne.style.display = 'flex';
                sliderBackground.style.backgroundImage = sliderOneOptions.background;
                currentSlider = sliderOne;
            }
        }
    }
}

function nextHandler() {

    if (currentSlider === sliderOne) {
        sliderOne.style.display = 'none';
        sliderTwo.style.display = 'flex';
        sliderBackground.style.backgroundImage = sliderTwoOptions.background;
        currentSlider = sliderTwo;
    } else {
        if (currentSlider === sliderTwo) {
            sliderTwo.style.display = 'none';
            sliderThree.style.display = 'flex';
            sliderBackground.style.backgroundImage = sliderThreeOptions.background;
            currentSlider = sliderThree;
        } else {
            if (currentSlider === sliderThree) {
                sliderThree.style.display = 'none';
                sliderOne.style.display = 'flex';
                sliderBackground.style.backgroundImage = sliderOneOptions.background;
                currentSlider = sliderOne;
            }
        }
    }
}

setInterval(nextHandler, 10000)
