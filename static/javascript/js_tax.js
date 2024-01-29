// This function is related to navigation of tax-form page. It makes currently selected category bold.
// It includes also functionality of "Next" and "Previous" buttons as well as clone of submit button.

// ===== BEGIN =====
const nextButton = document.querySelectorAll('.next-btn');
const previousButton = document.querySelectorAll('.previous-btn');

const personalInfo = document.querySelector("#tax-navigation #personal-info");
const travelInfo = document.querySelector("#tax-navigation #travel-info");
const employerInfo = document.querySelector("#tax-navigation #employer-info");
const bankInfo = document.querySelector("#tax-navigation #bank-info");
const attachments = document.querySelector("#tax-navigation #attachments");
const progress = document.querySelector("#tax-navigation #progress");

const personalInfoContent = document.querySelector(".taxes-section form#norm .personal-info")
const travelInfoContent = document.querySelector(".taxes-section form#norm .travel-info")
const employerInfoContent = document.querySelector(".taxes-section form#norm .employer-info")
const bankInfoContent = document.querySelector(".taxes-section form#norm .bank-info")
const attachmentsContent = document.querySelector(".taxes-section form#norm .attachments")
const progressContent = document.querySelector(".taxes-section form#norm .progress")

let currentTab = personalInfo

function personalInfoHandler() {
    personalInfo.style.fontWeight = '700'
    personalInfo.style.color = 'black'
    personalInfoContent.style.display = 'flex'
    currentTab = personalInfo

    travelInfo.style.fontWeight = '400'
    travelInfo.style.color = 'rgb(75, 75, 75)'
    travelInfoContent.style.display = 'none'
    employerInfo.style.fontWeight = '400'
    employerInfo.style.color = 'rgb(75, 75, 75)'
    employerInfoContent.style.display = 'none'
    bankInfo.style.fontWeight = '400'
    bankInfo.style.color = 'rgb(75, 75, 75)'
    bankInfoContent.style.display = 'none'
    attachments.style.fontWeight = '400'
    attachments.style.color = 'rgb(75, 75, 75)'
    attachmentsContent.style.display = 'none'
    progress.style.fontWeight = '400'
    progress.style.color = 'rgb(75, 75, 75)'
    progressContent.style.display = 'none'
}

function travelInfoHandler() {
    travelInfo.style.fontWeight = '700'
    travelInfo.style.color = 'black'
    travelInfoContent.style.display = 'flex'
    currentTab = travelInfo

    personalInfo.style.fontWeight = '400'
    personalInfo.style.color = 'rgb(75, 75, 75)'
    personalInfoContent.style.display = 'none'
    employerInfo.style.fontWeight = '400'
    employerInfo.style.color = 'rgb(75, 75, 75)'
    employerInfoContent.style.display = 'none'
    bankInfo.style.fontWeight = '400'
    bankInfo.style.color = 'grrgb(75, 75, 75)ay'
    bankInfoContent.style.display = 'none'
    attachments.style.fontWeight = '400'
    attachments.style.color = 'rgb(75, 75, 75)'
    attachmentsContent.style.display = 'none'
    progress.style.fontWeight = '400'
    progress.style.color = 'rgb(75, 75, 75)'
    progressContent.style.display = 'none'
}

function employerInfoHandler() {
    employerInfo.style.fontWeight = '700'
    employerInfo.style.color = 'black'
    employerInfoContent.style.display = 'flex'
    currentTab = employerInfo

    personalInfo.style.fontWeight = '400'
    personalInfo.style.color = 'rgb(75, 75, 75)'
    personalInfoContent.style.display = 'none'
    travelInfo.style.fontWeight = '400'
    travelInfo.style.color = 'rgb(75, 75, 75)'
    travelInfoContent.style.display = 'none'
    bankInfo.style.fontWeight = '400'
    bankInfo.style.color = 'rgb(75, 75, 75)'
    bankInfoContent.style.display = 'none'
    attachments.style.fontWeight = '400'
    attachments.style.color = 'rgb(75, 75, 75)'
    attachmentsContent.style.display = 'none'
    progress.style.fontWeight = '400'
    progress.style.color = 'rgb(75, 75, 75)'
    progressContent.style.display = 'none'
}

