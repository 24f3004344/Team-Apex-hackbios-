/**
 * AarogyaSahay Multilingual Localization System
 * Full Website Vernacular Translation Engine:
 * - Direct Client-side DOM translation (Instant, 100% Offline-Ready)
 * - Headless Google Translate Orchestration (Whole-site deep machine translation)
 * - State persistence across page navigations & sessions via localStorage & cookies
 */

const VERNACULAR_NOTICES = {
    hi: "भाषा हिन्दी पर सेट की गई। संपूर्ण वेबसाइट और स्वास्थ्य प्रणाली अब हिन्दी में सक्रिय है।",
    bn: "ভাষা বাংলায় পরিবর্তিত হয়েছে। সমগ্র ওয়েবসাইট এবং স্বাস্থ্য গ্রিড সক্রিয়।",
    te: "భాష తెలుగులోకి మార్చబడింది. మొత్తం వెబ్‌సైట్ మరియు ఆరోగ్య వ్యవస్థ సిద్ధంగా ఉంది.",
    mr: "भाषा मराठीवर सेट केली आहे. संपूर्ण वेबसाइट आणि ग्रामीण आरोग्य प्रणाली सक्रिय.",
    ta: "மொழி தமிழுக்கு மாற்றப்பட்டது. முழு வலைத்தளமும் சுகாதார கட்டமைப்பும் தயார்.",
    en: "Interface set to English. Rural Public Health Grid active."
};

