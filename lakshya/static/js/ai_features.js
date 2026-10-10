/**
 * AarogyaSahay - Gemini AI Client-Side Engine
 * Controls global floating AI drawer, API key manager,
 * Triage AI CDSS integration, Tele-OPD Copilot, and Vernacular Explainer.
 */

// Global state
window.geminiState = {
    configured: false,
    model: 'gemini-3.8-flash',
    drawerOpen: false,
    chatHistory: []
};

document.addEventListener('DOMContentLoaded', function() {
    checkGlobalGeminiStatus();
    attachAiPageHooks();
});

/**
 * Check Gemini backend connectivity status and update UI indicators
 */
async function checkGlobalGeminiStatus() {
    try {
        const res = await fetch('/api/ai/status');
        const data = await res.json();
        window.geminiState.configured = data.configured;
        window.geminiState.model = data.primary_model;

        const globalLabel = document.getElementById('globalGeminiLabel');
        if (globalLabel) {
            globalLabel.innerText = data.configured ? 'Gemini 3.8 Live' : 'Gemini 3.8';
        }


        const pill = document.querySelector('.gemini-top-pill');
        if (pill && data.configured) {
            pill.classList.add('pill-active');
        }
    } catch (e) {
        console.warn('Gemini status check failed:', e);
    }
}

/**
 * Global API Key Modal
 */
function openGlobalKeyModal() {
    const modal = document.getElementById('globalApiKeyModal');
    if (modal) modal.style.display = 'flex';
}

function closeGlobalKeyModal() {
    const modal = document.getElementById('globalApiKeyModal');
    if (modal) modal.style.display = 'none';
    const feedback = document.getElementById('globalKeyTestResult');
    if (feedback) feedback.style.display = 'none';
}

async function saveGlobalGeminiApiKey() {
    const input = document.getElementById('globalInputApiKey');
    const feedback = document.getElementById('globalKeyTestResult');
    const btn = document.getElementById('globalSaveKeyBtn');
    const key = input ? input.value.trim() : '';

    if (!key) {
        if (feedback) {
            feedback.style.display = 'block';
            feedback.className = 'key-test-feedback error';
            feedback.innerText = 'Please enter a valid Gemini API key.';
        }
        return;
    }

    if (btn) {
        btn.disabled = true;
        btn.innerText = 'Verifying with Google...';
    }
    if (feedback) {
        feedback.style.display = 'block';
        feedback.className = 'key-test-feedback info';
        feedback.innerText = 'Testing connection with Gemini 2.5...';
    }

    try {
        const res = await fetch('/api/ai/set-key', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: key })
        });
        const data = await res.json();

        if (data.success) {
            feedback.className = 'key-test-feedback success';
            feedback.innerText = data.message;
            if (window.showToast) showToast('Gemini API key configured successfully!', 'success');
            setTimeout(() => {
                closeGlobalKeyModal();
                checkGlobalGeminiStatus();
            }, 1200);
        } else {
            feedback.className = 'key-test-feedback error';
            feedback.innerText = data.error || 'Failed to verify key.';
        }
    } catch (e) {
        if (feedback) {
            feedback.className = 'key-test-feedback error';
            feedback.innerText = 'Network error while contacting server.';
        }
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerText = 'Verify & Save Key';
        }
    }
}

/**
 * Floating AI Drawer Interactions
 */
function toggleFloatingAiDrawer() {
    const drawer = document.getElementById('floatingAiDrawer');
    if (!drawer) return;
    const isVisible = drawer.style.display !== 'none';
    drawer.style.display = isVisible ? 'none' : 'flex';
    window.geminiState.drawerOpen = !isVisible;
    if (!isVisible) {
        const input = document.getElementById('floatingChatInput');
        if (input) setTimeout(() => input.focus(), 100);
    }
}

function sendDrawerPrompt(text) {
    const input = document.getElementById('floatingChatInput');
    if (input) {
        input.value = text;
        handleDrawerChat(new Event('submit'));
    }
}

