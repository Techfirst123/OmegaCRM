const CONFIG = {
    MAX_FILE_SIZE: 5 * 1024 * 1024,
    ALLOWED_FILE_TYPES: [
        'application/pdf',
        'image/jpeg',
        'image/png'
    ],
    PDF_WORKER_URL: 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.4.168/pdf.worker.min.js'
};

const state = { isSubmitting: false, ocrInProgress: false };

let currentStep = 1;
const TOTAL_STEPS = 5;

function showStep(stepNumber) {
    currentStep = Math.max(1, Math.min(TOTAL_STEPS, stepNumber));
    document.querySelectorAll('.form-step').forEach((el) => {
        el.classList.add('d-none');
        if (parseInt(el.dataset.step, 10) === currentStep) el.classList.remove('d-none');
    });
    document.querySelectorAll('.step-label').forEach((el) => {
        const isActive = parseInt(el.dataset.step || '0', 10) === currentStep;
        el.classList.toggle('active', isActive);
        el.classList.toggle('text-muted', !isActive);
        el.setAttribute('aria-current', isActive ? 'step' : 'false');
    });

    const pct = (currentStep / TOTAL_STEPS) * 100;
    const bar = document.getElementById('formProgress');
    if (bar) bar.style.width = `${pct}%`;

    const prev = document.getElementById('prevBtn');
    const next = document.getElementById('nextBtn');
    const submit = document.getElementById('submitBtn');
    if (prev) prev.style.display = currentStep === 1 ? 'none' : 'inline-block';
    if (next) next.style.display = currentStep === TOTAL_STEPS ? 'none' : 'inline-block';
    if (submit) submit.classList.toggle('d-none', currentStep !== TOTAL_STEPS);
    if (currentStep === TOTAL_STEPS) populateReview();

    const titles = {
        1: 'Vendor Registration - Company Information',
        2: 'Vendor Registration - Contact Information',
        3: 'Vendor Registration - KYC',
        4: 'Vendor Registration - Financial Details',
        5: 'Vendor Registration - Review'
    };
    document.title = titles[currentStep] || 'Vendor Registration';
}

function nextStep() {
    if (currentStep === 1 && !validateCompanyStep()) return;
    if (currentStep === 2 && !validateContactStep()) return;
    if (currentStep === 3 && !validateKycStep()) return;
    if (currentStep === 4 && !validateFinancialStep()) return;
    showStep(currentStep + 1);
}

function prevStep() {
    showStep(currentStep - 1);
}

function validateCompanyStep() {
    const requiredIds = ['companyName', 'address', 'city', 'state', 'pin', 'country'];
    for (const id of requiredIds) {
        const el = document.getElementById(id);
        if (!el || !el.value.trim()) {
            showError('Please complete company and address details before proceeding');
            return false;
        }
    }
    return true;
}

function validateContactStep() {
    const requiredIds = ['vendorType', 'vendorCategory', 'contactPerson', 'emailId', 'attendeeName', 'bdeName', 'meetingWith'];
    for (const id of requiredIds) {
        const el = document.getElementById(id);
        if (!el || !el.value.trim()) {
            showError('Please fill contact information and meeting details');
            return false;
        }
    }
    const email = document.getElementById('emailId');
    if (!email.checkValidity()) {
        showError('Please enter a valid Email-id');
        return false;
    }
    return true;
}

function getClientValues() {
    return Array.from(document.querySelectorAll('.client-name-input'))
        .map((input) => input.value.trim())
        .filter(Boolean);
}

function validateKycStep() {
    const requiredIds = ['experienceDetails', 'msmeReg', 'panNo', 'pfReg', 'aadhaarNo'];
    for (const id of requiredIds) {
        const el = document.getElementById(id);
        if (!el || !el.value.trim()) {
            showError('Please complete the required KYC details');
            return false;
        }
    }
    if (!getClientValues().length) {
        showError('Please add at least one client below the experience details');
        return false;
    }
    const gstNo = document.getElementById('gstNo').value.trim();
    if (gstNo) {
        const gstRequiredIds = ['gstType', 'gstStatus', 'lastGstr1', 'gstPendingStatus'];
        for (const id of gstRequiredIds) {
            const el = document.getElementById(id);
            if (!el || !el.value.trim()) {
                showError('Please complete GST details when GST No is provided');
                return false;
            }
        }
    }
    return true;
}

