// Show the date format hint in the date form fields on the edit-tax page.

let date_hints = document.querySelectorAll('.date-hint');

date_hints.forEach(function (element) {
    let parentElement = element.parentNode;
    parentElement.addEventListener('mouseover', function () {
        element.style.display = 'flex';
        setTimeout(function () {
            element.style.display = "none";
        }, 3000);
    });
});


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

const personalInfoContent = document.querySelector(".taxes-section form.norm .personal-info")
const travelInfoContent = document.querySelector(".taxes-section form.norm .travel-info")
const employerInfoContent = document.querySelector(".taxes-section form.norm .employer-info")
const bankInfoContent = document.querySelector(".taxes-section form.norm .bank-info")
const attachmentsContent = document.querySelector(".taxes-section form.norm .attachments")
const progressContent = document.querySelector(".taxes-section form.norm .progress")

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
    bankInfo.style.color = 'rgb(75, 75, 75)'
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

let personalInfoStep = document.getElementById('id_personal_info_done');
let travelInfoStep = document.getElementById('id_travel_info_done');
let employerInfoStep = document.getElementById('id_employer_info_done');
let bankInfoStep = document.getElementById('id_bank_info_done');
let attachmentsInfoStep = document.getElementById('id_attachments_info_done');

function stepHandler() {
    let progressDoc = document.querySelector('label[for="id_stat_docs"]');
    if (bankInfoStep.value === 'yes') {
        bankInfoHandler();
    } else {
        if (employerInfoStep.value === 'yes') {
            employerInfoHandler();
        } else {
            if (travelInfoStep.value === 'yes') {
                travelInfoHandler();
            } else {
                if (personalInfoStep.value === 'yes') {
                    personalInfoHandler();
                } else {

                }
            }
        }
    }

    if (isSent.value === 'true') {
        progressHandler();
    }

    progressDoc.addEventListener('click', function () {
        attachmentsHandler();
    })

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
    let cloneSubmitButton = document.getElementById('cloneSubmitButton');

    cloneSubmitButton.addEventListener('click', function () {
        document.getElementById('norm').submit();
        nextButtonHandler();
    });
}

// ===== END =====



// following code is responsible for dynamically updating the status indicator of categories - red, yellow, green

// ===== BEGIN =====

let statusPersonalInfoCat = document.getElementById('status-personal-info');
let statusTravelInfoCat = document.getElementById('status-travel-info');
let statusEmployerInfoCat = document.getElementById('status-employer-info');
let statusBankInfoCat = document.getElementById('status-bank-info');
let statusAttachmentsCat = document.getElementById('status-attachments');

let progressPersonalInfo = document.getElementById('progress-personal-info');
let progressFieldPersonalInfo = document.getElementById('id_stat_pers_dat');
let progressDocuments = document.getElementById('progress-documents');
let progressFieldDocuments = document.getElementById('id_stat_docs')
let progressInProgress = document.getElementById('progress-in-progress');
let isSent = document.getElementById('id_is_sent');