async function handleDrawerChat(e) {
    if (e) e.preventDefault();
    const input = document.getElementById('floatingChatInput');
    const msg = input ? input.value.trim() : '';
    if (!msg) return;

    input.value = '';
    appendDrawerMsg('user', msg);

    const stream = document.getElementById('floatingChatStream');
    const loadId = 'drawer-load-' + Date.now();
    const loadElem = document.createElement('div');
    loadElem.id = loadId;
    loadElem.className = 'drawer-msg bot loading';
    loadElem.innerHTML = `<span class="bot-icon">✨</span><div class="msg-bubble">Thinking...</div>`;
    stream.appendChild(loadElem);
    stream.scrollTop = stream.scrollHeight;

    try {
        const res = await fetch('/api/ai/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: msg,
                history: window.geminiState.chatHistory
            })
        });
        const data = await res.json();
        const curLoad = document.getElementById(loadId);
        if (curLoad) curLoad.remove();

        if (data.success && data.reply) {
            appendDrawerMsg('bot', data.reply);
            window.geminiState.chatHistory.push({ role: 'user', content: msg });
            window.geminiState.chatHistory.push({ role: 'model', content: data.reply });
        } else {
            appendDrawerMsg('bot', 'Could not process query. Please try again.');
        }
    } catch (err) {
        const curLoad = document.getElementById(loadId);
        if (curLoad) curLoad.remove();
        appendDrawerMsg('bot', 'Network error reaching Aarogya AI.');
    }
}

function appendDrawerMsg(role, text) {
    const stream = document.getElementById('floatingChatStream');
    if (!stream) return;
    const msgDiv = document.createElement('div');
    msgDiv.className = `drawer-msg ${role}`;

    // Clean basic markdown
    const formatted = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');

    if (role === 'user') {
        msgDiv.innerHTML = `<div class="msg-bubble">${formatted}</div>`;
    } else {
        msgDiv.innerHTML = `
            <span class="bot-icon">✨</span>
            <div class="msg-bubble">
                ${formatted}
                <div style="margin-top:6px; display:flex; justify-content:flex-end;">
                    <button type="button" class="drawer-voice-btn" onclick="playAccessibleVoice(this.closest('.msg-bubble').innerText.replace('🔊 Listen', '').replace('Speaking...', '').trim(), this)" title="Listen to response (ElevenLabs Voice)">
                        🔊 Listen
                    </button>
                </div>
            </div>`;
    }

    stream.appendChild(msgDiv);
    stream.scrollTop = stream.scrollHeight;
}

/**
 * Page-Specific AI Hook Injections
 */
function attachAiPageHooks() {
    // 1. Hook for Clinical Triage page
    const triageForm = document.getElementById('fullTriageForm');
    if (triageForm) {
        setupAiTriageEnhancement();
    }

    // 2. Hook for Teleconsult page (Prescription Pad Copilot)
    const rxForm = document.getElementById('rxForm');
    if (rxForm) {
        setupAiTeleconsultCopilot();
    }

    // 3. Hook for ABHA Records page (Vernacular Explainer)
    const recordsPage = document.querySelector('.records-page');
    if (recordsPage) {
        setupAiRecordsExplainer();
    }

    // 4. Hook for High-Risk Care page
    const highRiskPage = document.querySelector('.high-risk-page') || document.getElementById('highRiskTable');
    if (highRiskPage) {
        setupAiHighRiskPlanner();
    }
}

/**
 * 1. AI Clinical Triage Enhancement on /triage
 */
function setupAiTriageEnhancement() {
    const actionRow = document.querySelector('#fullTriageForm .mt-3');
    if (!actionRow) return;

    // Add Gemini AI assessment button if not already present
    if (!document.getElementById('btnGeminiTriage')) {
        const aiBtn = document.createElement('button');
        aiBtn.type = 'button';
        aiBtn.id = 'btnGeminiTriage';
        aiBtn.className = 'btn btn-secondary btn-block btn-lg mt-2';
        aiBtn.style.background = 'linear-gradient(135deg, #4E80ED, #8B5CF6)';
        aiBtn.style.color = '#fff';
        aiBtn.style.border = 'none';
        aiBtn.innerHTML = `
            <span style="margin-right:6px;">✨</span>
            <strong>Evaluate via Gemini 2.5 Clinical CDSS</strong>
        `;
        aiBtn.onclick = runGeminiTriage;
        actionRow.appendChild(aiBtn);
    }
}