function validateFinancialStep() {
    const requiredIds = ['turnoverYear1', 'turnoverYear2', 'turnoverYear3', 'bankAccountName', 'bankNameAddress', 'accountType', 'accountNumber', 'bankProofType'];
    for (const id of requiredIds) {
        const el = document.getElementById(id);
        if (!el || !el.value.trim()) {
            showError('Please complete the financial details section');
            return false;
        }
    }
    const bankProofFile = document.getElementById('bankProofFile');
    if (!bankProofFile.files || !bankProofFile.files[0]) {
        showError('Please upload the passbook or cancelled cheque file');
        return false;
    }
    if (state.ocrInProgress) {
        showError('Please wait for the bank proof reading process to finish');
        return false;
    }
    return true;
}

function populateReview() {
    const container = document.getElementById('reviewReportSections');
    if (!container) return;

    const statusValue = (document.querySelector('input[name="qualification_status"]:checked') || { value: '' }).value;
    const reviewTitle = document.getElementById('reviewReportTitle');
    const reviewDateValue = document.getElementById('reviewDateValue');
    const reviewStatusValue = document.getElementById('reviewStatusValue');
    const reviewBanner = document.getElementById('reviewBanner');
    const companyName = getValue('companyName') || 'Vendor Information Review';
    const bankProofFile = document.getElementById('bankProofFile');
    const bankProofFileName = bankProofFile && bankProofFile.files && bankProofFile.files[0]
        ? bankProofFile.files[0].name
        : 'Not uploaded';

    if (reviewTitle) reviewTitle.textContent = `${companyName} - Verification Summary`;
    if (reviewDateValue) reviewDateValue.textContent = new Date().toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
    });
    if (reviewStatusValue) reviewStatusValue.textContent = formatStatus(statusValue || 'pending review');
    if (reviewBanner) {
        reviewBanner.textContent = statusValue
            ? `Vendor marked as ${formatStatus(statusValue)}. Please verify all sections below before submission.`
            : 'Confirm company details, KYC data, financial proof, and vendor status before submitting.';
    }

    const sections = [
        {
            title: 'Company Information',
            rows: [
                ['Company Name', getValue('companyName')],
                ['Address', joinParts([getValue('address'), getValue('address2')])],
                ['Location', joinParts([getValue('city'), getValue('state'), getValue('pin')])],
                ['Country', getValue('country')]
            ]
        },
        {
            title: 'Contact Information',
            rows: [
                ['Vendor Type', getValue('vendorType')],
                ['Vendor Category', getValue('vendorCategory')],
                ['Contact Person', getValue('contactPerson')],
                ['Email-id', getValue('emailId')],
                ['Attendee Name', getValue('attendeeName')],
                ['Contacted By (BDE)', getValue('bdeName')],
                ['Meeting With', getValue('meetingWith')]
            ]
        },
        {
            title: 'KYC Information',
            rows: [
                ['Experience Details', getValue('experienceDetails')],
                ['Client List', getClientValues().join(', ')],
                ['MSME Reg', getValue('msmeReg')],
                ['PAN No', getValue('panNo')],
                ['PF Reg', getValue('pfReg')],
                ['GST No', getValue('gstNo') || 'Not provided'],
                ['GST Type', getValue('gstType') || 'Not provided'],
                ['GST Status', getValue('gstStatus') || 'Not provided'],
                ['Last GSTR-1', getValue('lastGstr1') || 'Not provided'],
                ['Status Pending', getValue('gstPendingStatus') || 'Not provided'],
                ['Aadhar No', getValue('aadhaarNo')],
                ['Labour Welfare Fund', getValue('labourWelfareFund') || 'Not provided'],
                ['Professional Tax', getValue('professionalTax') || 'Not provided']
            ]
        },
        {
            title: 'Financial Details',
            rows: [
                ['Turnover Last Financial Year', getValue('turnoverYear1')],
                ['Turnover Previous Financial Year', getValue('turnoverYear2')],
                ['Turnover Third Financial Year', getValue('turnoverYear3')],
                ['Name as per Bank A/C', getValue('bankAccountName')],
                ['Bank Name & Address', getValue('bankNameAddress')],
                ['Account Type', getValue('accountType')],
                ['Account No', getValue('accountNumber')],
                ['Bank Proof Type', getValue('bankProofType')],
                ['Uploaded Proof File', bankProofFileName]
            ]
        },
        {
            title: 'Approval Check',
            rows: [
                ['Vendor Status', statusValue ? formatStatus(statusValue) : 'Pending review']
            ]
        }
    ];

    container.innerHTML = sections.map(renderReviewSection).join('');
}

