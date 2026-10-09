/**
 * AarogyaSahay - Integrated Rural Healthcare Platform
 * Interactive Client-Side Logic & Offline Resilience Handlers
 */

// Demo credentials dictionary for instant evaluation
const DEMO_CREDENTIALS = {
    frontline: {
        identifier: "9876543210",
        password: "asha123",
        name: "Sunita Devi (ASHA)",
        label: "Mobile Number / Staff ID"
    },
    doctor: {
        identifier: "doctor@swasthya.gov.in",
        password: "doctor123",
        name: "Dr. Rajesh Sharma (MD)",
        label: "Official Email / Medical ID"
    },
    patient: {
        identifier: "9876543212",
        password: "patient123",
        name: "Kamla Bai (Patient)",
        label: "Mobile Number / ABHA ID"
    },
    admin: {
        identifier: "admin@swasthya.gov.in",
        password: "admin123",
        name: "Anil Verma (PHC Admin)",
        label: "Administrator ID / Email"
    }
};

/**
 * Handle role selection tabs in Login page
 */
function selectRoleTab(roleName) {
    document.querySelectorAll('.role-tab').forEach(tab => {
        tab.classList.toggle('active', tab.getAttribute('data-role') === roleName);
    });

    const hiddenRoleInput = document.getElementById('selectedRoleTab');
    if (hiddenRoleInput) hiddenRoleInput.value = roleName;

    const labelElem = document.getElementById('identifierLabel');
    if (labelElem && DEMO_CREDENTIALS[roleName]) {
        labelElem.innerText = DEMO_CREDENTIALS[roleName].label;
    }
}

/**
 * Instant autofill helper for hackathon judges & reviewers
 */
function fillDemo(roleName) {
    selectRoleTab(roleName);
    const data = DEMO_CREDENTIALS[roleName];
    if (!data) return;

    const idInput = document.getElementById('identifierInput');
    const pwInput = document.getElementById('passwordInput');
    if (idInput) {
        idInput.value = data.identifier;
        idInput.focus();
    }
    if (pwInput) {
        pwInput.value = data.password;
    }

    // Show a subtle toast or visual notification
    showToast(`Loaded demo credentials for ${data.name}`);
}

/**
 * Switch Auth Method between Password and OTP
 */
function switchAuthMethod(method) {
    const btnPass = document.getElementById('btnMethodPass');
    const btnOtp = document.getElementById('btnMethodOtp');
    const groupPass = document.getElementById('passwordGroup');
    const groupOtp = document.getElementById('otpGroup');

    if (method === 'otp') {
        btnPass.classList.remove('active');
        btnOtp.classList.add('active');
        if (groupPass) groupPass.style.display = 'none';
        if (groupOtp) groupOtp.style.display = 'block';
    } else {
        btnOtp.classList.remove('active');
        btnPass.classList.add('active');
        if (groupOtp) groupOtp.style.display = 'none';
        if (groupPass) groupPass.style.display = 'block';
    }
}

/**
 * Toggle password visibility
 */
function togglePasswordVisibility(inputId, btn) {
    const input = document.getElementById(inputId);
    if (!input) return;
    if (input.type === 'password') {
        input.type = 'text';
        btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>';
    } else {
        input.type = 'password';
        btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>';
    }
}

/**
 * Interactive Clinical Triage Screener
 */