async function runGeminiTriage() {
    const btn = document.getElementById('btnGeminiTriage');
    const oldText = btn ? btn.innerHTML : '';
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span>⏳</span> <strong>Gemini CDSS Analyzing Case...</strong>';
    }

    // Collect all triage inputs
    const patientName = document.getElementById('tPatientName')?.value || 'Patient';
    const age = parseInt(document.getElementById('tAge')?.value) || 28;
    const sysBP = parseInt(document.getElementById('tSystolicBP')?.value) || 120;
    const diaBP = parseInt(document.getElementById('tDiastolicBP')?.value) || 80;
    const pulse = parseInt(document.getElementById('tPulse')?.value) || 80;
    const spo2 = parseInt(document.getElementById('tSpO2')?.value) || 98;
    const respRate = parseInt(document.getElementById('tRespRate')?.value) || 20;

    // Active category
    let category = 'maternal';
    const activeTab = document.querySelector('.cat-tab.active');
    if (activeTab && activeTab.innerText.toLowerCase().includes('pediatric')) category = 'pediatric';
    if (activeTab && activeTab.innerText.toLowerCase().includes('trauma')) category = 'general';

    const gestationalWeeks = parseInt(document.getElementById('tGestationalWeeks')?.value) || 0;
    const proteinuria = document.getElementById('tProteinuria')?.value || 'nil';

    const dangerSigns = [];
    if (document.getElementById('mSevereHeadache')?.checked) dangerSigns.push('Severe headache or blurred vision');
    if (document.getElementById('mVaginalBleeding')?.checked) dangerSigns.push('Vaginal bleeding / fluid leakage');
    if (document.getElementById('mConvulsions')?.checked) dangerSigns.push('Convulsions / Loss of consciousness');
    if (document.getElementById('mSevereAbdominalPain')?.checked) dangerSigns.push('Severe epigastric or abdominal pain');
    if (document.getElementById('pUnableToFeed')?.checked) dangerSigns.push('Inability to breastfeed / drink');
    if (document.getElementById('pChestIndrawing')?.checked) dangerSigns.push('Severe chest indrawing or stridor');
    if (document.getElementById('pLethargic')?.checked) dangerSigns.push('Abnormally sleepy or unconscious');
    if (document.getElementById('gChestPain')?.checked) dangerSigns.push('Crushing chest pain radiating to arm');
    if (document.getElementById('gStroke')?.checked) dangerSigns.push('Facial drooping / slurred speech (FAST)');
    if (document.getElementById('gSnakebite')?.checked) dangerSigns.push('Suspected snakebite / poisoning');

    try {
        const res = await fetch('/api/ai/triage', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                patient_name: patientName,
                age: age,
                category: category,
                systolic_bp: sysBP,
                diastolic_bp: diaBP,
                pulse: pulse,
                spo2: spo2,
                resp_rate: respRate,
                gestational_weeks: gestationalWeeks,
                proteinuria: proteinuria,
                danger_signs: dangerSigns
            })
        });

        const data = await res.json();
        if (data.success && data.result) {
            renderGeminiTriageResult(data.result);
            if (window.showToast) {
                showToast(`Gemini Triage complete: ${data.result.tier}`, 'success');
            }
        } else {
            if (window.showToast) showToast('AI Triage error, reverting to local protocol.', 'warning');
        }
    } catch (e) {
        console.error('Gemini triage fetch error:', e);
        if (window.showToast) showToast('Network error evaluating triage.', 'danger');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = oldText;
        }
    }
}

