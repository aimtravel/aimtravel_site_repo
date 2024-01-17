const nextButton = document.querySelectorAll('.next-btn');
const previousButton = document.querySelectorAll('.previous-btn');

const personalInfo = document.querySelector("#tax-navigation #personal-info");
const travelInfo = document.querySelector("#tax-navigation #travel-info");
const employerInfo = document.querySelector("#tax-navigation #employer-info");
const bankInfo = document.querySelector("#tax-navigation #bank-info");
const attachments = document.querySelector("#tax-navigation #attachments");

const personalInfoContent = document.querySelector(".taxes-section form#norm .personal-info")
const travelInfoContent = document.querySelector(".taxes-section form#norm .travel-info")
const employerInfoContent = document.querySelector(".taxes-section form#norm .employer-info")
const bankInfoContent = document.querySelector(".taxes-section form#norm .bank-info")
const attachmentsContent = document.querySelector(".taxes-section form#norm .attachments")

let currentTab = personalInfo

function personalInfoHandler() {
    personalInfo.style.fontWeight = '700'
    personalInfo.style.color = 'black'
    personalInfoContent.style.display = 'flex'
    currentTab = personalInfo

    travelInfo.style.fontWeight = '400'
    travelInfo.style.color = 'gray'
    travelInfoContent.style.display = 'none'
    employerInfo.style.fontWeight = '400'
    employerInfo.style.color = 'gray'
    employerInfoContent.style.display = 'none'
    bankInfo.style.fontWeight = '400'
    bankInfo.style.color = 'gray'
    bankInfoContent.style.display = 'none'
    attachments.style.fontWeight = '400'
    attachments.style.color = 'gray'
    attachmentsContent.style.display = 'none'
}

function travelInfoHandler() {
    travelInfo.style.fontWeight = '700'
    travelInfo.style.color = 'black'
    travelInfoContent.style.display = 'flex'
    currentTab = travelInfo

    personalInfo.style.fontWeight = '400'
    personalInfo.style.color = 'gray'
    personalInfoContent.style.display = 'none'
    employerInfo.style.fontWeight = '400'
    employerInfo.style.color = 'gray'
    employerInfoContent.style.display = 'none'
    bankInfo.style.fontWeight = '400'
    bankInfo.style.color = 'gray'
    bankInfoContent.style.display = 'none'
    attachments.style.fontWeight = '400'
    attachments.style.color = 'gray'
    attachmentsContent.style.display = 'none'
}

function employerInfoHandler() {
    employerInfo.style.fontWeight = '700'
    employerInfo.style.color = 'black'
    employerInfoContent.style.display = 'flex'
    currentTab = employerInfo

    personalInfo.style.fontWeight = '400'
    personalInfo.style.color = 'gray'
    personalInfoContent.style.display = 'none'
    travelInfo.style.fontWeight = '400'
    travelInfo.style.color = 'gray'
    travelInfoContent.style.display = 'none'
    bankInfo.style.fontWeight = '400'
    bankInfo.style.color = 'gray'
    bankInfoContent.style.display = 'none'
    attachments.style.fontWeight = '400'
    attachments.style.color = 'gray'
    attachmentsContent.style.display = 'none'
}

function bankInfoHandler() {
    bankInfo.style.fontWeight = '700'
    bankInfo.style.color = 'black'
    bankInfoContent.style.display = 'flex'
    currentTab = bankInfo

    personalInfo.style.fontWeight = '400'
    personalInfo.style.color = 'gray'
    personalInfoContent.style.display = 'none'
    travelInfo.style.fontWeight = '400'
    travelInfo.style.color = 'gray'
    travelInfoContent.style.display = 'none'
    employerInfo.style.fontWeight = '400'
    employerInfo.style.color = 'gray'
    employerInfoContent.style.display = 'none'
    attachments.style.fontWeight = '400'
    attachments.style.color = 'gray'
    attachmentsContent.style.display = 'none'
}

function attachmentsHandler() {
    attachments.style.fontWeight = '700'
    attachments.style.color = 'black'
    attachmentsContent.style.display = 'flex'
    currentTab = attachments

    personalInfo.style.fontWeight = '400'
    personalInfo.style.color = 'gray'
    personalInfoContent.style.display = 'none'
    travelInfo.style.fontWeight = '400'
    travelInfo.style.color = 'gray'
    travelInfoContent.style.display = 'none'
    employerInfo.style.fontWeight = '400'
    employerInfo.style.color = 'gray'
    employerInfoContent.style.display = 'none'
    bankInfo.style.fontWeight = '400'
    bankInfo.style.color = 'gray'
    bankInfoContent.style.display = 'none'
}

function nextButtonHandler() {
    if (currentTab === personalInfo) {
        travelInfoHandler()
    } else if (currentTab === travelInfo) {
        employerInfoHandler()
    } else if (currentTab === employerInfo) {
        bankInfoHandler()
    } else if (currentTab === bankInfo) {
        attachmentsHandler()
    } else if (currentTab === attachments) {
        personalInfoHandler()
    }
}

function previousButtonHandler() {
    if (currentTab === personalInfo) {
        attachmentsHandler()
    } else if (currentTab === attachments) {
        bankInfoHandler()
    } else if (currentTab === bankInfo) {
        employerInfoHandler()
    } else if (currentTab === employerInfo) {
        travelInfoHandler()
    } else if (currentTab === travelInfo) {
        personalInfoHandler()
    }
}



personalInfo.addEventListener('click', personalInfoHandler)

travelInfo.addEventListener('click', travelInfoHandler)

employerInfo.addEventListener('click', employerInfoHandler)

bankInfo.addEventListener('click', bankInfoHandler)

attachments.addEventListener('click', attachmentsHandler)


nextButton.forEach((element) => {
    element.addEventListener('click', nextButtonHandler)
})

previousButton.forEach((element) =>{
    element.addEventListener('click', previousButtonHandler)
})


// taxHeaders.forEach((header) => {
//     header.addEventListener("click", function () {
//         const contentDescription = this.nextElementSibling;
//         const arrowUp = this.querySelector(".arrow-up");
//         const arrowDown = this.querySelector(".arrow-down");
//
//         if (contentDescription.style.display === "none" || contentDescription.style.display === "") {
//             contentDescription.style.display = "flex";
//             arrowUp.style.display = "flex";
//             arrowDown.style.display = "none";
//         } else {
//             contentDescription.style.display = "none";
//             arrowUp.style.display = "none";
//             arrowDown.style.display = "flex";
//         }
//     });
// });



document.getElementById('cloneSubmitButton').addEventListener('click', function() {
        document.getElementById('norm').submit();
    });