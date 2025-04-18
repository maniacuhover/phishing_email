import streamlit as st
import random
import json
import os
import requests
from datetime import datetime
import time

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
    # Verificăm și debugăm cheia API
    api_key = None
    
    # Încearcă să accesezi cheia din variabile de mediu
    env_api_key = os.environ.get("HF_API_KEY")
    if env_api_key:
        api_key = env_api_key
        st.sidebar.success("API key găsit în variabile de mediu!")
    
    # Încearcă să accesezi cheia din secrets
    try:
        if hasattr(st, 'secrets') and 'HF_API_KEY' in st.secrets:
            secrets_api_key = st.secrets['HF_API_KEY']
            api_key = secrets_api_key
            st.sidebar.success("API key găsit în secrets!")
        else:
            # Încearcă acces alternativ la secrets
            if hasattr(st, 'secrets'):
                st.sidebar.info(f"Cheile disponibile în secrets: {list(st.secrets.keys())}")
            else:
                st.sidebar.warning("Obiectul st.secrets nu există")
    except Exception as e:
        st.sidebar.error(f"Eroare la accesarea secrets: {str(e)}")
    
    # Afișează informații despre cheie pentru debugging
    if api_key:
        # Afișează primele și ultimele 4 caractere pentru securitate
        masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "***"
        st.sidebar.info(f"API key găsit: {masked_key} (lungime: {len(api_key)})")
    else:
        st.sidebar.warning("Nu s-a găsit niciun API key. Se va folosi generarea demo.")
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
        # Folosim un model mai mic, compatibil cu API-ul gratuit
        MODEL_URL = "https://api-inference.huggingface.co/models/gpt2"
        
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
        
        # Facem request-urile către API cu mai multe informații de debug
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Request pentru email legitim cu parametri ajustați pentru model mai mic
        real_payload = {
            "inputs": prompt_real,
            "parameters": {
                "max_length": 200,
                "temperature": 0.8,
                "top_p": 0.9,
                "do_sample": True
            }
        }
        
        # Implementăm logica cu retry
        def make_api_request(payload, max_retries=3):
            for attempt in range(max_retries):
                try:
                    response = requests.post(MODEL_URL, headers=headers, json=payload)
                    if response.status_code == 200:
                        return response
                    elif response.status_code == 429:  # Too Many Requests
                        wait_time = (attempt + 1) * 2  # Așteptare exponențială
                        st.warning(f"Limită de rată depășită. Așteptăm {wait_time} secunde...")
                        time.sleep(wait_time)
                    else:
                        st.error(f"Eroare API: {response.status_code}, {response.text}")
                        return response
                except Exception as e:
                    st.error(f"Excepție la solicitarea API: {str(e)}")
                    time.sleep(1)
            return None
        
        # Facem requesturile cu retry
        response_real = make_api_request(real_payload)
        fake_payload = {
            "inputs": prompt_fake,
            "parameters": {
                "max_length": 200,
                "temperature": 0.8,
                "top_p": 0.9,
                "do_sample": True
            }
        }
        response_fake = make_api_request(fake_payload)
        
        # Procesăm răspunsurile cu verificare mai atentă
        if response_real and response_fake and response_real.status_code == 200 and response_fake.status_code == 200:
            try:
                real_json = response_real.json()
                fake_json = response_fake.json()
                
                # Afișăm informații despre structura răspunsului pentru debug
                st.sidebar.info(f"Structura răspuns real: {type(real_json)}")
                
                # Adaptăm extragerea în funcție de structura răspunsului specifică modelului GPT-2
                if isinstance(real_json, list) and len(real_json) > 0:
                    real_text = real_json[0].get("generated_text", "")
                elif isinstance(real_json, dict):
                    real_text = real_json.get("generated_text", "")
                else:
                    real_text = str(real_json)  # Fallback
                
                if isinstance(fake_json, list) and len(fake_json) > 0:
                    fake_text = fake_json[0].get("generated_text", "")
                elif isinstance(fake_json, dict):
                    fake_text = fake_json.get("generated_text", "")
                else:
                    fake_text = str(fake_json)  # Fallback
                
                # Pentru modelul GPT-2, răspunsul ar putea să nu fie structurat cu subiect
                # Așa că vom crea un format manual
                
                # Convertim textul generat în format de email
                def format_as_email(text, is_phishing=False):
                    lines = text.split("\n")
                    
                    # Creăm un subiect adecvat
                    if is_phishing:
                        subject = f"URGENT: Acțiune necesară - {phishing_type}"
                        if len(lines) > 0 and len(lines[0]) < 60:  # Folosim prima linie ca subiect dacă e scurtă
                            subject = lines[0]
                    else:
                        subject = f"Informare privind {phishing_type}"
                        if len(lines) > 0 and len(lines[0]) < 60:
                            subject = lines[0]
                    
                    # Corpul emailului
                    body = "\n".join(lines[1:] if len(lines) > 1 else lines)
                    
                    # Adăugăm elemente specifice pentru phishing
                    if is_phishing:
                        if "http" not in body:
                            body += f"\n\nVerifică urgent aici: http://verificare-{phishing_type.lower().replace(' ', '-')}.com"
                        if "urgent" not in body.lower():
                            body += "\n\nAcțiune urgentă necesară!"
                    
                    # Adăugăm semnătură pentru email legitim
                    if not is_phishing:
                        if "Cu stimă" not in body:
                            body += "\n\nCu stimă,\nEchipa de Support"
                    
                    return {
                        "subject": subject,
                        "body": body
                    }
                
                # Formatăm răspunsurile ca emailuri
                real_email = format_as_email(real_text, is_phishing=False)
                fake_email = format_as_email(fake_text, is_phishing=True)
                
                return {
                    "real": real_email,
                    "fake": fake_email
                }
            except Exception as e:
                st.error(f"Eroare la procesarea răspunsului: {str(e)}")
                raise e
        else:
            # Afișăm informații detaliate despre erori
            if response_real:
                st.error(f"Eroare la requestul pentru email legitim: Status code {response_real.status_code}, Răspuns: {response_real.text}")
            if response_fake:
                st.error(f"Eroare la requestul pentru email phishing: Status code {response_fake.status_code}, Răspuns: {response_fake.text}")
            # Fallback la exemple statice
            raise Exception("API error - vezi detaliile de mai sus")
            
    except Exception as e:
        st.error(f"Eroare detaliată la generarea cu AI: {str(e)}")
        # Răspuns de fallback - emailuri predefinite bune pentru acest tip
        return {
            "real": {
                "subject": f"Informare privind {phishing_type}",
                "body": f"Stimată doamnă/Stimate domn,\n\nVă trimitem această informare privind {phishing_type}. \n\nDacă aveți întrebări, vă rugăm să ne contactați la numărul de telefon oficial sau să vizitați site-ul nostru www.companie-legitima.ro.\n\nCu stimă,\nEchipa de Relații Clienți"
            },
            "fake": {
                "subject": f"URGENT: Problemă de securitate - {phishing_type}",
                "body": f"ATENȚIE!\n\nAm detectat o activitate suspectă legată de {phishing_type}. \n\nPentru a preveni compromiterea contului, vă rugăm să accesați urgent acest link: http://verificare-securitate.net și să introduceți datele de autentificare pentru verificare.\n\nDepartamentul de Securitate"
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