const TRANSLATION_DICTIONARIES = {
    hi: {
        // Top Bar & Helplines
        "108 Rural SOS": "108 ग्रामीण आपातकालीन",
        "104 Maternal Helpline": "104 मातृ हेल्पलाइन",
        "14416 Tele-MANAS": "14416 टेली-मानस",
        "Field Sync: Active (Offline-Ready)": "फील्ड सिंक: सक्रिय (ऑफलाइन तैयार)",
        "Field Sync:": "फील्ड सिंक:",
        "Active (Offline-Ready)": "सक्रिय (ऑफलाइन तैयार)",
        "Light": "लाइट",
        "Dark": "डार्क",

        // Main Navigation
        "Tele-OPD": "टेली-ओपीडी",
        "Clinical Triage": "क्लिनिकल ट्राइएज",
        "ABHA Records": "आभा रिकॉर्ड्स",
        "Referrals": "रेफरल्स",
        "Medicines & Labs": "दवाएं और लैब्स",
        "High-Risk Care": "उच्च-जोखिम देखभाल",
        "Analytics": "एनालिटिक्स",
        "Dashboard": "डैशबोर्ड",
        "Sign In": "साइन इन",
        "Sign Out": "साइन आउट",
        "Join Grid": "ग्रिड से जुड़ें",
        "AarogyaSahay": "आरोग्यसहाय",
        "Apex Rural Public Health Grid": "सर्वोच्च ग्रामीण सार्वजनिक स्वास्थ्य ग्रिड",

        // Hero Section & Taglines
        "Strengthening Public Health Infrastructure": "सार्वजनिक स्वास्थ्य बुनियादी ढांचे को सुदृढ़ बनाना",
        "ABDM & ABHA Aligned": "ABDM और आभा से संबद्ध",
        "Timely, Continuous & Quality Healthcare for Every Rural Community": "प्रत्येक ग्रामीण समुदाय के लिए समय पर, निरंतर और गुणवत्तापूर्ण स्वास्थ्य सेवा",
        "Every Rural Community": "प्रत्येक ग्रामीण समुदाय",
        "Bridging geographical distance, specialist shortages, and low connectivity. An assisted teleconsultation, digital clinical triage, real-time medicine inventory, and referral continuity network empowering frontline workers and patients.": "भौगोलिक दूरी, विशेषज्ञ डॉक्टरों की कमी और कमजोर कनेक्टिविटी को दूर करना। एक सहायता प्राप्त टेली-परामर्श, डिजिटल क्लिनिकल ट्राइएज, रियल-टाइम दवा सूची और रेफरल निरंतरता नेटवर्क जो स्वास्थ्य कार्यकर्ताओं और मरीजों को सशक्त बनाता है।",
        "Frontline Worker Portal": "आशा / कार्यकर्ता पोर्टल",
        "Run Digital Triage": "डिजिटल ट्राइएज चलाएं",
        "Check Medicine Stock": "दवा स्टॉक जांचें",
        "Zero-Connectivity Resilience: Frontline workers can capture patient vitals, triage, and records fully offline. Automatic bidirectional sync triggers as soon as 2G/Wi-Fi is detected.": "शून्य-कनेक्टिविटी लचीलापन: स्वास्थ्य कार्यकर्ता पूरी तरह से ऑफ़लाइन रोगी के महत्वपूर्ण लक्षण, ट्राइएज और रिकॉर्ड दर्ज कर सकते हैं। 2G/Wi-Fi मिलते ही स्वचालित द्विदिश सिंक शुरू होता है।",
        "Live Rural Tele-OPD & Triage Grid": "लाइव ग्रामीण टेली-ओपीडी और ट्राइएज ग्रिड",
        "Active": "सक्रिय",
        "Sub-Centres Linked": "उप-केंद्र जुड़े",
        "Referral Closure Rate": "रेफरल समाधान दर",
        "Avg. Travel Time Saved": "औसत यात्रा समय बचत",
        "URGENT": "अति आवश्यक",
        "RED ALERT": "रेड अलर्ट (आपातकाल)",
        "NCD FOLLOWUP": "एनसीडी फॉलोअप",
        "High-Risk Pregnancy (32 Wks)": "उच्च-जोखिम गर्भावस्था (32 सप्ताह)",
        "Severe Acute Malnutrition + Fever": "गंभीर कुपोषण + बुखार",
        "Hypertension & Diabetes Refill": "उच्च रक्तचाप और मधुमेह रिफिल",
        "Tele-OPD Linked": "टेली-ओपीडी से जुड़ा",
        "En Route": "मार्ग में",
        "Dispensed": "वितरित",
        "Offline Sync: 100% Resilient": "ऑफलाइन सिंक: 100% लचीला",
        "Real-Time Bed/Drug Telemetry": "रियल-टाइम बेड/दवा टेलीमेट्री",

        // Feature Sections & Headings
        "Core Public Health Capabilities": "मुख्य सार्वजनिक स्वास्थ्य क्षमताएं",
        "Architected specifically for Sub-Centres, PHCs, CHCs, and District Hospitals.": "उप-केंद्रों, प्राथमिक स्वास्थ्य केंद्रों, सीएचसी और जिला अस्पतालों के लिए विशेष रूप से डिज़ाइन किया गया।",
        "Assisted Tele-OPD": "सहायता प्राप्त टेली-ओपीडी",
        "Field Clinical Triage": "फील्ड क्लिनिकल ट्राइएज",
        "Continuity of Care Records": "निरंतर देखभाल रिकॉर्ड",
        "Live Medicine Inventory": "लाइव दवा इन्वेंटरी",
        "High-Risk Escalation": "उच्च-जोखिम वृद्धि",
        "Public Health Analytics": "सार्वजनिक स्वास्थ्य एनालिटिक्स",
        "Regional Dialect Audio": "क्षेत्रीय बोली ऑडियो",
        "Offline First Architecture": "ऑफलाइन-प्रथम प्रणाली",
        "ABHA / ABDM Native": "आभा / ABDM मूल",

        // Action Buttons & Controls
        "Search": "खोजें",
        "Filter": "फ़िल्टर",
        "Reset": "रीसेट",
        "Submit": "जमा करें",
        "Cancel": "रद्द करें",
        "Save": "सुरक्षित करें",
        "Close": "बंद करें",
        "View All": "सभी देखें",
        "View Records": "रिकॉर्ड्स देखें",
        "Book Consultation": "परामर्श बुक करें",
        "Book Tele-OPD": "टेली-ओपीडी बुक करें",
        "Start Digital Triage": "डिजिटल ट्राइएज शुरू करें",
        "Evaluate Vitals & Symptoms": "लक्षण व वाइटल्स जांचें",
        "Generate ABDM Referral": "ABDM रेफरल बनाएं",
        "Dispatch 108 Ambulance": "108 एम्बुलेंस भेजें",
        "Sync Field Consultations": "फील्ड परामर्श सिंक करें",
        "Sync Field Data": "फील्ड डेटा सिंक करें",
        "Join Health Grid": "स्वास्थ्य ग्रिड से जुड़ें",
        "Sign In to Grid": "ग्रिड में साइन इन करें",
        "Create Account": "खाता बनाएं",

        // Forms & Labels
        "Patient Name": "रोगी का नाम",
        "Full Name": "पूरा नाम",
        "Mobile Number": "मोबाइल नंबर",
        "Mobile Number / Staff ID": "मोबाइल नंबर / स्टाफ आईडी",
        "Mobile Number / ABHA ID": "मोबाइल नंबर / आभा आईडी",
        "Official Email / Medical ID": "आधिकारिक ईमेल / मेडिकल आईडी",
        "Administrator ID / Email": "प्रशासक आईडी / ईमेल",
        "Password": "पासवर्ड",
        "Confirm Password": "पासवर्ड की पुष्टि करें",
        "Facility Name": "सुविधा / अस्पताल का नाम",
        "District": "जिला",
        "State": "राज्य",
        "Age": "आयु",
        "Gender": "लिंग",
        "Select Gender": "लिंग चुनें",
        "Male": "पुरुष",
        "Female": "महिला",
        "Other": "अन्य",
        "Role": "भूमिका",
        "Select Role": "भूमिका चुनें",
        "Preferred Language": "पसंदीदा भाषा",
        "Preferred Regional Dialect": "पसंदीदा क्षेत्रीय बोली",
        "ABHA ID": "आभा आईडी",
        "Systolic BP": "सिस्टोलिक बीपी",
        "Diastolic BP": "डायस्टोलिक बीपी",
        "Pulse Rate": "नाड़ी गति",
        "SpO2 (Oxygen %)": "ऑक्सीजन (SpO2 %)",
        "Temperature": "तापमान",
        "Symptoms": "लक्षण",
        "Urgency": "प्राथमिकता",
        "Normal": "सामान्य",
        "Urgent": "आवश्यक",
        "Emergency": "आपातकालीन",
        "Clinical Notes": "क्लिनिकल नोट्स",
        "Specialty Needed": "आवश्यक विशेषज्ञता",
        "Target Facility": "लक्षित अस्पताल",

        // Tables & Stock
        "Medicine Name": "दवा का नाम",
        "Category": "श्रेणी",
        "Facility": "स्वास्थ्य सुविधा",
        "Stock Status": "स्टॉक स्थिति",
        "Available Units": "उपलब्ध इकाइयां",
        "Last Updated": "अंतिम अद्यतन",
        "Available": "उपलब्ध",
        "In Stock": "उपलब्ध",
        "Low Stock": "कम स्टॉक",
        "Out of Stock": "स्टॉक समाप्त",
        "Units": "इकाइयां",
        "Today": "आज",
        "Action": "कार्रवाई",
        "Status": "स्थिति",

        // Footer & Badges
        "Privacy & ABHA Consent": "गोपनीयता और आभा सहमति",
        "Offline Sync Guidelines": "ऑफलाइन सिंक दिशानिर्देश",
        "Health Data Governance": "स्वास्थ्य डेटा शासन",
        "Built by Team Apex for Public Rural Healthcare Access": "सार्वजनिक ग्रामीण स्वास्थ्य पहुंच के लिए टीम एपेक्स द्वारा निर्मित",
        "Strengthening, not replacing, the public health architecture. Empowering Sub-Centres, PHCs, CHCs, and District Hospitals with assisted tele-consultation, digital triage, continuity of care records, and live medicine availability.": "सार्वजनिक स्वास्थ्य प्रणाली को बदलना नहीं, बल्कि सुदृढ़ करना। उप-केंद्रों, पीएचसी, सीएचसी और जिला अस्पतालों को सहायता प्राप्त टेली-परामर्श, डिजिटल ट्राइएज, निरंतर रिकॉर्ड और लाइव दवा उपलब्धता के साथ सशक्त बनाना।",
        "ABDM / ABHA Interoperable": "ABDM / आभा इंटरऑपरेबल",
        "FHIR & SNOMED-CT Ready": "FHIR और SNOMED-CT तैयार",
        "Low-Bandwidth Resilient": "कम-बैंडविड्थ अनुकूल",
        "Search essential medicines...": "आवश्यक दवाएं खोजें...",
        "Filter by district...": "जिले के अनुसार फ़िल्टर करें...",
        "Enter ABHA ID or Mobile...": "आभा आईडी या मोबाइल दर्ज करें..."
    },
    bn: {
        "108 Rural SOS": "১০৮ গ্রামীণ জরুরি",
        "104 Maternal Helpline": "১০৪ মাতৃত্ব হেল্পলাইন",
        "14416 Tele-MANAS": "১৪৪১৬ টেলি-মানস",
        "Field Sync: Active (Offline-Ready)": "ফিল্ড সিঙ্ক: সক্রিয় (অফলাইন প্রস্তুত)",
        "Field Sync:": "ফিল্ড সিঙ্ক:",
        "Active (Offline-Ready)": "সক্রিয় (অফলাইন প্রস্তুত)",
        "Light": "হালকা",
        "Dark": "অন্ধকার",
        "Tele-OPD": "টেলি-ওপিডি",
        "Clinical Triage": "ক্লিনিক্যাল ট্রায়াজ",
        "ABHA Records": "আভা রেকর্ড",
        "Referrals": "রেফারেল",
        "Medicines & Labs": "ওষুধ ও ল্যাব",
        "High-Risk Care": "উচ্চ-ঝুঁকি যত্ন",
        "Analytics": "অ্যানালিটিক্স",
        "Dashboard": "ড্যাশবোর্ড",
        "Sign In": "সাইন ইন",
        "Sign Out": "সাইন আউট",
        "Join Grid": "গ্রিডে যোগ দিন",
        "AarogyaSahay": "আরোগ্যসহায়",
        "Apex Rural Public Health Grid": "গ্রামীণ জনস্বাস্থ্য গ্রিড",
        "Strengthening Public Health Infrastructure": "জনস্বাস্থ্য পরিকাঠামো শক্তিশালীকরণ",
        "ABDM & ABHA Aligned": "ABDM এবং আভা সংযুক্ত",
        "Timely, Continuous & Quality Healthcare for Every Rural Community": "প্রতিটি গ্রামীণ জনগোষ্ঠীর জন্য সময়োপযোগী, ধারাবাহিক ও মানসম্মত স্বাস্থ্যসেবা",
        "Frontline Worker Portal": "স্বাস্থ্যকর্মী পোর্টাল",
        "Run Digital Triage": "ডিজিটাল ট্রায়াজ চালান",
        "Check Medicine Stock": "ওষুধের স্টক দেখুন",
        "Live Rural Tele-OPD & Triage Grid": "লাইভ গ্রামীণ টেলি-ওপিডি ও ট্রায়াজ গ্রিড",
        "Sub-Centres Linked": "উপ-কেন্দ্র সংযুক্ত",
        "Referral Closure Rate": "রেফারেল সমাপ্তির হার",
        "Avg. Travel Time Saved": "গড় ভ্রমণ সময় সাশ্রয়",
        "URGENT": "জরুরি",
        "RED ALERT": "রেড এলার্ট",
        "NCD FOLLOWUP": "এনসিডি ফলোআপ",
        "Search": "অনুসন্ধান",
        "Filter": "ফিল্টার",
        "Reset": "রিসেট",
        "Submit": "জমা দিন",
        "Cancel": "বাতিল",
        "Save": "সংরক্ষণ",
        "Available": "উপলব্ধ",
        "In Stock": "উপলব্ধ",
        "Low Stock": "কম স্টক",
        "Out of Stock": "স্টক শেষ",
        "Units": "ইউনিট",
        "Today": "আজ",
        "Patient Name": "রোগীর নাম",
        "Full Name": "পূর্ণ নাম",
        "Mobile Number": "মোবাইল নম্বর",
        "Password": "পাসওয়ার্ড",
        "Facility Name": "হাসপাতালের নাম",
        "District": "জেলা",
        "State": "রাজ্য",
        "Age": "বয়স",
        "Gender": "লিঙ্গ",
        "Symptoms": "উপসর্গ",
        "Urgency": "জরুরিতা",
        "Normal": "স্বাভাবিক",
        "Emergency": "জরুরি অবস্থা",
        "Medicine Name": "ওষুধের নাম",
        "Category": "বিভাগ",
        "Stock Status": "স্টক স্থিতি"
    },
    te: {
        "108 Rural SOS": "108 గ్రామీణ అత్యవసర",
        "104 Maternal Helpline": "104 ప్రసూతి హెల్ప్‌లైన్",
        "14416 Tele-MANAS": "14416 టెలి-మానస్",
        "Field Sync: Active (Offline-Ready)": "ఫీల్డ్ సింక్: సక్రియం (ఆఫ్‌లైన్ సిద్ధం)",
        "Field Sync:": "ఫీల్డ్ సింక్:",
        "Active (Offline-Ready)": "సక్రియం (ఆఫ్‌లైన్ సిద్ధం)",
        "Light": "లైట్",
        "Dark": "డార్క్",
        "Tele-OPD": "టెలి-ఓపీడీ",
        "Clinical Triage": "క్లినికల్ ట్రయేజ్",
        "ABHA Records": "ఆభా రికార్డులు",
        "Referrals": "రెఫరల్స్",
        "Medicines & Labs": "మందులు & ల్యాబ్‌లు",
        "High-Risk Care": "అధిక-రిస్క్ సంరక్షణ",
        "Analytics": "విశ్లేషణలు",
        "Dashboard": "డ్యాష్‌బోర్డ్",
        "Sign In": "సైన్ ఇన్",
        "Sign Out": "సైన్ అవుట్",
        "Join Grid": "గ్రిడ్‌లో చేరండి",
        "AarogyaSahay": "ఆరోగ్యసహాయ్",
        "Apex Rural Public Health Grid": "గ్రామీణ ప్రజా ఆరోగ్య గ్రిడ్",
        "Strengthening Public Health Infrastructure": "ప్రజా ఆరోగ్య మౌలిక సదుపాయాల బలోపేతం",
        "ABDM & ABHA Aligned": "ABDM మరియు ఆభా అనుసంధానం",
        "Timely, Continuous & Quality Healthcare for Every Rural Community": "ప్రతి గ్రామీణ సమాజానికి సకాలంలో, నిరంతర & నాణ్యమైన ఆరోగ్య సంరక్షణ",
        "Frontline Worker Portal": "ఆరోగ్య కార్యకర్తల పోర్టల్",
        "Run Digital Triage": "డిజిటల్ ట్రయేజ్ ప్రారంభించండి",
        "Check Medicine Stock": "మందుల నిల్వను తనిఖీ చేయండి",
        "Live Rural Tele-OPD & Triage Grid": "లైవ్ గ్రామీణ టెలి-ఓపీడీ & ట్రయేజ్ గ్రిడ్",
        "Sub-Centres Linked": "ఉపకేంద్రాలు అనుసంధానించబడ్డాయి",
        "Referral Closure Rate": "రెఫరల్ పూర్తి రేటు",
        "Avg. Travel Time Saved": "సగటు ప్రయాణ సమయం ఆదా",
        "URGENT": "అత్యవసరం",
        "RED ALERT": "రెడ్ అలర్ట్",
        "NCD FOLLOWUP": "ఎన్‌సీడీ ఫాలోఅప్",
        "Search": "శోధించండి",
        "Filter": "ఫిల్టర్",
        "Reset": "రీసెట్",
        "Submit": "సమర్పించండి",
        "Cancel": "రద్దు",
        "Save": "భద్రపరచు",
        "Available": "అందుబాటులో ఉంది",
        "In Stock": "అందుబాటులో ఉంది",
        "Low Stock": "తక్కువ స్టాక్",
        "Out of Stock": "స్టాక్ లేదు",
        "Units": "యూనిట్లు",
        "Today": "ఈ రోజు",
        "Patient Name": "రోగి పేరు",
        "Full Name": "పూర్తి పేరు",
        "Mobile Number": "మొబైల్ నంబర్",
        "Password": "పాస్‌వర్డ్",
        "Facility Name": "ఆసుపత్రి పేరు",
        "District": "జిల్లా",
        "State": "రాష్ట్రం",
        "Age": "వయస్సు",
        "Gender": "లింగం",
        "Symptoms": "లక్షణాలు",
        "Urgency": "అత్యవసర స్థాయి",
        "Normal": "సాధారణం",
        "Emergency": "అత్యవసరం",
        "Medicine Name": "మందు పేరు",
        "Category": "వర్గం",
        "Stock Status": "స్టాక్ స్థితి"
    },
    mr: {
        "108 Rural SOS": "१०८ ग्रामीण आपत्कालीन",
        "104 Maternal Helpline": "१०४ मातृ मदत केंद्र",
        "14416 Tele-MANAS": "१४४१६ टेली-मानस",
        "Field Sync: Active (Offline-Ready)": "फील्ड सिंक: सक्रिय (ऑफलाइन तयार)",
        "Field Sync:": "फील्ड सिंक:",
        "Active (Offline-Ready)": "सक्रिय (ऑफलाइन तयार)",
        "Light": "लाइट",
        "Dark": "डार्क",
        "Tele-OPD": "टेली-ओपीडी",
        "Clinical Triage": "क्लिनिकल ट्रायज",
        "ABHA Records": "आभा रेकॉर्ड्स",
        "Referrals": "रेफरल्स",
        "Medicines & Labs": "औषधे आणि लॅब्स",
        "High-Risk Care": "उच्च-जोखीम काळजी",
        "Analytics": "विश्लेषण",
        "Dashboard": "डॅशबोर्ड",
        "Sign In": "साइन इन",
        "Sign Out": "बाहेर पडा",
        "Join Grid": "ग्रिडमध्ये सामील व्हा",
        "AarogyaSahay": "आरोग्यसहाय",
        "Apex Rural Public Health Grid": "सर्वोच्च ग्रामीण सार्वजनिक आरोग्य ग्रिड",
        "Strengthening Public Health Infrastructure": "सार्वजनिक आरोग्य पायाभूत सुविधांचे सक्षमीकरण",
        "ABDM & ABHA Aligned": "ABDM आणि आभाशी जोडलेले",
        "Timely, Continuous & Quality Healthcare for Every Rural Community": "प्रत्येक ग्रामीण समुदायासाठी वेळेवर, निरंतर आणि दर्जेदार आरोग्य सेवा",
        "Frontline Worker Portal": "आशा / कार्यकर्ता पोर्टल",
        "Run Digital Triage": "डिजिटल ट्रायज चालवा",
        "Check Medicine Stock": "औषध साठा तपासा",
        "Live Rural Tele-OPD & Triage Grid": "थेट ग्रामीण टेली-ओपीडी आणि ट्रायज ग्रिड",
        "Sub-Centres Linked": "उप-केंद्रे जोडली",
        "Referral Closure Rate": "रेफरल पूर्तता दर",
        "Avg. Travel Time Saved": "सरासरी प्रवास वेळ बचत",
        "URGENT": "तातडीचे",
        "RED ALERT": "रेड अलर्ट",
        "NCD FOLLOWUP": "एनसीडी फॉलोअप",
        "Search": "शोधा",
        "Filter": "फिल्टर",
        "Reset": "रीसेट",
        "Submit": "सादर करा",
        "Cancel": "रद्द करा",
        "Save": "जतन करा",
        "Available": "उपलब्ध",
        "In Stock": "उपलब्ध",
        "Low Stock": "कमी साठा",
        "Out of Stock": "साठा संपला",
        "Units": "नग",
        "Today": "आज",
        "Patient Name": "रुग्णाचे नाव",
        "Full Name": "पूर्ण नाव",
        "Mobile Number": "मोबाईल नंबर",
        "Password": "पासवर्ड",
        "Facility Name": "रुग्णालयाचे नाव",
        "District": "जिल्हा",
        "State": "राज्य",
        "Age": "वय",
        "Gender": "लिंग",
        "Symptoms": "लक्षणे",
        "Urgency": "प्राधान्य",
        "Normal": "सामान्य",
        "Emergency": "आणीबाणी",
        "Medicine Name": "औषधाचे नाव",
        "Category": "वर्ग",
        "Stock Status": "साठा स्थिती"
    },
    ta: {
        "108 Rural SOS": "108 கிராமப்புற அவசர உதவி",
        "104 Maternal Helpline": "104 தாய்மை உதவி எண்",
        "14416 Tele-MANAS": "14416 டெலி-மானாஸ்",
        "Field Sync: Active (Offline-Ready)": "கள ஒத்திசைவு: செயலில் (ஆஃப்லைன் தயார்)",
        "Field Sync:": "கள ஒத்திசைவு:",
        "Active (Offline-Ready)": "செயலில் (ஆஃப்லைன் தயார்)",
        "Light": "லைட்",
        "Dark": "டார்க்",
        "Tele-OPD": "டெலி-ஓபிடி",
        "Clinical Triage": "மருத்துவ ட்ரையேஜ்",
        "ABHA Records": "ஆபா பதிவுகள்",
        "Referrals": "பரிந்துரைகள்",
        "Medicines & Labs": "மருந்துகள் & ஆய்வகங்கள்",
        "High-Risk Care": "அதிக-ஆபத்து பராமரிப்பு",
        "Analytics": "பகுப்பாய்வு",
        "Dashboard": "டாஷ்போர்டு",
        "Sign In": "உள்நுழைக",
        "Sign Out": "வெளியேறுக",
        "Join Grid": "கட்டமைப்பில் இணையுங்கள்",
        "AarogyaSahay": "ஆரோக்கியசகாய்",
        "Apex Rural Public Health Grid": "கிராமப்புற பொது சுகாதார கட்டமைப்பு",
        "Strengthening Public Health Infrastructure": "பொது சுகாதார உள்கட்டமைப்பை வலுப்படுத்துதல்",
        "ABDM & ABHA Aligned": "ABDM மற்றும் ஆபா ஒருங்கிணைப்பு",
        "Timely, Continuous & Quality Healthcare for Every Rural Community": "ஒவ்வொரு கிராமப்புற மக்களுக்கும் சரியான நேரத்தில், தொடர்ச்சியான மற்றும் தரமான சுகாதாரம்",
        "Frontline Worker Portal": "முன்னணி பணியாளர் தளம்",
        "Run Digital Triage": "டிஜிட்டல் ட்ரையேஜ் செய்க",
        "Check Medicine Stock": "மருந்து இருப்பை சரிபார்க்கவும்",
        "Live Rural Tele-OPD & Triage Grid": "நேரலை கிராமப்புற டெலி-ஓபிடி & ட்ரையேஜ்",
        "Sub-Centres Linked": "துணை மையங்கள் இணைக்கப்பட்டன",
        "Referral Closure Rate": "பரிந்துரை தீர்வு விகிதம்",
        "Avg. Travel Time Saved": "சராசரி பயண நேரம் சேமிப்பு",
        "URGENT": "அவசரம்",
        "RED ALERT": "ரெட் அலர்ட்",
        "NCD FOLLOWUP": "என்சிடி பின்தொடர்தல்",
        "Search": "தேடுக",
        "Filter": "வடிகட்டுக",
        "Reset": "மீட்டமை",
        "Submit": "சமர்ப்பிக்கவும்",
        "Cancel": "ரத்துசெய்",
        "Save": "சேமி",
        "Available": "இருப்பில் உள்ளது",
        "In Stock": "இருப்பில் உள்ளது",
        "Low Stock": "குறைந்த இருப்பு",
        "Out of Stock": "இருப்பு இல்லை",
        "Units": "அலகுகள்",
        "Today": "இன்று",
        "Patient Name": "நோயாளி பெயர்",
        "Full Name": "முழு பெயர்",
        "Mobile Number": "மொபைல் எண்",
        "Password": "கடவுச்சொல்",
        "Facility Name": "மருத்துவமனை பெயர்",
        "District": "மாவட்டம்",
        "State": "மாநிலம்",
        "Age": "வயது",
        "Gender": "பாலினம்",
        "Symptoms": "அறிகுறிகள்",
        "Urgency": "அவசரநிலை",
        "Normal": "இயல்பான",
        "Emergency": "அவசரகாலம்",
        "Medicine Name": "மருந்து பெயர்",
        "Category": "பிரிவு",
        "Stock Status": "இருப்பு நிலை"
    }
};