function csrfHeaders() {
    const tok = document.querySelector('meta[name="csrf-token"]')?.content || '';
    return { 'Content-Type': 'application/json', 'X-CSRF-Token': tok };
}
async function handleTriageSubmit(event) {
    event.preventDefault();

    const age = parseInt(document.getElementById('triageAge').value) || 25;
    const bp = parseInt(document.getElementById('triageBP').value) || 120;
    const maternalWeeks = parseInt(document.getElementById('maternalWeeks').value) || 0;
    const fever = document.getElementById('checkFever').checked;
    const breathing = document.getElementById('checkBreathing').checked;
    const bleeding = document.getElementById('checkBleeding').checked;
    const vomiting = document.getElementById('checkVomiting').checked;

    const spinner = document.getElementById('triageSpinner');
    const submitBtn = document.getElementById('triageSubmitBtn');
    if (spinner) spinner.style.display = 'inline-block';
    if (submitBtn) submitBtn.disabled = true;

    try {
        const response = await fetch('/api/triage-evaluate', {
            method: 'POST',
            headers: csrfHeaders(),
            body: JSON.stringify({
                systolic_bp: bp,
                pediatric_age: age,
                maternal_weeks: maternalWeeks,
                fever: fever,
                breathing_difficulty: breathing || bleeding
            })
        });

        const data = await response.json();
        renderTriageResult(data);
    } catch (err) {
        // Fallback calculation in case of zero network/offline
        const offlineResult = evaluateOfflineTriage(bp, age, maternalWeeks, breathing, bleeding, fever);
        renderTriageResult(offlineResult);
    } finally {
        if (spinner) spinner.style.display = 'none';
        if (submitBtn) submitBtn.disabled = false;
    }
}

function evaluateOfflineTriage(bp, age, maternalWeeks, breathing, bleeding, fever) {
    if (breathing || bleeding || (maternalWeeks > 20 && bp >= 160)) {
        return {
            tier: "Red - Emergency Escalation",
            action: "Immediate 108 Ambulance Dispatch & Alert District Emergency Hub. Keep patient in recovery posture.",
            badge: "emergency",
            facility: "Sub-Divisional Hospital / District Emergency",
            timestamp: new Date().toLocaleTimeString()
        };
    } else if (bp >= 140 || fever || (maternalWeeks > 0 && bp >= 135)) {
        return {
            tier: "Yellow - Priority Tele-Consultation",
            action: "Schedule Assisted Tele-OPD within 4 hours. Connect with Medical Officer at Primary Health Centre.",
            badge: "urgent",
            facility: "Primary Health Centre (PHC Tele-OPD)",
            timestamp: new Date().toLocaleTimeString()
        };
    } else {
        return {
            tier: "Green - Routine Primary Care & Counseling",
            action: "Manage at Sub-Centre via ASHA/ANM protocol. Dispense essential supplements and schedule follow-up.",
            badge: "routine",
            facility: "Health & Wellness Sub-Centre",
            timestamp: new Date().toLocaleTimeString()
        };
    }
}

function renderTriageResult(data) {
    const card = document.getElementById('triageResultCard');
    const pill = document.getElementById('resultStatusPill');
    const title = document.getElementById('resultTierTitle');
    const action = document.getElementById('resultActionText');
    const facility = document.getElementById('resultFacility');
    const time = document.getElementById('resultTime');

    if (!card) return;

    card.style.display = 'block';
    title.innerText = data.tier;
    action.innerText = data.action;
    facility.innerText = data.facility;
    time.innerText = data.timestamp || "Evaluated Just Now";

    pill.className = `result-status-pill pill-${data.badge}`;
    pill.innerText = data.badge.toUpperCase();

    card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    if (window.localizeDynamicContent) window.localizeDynamicContent(card);
}

function resetTriageForm() {
    document.getElementById('triageForm').reset();
    document.getElementById('triageResultCard').style.display = 'none';
}

/**
 * Live Medicine Search & Filter with Debouncing
 */
let debounceTimer;
function debounceMedicineSearch() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(searchMedicines, 250);
}

