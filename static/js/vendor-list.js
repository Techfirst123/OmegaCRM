const vendorDetailData = JSON.parse(document.getElementById('vendor-detail-data')?.textContent || '[]');

function vdEscape(value) {
    const div = document.createElement('div');
    div.textContent = value;
    return div.innerHTML;
}

function vdDisplay(value) {
    if (value && typeof value === 'object' && value.html) return value.html;
    const text = Array.isArray(value) ? value.filter(Boolean).join(', ') : String(value || '').trim();
    return text ? vdEscape(text).replace(/\n/g, '<br>') : '<span class="vendor-detail-empty">Not provided</span>';
}

function vdStatusClass(value) {
    const normalized = String(value || '').trim().toLowerCase();
    return normalized || 'unknown';
}

function vdStatusText(value) {
    const normalized = String(value || '').trim();
    if (!normalized) return 'Pending';
    return normalized.replace(/-/g, ' ').replace(/\b\w/g, (char) => char.toUpperCase());
}

function buildVendorSection(title, rows) {
    const content = rows.map(([label, value]) => `
        <div class="vendor-detail-row">
            <div class="vendor-detail-label">${vdEscape(label)}</div>
            <div class="vendor-detail-value">${vdDisplay(value)}</div>
        </div>
    `).join('');

    return `
        <section class="vendor-detail-section">
            <div class="vendor-detail-section-title">${vdEscape(title)}</div>
            <div class="vendor-detail-grid">${content}</div>
        </section>
    `;
}

function renderVendorDrawer(vendor) {
    const title = document.getElementById('vendorDetailTitle');
    const subtitle = document.getElementById('vendorDetailSubtitle');
    const status = document.getElementById('vendorDetailStatus');
    const created = document.getElementById('vendorDetailCreated');
    const body = document.getElementById('vendorDetailBody');

    if (title) title.textContent = `${vendor.company_name || 'Vendor'} Details`;
    if (subtitle) subtitle.textContent = `${vendor.vendor_id || '-'} | ${vendor.vendor_type || 'Vendor profile'}`;
    if (status) {
        status.textContent = vdStatusText(vendor.qualification_status);
        status.className = `status-pill ${vdStatusClass(vendor.qualification_status)}`;
    }
    if (created) created.textContent = vendor.created_at || '-';

    const sections = [
        buildVendorSection('Company Information', [
            ['Vendor ID', vendor.vendor_id],
            ['Company Name', vendor.company_name],
            ['Address', [vendor.address, vendor.address2].filter(Boolean).join(', ')],
            ['City', vendor.city],
            ['State', vendor.state],
            ['Pin Code', vendor.pin_code],
            ['Country', vendor.country],
            ['Experience Details', vendor.experience_details]
        ]),
        buildVendorSection('Contact Information', [
            ['Vendor Type', vendor.vendor_type],
            ['Vendor Category', vendor.vendor_category],
            ['Contact Person', vendor.contact_person],
            ['Email Id', vendor.email_id],
            ['Attendee Name', vendor.attendee_name],
            ['Contacted By (BDE)', vendor.bde_name],
            ['Meeting With', vendor.meeting_with]
        ]),
        buildVendorSection('KYC Information', [
            ['MSME Reg', vendor.msme_reg],
            ['PAN No', vendor.pan_no],
            ['PF Reg', vendor.pf_reg],
            ['GST No', vendor.gst_no],
            ['GST Type', vendor.gst_type],
            ['GST Status', vendor.gst_status],
            ['Last GSTR-1', vendor.last_gstr1],
            ['Status Pending', vendor.gst_pending_status],
            ['Aadhaar No', vendor.aadhaar_no],
            ['Labour Welfare Fund', vendor.labour_welfare_fund],
            ['Professional Tax', vendor.professional_tax],
            ['Client List', vendor.client_list]
        ]),
        buildVendorSection('Financial Details', [
            ['Turnover Last Financial Year', vendor.turnover_year_1],
            ['Turnover Previous Financial Year', vendor.turnover_year_2],
            ['Turnover Third Financial Year', vendor.turnover_year_3],
            ['Name as per Bank A/C', vendor.bank_account_name],
            ['Bank Name & Address', vendor.bank_name_address],
            ['Account Type', vendor.account_type],
            ['Account Number', vendor.account_number],
            ['Bank Proof Type', vendor.bank_proof_type],
            ['Bank Proof File', vendor.bank_proof_url ? { html: `<a href="${vdEscape(vendor.bank_proof_url)}" target="_blank" rel="noopener">Open uploaded document</a>` } : '']
        ]),
        buildVendorSection('Registration Audit', [
            ['Status', vdStatusText(vendor.qualification_status)],
            ['Created At', vendor.created_at]
        ])
    ];

    if (body) body.innerHTML = sections.join('');
}

function openVendorDrawer(vendorId) {
    const vendor = vendorDetailData.find((item) => item.vendor_id === vendorId);
    if (!vendor) return;

    renderVendorDrawer(vendor);

    const drawer = document.getElementById('vendorDetailDrawer');
    const backdrop = document.getElementById('vendorDetailBackdrop');
    if (drawer) {
        drawer.classList.add('is-open');
        drawer.setAttribute('aria-hidden', 'false');
    }
    if (backdrop) backdrop.classList.add('is-visible');
    document.body.classList.add('overflow-hidden');
}

function closeVendorDrawer() {
    const drawer = document.getElementById('vendorDetailDrawer');
    const backdrop = document.getElementById('vendorDetailBackdrop');
    if (drawer) {
        drawer.classList.remove('is-open');
        drawer.setAttribute('aria-hidden', 'true');
    }
    if (backdrop) backdrop.classList.remove('is-visible');
    document.body.classList.remove('overflow-hidden');
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.vendor-view-btn').forEach((button) => {
        button.addEventListener('click', () => openVendorDrawer(button.dataset.vendorId || ''));
    });

    document.getElementById('vendorDetailCloseBtn')?.addEventListener('click', closeVendorDrawer);
    document.getElementById('vendorDetailBackdrop')?.addEventListener('click', closeVendorDrawer);

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') closeVendorDrawer();
    });
});