/**
 * Restore original text across DOM
 */
function restoreOriginalText(root = document.body) {
    if (!root) return;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
    let node;
    while ((node = walker.nextNode())) {
        if (node._origText !== undefined) {
            node.nodeValue = node._origText;
        }
    }

    const elements = root.querySelectorAll ? root.querySelectorAll('[data-orig-placeholder], [data-orig-title]') : [];
    elements.forEach(el => {
        if (el.hasAttribute('data-orig-placeholder')) {
            el.placeholder = el.getAttribute('data-orig-placeholder');
        }
        if (el.hasAttribute('data-orig-title')) {
            el.title = el.getAttribute('data-orig-title');
        }
    });
}

/**
 * Apply fast dictionary-based translation across all DOM text nodes
 */
function applyDictionaryTranslation(langCode, root = document.body) {
    if (!root) return;
    if (langCode === 'en') {
        restoreOriginalText(root);
        return;
    }

    const dict = TRANSLATION_DICTIONARIES[langCode];
    if (!dict) return;

    const sortedKeys = Object.keys(dict).sort((a, b) => b.length - a.length);

    const walker = document.createTreeWalker(
        root,
        NodeFilter.SHOW_TEXT,
        {
            acceptNode: function(node) {
                const parent = node.parentElement;
                if (!parent) return NodeFilter.FILTER_REJECT;
                const tag = parent.tagName.toLowerCase();
                if (['script', 'style', 'code', 'noscript'].includes(tag)) return NodeFilter.FILTER_REJECT;
                if (parent.closest('#google_translate_element') || parent.closest('.lang-dropdown') || parent.classList.contains('notranslate')) {
                    return NodeFilter.FILTER_REJECT;
                }
                return NodeFilter.FILTER_ACCEPT;
            }
        },
        false
    );

    let textNode;
    while ((textNode = walker.nextNode())) {
        if (textNode._origText === undefined) {
            textNode._origText = textNode.nodeValue;
        }

        const source = textNode._origText;
        const trimmed = source.trim();

        if (dict[trimmed]) {
            textNode.nodeValue = source.replace(trimmed, dict[trimmed]);
        } else {
            let replaced = source;
            let modified = false;
            for (const key of sortedKeys) {
                if (key.length >= 3 && replaced.includes(key)) {
                    replaced = replaced.split(key).join(dict[key]);
                    modified = true;
                }
            }
            if (modified) {
                textNode.nodeValue = replaced;
            }
        }
    }

    const inputsAndElements = root.querySelectorAll ? root.querySelectorAll('input, textarea, select, [title]') : [];
    inputsAndElements.forEach(el => {
        if (el.classList.contains('notranslate') || el.closest('.notranslate')) return;

        if (el.placeholder) {
            if (!el.hasAttribute('data-orig-placeholder')) {
                el.setAttribute('data-orig-placeholder', el.placeholder);
            }
            const origP = el.getAttribute('data-orig-placeholder').trim();
            if (dict[origP]) {
                el.placeholder = dict[origP];
            }
        }

        if (el.title) {
            if (!el.hasAttribute('data-orig-title')) {
                el.setAttribute('data-orig-title', el.title);
            }
            const origT = el.getAttribute('data-orig-title').trim();
            if (dict[origT]) {
                el.title = dict[origT];
            }
        }
    });
}

