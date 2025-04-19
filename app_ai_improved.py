import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime
import random

# Importuri pentru analiza detaliată
from phishing_analyzer import analyze_phishing_email
from text_highlighter import highlight_phishing_indicators

# PAGE CONFIGURATION - must be first
st.set_page_config(page_title="Vaccin Anti-Phishing", page_icon="🛡️", layout="wide")

# HTML renderer
from html_email_renderer import render_html_email as format_email_html

# Load examples
@st.cache_data
def load_examples():
    try:
        with open("examples.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Initialize session state
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
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Load data
examples = load_examples()
max_questions = len(examples)

# Header
st.title("🛡️ Antrenament Anti-Phishing")
st.markdown("""
#### Dezvoltă-ți abilitățile de a identifica atacurile online!
Acest simulator te pregătește să recunoști diverse tipuri de înșelătorii digitale.
""")

# Sidebar
with st.sidebar:
    st.header("Statistici și Setări")
    st.metric("Scor curent", f"{st.session_state.score}/{st.session_state.total}")
    if st.session_state.total:
        acc = st.session_state.score / st.session_state.total
        st.progress(acc, f"Acuratețe: {acc*100:.1f}%")
    elapsed = (datetime.now() - st.session_state.start_time).total_seconds()
    m, s = divmod(int(elapsed), 60)
    st.info(f"Timp petrecut: {m}m {s}s")

    st.subheader("Progres")
    done = len(st.session_state.answered_types)
    st.progress(done/max_questions if max_questions else 0, f"Progres: {done}/{max_questions}")

    st.subheader("Interfață")
    st.session_state.enhanced_ui = st.toggle("Interfață îmbunătățită", value=st.session_state.enhanced_ui)
    
    # Nou: opțiune pentru explicații detaliate
    st.session_state.detailed_explanations = st.toggle("Explicații detaliate", value=st.session_state.detailed_explanations)

    if st.button("Resetează tot"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.experimental_rerun()

# Main
if st.session_state.quiz_complete:
    # Final report
    st.header("🎓 Raport Final")
    sc, tot = st.session_state.score, st.session_state.total
    pct = (sc/tot*100) if tot else 0
    st.subheader(f"Scor final: {sc}/{tot} ({pct:.1f}%)")
    elapsed = (datetime.now() - st.session_state.start_time).total_seconds()
    m, s = divmod(int(elapsed), 60)
    st.info(f"Timp total: {m}m {s}s")

    # Table of results
    rows = []
    for t, info in st.session_state.answered_types.items():
        rows.append({
            "Tip phishing": t,
            "Corect": "✅" if info["correct"] else "❌",
            "Explicație": info["explanation"]
        })
    st.table(rows)

    # Feedback on wrong types
    wrong = [t for t, inf in st.session_state.answered_types.items() if not inf["correct"]]
    if wrong:
        st.markdown("**Atenție! La următoarele tipuri ai avut erori:**")
        for t in wrong:
            st.markdown(f"- {t}")
        st.markdown(
            "**Sfaturi pentru viitor:** Analizează mai atent link-urile suspecte, tonul de urgență și verifică domeniile înainte de a da click."
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
        rem = [i for i in range(max_questions) if examples[i]["type"] not in st.session_state.answered_types]
        if not rem or st.session_state.total >= max_questions:
            st.session_state.quiz_complete = True
            st.experimental_rerun()
        idx = random.choice(rem)
        st.session_state.current_index = idx
        cur = examples[idx]

        # Build emails
        real = {"subject": cur["real"]["subject"], "body": cur["real"]["body"]}
        fake = {"subject": cur["fake"]["subject"], "body": cur["fake"]["body"]}

        # Alternate position
        if not st.session_state.phish_positions:
            seq = [True, False] * ((max_questions//2) + 1)
            random.shuffle(seq)
            st.session_state.phish_positions = seq
        left = st.session_state.phish_positions.pop(0)
        pair = [(fake, True), (real, False)] if left else [(real, False), (fake, True)]

        st.session_state.current_emails = pair
        st.session_state.just_verified = False
        current = cur
        
        # Nou: analizează emailul de phishing pentru explicații detaliate
        phish_email = fake
        st.session_state.current_analysis = analyze_phishing_email(phish_email, cur["type"])
    else:
        pair = st.session_state.current_emails
        current = examples[st.session_state.current_index]

    # Display side-by-side
    st.header(f"Tip: {current['type']}")
    col1, col2 = st.columns(2)
    for i, (data, _) in enumerate(pair):
        with (col1 if i == 0 else col2):
            st.subheader(f"Mesaj #{i+1}")
            if st.session_state.enhanced_ui:
                lines = data['body'].count("\n") + 5
                h = min(600, 100 + lines * 30)
                components.html(format_email_html(data), height=h, scrolling=True)
            else:
                st.text_area("Subiect:", data['subject'], height=50, disabled=True)
                st.text_area("", data['body'], height=200, disabled=True)

    choice = st.selectbox(
        "Care mesaj este phishing?",
        ["", "Mesaj #1", "Mesaj #2"],
        index=0
    )
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
            
            # Explicație de bază
            st.markdown(f"**Explicație de bază:** {current['explanation']}")
            
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
                
                # Sfaturi pentru protecție
                st.markdown("### Cum te protejezi împotriva acestui tip de phishing")
                
                # Tips adaptate tipului de phishing
                general_tips = [
                    "Verifică atent adresa expeditorului și URL-urile",
                    "Nu furniza niciodată date sensibile prin email",
                    "Folosește autentificarea în doi factori",
                    "Accesează direct site-urile web, nu prin link-uri din email"
                ]
                
                for tip in general_tips:
                    st.markdown(f"✅ {tip}")
            
            st.session_state.answered_types[current['type']] = {
                'correct': correct,
                'explanation': current['explanation']
            }
            st.session_state.current_emails = None
            st.session_state.just_verified = True

    if st.session_state.just_verified and st.button("Următorul exemplu", use_container_width=True):
        st.session_state.current_emails = None
        st.session_state.just_verified = False
        st.experimental_rerun()

# Educational expanders
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