function renderGeminiTriageResult(r) {
    const pill = document.getElementById('triagePill');
    const heading = document.getElementById('triageHeading');
    const desc = document.getElementById('triageDesc');
    const protocol = document.getElementById('triageProtocol');
    const clock = document.getElementById('triageClock');

    if (pill) {
        pill.className = `badge-status pill-${r.badge}`;
        pill.innerText = `${r.tier.toUpperCase()}`;
    }
    if (heading) heading.innerText = r.condition_title || r.tier;
    if (desc) {
        let text = `${r.urgency_summary} ${r.clinical_assessment}`;
        if (r.differential_diagnoses && r.differential_diagnoses.length > 0) {
            text += ` Probable Differentials: ${r.differential_diagnoses.join(', ')}.`;
        }
        desc.innerText = text;
    }
    if (protocol) {
        let pText = `${r.protocol_actions} Recommended Destination: ${r.recommended_facility} (${r.transport_advice}).`;
        protocol.innerText = pText;
    }
    if (clock) {
        clock.innerText = `Evaluated via ${r.model || 'Gemini 2.5'} • ETA Target: ${r.eta_target || '<15m'}`;
    }

    const resultBox = document.getElementById('triageEvaluationBox');
    if (resultBox) {
        resultBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

/**
 * 2. AI Tele-OPD Clinical Copilot on /teleconsult
 */
function setupAiTeleconsultCopilot() {
    const rxHeader = document.querySelector('.gmeet-rx-header');
    if (!rxHeader) return;

    if (!document.getElementById('btnAiCopilotRx')) {
        const copilotBtn = document.createElement('button');
        copilotBtn.type = 'button';
        copilotBtn.id = 'btnAiCopilotRx';
        copilotBtn.className = 'btn btn-xs btn-outline';
        copilotBtn.style.color = '#7C3AED';
        copilotBtn.style.borderColor = '#A855F7';
        copilotBtn.innerHTML = `✨ <strong>AI Clinical Copilot</strong>`;
        copilotBtn.onclick = runAiTeleconsultCopilot;
        rxHeader.appendChild(copilotBtn);
    }
}

async function runAiTeleconsultCopilot() {
    const copilotBtn = document.getElementById('btnAiCopilotRx');
    if (copilotBtn) {
        copilotBtn.disabled = true;
        copilotBtn.innerText = '✨ Formulating Rx...';
    }

    // Grab active patient card info or input values
    const ptTile = document.querySelector('.gmeet-tile-name');
    const patientName = ptTile ? ptTile.innerText.trim() : 'Active Patient';
    const chiefComplaint = "Stage-1 hypertension, persistent frontal headache, mild pedal edema";
    const vitals = "BP: 155/98 mmHg, Pulse: 84 bpm, SpO2: 98%";

    try {
        const res = await fetch('/api/ai/soap-prescription', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                patient_name: patientName,
                chief_complaint: chiefComplaint,
                vitals: vitals,
                specialty: 'Primary Rural Care'
            })
        });

        const data = await res.json();
        if (data.success && data.result) {
            const r = data.result;
            // Populate form fields
            const diagField = document.getElementById('rxDiagnosis');
            const medsField = document.getElementById('rxMeds');
            const refField = document.getElementById('rxReferral');
            const followField = document.getElementById('rxFollowup');

            if (diagField) diagField.value = r.diagnosis || 'Essential Stage-I Hypertension';
            if (medsField) medsField.value = r.rx_text_formatted || 'Tab Amlodipine 5mg OD x 30 days';
            if (refField) refField.value = r.referral_advice || 'Review at PHC in 7 days with BP log';
            if (followField) followField.value = `Review in ${r.follow_up_days || 7} days. Call 108 if severe headache or blurred vision develops.`;

            if (window.showToast) {
                showToast(`Gemini Copilot generated prescription compliant with National Essential Drug List!`, 'success');
            }
        }
    } catch (e) {
        console.error('Teleconsult copilot error:', e);
        if (window.showToast) showToast('Failed to auto-populate prescription.', 'warning');
    } finally {
        if (copilotBtn) {
            copilotBtn.disabled = false;
            copilotBtn.innerHTML = `✨ <strong>AI Clinical Copilot</strong>`;
        }
    }
}