function bankInfoHandler() {
    bankInfo.style.fontWeight = '700'
    bankInfo.style.color = 'black'
    bankInfoContent.style.display = 'flex'
    currentTab = bankInfo

    personalInfo.style.fontWeight = '400'
    personalInfo.style.color = 'rgb(75, 75, 75)'
    personalInfoContent.style.display = 'none'
    travelInfo.style.fontWeight = '400'
    travelInfo.style.color = 'rgb(75, 75, 75)'
    travelInfoContent.style.display = 'none'
    employerInfo.style.fontWeight = '400'
    employerInfo.style.color = 'rgb(75, 75, 75)'
    employerInfoContent.style.display = 'none'
    attachments.style.fontWeight = '400'
    attachments.style.color = 'rgb(75, 75, 75)'
    attachmentsContent.style.display = 'none'
    progress.style.fontWeight = '400'
    progress.style.color = 'rgb(75, 75, 75)'
    progressContent.style.display = 'none'
}

function attachmentsHandler() {
    attachments.style.fontWeight = '700'
    attachments.style.color = 'black'
    attachmentsContent.style.display = 'flex'
    currentTab = attachments

    personalInfo.style.fontWeight = '400'
    personalInfo.style.color = 'rgb(75, 75, 75)'
    personalInfoContent.style.display = 'none'
    travelInfo.style.fontWeight = '400'
    travelInfo.style.color = 'rgb(75, 75, 75)'
    travelInfoContent.style.display = 'none'
    employerInfo.style.fontWeight = '400'
    employerInfo.style.color = 'rgb(75, 75, 75)'
    employerInfoContent.style.display = 'none'
    bankInfo.style.fontWeight = '400'
    bankInfo.style.color = 'rgb(75, 75, 75)'
    bankInfoContent.style.display = 'none'
    progress.style.fontWeight = '400'
    progress.style.color = 'rgb(75, 75, 75)'
    progressContent.style.display = 'none'
}

function progressHandler() {
    progress.style.fontWeight = '700'
    progress.style.color = 'black'
    progressContent.style.display = 'flex'
    currentTab = progress

    personalInfo.style.fontWeight = '400'
    personalInfo.style.color = 'rgb(75, 75, 75)'
    personalInfoContent.style.display = 'none'
    travelInfo.style.fontWeight = '400'
    travelInfo.style.color = 'rgb(75, 75, 75)'
    travelInfoContent.style.display = 'none'
    employerInfo.style.fontWeight = '400'
    employerInfo.style.color = 'rgb(75, 75, 75)'
    employerInfoContent.style.display = 'none'
    bankInfo.style.fontWeight = '400'
    bankInfo.style.color = 'rgb(75, 75, 75)'
    bankInfoContent.style.display = 'none'
    attachments.style.fontWeight = '400'
    attachments.style.color = 'rgb(75, 75, 75)'
    attachmentsContent.style.display = 'none'
}

function nextButtonHandler() {
    if (currentTab === personalInfo) {
        // document.getElementById('norm').submit();
        travelInfoHandler()

    } else if (currentTab === travelInfo) {
        // document.getElementById('norm').submit();
        employerInfoHandler()

    } else if (currentTab === employerInfo) {
        // document.getElementById('norm').submit();
        bankInfoHandler()

    } else if (currentTab === bankInfo) {
        // document.getElementById('norm').submit();
        attachmentsHandler()
    } else if (currentTab === attachments) {
        // document.getElementById('norm').submit();
        progressHandler()
    } else if (currentTab === progress) {
        // document.getElementById('norm').submit();
        personalInfoHandler()
    }
}

function previousButtonHandler() {
    if (currentTab === personalInfo) {
        progressHandler()
        // document.getElementById('norm').submit();
    } else if (currentTab === progress) {
        attachmentsHandler()
        // document.getElementById('norm').submit();
    } else if (currentTab === attachments) {
        bankInfoHandler()
        // document.getElementById('norm').submit();
    } else if (currentTab === bankInfo) {
        employerInfoHandler()
        // document.getElementById('norm').submit();
    } else if (currentTab === employerInfo) {
        travelInfoHandler()
        // document.getElementById('norm').submit();
    } else if (currentTab === travelInfo) {
        personalInfoHandler()
        // document.getElementById('norm').submit();
    }
}


personalInfo.addEventListener('click', personalInfoHandler)

travelInfo.addEventListener('click', travelInfoHandler)

employerInfo.addEventListener('click', employerInfoHandler)

bankInfo.addEventListener('click', bankInfoHandler)

attachments.addEventListener('click', attachmentsHandler)

progress.addEventListener('click', progressHandler)