function addGrayBorder() {
    let allInputs = document.querySelectorAll('.tax-content p input');
    let allSelect = document.querySelectorAll('.tax-content p select');
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
    let name = document.getElementById('id_first_name');
    let fieldName = name.value;
    let family = document.getElementById('id_family_name');
    let fieldFamily = family.value;
    let name_en = document.getElementById('id_first_name_en');
    let fieldNameEn = name_en.value;
    let family_en = document.getElementById('id_family_name_en');
    let fieldFamilyEn = family_en.value;
    let bDay = document.getElementById('id_birth_date');
    let fieldBday = bDay.value;
    let bCity = document.getElementById('id_birth_city');
    let fieldBcity = bCity.value;
    let address = document.getElementById('id_address');
    let fieldAddress = address.value;
    let city = document.getElementById('id_city');
    let fieldCity = city.value;
    let country = document.getElementById('id_country');
    let fieldCountry = country.value;
    let email = document.getElementById('id_email');
    let fieldEmail = email.value;
    let phone = document.getElementById('id_phone_number');
    let fieldPhone = phone.value;
    let id_number = document.getElementById('id_id_number');
    let fieldIdNumber = id_number.value;
    let issue_date = document.getElementById('id_issue_date');
    let fieldIssueDate = issue_date.value;
    let is_done = document.getElementById('id_personal_info_done')

    if (!fieldName && !fieldFamily &&
        !fieldNameEn && !fieldFamilyEn &&
        !fieldBday && !fieldBcity &&
        !fieldAddress && !fieldCity &&
        !fieldCountry && !fieldEmail &&
        !fieldPhone && !fieldPhone &&
        !fieldIdNumber && !fieldIssueDate) {
        is_done.value = 'no';
        statusPersonalInfoCat.classList.add('red-color');
        statusPersonalInfoCat.classList.remove('yellow-color');
        statusPersonalInfoCat.classList.remove('green-color');
    } else if (fieldName && fieldFamily &&
        fieldNameEn && fieldFamilyEn &&
        fieldBday && fieldBcity &&
        fieldAddress && fieldCity &&
        fieldCountry && fieldEmail &&
        fieldPhone && fieldPhone &&
        fieldIdNumber && fieldIssueDate) {
        is_done.value = 'yes';
        statusPersonalInfoCat.classList.add('green-color');
        statusPersonalInfoCat.classList.remove('yellow-color');
        statusPersonalInfoCat.classList.remove('red-color');
    } else {
        is_done.value = 'no';
        statusPersonalInfoCat.classList.add('yellow-color');
        statusPersonalInfoCat.classList.remove('green-color');
        statusPersonalInfoCat.classList.remove('red-color');
    }

    // create a list of fields

    let fieldsArray = [
        name,
        family,
        name_en,
        family_en,
        bDay,
        bCity,
        address,
        city,
        country,
        email,
        phone,
        id_number,
        issue_date
    ];

    addGreenRedBorder(fieldsArray);

}

function statusTravelInfo() {
    let ssn = document.getElementById('id_social_security');
    let fieldSsn = ssn.value;
    let workingYear = document.getElementById('id_working_year');
    let fieldWorkingYear = workingYear.value;
    let arrivalDate = document.getElementById('id_arrival_date_in_usa');
    let fieldArrivalDate = arrivalDate.value;
    let departureDate = document.getElementById('id_departure_date_in_usa');
    let fieldDepartureDate = departureDate.value;
    let visaType = document.getElementById('id_visa_type');
    let fieldVisaType = visaType.value;
    let programType = document.getElementById('id_program_type');
    let fieldProgramType = programType.value;
    let previousTax = document.getElementById('id_previous_tax_declarations');
    let fieldPreviousTax = previousTax.value;
    let is_done = document.getElementById('id_travel_info_done')

    let fieldsArray = [
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
        is_done.value = 'no';
        statusTravelInfoCat.classList.add('red-color');
        statusTravelInfoCat.classList.remove('yellow-color');
        statusTravelInfoCat.classList.remove('green-color');
    } else if (fieldSsn && fieldWorkingYear &&
        fieldArrivalDate && fieldDepartureDate &&
        fieldVisaType && fieldProgramType &&
        fieldPreviousTax) {
        is_done.value = 'yes';
        statusTravelInfoCat.classList.add('green-color');
        statusTravelInfoCat.classList.remove('yellow-color');
        statusTravelInfoCat.classList.remove('red-color');
    } else {
        is_done.value = 'no';
        statusTravelInfoCat.classList.add('yellow-color');
        statusTravelInfoCat.classList.remove('green-color');
        statusTravelInfoCat.classList.remove('red-color');
    }

    addGreenRedBorder(fieldsArray);
}

function statusEmployerInfo() {
    let cName = document.getElementById('id_company_name');
    let fieldCname = cName.value;
    let cAddress = document.getElementById('id_company_address');
    let fieldCaddress = cAddress.value;
    let cCity = document.getElementById('id_company_city');
    let fieldCcity = cCity.value;
    let cState = document.getElementById('id_company_state');
    let fieldCstate = cState.value;
    let cZip = document.getElementById('id_company_zip');
    let fieldCzip = cZip.value;
    let is_done = document.getElementById('id_employer_info_done')

    let fieldsArray = [
        cName,
        cAddress,
        cCity,
        cState,
        cZip
    ]

    if (!fieldCname && !fieldCaddress &&
        !fieldCcity && !fieldCstate &&
        !fieldCzip) {
        is_done.value = 'no';
        statusEmployerInfoCat.classList.add('red-color');
        statusEmployerInfoCat.classList.remove('yellow-color');
        statusEmployerInfoCat.classList.remove('green-color');
    } else if (fieldCname && fieldCaddress &&
        fieldCcity && fieldCstate &&
        fieldCzip) {
        is_done.value = 'yes';
        statusEmployerInfoCat.classList.add('green-color');
        statusEmployerInfoCat.classList.remove('yellow-color');
        statusEmployerInfoCat.classList.remove('red-color');
    } else {
        is_done.value = 'no';
        statusEmployerInfoCat.classList.add('yellow-color');
        statusEmployerInfoCat.classList.remove('green-color');
        statusEmployerInfoCat.classList.remove('red-color');
    }

    addGreenRedBorder(fieldsArray);
}

