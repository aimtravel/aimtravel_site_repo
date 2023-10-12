var feedbackText1 = document.getElementById('feedback-text-1');
var feedbackText2 = document.getElementById('feedback-text-2');
var feedbackText3 = document.getElementById('feedback-text-3');

var feedbackImg1 = document.getElementById('feedback-img-1');
var feedbackImg2 = document.getElementById('feedback-img-2');
var feedbackImg3 = document.getElementById('feedback-img-3');

var feedbackImgContainer1 = document.getElementById('feedback-img-container1');
var feedbackImgContainer2 = document.getElementById('feedback-img-container2');
var feedbackImgContainer3 = document.getElementById('feedback-img-container3');

var feedbackName1 = document.getElementById('student-name-1')
var feedbackName2 = document.getElementById('student-name-2')
var feedbackName3 = document.getElementById('student-name-3')

var tooltipElement = document.getElementById('feedback-text-container');

var currentFeedbackSlider = feedbackText1;

var prevFeedbackButton = document.querySelector('#prev-feedback-button');
var nextFeedbackButton = document.querySelector('#next-feedback-button');

prevFeedbackButton.addEventListener('click', prevFeedbackHandler);
nextFeedbackButton.addEventListener('click', nextFeedbackHandler);


function prevFeedbackHandler() {
    if (currentFeedbackSlider === feedbackText1) {
        feedbackText1.style.display = 'none';
        feedbackText3.style.display = 'flex';
        feedbackImg1.classList.remove('on-focus-img');
        feedbackImg1.classList.add('background-img');
        feedbackImg3.classList.add('on-focus-img');
        feedbackImg3.classList.remove('background-img');
        feedbackImgContainer1.classList.remove('on-focus-container');
        feedbackImgContainer3.classList.add('on-focus-container');
        feedbackName1.style.display = 'none';
        feedbackName3.style.display = 'block';
        tooltipElement.classList.add('tooltip3');
        tooltipElement.classList.remove('tooltip1');
        currentFeedbackSlider = feedbackText3;
    } else {
        if (currentFeedbackSlider === feedbackText3) {
            feedbackText3.style.display = 'none';
            feedbackText2.style.display = 'flex';
            feedbackImg3.classList.remove('on-focus-img');
            feedbackImg3.classList.add('background-img');
            feedbackImg2.classList.add('on-focus-img');
            feedbackImg2.classList.remove('background-img');
            feedbackImgContainer3.classList.remove('on-focus-container');
            feedbackImgContainer2.classList.add('on-focus-container');
            feedbackName3.style.display = 'none';
            feedbackName2.style.display = 'block';
            tooltipElement.classList.add('tooltip2');
            tooltipElement.classList.remove('tooltip3');
            currentFeedbackSlider = feedbackText2;
        } else {
            if (currentFeedbackSlider === feedbackText2) {
                feedbackText2.style.display = 'none';
                feedbackText1.style.display = 'flex';
                feedbackImg2.classList.remove('on-focus-img');
                feedbackImg2.classList.add('background-img');
                feedbackImg1.classList.add('on-focus-img');
                feedbackImg1.classList.remove('background-img');
                feedbackImgContainer2.classList.remove('on-focus-container');
                feedbackImgContainer1.classList.add('on-focus-container');
                feedbackName2.style.display = 'none';
                feedbackName1.style.display = 'block';
                tooltipElement.classList.add('tooltip1');
                tooltipElement.classList.remove('tooltip2');
                currentFeedbackSlider = feedbackText1;
            }
        }
    }
}


function nextFeedbackHandler() {
    if (currentFeedbackSlider === feedbackText1) {
        feedbackText1.style.display = 'none';
        feedbackText2.style.display = 'flex';
        feedbackImg1.classList.remove('on-focus-img');
        feedbackImg1.classList.add('background-img');
        feedbackImg2.classList.add('on-focus-img');
        feedbackImg2.classList.remove('background-img');
        feedbackImgContainer1.classList.remove('on-focus-container');
        feedbackImgContainer2.classList.add('on-focus-container');
        feedbackName1.style.display = 'none';
        feedbackName2.style.display = 'block';
        tooltipElement.classList.add('tooltip2');
        tooltipElement.classList.remove('tooltip1');
        currentFeedbackSlider = feedbackText2;
    } else {
        if (currentFeedbackSlider === feedbackText2) {
            feedbackText2.style.display = 'none';
            feedbackText3.style.display = 'flex';
            feedbackImg2.classList.remove('on-focus-img');
            feedbackImg2.classList.add('background-img');
            feedbackImg3.classList.add('on-focus-img');
            feedbackImg3.classList.remove('background-img');
            feedbackImgContainer2.classList.remove('on-focus-container');
            feedbackImgContainer3.classList.add('on-focus-container');
            feedbackName2.style.display = 'none';
            feedbackName3.style.display = 'block';
            tooltipElement.classList.add('tooltip3');
            tooltipElement.classList.remove('tooltip2');
            currentFeedbackSlider = feedbackText3;
        } else {
            if (currentFeedbackSlider === feedbackText3) {
                feedbackText3.style.display = 'none';
                feedbackText1.style.display = 'flex';
                feedbackImg3.classList.remove('on-focus-img');
                feedbackImg3.classList.add('background-img');
                feedbackImg1.classList.add('on-focus-img');
                feedbackImg1.classList.remove('background-img');
                feedbackImgContainer3.classList.remove('on-focus-container');
                feedbackImgContainer1.classList.add('on-focus-container');
                feedbackName3.style.display = 'none';
                feedbackName1.style.display = 'block';
                tooltipElement.classList.add('tooltip1');
                tooltipElement.classList.remove('tooltip3');
                currentFeedbackSlider = feedbackText1;
            }
        }
    }
}

setInterval(nextFeedbackHandler, 8000)