function getValue(id) {
    const el = document.getElementById(id);
    return el ? el.value.trim() : '';
}

function joinParts(parts) {
    return parts.filter(Boolean).join(', ');
}

function formatStatus(value) {
    return String(value || '')
        .replace(/-/g, ' ')
        .replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatDisplayValue(value) {
    const text = String(value || '').trim();
    return text ? sanitizeInput(text).replace(/\n/g, '<br>') : '<span class="review-empty">Not provided</span>';
}

function renderReviewSection(section) {
    const rows = section.rows.map(([label, value]) => `
        <div class="review-row">
            <div class="review-label">${sanitizeInput(label)}</div>
            <div class="review-value">${formatDisplayValue(value)}</div>
        </div>
    `).join('');

    return `
        <section class="review-section">
            <div class="review-section-heading">${sanitizeInput(section.title)}</div>
            <div class="review-section-body">${rows}</div>
        </section>
    `;
}

function getCookie(name) {
    const v = document.cookie.match(`(^|;)\\s*${name}\\s*=\\s*([^;]+)`);
    return v ? v.pop() : '';
}

function attachStepLabelHandlers() {
    document.querySelectorAll('.step-label').forEach((el) => {
        const step = parseInt(el.dataset.step || '0', 10);
        el.addEventListener('mouseenter', (e) => {
            e.preventDefault();
            if (step) showStep(step);
        });
        el.addEventListener('click', (e) => {
            e.preventDefault();
            if (step) showStep(step);
        });
    });
}

function sanitizeInput(input) {
    const temp = document.createElement('div');
    temp.textContent = input;
    return temp.innerHTML;
}

function validateFile(file) {
    if (file.size > CONFIG.MAX_FILE_SIZE) {
        showError('File size exceeds 5MB');
        return false;
    }
    if (!CONFIG.ALLOWED_FILE_TYPES.includes(file.type)) {
        showError('Invalid file type');
        return false;
    }
    return true;
}

function showError(message) {
    const errorContainer = document.getElementById('errorContainer');
    if (!errorContainer) return;
    errorContainer.innerHTML = Array.isArray(message)
        ? message.map((item) => `<div>${sanitizeInput(String(item))}</div>`).join('')
        : sanitizeInput(String(message));
    errorContainer.classList.remove('d-none');
    setTimeout(() => errorContainer.classList.add('d-none'), 6000);
}

function showBankProofStatus(message, level) {
    const statusEl = document.getElementById('bankProofStatus');
    if (!statusEl) return;
    statusEl.className = `file-upload-status mt-2 alert p-2 show alert-${level}`;
    statusEl.textContent = message;
}

function updateGstDetailsVisibility() {
    const gstNo = document.getElementById('gstNo').value.trim();
    const section = document.getElementById('gstDetailsSection');
    if (!section) return;
    section.classList.toggle('d-none', !gstNo);
    if (!gstNo) {
        ['gstType', 'gstStatus', 'lastGstr1', 'gstPendingStatus'].forEach((id) => {
            const el = document.getElementById(id);
            if (el) el.value = '';
        });
    }
}

function createClientEntry(value = '') {
    const row = document.createElement('div');
    row.className = 'client-entry-row';
    row.innerHTML = `
        <input class="form-control client-name-input" type="text" maxlength="120" placeholder="Enter client name" value="${sanitizeInput(value)}" required>
        <button type="button" class="btn btn-outline-danger client-remove-btn" aria-label="Remove client">-</button>
    `;
    const removeBtn = row.querySelector('.client-remove-btn');
    removeBtn.addEventListener('click', () => {
        row.remove();
        syncClientRemoveButtons();
    });
    return row;
}

function syncClientRemoveButtons() {
    const rows = Array.from(document.querySelectorAll('.client-entry-row'));
    rows.forEach((row, index) => {
        const removeBtn = row.querySelector('.client-remove-btn');
        if (removeBtn) removeBtn.classList.toggle('d-none', rows.length === 1 && index === 0);
    });
}

function attachClientHandlers() {
    const addClientBtn = document.getElementById('addClientBtn');
    const container = document.getElementById('clientListContainer');
    if (!addClientBtn || !container) return;

    addClientBtn.addEventListener('click', () => {
        container.appendChild(createClientEntry());
        syncClientRemoveButtons();
    });

    container.querySelectorAll('.client-entry-row').forEach((row) => {
        const removeBtn = row.querySelector('.client-remove-btn');
        if (removeBtn) {
            removeBtn.addEventListener('click', () => {
                row.remove();
                syncClientRemoveButtons();
            });
        }
    });
    syncClientRemoveButtons();
}

function parseAccountNumber(text) {
    const normalized = text.replace(/\s+/g, ' ').trim();
    const directPatterns = [
        /account\s*(?:number|no|#)?\s*[:\-]?\s*([0-9]{9,18})/i,
        /a\/c\s*(?:number|no|#)?\s*[:\-]?\s*([0-9]{9,18})/i
    ];
    for (const pattern of directPatterns) {
        const match = normalized.match(pattern);
        if (match) return match[1];
    }

    const candidates = normalized.match(/[0-9]{9,18}/g) || [];
    if (!candidates.length) return '';
    candidates.sort((a, b) => b.length - a.length);
    return candidates[0];
}

function parseBankNameAndAddress(text) {
    const lines = text
        .split(/\r?\n/)
        .map((line) => line.replace(/\s+/g, ' ').trim())
        .filter(Boolean);

    let bankLineIndex = lines.findIndex((line) => /\bbank\b/i.test(line) && !/account|ifsc|micr|statement/i.test(line));
    if (bankLineIndex === -1) bankLineIndex = lines.findIndex((line) => /branch/i.test(line));

    let bankName = '';
    let addressLines = [];

    if (bankLineIndex !== -1) {
        bankName = lines[bankLineIndex];
        for (let i = bankLineIndex + 1; i < lines.length && addressLines.length < 3; i++) {
            const line = lines[i];
            if (/account|a\/c|ifsc|micr|customer|date|phone|email/i.test(line)) break;
            if (/road|rd|street|st|nagar|colony|branch|floor|building|lane|city|state|pin|pincode|\d{6}|,|\-/i.test(line)) {
                addressLines.push(line);
            }
        }
    }

    return {
        bankName,
        bankAddress: addressLines.join(', ')
    };
}

async function extractTextFromImage(file) {
    const result = await Tesseract.recognize(file, 'eng', { logger: () => {} });
    return result.data.text || '';
}

async function extractTextFromPdf(file) {
    if (!window.pdfjsLib) throw new Error('PDF reader not available');
    window.pdfjsLib.GlobalWorkerOptions.workerSrc = CONFIG.PDF_WORKER_URL;

    const buffer = await file.arrayBuffer();
    const pdf = await window.pdfjsLib.getDocument({ data: buffer }).promise;
    const page = await pdf.getPage(1);
    const viewport = page.getViewport({ scale: 2 });
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    canvas.width = viewport.width;
    canvas.height = viewport.height;
    await page.render({ canvasContext: context, viewport }).promise;

    const result = await Tesseract.recognize(canvas, 'eng', { logger: () => {} });
    return result.data.text || '';
}

async function readBankProofDetails(file) {
    if (!validateFile(file)) {
        document.getElementById('bankProofFile').value = '';
        return;
    }

    const accountNumberField = document.getElementById('accountNumber');
    const bankNameAddressField = document.getElementById('bankNameAddress');
    state.ocrInProgress = true;
    showBankProofStatus('Reading bank proof details. Please wait...', 'info');

    try {
        let extractedText = '';
        if (file.type === 'application/pdf') {
            extractedText = await extractTextFromPdf(file);
        } else {
            extractedText = await extractTextFromImage(file);
        }

        const accountNumber = parseAccountNumber(extractedText);
        const bankDetails = parseBankNameAndAddress(extractedText);

        if (accountNumber) accountNumberField.value = accountNumber;
        if (bankDetails.bankName || bankDetails.bankAddress) {
            bankNameAddressField.value = [bankDetails.bankName, bankDetails.bankAddress].filter(Boolean).join('\n');
        }

        if (accountNumber || bankDetails.bankName || bankDetails.bankAddress) {
            showBankProofStatus('Bank proof processed. Bank details and account number were filled where detected.', 'success');
        } else {
            showBankProofStatus('Bank proof uploaded, but auto-reading could not find enough details. Please complete the fields manually.', 'warning');
        }
    } catch (error) {
        console.error(error);
        showBankProofStatus('Bank proof uploaded, but automatic reading failed. Please enter the bank details manually.', 'warning');
    } finally {
        state.ocrInProgress = false;
    }
}

async function handleSubmit(e) {
    e.preventDefault();
    if (state.isSubmitting) return;

    const requiredInputs = document.querySelectorAll('#vendorForm input[required]:not([type="radio"]):not([type="file"]), #vendorForm select[required], #vendorForm textarea[required]');
    for (const input of requiredInputs) {
        if (!input.value.trim()) {
            showError('Please fill required fields');
            return;
        }
    }

    const bankProofFile = document.getElementById('bankProofFile');
    if (!bankProofFile.files || !bankProofFile.files[0]) {
        showError('Please upload the passbook or cancelled cheque file');
        return;
    }

    const email = document.getElementById('emailId');
    if (!email.checkValidity()) {
        showError('Please enter a valid Email-id');
        return;
    }

    if (!validateKycStep() || !validateFinancialStep()) return;

    const qual = document.querySelector('input[name="qualification_status"]:checked');
    if (!qual) {
        showError('Please select vendor status');
        return;
    }

    state.isSubmitting = true;
    document.getElementById('submitBtn').disabled = true;

    try {
        const formData = new FormData();
        const fieldIds = [
            'companyName', 'address', 'address2', 'city', 'state', 'pin', 'country',
            'experienceDetails', 'vendorType', 'vendorCategory', 'contactPerson', 'emailId',
            'attendeeName', 'bdeName', 'meetingWith', 'msmeReg', 'panNo', 'pfReg',
            'gstNo', 'gstType', 'gstStatus', 'lastGstr1', 'gstPendingStatus', 'aadhaarNo',
            'labourWelfareFund', 'professionalTax', 'turnoverYear1', 'turnoverYear2',
            'turnoverYear3', 'bankAccountName', 'bankNameAddress', 'accountType', 'accountNumber',
            'bankProofType'
        ];
        fieldIds.forEach((id) => formData.append(id, getValue(id)));
        formData.append('clientListData', JSON.stringify(getClientValues()));
        formData.append('qualification_status', qual.value);
        if (bankProofFile.files[0]) formData.append('bankProofFile', bankProofFile.files[0]);

        const csrftoken = getCookie('csrftoken');
        const resp = await fetch(REGISTER_URL, {
            method: 'POST',
            body: formData,
            headers: { 'X-CSRFToken': csrftoken }
        });
        const data = await resp.json().catch(() => ({}));
        if (!resp.ok) {
            showError(data.error || 'Failed to submit');
            return;
        }

        const vendorId = data.vendor_id || '';
        if (vendorId) showSuccessModal(vendorId);
        else showError('No vendor ID returned');
    } catch (err) {
        console.error(err);
        showError('Network error');
    } finally {
        state.isSubmitting = false;
        document.getElementById('submitBtn').disabled = false;
    }
}

function showSuccessModal(vendorId) {
    const idEl = document.getElementById('vendorId');
    if (idEl) idEl.textContent = vendorId;
    const modalEl = document.getElementById('successModal');
    if (modalEl && window.bootstrap) bootstrap.Modal.getOrCreateInstance(modalEl).show();
}

function copyVendorId() {
    const code = document.getElementById('vendorId').textContent;
    if (!code) return;
    navigator.clipboard?.writeText(code).then(() => {}).catch(() => {});
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('vendorForm');
    if (form) form.addEventListener('submit', handleSubmit);

    const gstNo = document.getElementById('gstNo');
    if (gstNo) gstNo.addEventListener('input', updateGstDetailsVisibility);

    const bankProofFile = document.getElementById('bankProofFile');
    if (bankProofFile) {
        bankProofFile.addEventListener('change', async (event) => {
            const file = event.target.files && event.target.files[0];
            if (file) await readBankProofDetails(file);
        });
    }

    attachStepLabelHandlers();
    attachClientHandlers();
    updateGstDetailsVisibility();
    showStep(1);
});