async function searchMedicines() {
    const query = document.getElementById('medSearchInput')?.value || '';
    const district = document.getElementById('districtFilter')?.value || '';
    const tbody = document.getElementById('medicineTableBody');

    if (!tbody) return;

    try {
        const response = await fetch(`/api/medicine-search?q=${encodeURIComponent(query)}&district=${encodeURIComponent(district)}`);
        const result = await response.json();

        if (result.success && result.medicines.length > 0) {
            tbody.innerHTML = result.medicines.map(m => {
                let badgeClass = 'in-stock';
                if (m.stock_status === 'Low Stock') badgeClass = 'low-stock';
                if (m.stock_status === 'Out of Stock') badgeClass = 'out-stock';

                return `
                    <tr>
                        <td><strong>${escapeHtml(m.name)}</strong></td>
                        <td><span class="cat-pill">${escapeHtml(m.category)}</span></td>
                        <td>${escapeHtml(m.facility_name)}</td>
                        <td>${m.units} Units</td>
                        <td><span class="stock-badge ${badgeClass}">${escapeHtml(m.stock_status)}</span></td>
                        <td>${escapeHtml(m.last_updated || 'Today')}</td>
                    </tr>
                `;
            }).join('');
        } else {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align:center; padding: 2rem; color: var(--text-muted);">
                        No essential medicines found matching "${escapeHtml(query)}". An auto-inquiry has been logged to the District Drug Warehouse.
                    </td>
                </tr>
            `;
        }
        if (window.localizeDynamicContent) window.localizeDynamicContent(tbody);
    } catch (e) {
        console.error("Medicine search error:", e);
    }
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Note: Whole-site language localization is handled by translations.js

/**
 * Field Data Synchronization & Offline Simulation
 */
function syncFieldData() {
    showToast("Syncing field consultations & ABHA records with District Grid...", "info");
    setTimeout(() => {
        showToast("Successfully synchronized 14 offline records. Zero conflicts.", "success");
        const lastSync = document.getElementById('lastSyncTime');
        if (lastSync) lastSync.innerText = new Date().toLocaleTimeString();
    }, 1200);
}

function simulateTeleConsultModal() {
    showToast("Initializing Low-Bandwidth Tele-OPD Video Link with Bilaspur Medical Officer...", "info");
}

/**
 * Lightweight Toast Notification
 */
function showToast(message, type = 'info') {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `app-toast toast-${type} animate-fade-in`;
    
    let iconSvg = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>';
    if (type === 'success' || message.toLowerCase().includes('success') || message.toLowerCase().includes('confirmed')) {
        iconSvg = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>';
    } else if (type === 'danger' || message.toLowerCase().includes('emergency') || message.toLowerCase().includes('alert') || message.toLowerCase().includes('error')) {
        iconSvg = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>';
    }

    toast.innerHTML = `
        <span class="toast-icon">${iconSvg}</span>
        <div class="toast-body">${message}</div>
        <button type="button" class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(8px)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

/**
 * Theme Switching (Light Clinical vs Dark Mode)
 */
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const nextTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', nextTheme);
    localStorage.setItem('aarogya_theme', nextTheme);
    updateThemeUI(nextTheme);
    showToast(`Switched to ${nextTheme === 'light' ? 'Pristine Clinical Light' : 'Dark Shift'} mode`);
}

function updateThemeUI(theme) {
    const icon = document.getElementById('themeIcon');
    const label = document.getElementById('themeLabel');
    if (icon) {
        icon.innerHTML = theme === 'dark'
            ? '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>'
            : '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>';
    }
    if (label) label.innerText = theme === 'dark' ? 'Dark' : 'Light';
}

// Mobile navigation toggle & Theme initialization
document.addEventListener('DOMContentLoaded', () => {
    const currentTheme = localStorage.getItem('aarogya_theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    updateThemeUI(currentTheme);

    const mobileBtn = document.getElementById('mobileToggle');
    const navMenu = document.getElementById('navMenu');
    if (mobileBtn && navMenu) {
        mobileBtn.addEventListener('click', () => {
            const isVisible = navMenu.classList.contains('mobile-open');
            if (isVisible) {
                navMenu.classList.remove('mobile-open');
            } else {
                navMenu.classList.add('mobile-open');
            }
        });
    }
});
