import streamlit as st
import random
import json
import os
import requests
from datetime import datetime

# Importăm utilitarele pentru emailuri realiste
from templates import generate_realistic_email, LEGITIMATE_TEMPLATES, PHISHING_TEMPLATES
from html_email_renderer import render_html_email

# Configurare pagină
st.set_page_config(
    page_title="Vaccin Anti-Phishing Realist",
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
        # Întoarcem o listă minimală de tip fallback
        return [
            {
                "type": "Banking",
                "explanation": "Verifică adresa expeditorului, link-urile și cererile de informații personale."
            },
            {
                "type": "E-commerce",
                "explanation": "Fii atent la urgența mesajului, link-uri suspecte și solicitări de date de card."
            },
            {
                "type": "Social Media",
                "explanation": "Verifică domeniul emailului, evită să dai click pe link-uri și nu introduce parole."
            }
        ]

# Funcție pentru generarea de emailuri realiste
def generate_realistic_emails(phishing_type):
    """
    Generează emailuri realiste bazate pe șabloane și AI
    """
    # Determinăm categoria din tipul de phishing
    category = phishing_type.lower().split()[0] if " " in phishing_type else phishing_type.lower()
    
    # Selectăm șablonul potrivit din categoriile disponibile
    available_categories = list(LEGITIMATE_TEMPLATES.keys())
    if category not in available_categories:
        category = random.choice(available_categories)
    
    # Generăm emailuri
    real_email = generate_realistic_email(category, is_phishing=False)
    fake_email = generate_realistic_email(category, is_phishing=True)
    
    # Folosim AI pentru a îmbogăți conținutul, dacă e disponibil
    if st.session_state.ai_mode:
        api_key = os.environ.get("HF_API_KEY", st.secrets.get("HF_API_KEY", None))
        if api_key:
            try:
                # Prompt îmbunătățit pentru email legitim
                prompt_real = f"""
                Generează un email profesional și legitim în limba română pe tema "{phishing_type}".
                Emailul trebuie să fie FOARTE REALIST și să includă:
                1. O formulă de adresare profesională
                2. Un conținut structurat clar cu paragrafe
                3. Detalii specifice și credibile
                4. Limbaj profesional fără greșeli gramaticale
                5. O concluzie clară cu next steps
                
                Emailul trebuie să fie COMPLET LEGITIM, fără niciun element suspect.
                """
                
                # Prompt îmbunătățit pentru email phishing
                prompt_fake = f"""
                Generează un email de phishing în limba română pe tema "{phishing_type}" care să pară foarte legitim la prima vedere, dar să conțină subtil indicii de phishing.
                
                Emailul trebuie să IMITE perfect un email corporativ legitim, dar să includă elemente de phishing SUBTILE cum ar fi:
                1. Domeniu de email puțin modificat (ex: netf1ix în loc de netflix)
                2. Link-uri care par legitime dar au URL-uri suspecte
                3. Greșeli ortografice minore, greu de observat
                4. Ton de urgență moderat dar prezent
                5. Solicitare de informații personale sau financiare într-un mod aparent justificat
                
                Fă acest email EXTREM DE CONVINGĂTOR, astfel încât doar o persoană foarte atentă să poată observa elementele de phishing.
                """
                
                # Facem request-urile către API
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                response_real = requests.post(
                    "https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf",
                    headers=headers,
                    json={"inputs": prompt_real, "parameters": {"max_length": 500}}
                )
                
                response_fake = requests.post(
                    "https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf",
                    headers=headers,
                    json={"inputs": prompt_fake, "parameters": {"max_length": 500}}
                )
                
                if response_real.status_code == 200:
                    real_email["body"] = response_real.json()[0]["generated_text"]
                
                if response_fake.status_code == 200:
                    fake_email["body"] = response_fake.json()[0]["generated_text"]
            
            except Exception as e:
                st.error(f"Eroare la generarea cu AI: {str(e)}")
    
    return real_email, fake_email

# Inițializare stare sesiune
if "score" not in st.session_state:
    st.session_state.score = 0
if "total" not in st.session_state:
    st.session_state.total = 0
if "examples_used" not in st.session_state:
    st.session_state.examples_used = []
if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.now()
if "ai_mode" not in st.session_state:
    st.session_state.ai_mode = True  # Activăm implicit modul AI
if "advanced_rendering" not in st.session_state:
    st.session_state.advanced_rendering = True  # Activăm implicit renderarea avansată

# Încărcăm exemplele și categoriile
examples = load_examples()
phishing_types = [ex["type"] for ex in examples]

# Interfață utilizator
st.title("🛡️ Vaccin Anti-Phishing Ultra-Realist")
st.markdown("""
#### Antrenează-te să recunoști atacurile de phishing extrem de sofisticate!
Acest quiz folosește șabloane profesionale și Inteligență Artificială pentru a genera 
emailuri realiste și te ajută să identifici mesajele frauduloase.
""")

# Sidebar cu scor, statistici și setări
with st.sidebar:
    st.header("Statistici și Setări")
    st.metric("Scor curent", f"{st.session_state.score}/{st.session_state.total}")
    if st.session_state.total > 0:
        accuracy = (st.session_state.score / st.session_state.total) * 100
        st.progress(accuracy/100, f"Acuratețe: {accuracy:.1f}%")
    
    elapsed_time = (datetime.now() - st.session_state.start_time).total_seconds()
    minutes, seconds = divmod(int(elapsed_time), 60)
    st.info(f"Timp petrecut: {minutes}m {seconds}s")
    
    st.subheader("Mod de funcționare")
    ai_mode = st.toggle("Folosește AI pentru îmbogățire conținut", value=st.session_state.ai_mode)
    if ai_mode != st.session_state.ai_mode:
        st.session_state.ai_mode = ai_mode
        if "current_example" in st.session_state:
            del st.session_state.current_example
    
    advanced_rendering = st.toggle("Renderare avansată emailuri", value=st.session_state.advanced_rendering)
    if advanced_rendering != st.session_state.advanced_rendering:
        st.session_state.advanced_rendering = advanced_rendering
        if "current_example" in st.session_state:
            del st.session_state.current_example
    
    if st.button("Resetează scorul"):
        st.session_state.score = 0
        st.session_state.total = 0
        st.session_state.examples_used = []
        st.session_state.start_time = datetime.now()
        if "current_example" in st.session_state:
            del st.session_state.current_example
        st.rerun()

# Container principal
main_container = st.container()

with main_container:
    # Selectăm tipul de phishing
    phishing_type = st.selectbox("Alege tipul de phishing", phishing_types)
    
    # Buton pentru generare sau regenerare
    generate_btn = st.button("Generează exemple realiste", use_container_width=True)
    
    # Generăm un exemplu nou sau folosim AI pentru a genera
    if generate_btn or "current_example" not in st.session_state:
        explanation = next((ex["explanation"] for ex in examples if ex["type"] == phishing_type), 
                          "Verifică adresa expeditorului, link-urile și solicitările de informații.")
        
        # Generăm emailuri realiste
        with st.spinner("Generez emailuri realiste..."):
            real_email, fake_email = generate_realistic_emails(phishing_type)
            
            # Setăm exemplul curent
            st.session_state.current_example = {
                "type": phishing_type,
                "real": real_email,
                "fake": fake_email,
                "explanation": explanation
            }
        
        # Pregătim lista cu două intrări și amestecăm ordinea
        items = [
            {"email": st.session_state.current_example["real"], "is_phish": False},
            {"email": st.session_state.current_example["fake"], "is_phish": True}
        ]
        random.shuffle(items)
        st.session_state.items = items
    
    # Afișăm cele două e-mailuri
    st.header(f"Tip: {st.session_state.current_example['type']}")
    
    if st.session_state.ai_mode:
        st.info("Aceste exemple folosesc AI pentru a genera conținut realist.")
    
    col1, col2 = st.columns(2)
    
    # Modul de afișare depinde de setarea de renderare avansată
    with col1:
    st.subheader("Mesaj #1")
    st.text_area("Subiect:", st.session_state.items[0]["email"]["subject"], height=50, key="subj1", disabled=True)
    st.text_area("", st.session_state.items[0]["email"]["body"], height=250, key="body1", disabled=True)

    with col2:
    st.subheader("Mesaj #2")
    st.text_area("Subiect:", st.session_state.items[1]["email"]["subject"], height=50, key="subj2", disabled=True)
    st.text_area("", st.session_state.items[1]["email"]["body"], height=250, key="body2", disabled=True)    else:
        # Folosim modul simplu de afișare
        with col1:
            st.subheader("Mesaj #1")
            st.text_area("Subiect:", st.session_state.items[0]["email"]["subject"], height=50, key="subj1", disabled=True)
            st.text_area("", st.session_state.items[0]["email"]["body"], height=250, key="body1", disabled=True)
        
        with col2:
            st.subheader("Mesaj #2")
            st.text_area("Subiect:", st.session_state.items[1]["email"]["subject"], height=50, key="subj2", disabled=True)
            st.text_area("", st.session_state.items[1]["email"]["body"], height=250, key="body2", disabled=True)
    
    # Secțiunea de decizie
    choice = st.radio("Care dintre mesaje crezi că este phishing?", ["Mesaj #1", "Mesaj #2"])
    idx = 0 if choice == "Mesaj #1" else 1
    
    # Verificare răspuns
    if st.button("Verifică răspunsul", use_container_width=True):
        st.session_state.total += 1
        correct = st.session_state.items[idx]["is_phish"]
        
        if correct:
            st.session_state.score += 1
            st.success("✅ Corect! Ai identificat corect mesajul de phishing.")
        else:
            st.error("❌ Greșit! Acesta nu era mesajul de phishing.")
        
        # Afișăm explicația
        st.markdown(f"**Explicație:** {st.session_state.current_example['explanation']}")
        
        # Afișăm care era răspunsul corect
        correct_idx = next((i for i, item in enumerate(st.session_state.items) if item["is_phish"]), None)
        st.info(f"Răspunsul corect era: Mesaj #{correct_idx + 1}")
        
        # Afișăm analiza detaliată a emailului de phishing
        st.subheader("Analiză detaliată a mesajului de phishing:")
        
        # Obținem emailul de phishing
        phish_email = st.session_state.items[correct_idx]["email"]
        
        # Analizăm și evidențiem indicatorii de phishing
        indicators = []
        
        # Verificăm adresa expeditorului
        sender_email = phish_email.get("sender_email", "")
        if "1" in sender_email or sender_email.count(".") > 2 or "-secure" in sender_email:
            indicators.append(("Adresă expeditor suspectă", sender_email, 
                              "Verifică cu atenție domeniul emailului. Atenție la caractere înlocuite sau domenii adăugate."))
        
        # Verificăm subiectul
        subject = phish_email.get("subject", "")
        if "URGENT" in subject or "imediat" in subject.lower() or "acum" in subject.lower():
            indicators.append(("Ton de urgență în subiect", subject,
                              "Mesajele legitime rareori folosesc un ton excesiv de urgent în subiect."))
        
        # Verificăm corpul emailului
        body = phish_email.get("body", "")
        
        # Verificăm link-uri
        if "http://" in body or ".xyz" in body or ".info" in body or "-secure" in body:
            link_sample = body.split("http://")[1].split(" ")[0] if "http://" in body else "domeniu-suspect.com"
            indicators.append(("Link-uri suspecte", f"http://{link_sample}",
                              "Verifică întotdeauna URL-urile înainte de a da click. Plasează cursorul peste link pentru a vedea adresa reală."))
        
        # Verificăm solicitări de date personale
        if "parolă" in body.lower() or "card" in body.lower() or "cod" in body.lower():
            indicators.append(("Solicitare de date personale", "Solicitare de informații sensibile",
                              "Companiile legitime nu cer niciodată parole sau date de card prin email."))
        
        # Verificăm presiunea de timp
        if "24 de ore" in body or "urgent" in body.lower() or "imediat" in body.lower():
            indicators.append(("Presiune de timp", "Acțiune urgentă solicitată",
                              "Crearea unui sentiment de urgență este o tactică comună pentru a determina utilizatorii să acționeze impulsiv."))
        
        # Afișăm indicatorii găsiți
        if indicators:
            cols = st.columns(3)
            cols[0].markdown("**Indicator**")
            cols[1].markdown("**Exemplu**")
            cols[2].markdown("**De ce e suspect**")
            
            for indicator, example, explanation in indicators:
                cols = st.columns(3)
                cols[0].markdown(f"🚨 **{indicator}**")
                cols[1].markdown(f"{example}")
                cols[2].markdown(f"{explanation}")
        else:
            st.write("Nu au fost detectați automat indicatori de phishing, dar verifică întotdeauna cu atenție detaliile emailurilor.")
            
        # Oferim recomandări generale
        st.markdown("""
        ### Recomandări generale:
        
        1. **Verifică întotdeauna adresa expeditorului** - Adresele de email falsificate adesea conțin greșeli subtile
        2. **Nu da click pe link-uri suspecte** - Accesează site-urile direct prin browser
        3. **Nu furniza date personale prin email** - Companiile legitime nu solicită astfel de informații
        4. **Contactează direct compania** - Dacă ai dubii, contactează compania prin canale oficiale
        5. **Raportează emailurile de phishing** - Ajută la protejarea altor utilizatori
        """)

# Informații educaționale în partea de jos
with st.expander("Cum să detectezi un email de phishing"):
    st.markdown("""
    ### Indicatori comuni de phishing:
    
    1. **Domenii de email modificate subtil**
       - Exemple: netfl1x.com, paypa1.com, amaz0n.com
       - Verifică întotdeauna adresa completă a expeditorului
    
    2. **Urgență și amenințări**
       - Crearea unui sentiment de urgență pentru a determina acțiuni impulsive
       - Amenințări cu suspendarea contului sau alte consecințe negative
    
    3. **Greșeli gramaticale și de ortografie**
       - Deși atacurile sofisticate pot avea text perfect, multe conțin erori subtile
       - Companiile mari au de obicei procese riguroase de verificare a comunicărilor
    
    4. **Solicitări de informații personale**
       - Bănci, magazine online și alte servicii nu solicită niciodată date sensibile prin email
       - Nu trimite niciodată parole, coduri PIN sau date de card prin email
    
    5. **Link-uri și atașamente suspecte**
       - Plasează cursorul peste link-uri pentru a vedea URL-ul real
       - Verifică dacă URL-ul coincide exact cu site-ul oficial al companiei
       - Fii precaut cu atașamentele neașteptate
    
    6. **Oferte prea bune pentru a fi adevărate**
       - Câștiguri neașteptate la loterii la care nu ai participat
       - Moșteniri de la persoane necunoscute
       - Reduceri extraordinare fără motiv aparent
    """)

with st.expander("Despre această aplicație"):
    st.markdown("""
    ### Despre Vaccinul Anti-Phishing Ultra-Realist
    
    Această aplicație a fost creată pentru a oferi un antrenament realist împotriva phishing-ului, folosind:
    
    - **Șabloane profesionale de email** - bazate pe comunicări reale ale companiilor
    - **Inteligență Artificială** - pentru a genera conținut variat și realist
    - **Elemente vizuale autentice** - pentru a simula cât mai bine emailurile reale
    
    Scopul este de a antrena utilizatorii să detecteze chiar și cele mai sofisticate atacuri de phishing.
    
    Aplicația nu colectează, stochează sau procesează niciun fel de date personale.
    
    ### Tehnologii folosite:
    - Frontend: Streamlit
    - Generare conținut: Șabloane + AI
    - Hosting: Streamlit Community Cloud
    """)

# Footer
st.markdown("---")
st.markdown("© 2025 Vaccin Anti-Phishing Ultra-Realist | Creat în scop educațional")
