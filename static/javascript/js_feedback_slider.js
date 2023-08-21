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

var tooltip = document.querySelector('.tooltip');
var tooltipComputed = getComputedStyle(tooltip, '::before');

var currentFeedbackSlider = feedbackText1;

var prevFeedbackButton = document.querySelector('#prev-feedback-button');
var nextFeedbackButton = document.querySelector('#next-feedback-button');

prevFeedbackButton.addEventListener('click', prevFeedbackHandler);
nextFeedbackButton.addEventListener('click', nextFeedbackHandler);


function prevFeedbackHandler() {
    if (currentFeedbackSlider === feedbackText1) {
        feedbackText1.style.display = 'none';
        feedbackText3.style.display = 'flex';
        feedbackImg1.style.width = '75px';
        feedbackImg1.style.height = '75px';
        feedbackImg3.style.width = '100px';
        feedbackImg3.style.height = '100px';
        feedbackImgContainer1.style.width = '75px';
        feedbackImgContainer1.style.height = '75px';
        feedbackImgContainer3.style.width = '100px';
        feedbackImgContainer3.style.height = '100px';
        feedbackName1.style.display = 'none';
        feedbackName3.style.display = 'block';

        currentFeedbackSlider = feedbackText3;
    } else {
        if (currentFeedbackSlider === feedbackText3) {
            feedbackText3.style.display = 'none';
            feedbackText2.style.display = 'flex';
            feedbackImg3.style.width = '75px';
            feedbackImg3.style.height = '75px';
            feedbackImg2.style.width = '100px';
            feedbackImg2.style.height = '100px';
            feedbackImgContainer3.style.width = '75px';
            feedbackImgContainer3.style.height = '75px';
            feedbackImgContainer2.style.width = '100px';
            feedbackImgContainer2.style.height = '100px';
            feedbackName3.style.display = 'none';
            feedbackName2.style.display = 'block';

            currentFeedbackSlider = feedbackText2;
        } else {
            if (currentFeedbackSlider === feedbackText2) {
                feedbackText2.style.display = 'none';
                feedbackText1.style.display = 'flex';
                feedbackImg2.style.width = '75px';
                feedbackImg2.style.height = '75px';
                feedbackImg1.style.width = '100px';
                feedbackImg1.style.height = '100px';
                feedbackImgContainer2.style.width = '75px';
                feedbackImgContainer2.style.height = '75px';
                feedbackImgContainer1.style.width = '100px';
                feedbackImgContainer1.style.height = '100px';
                feedbackName2.style.display = 'none';
                feedbackName1.style.display = 'block';

                currentFeedbackSlider = feedbackText1;
            }
        }
    }
}


function nextFeedbackHandler() {
    if (currentFeedbackSlider === feedbackText1) {
        feedbackText1.style.display = 'none';
        feedbackText2.style.display = 'flex';
        feedbackImg1.style.width = '75px';
        feedbackImg1.style.height = '75px';
        feedbackImg2.style.width = '100px';
        feedbackImg2.style.height = '100px';
        feedbackImgContainer1.style.width = '75px';
        feedbackImgContainer1.style.height = '75px';
        feedbackImgContainer2.style.width = '100px';
        feedbackImgContainer2.style.height = '100px';
        feedbackName1.style.display = 'none';
        feedbackName2.style.display = 'block';

        currentFeedbackSlider = feedbackText2;
    } else {
        if (currentFeedbackSlider === feedbackText2) {
            feedbackText2.style.display = 'none';
            feedbackText3.style.display = 'flex';
            feedbackImg2.style.width = '75px';
            feedbackImg2.style.height = '75px';
            feedbackImg3.style.width = '100px';
            feedbackImg3.style.height = '100px';
            feedbackImgContainer2.style.width = '75px';
            feedbackImgContainer2.style.height = '75px';
            feedbackImgContainer3.style.width = '100px';
            feedbackImgContainer3.style.height = '100px';
            feedbackName2.style.display = 'none';
            feedbackName3.style.display = 'block';

            currentFeedbackSlider = feedbackText3;
        } else {
            if (currentFeedbackSlider === feedbackText3) {
                feedbackText3.style.display = 'none';
                feedbackText1.style.display = 'flex';
                feedbackImg3.style.width = '75px';
                feedbackImg3.style.height = '75px';
                feedbackImg1.style.width = '100px';
                feedbackImg1.style.height = '100px';
                feedbackImgContainer3.style.width = '75px';
                feedbackImgContainer3.style.height = '75px';
                feedbackImgContainer1.style.width = '100px';
                feedbackImgContainer1.style.height = '100px';
                feedbackName3.style.display = 'none';
                feedbackName1.style.display = 'block';

                currentFeedbackSlider = feedbackText1;
            }
        }
    }
}