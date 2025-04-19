import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime
import random

# Ensure this is the first Streamlit call
st.set_page_config(page_title="Vaccin Anti-Phishing", page_icon="🛡️", layout="wide")
# La începutul aplicației, după st.set_page_config
st.markdown("""
<style>
    @media (max-width: 768px) {
        .stHorizontalBlock {
            flex-direction: column;
        }
        .stHorizontalBlock > div {
            width: 100% !important;
        }
        /* Ajustează spațierea pentru mobile */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)


# Load examples from JSON file
@st.cache_data
def load_examples():
    try:
        with open("examples.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Funcția de analiză phishing direct în app_ai.py
def analyze_phishing_email(email_data, email_type):
    """
    Analizează un email de phishing și identifică indicatorii de fraudă
    """
    indicators = []
    
    # Analizarea subiectului
    subject = email_data.get("subject", "").lower()
    if any(word in subject for word in ["urgent", "urgentă", "imediat", "acum", "alertă", "atenție"]):
        indicators.append({
            "tip": "Ton de urgență în subiect",
            "detalii": "Emailurile frauduloase folosesc adesea un ton de urgență pentru a te determina să acționezi impulsiv.",
            "exemplu": email_data.get("subject"),
            "risc": "ridicat"
        })  
    
    # Analizarea corpului
    body = email_data.get("body", "").lower()
    
    # Verificarea URL-urilor suspecte
    import re
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', body)
    
    for url in urls:
        suspicious = False
        reasons = []
        
        # URL scurtat
        if any(domain in url for domain in ["bit.ly", "tinyurl", "goo.gl", "t.co"]):
            suspicious = True
            reasons.append("URL scurtat care ascunde destinația reală")
        
        if suspicious:
            indicators.append({
                "tip": "URL suspect",
                "detalii": "Link-ul poate fi fraudulos: " + ", ".join(reasons),
                "exemplu": url,
                "risc": "ridicat"
            })  
    
    # Verificarea solicitărilor de informații sensibile
    sensitive_patterns = [
        "parolă", "password", "user", "login", "autentificare", "cont", "card"
    ]
    
    if any(pattern in body for pattern in sensitive_patterns):
        indicators.append({
            "tip": "Solicitare de informații sensibile",
            "detalii": "Emailul cere date confidențiale. Companiile legitime nu solicită niciodată informații sensibile prin email.",
            "exemplu": "Mesajul conține termeni ce sugerează solicitarea de date confidențiale.",
            "risc": "ridicat"
        })  
    
    return {
        "indicators": indicators,
        "total_risk_score": len(indicators),
        "primary_risk": next((ind["tip"] for ind in indicators if ind["risc"] == "ridicat"), "Risc scăzut")
    }  

def highlight_phishing_indicators(email_text, indicators):
    """
    Evidențiază indicatori de phishing în textul emailului
    
    Args:
        email_text: Textul emailului
        indicators: Lista de indicatori detectați
    
    Returns:
        str: Textul emailului cu evidențieri HTML
    """
    highlighted_text = email_text
    
    # Definim stilurile de evidențiere
    highlight_styles = {
        "ridicat": "background-color: #ffcccc; border-bottom: 2px solid red; padding: 2px;",
        "mediu": "background-color: #fff2cc; border-bottom: 2px solid orange; padding: 2px;",
        "informativ": "background-color: #e6f3ff; border-bottom: 2px solid blue; padding: 2px;"
    }
    
    # Evidențiază URL-uri suspecte
    import re
    for indicator in indicators:
        if indicator["tip"] == "URL suspect" and indicator["exemplu"]:
            url = indicator["exemplu"]
            url_pattern = re.escape(url)
            replacement = f'<span style="{highlight_styles["ridicat"]}" title="URL suspect: {indicator["detalii"]}">{url}</span>'
            highlighted_text = re.sub(url_pattern, replacement, highlighted_text)
    
    # Evidențiază fraze cu ton de urgență
    urgency_words = ["urgent", "imediat", "acum", "alertă", "atenție", "pericol", "expiră", "limitat"]
    for word in urgency_words:
        pattern = r'\b' + word + r'\b'
        replacement = f'<span style="{highlight_styles["mediu"]}" title="Ton de urgență: Poate indica o tentativă de phishing">{word}</span>'
        highlighted_text = re.sub(pattern, replacement, highlighted_text, flags=re.IGNORECASE)
    
    # Evidențiază solicitări de informații sensibile
    sensitive_phrases = [
        "introduceți parola", "confirmați datele", "actualizați informațiile", 
        "verificați contul", "introduceți codul", "datele cardului"
    ]
    
    for phrase in sensitive_phrases:
        if phrase.lower() in highlighted_text.lower():
            pattern = re.escape(phrase)
            replacement = f'<span style="{highlight_styles["ridicat"]}" title="Solicitare informații sensibile: Risc ridicat de phishing">{phrase}</span>'
            highlighted_text = re.sub(pattern, replacement, highlighted_text, flags=re.IGNORECASE)
    
    return highlighted_text

# Integrează funcția direct în app_ai.py
def format_email_html(email_data):
    """
    Transformă un obiect email într-un format HTML realist
    
    Args:
        email_data: Dicționar cu datele emailului
    
    Returns:
        str: Reprezentarea HTML a emailului
    """
    company_logo = email_data.get("logo", "COMPANIE")
    company_color = email_data.get("colors", "#007bff")
    sender_name = email_data.get("sender", "Expeditor")
    sender_email = email_data.get("sender_email", "expeditor@domain.com")
    subject = email_data.get("subject", "Subiect email")
    body = email_data.get("body", "").replace("\n", "<br>")
    date = email_data.get("date", "01.01.2025")
    footer = email_data.get("footer", "© 2025 Companie")
    
    # Construim headerul emailului în stil realist cu design responsiv
    header_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            @media screen and (max-width: 600px) {{
                .email-container {{
                    width: 100% !important;
                    padding: 0 !important;
                }}
                .email-header {{
                    padding: 10px !important;
                }}
                .email-content {{
                    padding: 10px !important;
                }}
                .email-footer {{
                    padding: 10px !important;
                    font-size: 10px !important;
                }}
                .email-meta td {{
                    display: block;
                    width: 100%;
                }}
                .email-meta td:first-child {{
                    font-weight: bold;
                    padding-bottom: 2px;
                }}
            }}
        </style>
    </head>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif;">
    <div class="email-container" style="border: 1px solid #ddd; border-radius: 8px; max-width: 100%; margin-bottom: 20px;">
        <!-- Header -->
        <div class="email-header" style="background-color: {company_color}; color: white; padding: 15px; border-top-left-radius: 8px; border-top-right-radius: 8px;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                    <td><h2 style="margin: 0;">{company_logo}</h2></td>
                    <td align="right" style="font-size: 12px;">
                        {date}
                    </td>
                </tr>
            </table>
        </div>
        
        <!-- Email metadata -->
        <div style="background-color: #f8f9fa; padding: 10px 15px; border-bottom: 1px solid #ddd;">
            <table class="email-meta" width="100%" style="font-size: 13px;" cellpadding="3" cellspacing="0" border="0">
                <tr>
                    <td width="60"><strong>De la:</strong></td>
                    <td>{sender_name} &lt;{sender_email}&gt;</td>
                </tr>
                <tr>
                    <td><strong>Către:</strong></td>
                    <td>recipient@example.com</td>
                </tr>
                <tr>
                    <td><strong>Subiect:</strong></td>
                    <td>{subject}</td>
                </tr>
            </table>
        </div>
    """
    
    # Construim corpul emailului cu suport pentru design responsiv
    body_html = f"""
        <!-- Email body -->
        <div class="email-content" style="padding: 15px; line-height: 1.5;">
            {body}
        </div>
    """
    
    # Construim footerul emailului
    footer_html = f"""
        <!-- Footer -->
        <div class="email-footer" style="background-color: #f8f9fa; padding: 10px 15px; font-size: 11px; color: #6c757d; border-top: 1px solid #ddd; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;">
            {footer}
        </div>
    </div>
    </body>
    </html>
    """
    
    # Combinăm toate componentele
    html = header_html + body_html + footer_html
    
    return html

# Initialize session state defaults
defaults = {
    "score": 0,
    "total": 0,
    "current_index": 0,
    "start_time": datetime.now(),
    "enhanced_ui": True,
    "answered_types": {},
    "quiz_complete": False,
    "current_emails": None,
    "phish_positions": [],
    "just_verified": False,
    "detailed_explanations": True,  # Nou: activează explicații detaliate
    "show_indicators": False,  # Nou: arată indicatorii de phishing
    "current_analysis": None  # Nou: stochează analiza curentă
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Load data and compute max questions
examples = load_examples()
max_questions = len(examples)

# App header
st.title("🛡️ Antrenament Anti-Phishing")
st.markdown(
    """
    #### Dezvoltă-ți abilitățile de a identifica atacurile online!
    Acest simulator te pregătește să recunoști diverse tipuri de înșelătorii digitale.
    """
)

# Sidebar for metrics and settings
with st.sidebar:
    st.header("Statistici și Setări")
    st.metric("Scor curent", f"{st.session_state.score}/{st.session_state.total}")
    if st.session_state.total > 0:
        accuracy = st.session_state.score / st.session_state.total
        st.progress(accuracy, f"Acuratețe: {accuracy*100:.1f}%")
    elapsed = (datetime.now() - st.session_state.start_time).total_seconds()
    minutes, seconds = divmod(int(elapsed), 60)
    st.info(f"Timp petrecut: {minutes}m {seconds}s")

    st.subheader("Progres")
    done = len(st.session_state.answered_types)
    if max_questions > 0:
        st.progress(done / max_questions, f"Progres: {done}/{max_questions} tipuri")
    else:
        st.write("Nicio probă disponibilă.")

    st.subheader("Setări Interfață")
    st.session_state.enhanced_ui = st.toggle(
        "Interfață îmbunătățită", value=st.session_state.enhanced_ui
    )
    # Adaugă după linia cu toggleul "Interfață îmbunătățită"
    st.session_state.detailed_explanations = st.toggle("Explicații detaliate", value=st.session_state.detailed_explanations)

    if st.button("Resetează tot"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

# Main quiz logic
if st.session_state.quiz_complete:
    # Final report
    st.header("🎓 Raport Final")
    sc, tot = st.session_state.score, st.session_state.total
    percent = (sc/tot*100) if tot > 0 else 0
    st.subheader(f"Scor final: {sc}/{tot} ({percent:.1f}%)")
    elapsed = (datetime.now() - st.session_state.start_time).total_seconds()
    m, s = divmod(int(elapsed), 60)
    st.info(f"Timp total: {m}m {s}s")

    # Table of results
    results = []
    for ph_type, info in st.session_state.answered_types.items():
        results.append({
            "Tip phishing": ph_type,
            "Corect": "✅" if info["correct"] else "❌",
            "Explicație": info["explanation"]
        })
    st.table(results)

    # Highlight wrong answers with advice
    wrong = [t for t, inf in st.session_state.answered_types.items() if not inf["correct"]]
    if wrong:
        st.markdown("**Atenție! La următoarele tipuri ai răspuns greșit:**")
        for t in wrong:
            st.markdown(f"- {t}")
        st.markdown(
            "**Sfaturi pentru viitor:** Verifică întotdeauna link-urile și tonul urgent, asigură-te că domeniul expeditorului este legitim."
        )
    else:
        st.success("Felicitări! Ai identificat corect toate tipurile de phishing.")

    if st.button("Reia testul", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

else:
    # Quiz in progress
    if st.session_state.current_emails is None:
        # Select next question
        remaining = [i for i in range(max_questions)
                     if examples[i]["type"] not in st.session_state.answered_types]
        if not remaining or st.session_state.total >= max_questions:
            st.session_state.quiz_complete = True
            st.experimental_rerun()
        idx = random.choice(remaining)
        st.session_state.current_index = idx
        current = examples[idx]

        # Build email dicts
        real = {"subject": current["real"]["subject"], "body": current["real"]["body"]}
        fake = {"subject": current["fake"]["subject"], "body": current["fake"]["body"]}

        # Alternate phishing position
        if not st.session_state.phish_positions:
            seq = [True, False] * ((max_questions//2) + 1)
            random.shuffle(seq)
            st.session_state.phish_positions = seq
        left = st.session_state.phish_positions.pop(0)
        pair = [(fake, True), (real, False)] if left else [(real, False), (fake, True)]

        st.session_state.current_emails = pair
        phish_email = fake
        st.session_state.current_analysis = analyze_phishing_email(phish_email, current["type"])
        st.session_state.just_verified = False

    else:
        pair = st.session_state.current_emails
        current = examples[st.session_state.current_index]

    # Display emails side-by-side
    st.header(f"Tip: {current['type']}")
    col1, col2 = st.columns(2)
    for i, (email, _) in enumerate(pair):
        with (col1 if i == 0 else col2):
            st.subheader(f"Mesaj #{i+1}")
            # Modifică secțiunea unde afișezi emailurile cu components.html:
            if st.session_state.enhanced_ui:
                lines = email['body'].count("\n") + 5
                height = min(600, 100 + lines * 30)
                
                # Adaugă o clasă diferită pentru mobile vs desktop
                components.html(
                    format_email_html(email), 
                    height=height, 
                    scrolling=True
                )
            else:
                st.text_area("Subiect:", email['subject'], height=50, disabled=True)
                st.text_area("", email['body'], height=200, disabled=True)

    # User answer selection
    choice = st.selectbox("Care mesaj este phishing?", ["", "Mesaj #1", "Mesaj #2"], index=0)
    if choice:
        if st.button("Verifică răspunsul", use_container_width=True):
            sel = 0 if choice == "Mesaj #1" else 1
            correct = pair[sel][1]
            st.session_state.total += 1
            if correct:
                st.session_state.score += 1
                st.success("✅ Corect!")
            else:
                st.error("❌ Greșit!")
            corr = 'Mesaj #1' if pair[0][1] else 'Mesaj #2'
            st.info(f"Răspuns corect: {corr}")
            st.markdown(f"**Explicație:** {current['explanation']}")
            
            # Nou: Afișare analiză detaliată dacă este activată
            if st.session_state.detailed_explanations:
                st.session_state.show_indicators = True
                st.subheader("Analiză detaliată a emailului de phishing")
                
                # Găsește emailul de phishing
                phish_index = 0 if pair[0][1] else 1
                phish_data = pair[phish_index][0]
                
                # Afișează indicatorii de phishing
                analysis = st.session_state.current_analysis
                
                # Arată scorul de risc
                risk_score = analysis["total_risk_score"]
                risk_level = "Scăzut" if risk_score < 5 else "Mediu" if risk_score < 10 else "Ridicat"
                risk_color = "#4CAF50" if risk_score < 5 else "#FF9800" if risk_score < 10 else "#F44336"
                
                st.markdown(f"""
                <div style="border-radius: 5px; padding: 10px; background-color: {risk_color}; color: white; margin-bottom: 15px;">
                    <h3 style="margin: 0;">Nivel de risc: {risk_level}</h3>
                    <p style="margin: 5px 0 0 0;">Indicator principal: {analysis["primary_risk"]}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Listează toți indicatorii identificați
                st.markdown("### Indicatori de phishing identificați")
                
                # Creăm un tabel pentru indicatori
                indicators_data = []
                for ind in analysis["indicators"]:
                    if ind["risc"] != "informativ":
                        indicators_data.append({
                            "Indicator": ind["tip"],
                            "Detalii": ind["detalii"],
                            "Exemplu": ind["exemplu"],
                            "Nivel de risc": ind["risc"].capitalize()
                        })
                
                if indicators_data:
                    st.table(indicators_data)
                else:
                    st.info("Nu au fost identificați indicatori specifici de phishing.")
                
                # Afișăm emailul cu indicatori evidențiați
                st.markdown("### Email cu elemente suspecte evidențiate")
                
                # Pregătim conținutul evidențiat
                if analysis["indicators"]:
                    highlighted_body = highlight_phishing_indicators(phish_data["body"], analysis["indicators"])
                    highlighted_subject = highlight_phishing_indicators(phish_data["subject"], analysis["indicators"])
                    
                    phish_data_highlighted = {
                        "subject": highlighted_subject,
                        "body": highlighted_body,
                        "sender": phish_data.get("sender", "Expeditor"),
                        "sender_email": phish_data.get("sender_email", "expeditor@domain.com"),
                        "logo": phish_data.get("logo", "LOGO"),
                        "colors": phish_data.get("colors", "#F44336"),  # Roșu pentru phishing
                        "footer": phish_data.get("footer", "© Email de phishing - Utilizat în scopuri educaționale"),
                        "date": phish_data.get("date", datetime.now().strftime("%d.%m.%Y"))
                    }
                    
                    components.html(format_email_html(phish_data_highlighted), height=400, scrolling=True)
                
                # Sfaturi specifice pentru acest tip de phishing
                st.markdown("### Cum te protejezi împotriva acestui tip de phishing")
                
                tips_by_type = {
                    "Email-phishing clasic": [
                        "Verifică adresa exactă a expeditorului, nu doar numele afișat",
                        "Nu face click pe link-uri din emailuri nesolicitate",
                        "Trecerea mouse-ului peste link-uri îți permite să vezi URL-ul real",
                        "Verifică greșelile gramaticale și formulările neobișnuite"
                    ],
                    "Spear-phishing": [
                        "Verifică contextul și istoricul conversațiilor anterioare",
                        "Confirmă prin alt canal de comunicare solicitările neobișnuite",
                        "Fii atent la tonul și formulările diferite de cele obișnuite",
                        "Verifică adresa de email cu atenție, chiar dacă pare de la un cunoscut"
                    ]
                    # Vei adăuga restul tipurilor aici
                }
                
                # Afișează sfaturile specifice tipului de phishing
                if current["type"] in tips_by_type:
                    for tip in tips_by_type[current["type"]]:
                        st.markdown(f"✅ {tip}")
                else:
                    # Sfaturi generale
                    st.markdown("""
                    ✅ Verifică atent adresa expeditorului și URL-urile
                    ✅ Nu furniza niciodată date sensibile prin email
                    ✅ Folosește autentificarea în doi factori
                    ✅ Accesează direct site-urile web, nu prin link-uri din email
                    """)
                    
            st.session_state.answered_types[current['type']] = {
                'correct': correct,
                'explanation': current['explanation']
            }
            # Prepare next
            st.session_state.current_emails = None
            st.session_state.just_verified = True
    
    # Next example button
    if st.session_state.just_verified and st.button("Următorul exemplu", use_container_width=True):
        st.session_state.current_emails = None
        st.session_state.just_verified = False
        st.experimental_rerun()

# Educational sections
with st.expander("Sfaturi detectare phishing"):
    st.markdown("""
    ### Ghid complet pentru detectarea emailurilor de phishing:
    
    #### 1. Verifică expeditorul 📧
    * Analizează adresa de email completă, nu doar numele afișat
    * Verifică pentru greșeli subtile (de ex., amazon-secure.com în loc de amazon.com)
    * Observă domeniile neobișnuite (.xyz, .info, .online în loc de .com, .ro, .org)
    
    #### 2. Analizează link-urile 🔍
    * Trecerea cursorului peste link-uri îți permite să vezi URL-ul real
    * Evită să dai click pe URL-uri scurte (bit.ly, tinyurl, etc.)
    * Accesează site-urile oficiale scriind manual adresa în browser, nu prin link-uri
    * Verifică prezența HTTPS și a certificatului de securitate
    
    #### 3. Atenție la tonul de urgență ⚠️
    * Emailurile de phishing creează un sentiment de panică sau urgență
    * Frazele precum "acționează acum", "urgent", "contul va fi suspendat" sunt alarmante
    * Deciziile luate sub presiune sunt adesea greșite - ia-ți timp să verifici
    
    #### 4. Nu furniza date sensibile 🔒
    * Instituțiile legitime nu solicită niciodată parole sau date de card pe email
    * Nu descărca atașamente neașteptate - pot conține malware
    * Dacă se cere autentificare, mergi direct pe site-ul oficial
    
    #### 5. Activează securitatea suplimentară 🛡️
    * Folosește autentificarea în doi factori (2FA) pentru toate conturile importante
    * Utilizează parole unice pentru fiecare cont și un manager de parole
    * Menține software-ul actualizat pentru a te proteja de vulnerabilități
    
    #### 6. Verifică greșelile gramaticale și de formatare 📝
    * Emailurile de phishing conțin adesea greșeli gramaticale sau de formatare
    * Calitatea slabă a imaginilor sau logo-uri deformate pot indica un email fals
    * Inconsistențele în formatare sau fonturi diferite în același email sunt suspecte
    """)

with st.expander("Exemple recente"):
    st.markdown("""
    ### Tactici recente de phishing (2025):
    
    #### 📱 Phishing prin QR code
    * Emailuri false de livrare cu coduri QR care te duc pe site-uri malițioase
    * Oferte care necesită scanarea unui cod QR pentru "verificarea identității"
    
    #### 🤖 Deepfake și AI phishing
    * Emailuri ce imită perfect stilul de comunicare al colegilor sau șefilor
    * Mesaje generate cu AI care par foarte credibile și personalizate
    
    #### 📄 Documente colaborative false
    * Invitații false pentru documente Google Workspace sau Microsoft Office
    * Solicitări de colaborare care cer reautentificare sau descărcarea de "actualizări"
    
    #### ☁️ Cloud storage phishing
    * Notificări false despre depășirea spațiului de stocare în cloud
    * Alerte de securitate false care solicită resetarea parolei
    
    #### 🏦 Phishing bancar sofisticat
    * Copii aproape perfecte ale site-urilor bancare legitime
    * Notificări false de tranzacții suspecte ce solicită verificare imediată
    
    #### 📊 Atacuri de spear-phishing corporative
    * Emailuri care imită platforme de colaborare precum Teams sau Slack
    * Mesaje care par a fi de la departamentul IT solicitând actualizări de securitate
    """)
    with st.expander("Despre proiect"):
    st.markdown("""
    ### Despre Simulatorul Anti-Phishing
    
    **Simulatorul Anti-Phishing** este o platformă educațională interactivă concepută pentru a îmbunătăți abilitățile utilizatorilor de a identifica și evita atacurile de phishing.
    
    #### Obiective educaționale:
    * Creșterea gradului de conștientizare privind amenințările cibernetice
    * Dezvoltarea abilităților practice de identificare a emailurilor de phishing
    * Formarea de reflexe digitale sănătoase pentru o navigare sigură online
    
    #### Caracteristici:
    * Exemple realiste bazate pe tehnici moderne de phishing
    * Analiză detaliată a indicatorilor de risc
    * Feedback personalizat și recomandări de îmbunătățire
    * Interfață intuitivă și responsivă
    
    #### Date tehnice:
    * Versiune: 2.1.0
    * Dezvoltat cu: Python, Streamlit
    * Toate exemplele sunt create în scop educațional
    * Actualizat: Aprilie 2025
    
    #### Mențiuni legale:
    Toate exemplele de phishing prezentate sunt fictive și create exclusiv în scop educațional. Orice asemănare cu emailuri reale este întâmplătoare. Acest simulator nu colectează date personale și nu încurajează practicarea atacurilor de phishing.
    
    © 2025 Simulatorul Anti-Phishing | Codul sursă disponibil sub licență GNU GPL-3.0
    """)

# Footer
st.markdown("---")
st.markdown("© 2025 Anti-Phishing Simulator")