/**
 * Headless Google Translate Orchestrator
 */
let googleTranslatePollTimer = null;
function applyGoogleTranslate(langCode) {
    const domain = window.location.hostname;
    const cookieVal = (langCode === 'en') ? '' : (`/en/${langCode}`);

    if (langCode === 'en') {
        document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        document.cookie = `googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; domain=${domain}; path=/;`;
        document.cookie = `googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; domain=.${domain}; path=/;`;
        document.cookie = "googtrans=/en/en; path=/;";
    } else {
        document.cookie = `googtrans=${cookieVal}; path=/;`;
        document.cookie = `googtrans=${cookieVal}; domain=${domain}; path=/;`;
        document.cookie = `googtrans=${cookieVal}; domain=.${domain}; path=/;`;
    }

    function triggerCombo() {
        const combo = document.querySelector('.goog-te-combo');
        if (combo) {
            if (combo.value !== langCode) {
                combo.value = langCode;
                combo.dispatchEvent(new Event('change'));
            }
            return true;
        }
        return false;
    }

    if (!triggerCombo()) {
        if (googleTranslatePollTimer) clearInterval(googleTranslatePollTimer);
        let retries = 0;
        googleTranslatePollTimer = setInterval(() => {
            retries++;
            if (triggerCombo() || retries >= 25) {
                clearInterval(googleTranslatePollTimer);
            }
        }, 200);
    }
}