function statusBankInfo() {
    let bank = document.getElementById('id_american_bank_account');
    let fieldBank = bank.value;
    let accountHolder = document.getElementById('id_account_holder');
    let fieldAccountHolder = accountHolder.value;
    let routingNumber = document.getElementById('id_routing_number');
    let fieldRoutingNumber = routingNumber.value;
    let accountNumber = document.getElementById('id_account_number');
    let fieldAccountNumber = accountNumber.value;
    let is_done = document.getElementById('id_bank_info_done')

    let fieldsArray = [
        bank,
        accountHolder,
        routingNumber,
        accountNumber
    ]

    if (fieldBank === "No") {
        is_done.value = 'yes';
        statusBankInfoCat.classList.add('green-color');
        statusBankInfoCat.classList.remove('yellow-color');
        statusBankInfoCat.classList.remove('red-color');
    } else if (fieldBank === "Yes") {
        if (!fieldAccountHolder && !fieldRoutingNumber && !fieldAccountNumber) {
            is_done.value = 'no';
            statusBankInfoCat.classList.add('red-color');
            statusBankInfoCat.classList.remove('yellow-color');
            statusBankInfoCat.classList.remove('green-color');
        } else if (fieldAccountHolder && fieldRoutingNumber && fieldAccountNumber) {
            is_done.value = 'yes';
            statusBankInfoCat.classList.add('green-color');
            statusBankInfoCat.classList.remove('yellow-color');
            statusBankInfoCat.classList.remove('red-color');
        } else {
            is_done.value = 'no';
            statusBankInfoCat.classList.add('yellow-color');
            statusBankInfoCat.classList.remove('green-color');
            statusBankInfoCat.classList.remove('red-color');
        }
    } else {
        is_done.value = 'no';
        statusBankInfoCat.classList.add('red-color');
        statusBankInfoCat.classList.remove('yellow-color');
        statusBankInfoCat.classList.remove('green-color');
    }

    addGreenRedBorder(fieldsArray);

}

function statusAttachments() {
    let fieldPassportDoc = document.getElementById('id_passport_copy_used');
    let fieldVisaDoc = document.getElementById('id_visa_copy_used');
    let fieldSsnDoc = document.getElementById('id_ssn_copy_used');
    let fieldPayCheckDoc = document.getElementById('id_last_paycheck_doc_used');
    let is_done = document.getElementById('id_attachments_info_done')

    let fieldsArray = [
        fieldPassportDoc,
        fieldVisaDoc,
        fieldSsnDoc,
        fieldPayCheckDoc
    ]

    if (!fieldPassportDoc.checked && !fieldVisaDoc.checked &&
        !fieldSsnDoc.checked && !fieldPayCheckDoc.checked) {
        is_done.value = 'no';
        statusAttachmentsCat.classList.add('red-color');
        statusAttachmentsCat.classList.remove('yellow-color');
        statusAttachmentsCat.classList.remove('green-color');
    } else if (fieldPassportDoc.checked && fieldVisaDoc.checked &&
        fieldSsnDoc.checked && fieldPayCheckDoc.checked) {
        is_done.value = 'yes';
        statusAttachmentsCat.classList.add('green-color');
        statusAttachmentsCat.classList.remove('red-color');
        statusAttachmentsCat.classList.remove('yellow-color');
    } else {
        is_done.value = 'no';
        statusAttachmentsCat.classList.add('yellow-color');
        statusAttachmentsCat.classList.remove('green-color');
        statusAttachmentsCat.classList.remove('red-color');
    }

    addGreenRedBorder(fieldsArray);

}