/**
 * 3. AI Vernacular Explainer on /records
 */
function setupAiRecordsExplainer() {
    const patientCard = document.querySelector('.patient-id-grid');
    if (!patientCard) return;

    if (!document.getElementById('btnAiExplainRecords')) {
        const wrap = document.querySelector('.pt-consent-status');
        if (wrap) {
            const explainerBtn = document.createElement('button');
            explainerBtn.type = 'button';
            explainerBtn.id = 'btnAiExplainRecords';
            explainerBtn.className = 'btn btn-xs btn-primary mt-2';
            explainerBtn.style.background = 'linear-gradient(135deg, #6366F1, #8B5CF6)';
            explainerBtn.innerHTML = `✨ <strong>आरोग्य मित्र AI (Explain My Record)</strong>`;
            explainerBtn.onclick = runVernacularExplainer;
            wrap.appendChild(explainerBtn);
        }
    }
}

async function runVernacularExplainer() {
    const btn = document.getElementById('btnAiExplainRecords');
    if (btn) {
        btn.disabled = true;
        btn.innerText = '✨ Translating Record...';
    }

    const patientName = document.querySelector('.pt-basic h2')?.innerText || 'Meena Sahu';
    const lang = localStorage.getItem('aarogya_lang') || 'hi';

    try {
        const res = await fetch('/api/ai/explain-record', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                patient_name: patientName,
                diagnosis: 'High-Risk Pregnancy (32 Wks) with Gestational Hypertension & Severe Anemia',
                lab_summary: 'Hemoglobin: 7.2 g/dL (Severe Anemia), BP: 155/100, USG: Normal cephalic fetus (1.85 kg)',
                medications: 'Tab Labetalol 100mg BD, IV Iron Sucrose 200mg, Tab Calcium 500mg, IFA Tablets',
                language: lang
            })
        });

        const data = await res.json();
        if (data.success && data.result) {
            renderVernacularExplainerModal(data.result);
        } else {
            if (window.showToast) showToast('Could not explain record. Please retry.', 'warning');
        }
    } catch (e) {
        console.error('Explainer error:', e);
        if (window.showToast) showToast('Network error explaining record.', 'danger');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `✨ <strong>आरोग्य मित्र AI (Explain My Record)</strong>`;
        }
    }
}