/**
 * Global Language Switcher - invoked directly from top selector
 */
function switchLanguage(langCode) {
    if (!langCode) return;

    // 1. Persist user choice in localStorage
    localStorage.setItem('aarogya_lang', langCode);
    document.documentElement.setAttribute('lang', langCode);

    // 2. Synchronize dropdown value
    const langSelect = document.getElementById('languageSelect');
    if (langSelect && langSelect.value !== langCode) {
        langSelect.value = langCode;
    }

    // 3. Immediately apply client-side dictionary translation to full DOM
    applyDictionaryTranslation(langCode);

    // 4. Trigger Google Translate for comprehensive machine translation
    applyGoogleTranslate(langCode);

    // 5. Provide vernacular status notification
    const notice = VERNACULAR_NOTICES[langCode] || VERNACULAR_NOTICES.en;
    if (typeof showToast === 'function') {
        showToast(notice, 'success');
    }
}

// Global localization helper for dynamically injected content
window.localizeDynamicContent = function(root) {
    const currentLang = localStorage.getItem('aarogya_lang') || 'en';
    if (currentLang !== 'en') {
        applyDictionaryTranslation(currentLang, root);
    }
};

// Immediate Language & Selector Sync on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    const savedLang = localStorage.getItem('aarogya_lang') || 'en';
    const langSelect = document.getElementById('languageSelect');
    if (langSelect) {
        langSelect.value = savedLang;
    }
    if (savedLang !== 'en') {
        applyDictionaryTranslation(savedLang);
        applyGoogleTranslate(savedLang);
    }
});
