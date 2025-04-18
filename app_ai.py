import streamlit as st
import random
import json
from datetime import datetime

# Configurare pagină
st.set_page_config(
    page_title="Vaccin Anti-Phishing",
    page_icon="🛡️",
    layout="wide"
)

# Funcție pentru încărcarea exemplelor predefinite
@st.cache_data
def load_examples():
    try:
        with open("examples.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        # Întoarcem o listă minimală de tip fallback dacă fișierul nu există
        return [
            {
                "type": "Email-phishing clasic",
                "real": {
                    "subject": "Factura lunii martie de la FurnizorulTau",
                    "body": "Stimate client,\n\nVă transmitem atașat factura pentru luna martie.\n\nCu stimă,\nEchipa FurnizorulTau."
                },
                "fake": {
                    "subject": "ACTIVITATE SUSPECTĂ pe contul tău – Verifică ACUM",
                    "body": "Contul tău a fost compromis. Click aici http://bit.ly/secure-check pentru resetare imediată."
                },
                "explanation": "Fals: ton de urgență, link scurt, domeniu neoficial. Real: limbaj formal, atașament legitim."
            },
            {
                "type": "Spear-phishing",
                "real": {
                    "subject": "Întâlnirea de proiect - agenda",
                    "body": "Bună ziua,\n\nVă trimit agenda pentru întâlnirea noastră de săptămâna viitoare.\nVă rog să confirmați participarea.\n\nCu stimă,\nMaria"
                },
                "fake": {
                    "subject": "Referitor la proiectul nostru",
                    "body": "Salut,\n\nAm observat că nu ai trimis încă documentele pentru proiectul X.\nDescarcă formularul de aici: http://docs-google.net/form și trimite-l urgent.\n\nMulțumesc,\nAndrei"
                },
                "explanation": "Fals: adresă URL suspectă (docs-google.net în loc de docs.google.com), presiune de timp."
            },
            {
                "type": "Fraudă bancară",
                "real": {
                    "subject": "Informare: Noi funcționalități în aplicația BancaX",
                    "body": "Stimată Doamnă/Stimate Domn,\n\nVă informăm că am actualizat aplicația mobilă cu noi funcționalități.\nPentru detalii, accesați aplicația sau www.banca-x.ro.\n\nBancaX"
                },
                "fake": {
                    "subject": "URGENT: Cardul dvs. va fi blocat",
                    "body": "Stimat client,\n\nCardul dvs. va fi blocat în 24h din cauza unei activități suspecte.\nPentru verificare, accesați: http://banca-x.secureverify.com și introduceți datele cardului.\n\nDepartament Securitate"
                },
                "explanation": "Fals: domeniu fals (banca-x.secureverify.com), solicitare date card, ton de urgență."
            }
        ]

# Inițializare stare sesiune
if "score" not in st.session_state:
    st.session_state.score = 0
if "total" not in st.session_state:
    st.session_state.total = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.now()

# Încărcăm exemplele
examples = load_examples()

# Interfață utilizator
st.title("🛡️ Vaccin Anti-Phishing")
st.markdown("""
#### Antrenează-te să recunoști atacurile de phishing!
Acest quiz te ajută să identifici mesajele frauduloase fără să îți cerem nicio informație personală.
""")

# Sidebar cu scor, statistici și setări
with st.sidebar:
    st.header("Statistici")
    st.metric("Scor curent", f"{st.session_state.score}/{st.session_state.total}")
    if st.session_state.total > 0:
        accuracy = (st.session_state.score / st.session_state.total) * 100
        st.progress(accuracy/100, f"Acuratețe: {accuracy:.1f}%")
    
    elapsed_time = (datetime.now() - st.session_state.start_time).total_seconds()
    minutes, seconds = divmod(int(elapsed_time), 60)
    st.info(f"Timp petrecut: {minutes}m {seconds}s")
    
    if st.button("Resetează scorul"):
        st.session_state.score = 0
        st.session_state.total = 0
        st.session_state.start_time = datetime.now()
        st.rerun()

# Container principal
main_container = st.container()

with main_container:
    # Alegem un exemplu aleatoriu
    example = random.choice(examples)
    
    # Afișăm tipul de phishing
    st.header(f"Tip: {example['type']}")
    
    # Creăm lista cu cele două emailuri și amestecăm ordinea
    emails = [
        {"content": f"Subiect: {example['real']['subject']}\n\n{example['real']['body']}", "is_phish": False},
        {"content": f"Subiect: {example['fake']['subject']}\n\n{example['fake']['body']}", "is_phish": True}
    ]
    random.shuffle(emails)
    
    # Afișăm emailurile
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Mesaj #1")
        st.text_area("", emails[0]["content"], height=300, key="msg1", disabled=True)
    
    with col2:
        st.subheader("Mesaj #2")
        st.text_area("", emails[1]["content"], height=300, key="msg2", disabled=True)
    
    # Secțiunea de decizie
    choice = st.radio("Care dintre mesaje crezi că este phishing?", ["Mesaj #1", "Mesaj #2"])
    idx = 0 if choice == "Mesaj #1" else 1
    
    # Verificare răspuns
    if st.button("Verifică răspunsul", use_container_width=True):
        st.session_state.total += 1
        correct = emails[idx]["is_phish"]
        
        if correct:
            st.session_state.score += 1
            st.success("✅ Corect! Ai identificat corect mesajul de phishing.")
        else:
            st.error("❌ Greșit! Acesta nu era mesajul de phishing.")
        
        # Afișăm explicația
        st.markdown(f"**Explicație:** {example['explanation']}")
        
        # Afișăm care era răspunsul corect
        correct_idx = 0 if emails[0]["is_phish"] else 1
        st.info(f"Răspunsul corect era: Mesaj #{correct_idx + 1}")
        
        # Buton pentru următorul exemplu
        if st.button("Următorul exemplu", use_container_width=True):
            st.rerun()

# Informații educaționale în partea de jos
with st.expander("Sfaturi pentru detectarea phishing-ului"):
    st.markdown("""
    ### Cum să recunoști un email de phishing:
    
    1. **Verifică adresa expeditorului** - Adresele de email care imită companii legitime adesea conțin greșeli sau domenii ciudate
    2. **Fii atent la tonul urgent** - Mesajele care creează un sentiment de urgență sunt adesea phishing
    3. **Verifică link-urile** - Plasează cursorul peste link (fără a da click) pentru a vedea URL-ul real
    4. **Fii prudent cu atașamentele** - Nu deschide atașamente neașteptate
    5. **Observă greșelile gramaticale** - Comunicările profesionale rareori conțin multe greșeli
    6. **Verifică modul de adresare** - Mesajele generice ("Dragă client") pot fi suspecte
    7. **Nu oferi informații personale** - Companiile legitime nu cer date sensibile prin email
    """)

with st.expander("Despre acest proiect"):
    st.markdown("""
    Acest quiz educațional a fost creat pentru a ajuta utilizatorii să recunoască diverse tipuri de atacuri de phishing. 
    
    Aplicația nu colectează, stochează sau procesează niciun fel de date personale.
    
    Toate exemplele sunt create în scop educațional și nu reprezintă comunicări reale.
    """)
    
    feedback = st.text_area("Feedback sau sugestii:")
    if st.button("Trimite feedback"):
        st.success("Mulțumim pentru feedback! Vom lua în considerare sugestiile tale pentru versiunile viitoare.")

# Footer
st.markdown("---")
st.markdown("© 2025 Vaccin Anti-Phishing | Creat în scop educațional")