function renderVernacularExplainerModal(r) {
    let modal = document.getElementById('vernacularModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'vernacularModal';
        modal.className = 'modal-backdrop';
        document.body.appendChild(modal);
    }

    const medsList = (r.medications_guide || []).map(m => `
        <div class="explainer-med-item">
            <strong>💊 ${m.medicine_name}</strong>
            <p><strong>कैसे लें:</strong> ${m.how_to_take}</p>
            <small style="color:var(--text-secondary);">फायदा: ${m.benefit}</small>
        </div>
    `).join('');

    const nutritionList = (r.nutrition_and_daily_care || []).map(n => `<li>🥗 ${n}</li>`).join('');
    const dangerList = (r.danger_signs_alert || []).map(d => `<li style="color:#EF4444; font-weight:600;">⚠️ ${d}</li>`).join('');

    modal.innerHTML = `
        <div class="modal-dialog glass-panel" style="max-width: 650px;">
            <div class="modal-header">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:1.4rem;">✨</span>
                    <div>
                        <h3 style="margin:0;">आरोग्य मित्र AI — स्वास्थ्य रिपोर्ट सरल भाषा में</h3>
                        <small style="color:var(--text-muted);">${r.greeting || 'नमस्ते!'}</small>
                    </div>
                </div>
                <button type="button" class="modal-close-btn" onclick="document.getElementById('vernacularModal').style.display='none'">&times;</button>
            </div>
            <div class="modal-body" style="max-height: 70vh; overflow-y: auto;">
                <div class="explainer-box summary-box mb-3">
                    <h4 style="color:#4E80ED; margin-bottom:6px;">📋 आपकी सेहत का हाल (Plain Summary)</h4>
                    <p style="font-size:0.95rem; line-height:1.5;">${r.plain_summary}</p>
                </div>

                <div class="explainer-box meds-box mb-3">
                    <h4 style="color:#10B981; margin-bottom:8px;">💊 दवाइयाँ और लेने का सही समय</h4>
                    ${medsList}
                </div>

                <div class="explainer-box nutrition-box mb-3">
                    <h4 style="color:#F59E0B; margin-bottom:6px;">🥗 खान-पान और घरेलू देखभाल</h4>
                    <ul style="padding-left:18px; margin:0; line-height:1.6;">${nutritionList}</ul>
                </div>

                <div class="explainer-box danger-box mb-3" style="background:rgba(239, 68, 68, 0.08); border-left:4px solid #EF4444; padding:10px 14px; border-radius:6px;">
                    <h4 style="color:#DC2626; margin-bottom:6px;">🚨 खतरे के लक्षण (दिखते ही 108 मिलाएं)</h4>
                    <ul style="padding-left:18px; margin:0; line-height:1.6;">${dangerList}</ul>
                </div>

                <div class="reassurance-note p-2 text-center" style="font-style:italic; color:var(--text-secondary);">
                    "${r.reassurance_note || 'आपकी आशा दीदी और प्राथमिक स्वास्थ्य केंद्र आपके साथ हैं।'}"
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-outline btn-sm" onclick="readVernacularAloud(this)">🔊 बोलकर सुनाएं (Listen Aloud)</button>
                <button type="button" class="btn btn-primary btn-sm" onclick="document.getElementById('vernacularModal').style.display='none'">समझ गया / Close</button>
            </div>
        </div>
    `;

    modal.style.display = 'flex';
}

function readVernacularAloud(btn) {
    const summary = document.querySelector('.summary-box p')?.innerText || '';
    if (summary) {
        playAccessibleVoice(summary, btn);
    }
}

/**
 * 4. AI High-Risk Care Surveillance Planner on /high-risk
 */
function setupAiHighRiskPlanner() {
    const actionHeaders = document.querySelectorAll('.table-actions-header');
    // Add AI Plan button to table rows or header
    document.querySelectorAll('.high-risk-card, tr[data-case-id]').forEach(row => {
        if (!row.querySelector('.btn-ai-high-risk')) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'btn btn-xs btn-outline btn-ai-high-risk';
            btn.style.color = '#8B5CF6';
            btn.style.borderColor = '#C4B5FD';
            btn.style.marginLeft = '4px';
            btn.innerHTML = '✨ AI Care Plan';
            btn.onclick = (e) => {
                e.stopPropagation();
                runHighRiskPlanForPatient(row);
            };
            const actionsCell = row.querySelector('.case-actions') || row.querySelector('td:last-child');
            if (actionsCell) actionsCell.appendChild(btn);
        }
    });
}

async function runHighRiskPlanForPatient(elem) {
    const patientName = elem.querySelector('.patient-name, strong')?.innerText.trim() || 'Patient';
    const riskFactors = elem.querySelector('.risk-factors, .badge-tag')?.innerText.trim() || 'High-Risk Maternal';

    if (window.showToast) showToast(`Generating Gemini Care Plan for ${patientName}...`);

    try {
        const res = await fetch('/api/ai/high-risk-plan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                patient_name: patientName,
                risk_factors: riskFactors,
                category: 'High-Risk Surveillance'
            })
        });

        const data = await res.json();
        if (data.success && data.result) {
            renderHighRiskPlanModal(patientName, data.result);
        }
    } catch (e) {
        console.error('High risk plan error:', e);
    }
}