nextButton.forEach((element) => {
    element.addEventListener('click', nextButtonHandler)
})

previousButton.forEach((element) => {
    element.addEventListener('click', previousButtonHandler)
})

function submitButtonHandler() {
    var submitButton = document.getElementById('cloneSubmitButton')

    submitButton.addEventListener('click', function () {
        document.getElementById('norm').submit();

    });
}

// ===== END =====


// following code is responsible for dynamically updating the status indicator of categories - red, yellow, green

// ===== BEGIN =====

var statusPersonalInfoCat = document.getElementById('status-personal-info');
var statusTravelInfoCat = document.getElementById('status-travel-info');
var statusEmployerInfoCat = document.getElementById('status-employer-info');
var statusBankInfoCat = document.getElementById('status-bank-info');
var statusAttachmentsCat = document.getElementById('status-attachments');

var progressPersonalInfo = document.getElementById('progress-personal-info');
var progressFieldPersonalInfo = document.getElementById('id_stat_pers_dat');
var progressDocuments = document.getElementById('progress-documents');
var progressFieldDocuments = document.getElementById('id_stat_docs')
var progressInProgress = document.getElementById('progress-in-progress');

function addGrayBorder() {
    var allInputs = document.querySelectorAll('.tax-content p input');
    var allSelect = document.querySelectorAll('.tax-content p select');
    allInputs.forEach(function (element) {
        element.classList.add('gray-border');
    })
    allSelect.forEach(function (element) {
        element.classList.add('gray-border');
    })
}

function addGreenRedBorder(list) {
    //adding red or green border, depending on the state of the field
    list.forEach(function (element) {
        if (!element.value) {
            element.classList.add('red-border');
            element.classList.remove('gray-border');
            element.classList.remove('green-border');
        } else if (element.value) {
            element.classList.add('green-border');
            element.classList.remove('gray-border');
            element.classList.remove('red-border');
        }
    });
}


function statusPersonalInfo() {
    var name = document.getElementById('id_first_name');
    var fieldName = name.value;
    var family = document.getElementById('id_family_name');
    var fieldFamily = family.value;
    var bDay = document.getElementById('id_birth_date');
    var fieldBday = bDay.value;
    var bCity = document.getElementById('id_birth_city');
    var fieldBcity = bCity.value;
    var address = document.getElementById('id_address');
    var fieldAddress = address.value;
    var city = document.getElementById('id_city');
    var fieldCity = city.value;
    var country = document.getElementById('id_country');
    var fieldCountry = country.value;
    var email = document.getElementById('id_email');
    var fieldEmail = email.value;
    var phone = document.getElementById('id_phone_number');
    var fieldPhone = phone.value;


    if (!fieldName && !fieldFamily &&
        !fieldBday && !fieldBcity &&
        !fieldAddress && !fieldCity &&
        !fieldCountry && !fieldEmail &&
        !fieldPhone && !fieldPhone) {
        statusPersonalInfoCat.classList.add('red-color');
        statusPersonalInfoCat.classList.remove('yellow-color');
        statusPersonalInfoCat.classList.remove('green-color');
    } else if (fieldName && fieldFamily &&
        fieldBday && fieldBcity &&
        fieldAddress && fieldCity &&
        fieldCountry && fieldEmail &&
        fieldPhone && fieldPhone) {
        statusPersonalInfoCat.classList.add('green-color');
        statusPersonalInfoCat.classList.remove('yellow-color');
        statusPersonalInfoCat.classList.remove('red-color');
    } else {
        statusPersonalInfoCat.classList.add('yellow-color');
        statusPersonalInfoCat.classList.remove('green-color');
        statusPersonalInfoCat.classList.remove('red-color');
    }

    // create a list of fields

    var fieldsArray = [
        name,
        family,
        bDay,
        bCity,
        address,
        city,
        country,
        email,
        phone
    ];

    addGreenRedBorder(fieldsArray);

}

