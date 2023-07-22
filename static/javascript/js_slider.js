var mainSlider = document.getElementById('main-slider');
var sliderOne = document.getElementById('slider-1');
var sliderTwo = document.getElementById('slider-2');
var sliderThree = document.getElementById('slider-3');
var sliderBackground = document.getElementById('background');

var mainSliderOptions = { slider: mainSlider, background: "linear-gradient(342.11deg, #000000 7.36%, rgba(40, 21, 21, 0) 57.67%), url('../static/img/Ready-stock/WEBP version/hero-banner_1.webp')" };
var sliderOneOptions = { slider: sliderOne, background: "linear-gradient(342.11deg, #000000 7.36%, rgba(40, 21, 21, 0) 57.67%), url('../static/img/Ready-stock/WEBP version/hero-banner_2.jpg')" };
var sliderTwoOptions = { slider: sliderTwo, background: "linear-gradient(342.11deg, #000000 7.36%, rgba(40, 21, 21, 0) 57.67%), url('../static/img/Ready-stock/WEBP version/hero-banner_3.webp')" };
var sliderThreeOptions = { slider: sliderThree, background: "linear-gradient(342.11deg, #000000 7.36%, rgba(40, 21, 21, 0) 57.67%), url('../static/img/Ready-stock/WEBP version/hero-banner_4.webp')" };

var prevButton = document.querySelector('#prev-button');
var nextButton = document.querySelector('#next-button');

var currentSlider = mainSlider;

prevButton.addEventListener('click', prevHandler);
nextButton.addEventListener('click', nextHandler);


function prevHandler() {
  if (currentSlider === mainSlider) {
    mainSlider.style.display = 'none';
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
      } else {
        if (currentSlider === sliderOne) {
          sliderOne.style.display = 'none';
          mainSlider.style.display = 'flex';
          sliderBackground.style.backgroundImage = mainSliderOptions.background;
          currentSlider = mainSlider;
        }
      }
    }
  }
};

function nextHandler() {
  if (currentSlider === mainSlider) {
    mainSlider.style.display = 'none';
    sliderOne.style.display = 'flex';
    sliderBackground.style.backgroundImage = sliderOneOptions.background;
    currentSlider = sliderOne;
  } else {
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
          mainSlider.style.display = 'flex';
          sliderBackground.style.backgroundImage = mainSliderOptions.background;
          currentSlider = mainSlider;
        }
      }
    }
  }
};

// setInterval(nextHandler, 10000)