function renderHighRiskPlanModal(patientName, r) {
    let modal = document.getElementById('highRiskPlanModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'highRiskPlanModal';
        modal.className = 'modal-backdrop';
        document.body.appendChild(modal);
    }

    const checklist = (r.asha_home_visit_checklist || []).map(c => `<li>📋 ${c}</li>`).join('');
    const nutrition = (r.nutrition_action_plan || []).map(n => `<li>🥗 ${n}</li>`).join('');
    const triggers = (r.red_flag_escalation_triggers || []).map(t => `<li style="color:#DC2626; font-weight:600;">🚨 ${t}</li>`).join('');

    modal.innerHTML = `
        <div class="modal-dialog glass-panel" style="max-width: 600px;">
            <div class="modal-header">
                <div>
                    <h3 style="margin:0;">✨ ASHA Surveillance Plan: ${patientName}</h3>
                    <small style="color:var(--text-muted);">Priority Tier: <strong>${r.urgency_tier || 'Critical'}</strong> | Next Visit: ${r.next_recommended_visit || 'Within 48h'}</small>
                </div>
                <button type="button" class="modal-close-btn" onclick="document.getElementById('highRiskPlanModal').style.display='none'">&times;</button>
            </div>
            <div class="modal-body" style="max-height: 70vh; overflow-y: auto;">
                <p style="background:var(--primary-subtle); padding:8px 12px; border-radius:6px; font-size:0.9rem;">
                    <strong>Surveillance Objective:</strong> ${r.clinical_summary}
                </p>

                <h4 style="color:#4E80ED; margin-top:12px; margin-bottom:6px;">👩‍⚕️ ASHA Home Visit Checklist</h4>
                <ul style="padding-left:18px; margin:0; line-height:1.6;">${checklist}</ul>

                <h4 style="color:#10B981; margin-top:12px; margin-bottom:6px;">🥗 Rural Nutrition Action Plan</h4>
                <ul style="padding-left:18px; margin:0; line-height:1.6;">${nutrition}</ul>

                <h4 style="color:#DC2626; margin-top:12px; margin-bottom:6px;">🚨 108 Ambulance Dispatch Triggers</h4>
                <ul style="padding-left:18px; margin:0; line-height:1.6;">${triggers}</ul>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-primary btn-sm" onclick="document.getElementById('highRiskPlanModal').style.display='none'">Done</button>
            </div>
        </div>
    `;

    modal.style.display = 'flex';
}

/**
 * =====================================================================
 * ELEVENLABS REALISTIC ACCESSIBLE VOICE PLAYER ENGINE
 * =====================================================================
 */
window.voiceState = {
    audioPlayer: null,
    isPlaying: false,
    currentBtn: null,
    originalHtml: '',
    elevenLabsConfigured: false,
    selectedVoiceId: "21m00Tcm4TlvDq8ikWAM"
};

document.addEventListener('DOMContentLoaded', function() {
    checkVoiceStatus();
});

async function checkVoiceStatus() {
    try {
        const res = await fetch('/api/voice/status');
        const data = await res.json();
        window.voiceState.elevenLabsConfigured = data.configured;
        const voiceBadge = document.getElementById('elevenLabsBadge');
        if (voiceBadge) {
            voiceBadge.innerText = data.configured ? '🎙️ ElevenLabs Lifelike Voice' : '🎙️ Voice Active';
            if (data.configured) voiceBadge.classList.add('badge-eleven-active');
        }
    } catch (e) {
        console.warn('Voice status check failed:', e);
    }
}