function statusTravelInfo() {
    var ssn = document.getElementById('id_social_security');
    var fieldSsn = ssn.value;
    var workingYear = document.getElementById('id_working_year');
    var fieldWorkingYear = workingYear.value;
    var arrivalDate = document.getElementById('id_arrival_date_in_usa');
    var fieldArrivalDate = arrivalDate.value;
    var departureDate = document.getElementById('id_departure_date_in_usa');
    var fieldDepartureDate = departureDate.value;
    var visaType = document.getElementById('id_visa_type');
    var fieldVisaType = visaType.value;
    var programType = document.getElementById('id_program_type');
    var fieldProgramType = programType.value;
    var previousTax = document.getElementById('id_previous_tax_declarations');
    var fieldPreviousTax = previousTax.value;

    var fieldsArray = [
        ssn,
        workingYear,
        arrivalDate,
        departureDate,
        visaType,
        programType,
        previousTax
    ]

    if (!fieldSsn && !fieldWorkingYear &&
        !fieldArrivalDate && !fieldDepartureDate &&
        !fieldVisaType && !fieldProgramType &&
        !fieldPreviousTax) {
        statusTravelInfoCat.classList.add('red-color');
        statusTravelInfoCat.classList.remove('yellow-color');
        statusTravelInfoCat.classList.remove('green-color');
    } else if (fieldSsn && fieldWorkingYear &&
        fieldArrivalDate && fieldDepartureDate &&
        fieldVisaType && fieldProgramType &&
        fieldPreviousTax) {
        statusTravelInfoCat.classList.add('green-color');
        statusTravelInfoCat.classList.remove('yellow-color');
        statusTravelInfoCat.classList.remove('red-color');
    } else {
        statusTravelInfoCat.classList.add('yellow-color');
        statusTravelInfoCat.classList.remove('green-color');
        statusTravelInfoCat.classList.remove('red-color');
    }

    addGreenRedBorder(fieldsArray);
}

function statusEmployerInfo() {
    var cName = document.getElementById('id_company_name');
    var fieldCname = cName.value;
    var cAddress = document.getElementById('id_company_address');
    var fieldCaddress = cAddress.value;
    var cCity = document.getElementById('id_company_city');
    var fieldCcity = cCity.value;
    var cState = document.getElementById('id_company_state');
    var fieldCstate = cState.value;
    var cZip = document.getElementById('id_company_zip');
    var fieldCzip = cZip.value;

    var fieldsArray = [
        cName,
        cAddress,
        cCity,
        cState,
        cZip
    ]

    if (!fieldCname && !fieldCaddress &&
        !fieldCcity && !fieldCstate &&
        !fieldCzip) {
        statusEmployerInfoCat.classList.add('red-color');
        statusEmployerInfoCat.classList.remove('yellow-color');
        statusEmployerInfoCat.classList.remove('green-color');
    } else if (fieldCname && fieldCaddress &&
        fieldCcity && fieldCstate &&
        fieldCzip) {
        statusEmployerInfoCat.classList.add('green-color');
        statusEmployerInfoCat.classList.remove('yellow-color');
        statusEmployerInfoCat.classList.remove('red-color');
    } else {
        statusEmployerInfoCat.classList.add('yellow-color');
        statusEmployerInfoCat.classList.remove('green-color');
        statusEmployerInfoCat.classList.remove('red-color');
    }

    addGreenRedBorder(fieldsArray);
}

function statusBankInfo() {
    var bank = document.getElementById('id_american_bank_account');
    var fieldBank = bank.value;
    var accountHolder = document.getElementById('id_account_holder');
    var fieldAccountHolder = accountHolder.value;
    var routingNumber = document.getElementById('id_routing_number');
    var fieldRoutingNumber = routingNumber.value;
    var accountNumber = document.getElementById('id_account_number');
    var fieldAccountNumber = accountNumber.value;

    var fieldsArray = [
        bank,
        accountHolder,
        routingNumber,
        accountNumber
    ]

    if (fieldBank === "No") {
        statusBankInfoCat.classList.add('green-color');
        statusBankInfoCat.classList.remove('yellow-color');
        statusBankInfoCat.classList.remove('red-color');
    } else if (fieldBank === "Yes") {
        if (!fieldAccountHolder && !fieldRoutingNumber && !fieldAccountNumber) {
            statusBankInfoCat.classList.add('red-color');
            statusBankInfoCat.classList.remove('yellow-color');
            statusBankInfoCat.classList.remove('green-color');
        } else if (fieldAccountHolder && fieldRoutingNumber && fieldAccountNumber) {
            statusBankInfoCat.classList.add('green-color');
            statusBankInfoCat.classList.remove('yellow-color');
            statusBankInfoCat.classList.remove('red-color');
        } else {
            statusBankInfoCat.classList.add('yellow-color');
            statusBankInfoCat.classList.remove('green-color');
            statusBankInfoCat.classList.remove('red-color');
        }
    } else {
        statusBankInfoCat.classList.add('red-color');
        statusBankInfoCat.classList.remove('yellow-color');
        statusBankInfoCat.classList.remove('green-color');
    }

    addGreenRedBorder(fieldsArray);

}

