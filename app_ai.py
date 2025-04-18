import streamlit as st
import random
import json
import os
import requests
from datetime import datetime

# Configurare pagină
st.set_page_config(
    page_title="Vaccin Anti-Phishing AI",
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

# Funcție pentru generarea emailurilor cu AI
def generate_emails_with_ai(phishing_type):
    """
    Generează emailuri folosind API-ul Hugging Face
    """
    # Verificăm dacă există o cheie API configurată
    api_key = os.environ.get("HF_API_KEY", st.secrets.get("HF_API_KEY", None))
    
    if not api_key:
        # Simulăm generarea dacă nu avem API key (pentru demo)
        return {
            "real": {
                "subject": f"Email legitim despre {phishing_type}",
                "body": f"Acesta este un email legitim generat pentru {phishing_type}.\n\nAre un ton profesional, nu solicită date personale și folosește un domeniu oficial."
            },
            "fake": {
                "subject": f"URGENT: Situație de {phishing_type}!!!",
                "body": f"ATENȚIE! Acesta este un email de phishing generat pentru {phishing_type}.\n\nAre un ton urgent, solicită acțiune imediată și probabil conține un link suspect: http://website-fals.com"
            }
        }
    
    # Dacă avem cheie API, facem cererea către serviciul AI
    try:
        # Prompt pentru email legitim
        prompt_real = f"""
        Generează un email PROFESIONAL și LEGITIM românesc pe tema "{phishing_type}".
        Email-ul trebuie să fie autentic, să respecte toate regulile profesionale de comunicare
        și să NU conțină elemente de phishing. Include subiect și corp.
        """
        
        # Prompt pentru email phishing
        prompt_fake = f"""
        Generează un email DE PHISHING românesc pe tema "{phishing_type}".
        Email-ul trebuie să PARĂ legitim, dar să conțină indicii care ar arăta că e phishing: 
        urgență, link-uri suspecte, cerere de date personale, etc. Include subiect și corp.
        """
        
        # Facem request-urile către API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Request pentru email legitim
        response_real = requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
            headers=headers,
            json={"inputs": prompt_real, "parameters": {"max_length": 300}}
        )
        
        # Request pentru email phishing
        response_fake = requests.post(
            "https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf",
            headers=headers,
            json={"inputs": prompt_fake, "parameters": {"max_length": 300}}
        )
        
        # Procesăm răspunsurile
        if response_real.status_code == 200 and response_fake.status_code == 200:
            real_text = response_real.json()[0]["generated_text"]
            fake_text = response_fake.json()[0]["generated_text"]
            
            # Extragem subiect și corp
            real_lines = real_text.split("\n")
            fake_lines = fake_text.split("\n")
            
            real_subject = next((line for line in real_lines if "subiect" in line.lower()), "Email legitim")
            fake_subject = next((line for line in fake_lines if "subiect" in line.lower()), "URGENȚĂ: Acțiune necesară")
            
            real_body = "\n".join(line for line in real_lines if "subiect" not in line.lower())
            fake_body = "\n".join(line for line in fake_lines if "subiect" not in line.lower())
            
            return {
                "real": {
                    "subject": real_subject.replace("Subiect:", "").strip(),
                    "body": real_body.strip()
                },
                "fake": {
                    "subject": fake_subject.replace("Subiect:", "").strip(),
                    "body": fake_body.strip()
                }
            }
        else:
            # Fallback la exemple statice
            raise Exception("API error")
            
    except Exception as e:
        st.error(f"Eroare la generarea cu AI: {str(e)}")
        # Răspuns de fallback
        return {
            "real": {
                "subject": f"Email legitim despre {phishing_type}",
                "body": f"Acesta este un email legitim despre {phishing_type}.\n\nAre un ton profesional, nu solicită date personale și folosește un domeniu oficial."
            },
            "fake": {
                "subject": f"URGENT: Situație de {phishing_type}!!!",
                "body": f"ATENȚIE! Acesta este un email de phishing pentru {phishing_type}.\n\nAre un ton urgent, solicită acțiune imediată și probabil conține un link suspect: http://website-fals.com"
            }
        }