function statusPersonalInfoChecker() {
    /// statusBankInfoCat.classList.contains('green-color') removed from first if condition.
    if (statusPersonalInfoCat.classList.contains('green-color') &&
        statusTravelInfoCat.classList.contains('green-color') &&
        statusEmployerInfoCat.classList.contains('green-color')) {
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
        isSent.value = false;
        progressPersonalInfo.classList.remove('yellow-not-completed');
        progressPersonalInfo.classList.remove('green-completed');
    } else {
        progressPersonalInfo.classList.add('yellow-not-completed');
        progressFieldPersonalInfo.value = '2';
        isSent.value = false;
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
    let sendApplicationBtn = document.getElementById('cloneSubmitButton');
    let generateContractBtn = document.getElementById('generate-contract-btn')
    let inProgress = document.getElementById('progress-in-progress')
    let cloneSubmitButtonText = document.getElementById('cloneSubmitButtonText')
    // excluded from below
    // &&
    //         progressDocuments.classList.contains('green-completed')
    generateContractBtn.classList.add('disabled');
    if (progressPersonalInfo.classList.contains('green-completed')) {
        sendApplicationBtn.classList.remove('disabled');
    } else {
        sendApplicationBtn.classList.add('disabled');
        generateContractBtn.classList.add('disabled');
    }

    if (isSent.value === 'true' &&
        progressPersonalInfo.classList.contains('green-completed')) {
        sendApplicationBtn.classList.add('disabled');
        generateContractBtn.classList.remove('disabled');
        cloneSubmitButtonText.textContent = "Формуляр изпратен"
        inProgress.classList.add('green-completed');
        inProgress.classList.remove('red-not-started')
        progressHandler();
    } else if (isSent.value === 'false' &&
        progressPersonalInfo.classList.contains('green-completed') &&
        progressDocuments.classList.contains('green-completed')) {
        sendApplicationBtn.classList.remove('disabled');
        generateContractBtn.classList.add('disabled');
        cloneSubmitButtonText.textContent = "Изпрати формуляр"
        inProgress.classList.add('red-not-started');
        inProgress.classList.remove('green-completed')
    }
}

function changeStatus() {
    let statDeclarationSubmitted = document.getElementById('id_stat_declaration_submitted');
    let statusDS = document.getElementById('declaration-submitted');
    let statWaitingState = document.getElementById('id_stat_waiting_state');
    let statusWS = document.getElementById('waiting-state');
    let statWaitingFederal = document.getElementById('id_stat_waiting_federal');
    let statusWF = document.getElementById('waiting-federal');
    let statStateCustomer = document.getElementById('id_stat_state_customer');
    let statusSC = document.getElementById('state-customer');
    let statFederalCustomer = document.getElementById('id_stat_federal_customer');
    let statusFC = document.getElementById('federal-customer');
    let statFederalFeePaid = document.getElementById('id_stat_federal_fee_paid');
    let statStateFeePaid = document.getElementById('id_stat_state_fee_paid');
    let statusTP = document.getElementById('tax-paid');
    // let generalStatus = document.getElementById('id_general_status');

    // if (statDeclarationSubmitted.value === '3') {
    //     if (statWaitingFederal.value === '3') {
    //         if (statWaitingState.value === '3') {
    //             if (statFederalFeePaid.value === '3' && statStateFeePaid.value === '1') {
    //                 generalStatus.value = 'federalfee';
    //             } else if (statStateFeePaid.value === '3' && statFederalFeePaid.value === '1') {
    //                 generalStatus.value = 'statefee';
    //             } else if (statFederalFeePaid.value === '3' && statStateFeePaid.value === '3') {
    //                 generalStatus.value = 'allpaid';
    //             }
    //         } else {
    //             generalStatus.value = 'state';
    //         }
    //     } else {
    //         generalStatus.value = 'federal';
    //     }
    // } else {
    //     generalStatus.value = 'declaration';
    // }

    if (statFederalFeePaid.value === '3' && statStateFeePaid.value === '3') {
        statusTP.classList.add("green-completed");
        statusTP.classList.remove("red-not-started");
        statusTP.classList.remove("yellow-not-completed");
    } else if (statFederalFeePaid.value === '1' && statStateFeePaid.value === '1') {
        statusTP.classList.add("red-not-started");
        statusTP.classList.remove("green-completed");
        statusTP.classList.remove("yellow-not-completed");
    } else {
        statusTP.classList.add("yellow-not-completed");
        statusTP.classList.remove("green-completed");
        statusTP.classList.remove("red-not-started");
    }

    let statsList = [
        {"name": statDeclarationSubmitted, "value": statusDS},
        {"name": statWaitingState, "value": statusWS},
        {"name": statWaitingFederal, "value": statusWF},
        {"name": statStateCustomer, "value": statusSC},
        {"name": statFederalCustomer, "value": statusFC}
    ];

    statsList.forEach(pair => {
        if (pair.name.value === "1") {
            pair.value.classList.add("red-not-started");
            pair.value.classList.remove("yellow-not-completed");
            pair.value.classList.remove("green-completed")
        } else if (pair.name.value === "2") {
            pair.value.classList.add("yellow-not-completed");
            pair.value.classList.remove("red-not-started");
            pair.value.classList.remove("green-completed")
        } else if (pair.name.value === "3") {
            pair.value.classList.add("green-completed");
            pair.value.classList.remove("red-not-started");
            pair.value.classList.remove("yellow-not-completed")
        }
    })

}

function hideBankDetails() {
    let checker = document.getElementById('id_american_bank_account');
    let divBankDetails = document.getElementById('bank-sub-category');
    let accountHolder = document.getElementById('id_account_holder');
    let routingNumber = document.getElementById('id_routing_number');
    let accountNumber = document.getElementById('id_account_number');

    if (checker.value === "No") {
        divBankDetails.classList.add("disabled");
        accountNumber.classList.add("grey-border")
        accountNumber.classList.remove('red-border')
        accountHolder.classList.add("grey-border")
        accountHolder.classList.remove('red-border')
        routingNumber.classList.add("grey-border")
        routingNumber.classList.remove('red-border')
    } else if (checker.value === 'Yes') {
        divBankDetails.classList.remove("disabled");
    }
}

function progressPercents() {
    let progressReg = document.getElementById('progress-registry');
    let progressPersInfo = document.getElementById('progress-personal-info');
    let progressInProg = document.getElementById('progress-in-progress');
    let progressDocs = document.getElementById('progress-documents');
    let progressDeclSub = document.getElementById('declaration-submitted');
    let progressWF = document.getElementById('waiting-federal');
    let progressWS = document.getElementById('waiting-state');
    let progressTaxesPaid = document.getElementById('tax-paid');
    let progressFC = document.getElementById('federal-customer');
    let progressSC = document.getElementById('state-customer');

    let prog10 = document.getElementById('progress10');
    let prog20 = document.getElementById('progress20');
    let prog30 = document.getElementById('progress30');
    let prog40 = document.getElementById('progress40');
    let prog50 = document.getElementById('progress50');
    let prog60 = document.getElementById('progress60');
    let prog70 = document.getElementById('progress70');
    let prog80 = document.getElementById('progress80');
    let prog90 = document.getElementById('progress90');
    let prog100 = document.getElementById('progress100');

    let counter = 0;

    let list = [
        progressReg,
        progressPersInfo,
        progressInProg,
        progressDocs,
        progressDeclSub,
        progressWF,
        progressWS,
        progressTaxesPaid,
        progressFC,
        progressSC
    ]

    let listPerc = [
        prog10,
        prog20,
        prog30,
        prog40,
        prog50,
        prog60,
        prog70,
        prog80,
        prog90,
        prog100
    ]

    function makeNone() {
        listPerc.forEach(element => {
            element.style.display = 'none';
        })
    }


    list.forEach(element => {
        if (element.classList.contains('green-completed')) {
            counter += 1;
        }
    })

    if (counter === 1) {
        makeNone();
        prog10.style.display = 'flex';
    } else if (counter === 2) {
        makeNone();
        prog20.style.display = 'flex';
    } else if (counter === 3) {
        makeNone();
        prog30.style.display = 'flex';
    } else if (counter === 4) {
        makeNone();
        prog40.style.display = 'flex';
    } else if (counter === 5) {
        makeNone();
        prog50.style.display = 'flex';
    } else if (counter === 6) {
        makeNone();
        prog60.style.display = 'flex';
    } else if (counter === 7) {
        makeNone();
        prog70.style.display = 'flex';
    } else if (counter === 8) {
        makeNone();
        prog80.style.display = 'flex';
    } else if (counter === 9) {
        makeNone();
        prog90.style.display = 'flex';
    } else if (counter === 10) {
        makeNone();
        prog100.style.display = 'flex';
    }
}

function colorpicker() {

}

window.onload = function () {
    addGrayBorder();
    statusPersonalInfo();
    statusTravelInfo();
    statusEmployerInfo();
    statusBankInfo();
    hideBankDetails();
    statusAttachments();
    statusPersonalInfoChecker();
    statusAttachmentsChecker();
    disableButton();
    changeStatus();
    progressPercents();
    submitButtonHandler();
    stepHandler();
    colorpicker()
}


// ===== END =====