function statusAttachments() {
    var fieldPassportDoc = document.getElementById('id_passport_copy_used');
    var fieldVisaDoc = document.getElementById('id_visa_copy_used');
    var fieldSsnDoc = document.getElementById('id_ssn_copy_used');
    var fieldPayCheckW2Doc = document.getElementById('id_last_paycheck_w2_used');

    var fieldsArray = [
        fieldPassportDoc,
        fieldVisaDoc,
        fieldSsnDoc,
        fieldPayCheckW2Doc
    ]

    if (!fieldPassportDoc.checked && !fieldVisaDoc.checked &&
        !fieldSsnDoc.checked && !fieldPayCheckW2Doc.checked) {
        statusAttachmentsCat.classList.add('red-color');
        statusAttachmentsCat.classList.remove('yellow-color');
        statusAttachmentsCat.classList.remove('green-color');
    } else if (fieldPassportDoc.checked && fieldVisaDoc.checked &&
        fieldSsnDoc.checked && fieldPayCheckW2Doc.checked) {
        statusAttachmentsCat.classList.add('green-color');
        statusAttachmentsCat.classList.remove('red-color');
        statusAttachmentsCat.classList.remove('yellow-color');
    } else {
        statusAttachmentsCat.classList.add('yellow-color');
        statusAttachmentsCat.classList.remove('green-color');
        statusAttachmentsCat.classList.remove('red-color');
    }

    addGreenRedBorder(fieldsArray);

}

function statusPersonalInfoChecker() {

    if (statusPersonalInfoCat.classList.contains('green-color') &&
        statusTravelInfoCat.classList.contains('green-color') &&
        statusEmployerInfoCat.classList.contains('green-color') &&
        statusBankInfoCat.classList.contains('green-color')) {
        progressPersonalInfo.classList.add('green-completed');
        progressFieldPersonalInfo.value = '3';
        progressPersonalInfo.classList.remove('yellow-not-completed');
        progressPersonalInfo.classList.remove('red-not-started');
    } else if (statusPersonalInfoCat.classList.contains('red-color') &&
        statusTravelInfoCat.classList.contains('red-color') &&
        statusEmployerInfoCat.classList.contains('red-color') &&
        statusBankInfoCat.classList.contains('red-color')) {
        progressPersonalInfo.classList.add('red-not-started');
        progressFieldPersonalInfo.value = '1';
        progressPersonalInfo.classList.remove('yellow-not-completed');
        progressPersonalInfo.classList.remove('green-completed');
    } else {
        progressPersonalInfo.classList.add('yellow-not-completed');
        progressFieldPersonalInfo.value = '2';
        progressPersonalInfo.classList.remove('green-completed');
        progressPersonalInfo.classList.remove('red-not-started');
    }

}

function statusAttachmentsChecker() {

    if (statusAttachmentsCat.classList.contains('green-color')) {
        progressDocuments.classList.add('green-completed');
        progressFieldDocuments.value = '3';
        progressDocuments.classList.remove('yellow-not-completed');
        progressDocuments.classList.remove('red-not-started');
    } else if (statusAttachmentsCat.classList.contains('red-color')) {
        progressDocuments.classList.add('red-not-started');
        progressFieldDocuments.value = '1';
        progressDocuments.classList.remove('yellow-not-completed');
        progressDocuments.classList.remove('green-completed');
    } else {
        progressDocuments.classList.add('yellow-not-completed');
        progressFieldDocuments.value = '2';
        progressDocuments.classList.remove('green-completed');
        progressDocuments.classList.remove('red-not-started');
    }

}

function disableButton() {
    var sendApplicationBtn = document.getElementById('cloneSubmitButton');

    if (progressPersonalInfo.classList.contains('green-completed') &&
        progressDocuments.classList.contains('green-completed')) {
        sendApplicationBtn.classList.remove('disabled');
    } else {
        sendApplicationBtn.classList.add('disabled');
    }
}

window.onload = function () {
    addGrayBorder();
    statusPersonalInfo();
    statusTravelInfo();
    statusEmployerInfo();
    statusBankInfo();
    statusAttachments();
    statusPersonalInfoChecker();
    statusAttachmentsChecker();
    disableButton();
    submitButtonHandler();
}

// ===== END =====