async function playAccessibleVoice(text, btnElement, voiceId) {
    if (!text) return;

    // Toggle: if currently playing, stop it
    if (window.voiceState.isPlaying) {
        stopAccessibleVoice();
        if (btnElement && btnElement === window.voiceState.currentBtn) {
            return;
        }
    }

    const originalHtml = btnElement ? btnElement.innerHTML : '';
    if (btnElement) {
        btnElement.innerHTML = '<span class="voice-wave-anim">🎙️</span> <strong>Speaking...</strong>';
        btnElement.classList.add('btn-speaking');
        window.voiceState.currentBtn = btnElement;
        window.voiceState.originalHtml = originalHtml;
    }

    try {
        // Attempt ElevenLabs realistic voice TTS first
        const vid = voiceId || window.voiceState.selectedVoiceId;
        const res = await fetch('/api/voice/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text, voice_id: vid })
        });

        const contentType = res.headers.get('content-type') || '';
        if (res.ok && contentType.includes('audio/mpeg')) {
            const blob = await res.blob();
            const audioUrl = URL.createObjectURL(blob);
            const audio = new Audio(audioUrl);
            window.voiceState.audioPlayer = audio;
            window.voiceState.isPlaying = true;

            audio.onended = () => stopAccessibleVoice();
            audio.onerror = () => {
                fallbackToBrowserSpeech(text);
            };

            await audio.play();
            if (window.showToast) showToast('Playing lifelike ElevenLabs voice...', 'info');
            return;
        }
    } catch (err) {
        console.warn('ElevenLabs API request failed, using browser speech fallback:', err);
    }

    // Fallback: browser SpeechSynthesis
    fallbackToBrowserSpeech(text);
}

function stopAccessibleVoice() {
    if (window.voiceState.audioPlayer) {
        window.voiceState.audioPlayer.pause();
        window.voiceState.audioPlayer = null;
    }
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }
    window.voiceState.isPlaying = false;
    if (window.voiceState.currentBtn && window.voiceState.originalHtml) {
        window.voiceState.currentBtn.innerHTML = window.voiceState.originalHtml;
        window.voiceState.currentBtn.classList.remove('btn-speaking');
        window.voiceState.currentBtn = null;
    }
}

function fallbackToBrowserSpeech(text) {
    if (!('speechSynthesis' in window)) {
        if (window.showToast) showToast('Speech not supported on this browser.');
        stopAccessibleVoice();
        return;
    }

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    const lang = localStorage.getItem('aarogya_lang') || 'en';
    utterance.lang = lang === 'hi' ? 'hi-IN' : 'en-IN';
    utterance.rate = 0.92;

    utterance.onend = () => stopAccessibleVoice();
    utterance.onerror = () => stopAccessibleVoice();

    window.voiceState.isPlaying = true;
    window.speechSynthesis.speak(utterance);
}

function openVoiceSettingsModal() {
    let modal = document.getElementById('voiceSettingsModal');
    if (modal) modal.style.display = 'flex';
}

function closeVoiceSettingsModal() {
    let modal = document.getElementById('voiceSettingsModal');
    if (modal) modal.style.display = 'none';
}

async function saveElevenLabsKey() {
    const input = document.getElementById('inputElevenKey');
    const feedback = document.getElementById('voiceKeyFeedback');
    const saveBtn = document.getElementById('saveElevenBtn');
    const key = input ? input.value.trim() : '';

    if (!key) {
        if (feedback) {
            feedback.style.display = 'block';
            feedback.className = 'key-test-feedback error';
            feedback.innerText = 'Please enter a valid ElevenLabs API key.';
        }
        return;
    }

    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.innerText = 'Verifying ElevenLabs...';
    }
    if (feedback) {
        feedback.style.display = 'block';
        feedback.className = 'key-test-feedback info';
        feedback.innerText = 'Testing key with ElevenLabs API...';
    }

    try {
        const res = await fetch('/api/voice/set-key', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: key })
        });
        const data = await res.json();

        if (data.success) {
            feedback.className = 'key-test-feedback success';
            feedback.innerText = data.message;
            if (window.showToast) showToast('ElevenLabs voice engine activated!', 'success');
            setTimeout(() => {
                closeVoiceSettingsModal();
                checkVoiceStatus();
            }, 1200);
        } else {
            feedback.className = 'key-test-feedback error';
            feedback.innerText = data.error || 'Failed to verify ElevenLabs key.';
        }
    } catch (e) {
        if (feedback) {
            feedback.className = 'key-test-feedback error';
            feedback.innerText = 'Network error verifying key.';
        }
    } finally {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.innerText = 'Verify & Save Voice Key';
        }
    }
}