# Funcție pentru a formata frumos emailul
def format_email_html(email_data):
    """
    Formatează emailul într-un format HTML mai frumos
    """
    subject = email_data.get("subject", "Fără subiect")
    body = email_data.get("body", "").replace("\n", "<br>")
    
    html = f"""
    <div style="border: 1px solid #ddd; border-radius: 5px; padding: 15px; background-color: #f9f9f9; font-family: Arial, sans-serif;">
        <div style="border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 15px;">
            <div style="font-weight: bold; color: #444; font-size: 16px;">{subject}</div>
        </div>
        <div style="color: #333; line-height: 1.5;">
            {body}
        </div>
    </div>
    """
    return html

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
    st.session_state.ai_mode = False
if "enhanced_ui" not in st.session_state:
    st.session_state.enhanced_ui = True
if "current_example_type" not in st.session_state:
    # Alegem un tip de phishing aleatoriu pentru a începe
    examples = load_examples()
    st.session_state.current_example_type = random.choice([ex["type"] for ex in examples])

# Încărcăm exemplele
examples = load_examples()

# Interfață utilizator
st.title("🛡️ Vaccin Anti-Phishing cu AI")
st.markdown("""
#### Antrenează-te să recunoști atacurile de phishing!
Acest quiz folosește Inteligența Artificială pentru a genera emailuri realiste și te ajută să identifici 
mesajele frauduloase fără să îți cerem nicio informație personală.
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
    ai_mode = st.toggle("Folosește AI pentru generare", value=st.session_state.ai_mode)
    if ai_mode != st.session_state.ai_mode:
        st.session_state.ai_mode = ai_mode
    
    enhanced_ui = st.toggle("Interfață îmbunătățită", value=st.session_state.enhanced_ui)
    if enhanced_ui != st.session_state.enhanced_ui:
        st.session_state.enhanced_ui = enhanced_ui
    
    if st.button("Resetează scorul"):
        st.session_state.score = 0
        st.session_state.total = 0
        st.session_state.examples_used = []
        st.session_state.start_time = datetime.now()
        st.rerun()

# Container principal
main_container = st.container()

with main_container:
    # Selector pentru tipul de phishing
    example_type = st.selectbox(
        "Alege tipul de phishing", 
        [ex["type"] for ex in examples],
        index=[ex["type"] for ex in examples].index(st.session_state.current_example_type)
    )
    
    # Actualizăm tipul curent dacă s-a schimbat
    if example_type != st.session_state.current_example_type:
        st.session_state.current_example_type = example_type
    
    # Buton pentru generare
    generate_button = st.button("Generează exemplu", use_container_width=True)
    
    # Dacă s-a apăsat butonul de generare sau nu avem încă example
    if generate_button or "current_emails" not in st.session_state:
        explanation = next((ex["explanation"] for ex in examples if ex["type"] == example_type), 
                          "Verifică adresa expeditorului, link-urile și solicitările de informații.")
        
        if st.session_state.ai_mode:
            # Generare cu AI
            with st.spinner("Generez emailuri cu AI..."):
                generated = generate_emails_with_ai(example_type)
                
                real_email = generated["real"]
                fake_email = generated["fake"]
        else:
            # Folosim exemplul predefinit
            example = next((ex for ex in examples if ex["type"] == example_type), None)
            if not example:
                st.error(f"Nu am găsit exemplu pentru tipul '{example_type}'")
                st.stop()
            
            real_email = example["real"]
            fake_email = example["fake"]
        
        # Pregătim lista cu cele două emailuri și amestecăm ordinea
        emails = [
            {"data": real_email, "is_phish": False},
            {"data": fake_email, "is_phish": True}
        ]
        random.shuffle(emails)
        
        # Salvăm emailurile și explicația în sesiune
        st.session_state.current_emails = emails
        st.session_state.current_explanation = explanation
    
    # Afișăm tipul de phishing
    st.header(f"Tip: {example_type}")
    
    if st.session_state.ai_mode:
        st.info("Aceste exemple au fost generate cu ajutorul Inteligenței Artificiale.")
    
    # Obținem emailurile din starea sesiunii
    emails = st.session_state.current_emails
    
    # Afișăm emailurile
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Mesaj #1")
        if st.session_state.enhanced_ui:
            # Afișăm emailul în format HTML îmbunătățit
            email_html = format_email_html(emails[0]["data"])
            st.markdown(email_html, unsafe_allow_html=True)
        else:
            # Afișăm emailul în format text simplu
            st.text_area(
                "Subiect:", 
                emails[0]["data"]["subject"], 
                height=50, 
                key="subj1", 
                disabled=True
            )
            st.text_area(
                "", 
                emails[0]["data"]["body"], 
                height=250, 
                key="body1", 
                disabled=True
            )
    
    with col2:
        st.subheader("Mesaj #2")
        if st.session_state.enhanced_ui:
            # Afișăm emailul în format HTML îmbunătățit
            email_html = format_email_html(emails[1]["data"])
            st.markdown(email_html, unsafe_allow_html=True)
        else:
            # Afișăm emailul în format text simplu
            st.text_area(
                "Subiect:", 
                emails[1]["data"]["subject"], 
                height=50, 
                key="subj2", 
                disabled=True
            )
            st.text_area(
                "", 
                emails[1]["data"]["body"], 
                height=250, 
                key="body2", 
                disabled=True
            )
    
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
        st.markdown(f"**Explicație:** {st.session_state.current_explanation}")
        
        # Afișăm care era răspunsul corect
        correct_idx = 0 if emails[0]["is_phish"] else 1
        st.info(f"Răspunsul corect era: Mesaj #{correct_idx + 1}")
        
        # Evidențiem elementele de phishing
        phish_idx = 0 if emails[0]["is_phish"] else 1
        phish_email = emails[phish_idx]["data"]
        
        st.subheader("Analiză detaliată a mesajului de phishing:")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Semne de phishing:**")
            signs = []
            
            # Verificăm subiectul
            subject = phish_email["subject"]
            if "URGENT" in subject or "imediat" in subject.lower() or "acum" in subject.lower():
                signs.append("Ton de urgență în subiect")
            
            # Verificăm corpul
            body = phish_email["body"]
            if "http://" in body or "bit.ly" in body:
                signs.append("Link-uri suspecte")
            
            if "card" in body.lower() or "parola" in body.lower() or "date" in body.lower():
                signs.append("Solicitare de date personale")
            
            if "urgent" in body.lower() or "imediat" in body.lower():
                signs.append("Presiune de timp")
            
            if len(signs) == 0:
                signs.append("Verifică tonul general și contextul mesajului")
            
            for sign in signs:
                st.markdown(f"- {sign}")
        
        with col2:
            st.markdown("**Cum să verifici legitimitatea:**")
            st.markdown("""
            - Verifică adresa expeditorului
            - Nu da click pe link-uri suspecte
            - Contactează direct compania prin canalele oficiale
            - Nu furniza date personale prin email
            - Verifică greșelile gramaticale și tonul
            """)

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

with st.expander("Despre funcționalitatea AI"):
    st.markdown("""
    ### Cum funcționează generarea cu AI:
    
    Aplicația folosește un model de limbaj pentru a genera două tipuri de emailuri:
    
    1. **Email-uri legitime** - Respectă toate regulile de comunicare profesională
    2. **Email-uri de phishing** - Conțin intenționat indicatori de phishing
    
    Generarea cu AI permite crearea de exemple diverse și actualizate, făcând antrenamentul mai eficient.
    
    Toate emailurile sunt generate doar în scop educațional și nu reprezintă comunicări reale.
    """)

with st.expander("Despre acest proiect"):
    st.markdown("""
    Acest quiz educațional a fost creat pentru a ajuta utilizatorii să recunoască diverse tipuri de atacuri de phishing. 
    
    Aplicația nu colectează, stochează sau procesează niciun fel de date personale.
    
    Toate exemplele sunt create în scop educațional și nu reprezintă comunicări reale.
    
    ### Tehnologii folosite:
    - Frontend: Streamlit
    - Generare conținut: Modele de limbaj
    - Hosting: Streamlit Community Cloud
    
    Dacă dorești să contribui cu exemple noi sau să raportezi probleme, lasă un comentariu mai jos.
    """)
    
    feedback = st.text_area("Feedback sau sugestii:")
    if st.button("Trimite feedback"):
        st.success("Mulțumim pentru feedback! Vom lua în considerare sugestiile tale pentru versiunile viitoare.")

# Footer
st.markdown("---")
st.markdown("© 2025 Vaccin Anti-Phishing | Creat în scop educațional")
