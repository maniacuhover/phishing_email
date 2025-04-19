import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime
import random

# Ensure this is the first Streamlit call
st.set_page_config(page_title="Vaccin Anti-Phishing", page_icon="🛡️", layout="wide")

# HTML renderer import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from html_email_renderer import render_html_email as format_email_html
from phishing_analyzer import analyze_phishing_email
from text_highlighter import highlight_phishing_indicators
# Load examples from JSON file
@st.cache_data
def load_examples():
    try:
        with open("examples.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

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
    "just_verified": False,  # Adaugă virgulă aici
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
        st.session_state.current_analysis = analyze_phishing_email(phish_email, cur["type"])
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
            if st.session_state.enhanced_ui:
                lines = email['body'].count("\n") + 5
                height = min(600, 100 + lines * 30)
                components.html(format_email_html(email), height=height, scrolling=True)
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
- Verifică expeditorul
- Analizează link-urile
- Atenție la tonul de urgență
- Nu furniza date sensibile
- Activează 2FA
""")
with st.expander("Exemple recente"):
    st.markdown("""
- Coșuri cadou false
- Vouchere false
- Felicitări cu malware
- Notificări false de livrare
""")
with st.expander("Despre proiect"):
    st.markdown("Educațional; exemple fictive.")

# Footer
st.markdown("---")
st.markdown("© 2025 Anti-Phishing Simulator")
