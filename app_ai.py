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

# Funcția pentru renderarea HTML a emailurilor
def render_html_email(email_data):
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
    
    # Construim headerul emailului în stil realist
    header_html = f"""
    <div style="border: 1px solid #ddd; border-radius: 8px; max-width: 100%; font-family: Arial, sans-serif; margin-bottom: 20px;">
        <!-- Header -->
        <div style="background-color: {company_color}; color: white; padding: 15px; border-top-left-radius: 8px; border-top-right-radius: 8px;">
            <table width="100%">
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
            <table width="100%" style="font-size: 13px;">
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
    
    # Construim corpul emailului
    body_html = f"""
        <!-- Email body -->
        <div style="padding: 15px; line-height: 1.5;">
            {body}
        </div>
    """
    
    # Construim footerul emailului
    footer_html = f"""
        <!-- Footer -->
        <div style="background-color: #f8f9fa; padding: 10px 15px; font-size: 11px; color: #6c757d; border-top: 1px solid #ddd; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;">
            {footer}
        </div>
    </div>
    """
    
    # Combinăm toate componentele
    html = header_html + body_html + footer_html
    
    return html

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

# Funcție pentru generarea de emailuri folosind un model AI
def generate_emails(phishing_type):
    # Verificăm dacă există o cheie API configurată
    api_key = os.environ.get("HF_API_KEY", st.secrets.get("HF_API_KEY", None))
    
    if not api_key:
        # Simulăm generarea dacă nu avem API key (pentru demo)
        return {
            "real": {
                "subject": f"Email legitim despre {phishing_type}",
                "body": f"Acesta este un email legitim generat pentru {phishing_type}.\n\nAre un ton profesional, nu solicită date personale și folosește un domeniu oficial.",
                "sender": "Serviciul Clienți",
                "sender_email": "serviciu@companie-legitima.ro",
                "logo": "COMPANIE",
                "colors": "#007bff",
                "date": datetime.now().strftime("%d.%m.%Y"),
                "footer": "© 2025 Companie Legitimă | Toate drepturile rezervate"
            },
            "fake": {
                "subject": f"URGENT: Situație de {phishing_type}!!!",
                "body": f"ATENȚIE! Acesta este un email de phishing generat pentru {phishing_type}.\n\nAre un ton urgent, solicită acțiune imediată și probabil conține un link suspect: http://website-fals.com",
                "sender": "Departament Securitate",
                "sender_email": "security@companie-1egitima.com",
                "logo": "COMPANIE",
                "colors": "#cc0000",
                "date": datetime.now().strftime("%d.%m.%Y"),
                "footer": "© 2025 Companie | Securitate"
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
            "https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf",
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
                    "body": real_body.strip(),
                    "sender": "Serviciul Clienți",
                    "sender_email": "serviciu@companie-legitima.ro",
                    "logo": "COMPANIE",
                    "colors": "#007bff",
                    "date": datetime.now().strftime("%d.%m.%Y"),
                    "footer": "© 2025 Companie Legitimă | Toate drepturile rezervate"
                },
                "fake": {
                    "subject": fake_subject.replace("Subiect:", "").strip(),
                    "body": fake_body.strip(),
                    "sender": "Departament Securitate",
                    "sender_email": "security@companie-1egitima.com",
                    "logo": "COMPANIE",
                    "colors": "#cc0000",
                    "date": datetime.now().strftime("%d.%m.%Y"),
                    "footer": "© 2025 Companie | Securitate"
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
                "body": f"Acesta este un email legitim despre {phishing_type}.\n\nAre un ton profesional, nu solicită date personale și folosește un domeniu oficial.",
                "sender": "Serviciul Clienți",
                "sender_email": "serviciu@companie-legitima.ro",
                "logo": "COMPANIE",
                "colors": "#007bff",
                "date": datetime.now().strftime("%d.%m.%Y"),
                "footer": "© 2025 Companie Legitimă | Toate drepturile rezervate"
            },
            "fake": {
                "subject": f"URGENT: Situație de {phishing_type}!!!",
                "body": f"ATENȚIE! Acesta este un email de phishing pentru {phishing_type}.\n\nAre un ton urgent, solicită acțiune imediată și probabil conține un link suspect: http://website-fals.com",
                "sender": "Departament Securitate",
                "sender_email": "security@companie-1egitima.com",
                "logo": "COMPANIE",
                "colors": "#cc0000",
                "date": datetime.now().strftime("%d.%m.%Y"),
                "footer": "© 2025 Companie | Securitate"
            }
        }

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
if "advanced_rendering" not in st.session_state:
    st.session_state.advanced_rendering = True

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
        if "current_example" in st.session_state:
            del st.session_state.current_example
    
    advanced_rendering = st.toggle("Renderare avansată emailuri", value=st.session_state.advanced_rendering)
    if advanced_rendering != st.session_state.advanced_rendering:
        st.session_state.advanced_rendering = advanced_rendering
    
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
    # Generăm un exemplu nou sau folosim AI pentru a genera
    if "current_example" not in st.session_state:
        # Alegem un tip aleatoriu din exemplele disponibile
        example_type = random.choice([ex["type"] for ex in examples])
        explanation = next((ex["explanation"] for ex in examples if ex["type"] == example_type), 
                         "Verifică adresa expeditorului, link-urile și solicitările de informații.")
        
        if st.session_state.ai_mode:
            # Generare cu AI
            with st.spinner("Generez emailuri cu AI..."):
                generated = generate_emails(example_type)
                
                # Pregătim emailurile complete
                real_email = generated["real"]
                fake_email = generated["fake"]
        else:
            # Folosim exemplul predefinit
            example = next((ex for ex in examples if ex["type"] == example_type), examples[0])
            
            # Pregătim emailurile complete
            real_email = {
                "subject": example["real"]["subject"],
                "body": example["real"]["body"],
                "sender": "Serviciul Clienți",
                "sender_email": "serviciu@companie-legitima.ro",
                "logo": "COMPANIE",
                "colors": "#007bff",
                "date": datetime.now().strftime("%d.%m.%Y"),
                "footer": "© 2025 Companie Legitimă | Toate drepturile rezervate"
            }
            
            fake_email = {
                "subject": example["fake"]["subject"],
                "body": example["fake"]["body"],
                "sender": "Departament Securitate",
                "sender_email": "security@companie-1egitima.com",
                "logo": "COMPANIE", 
                "colors": "#cc0000",
                "date": datetime.now().strftime("%d.%m.%Y"),
                "footer": "© 2025 Companie | Securitate"
            }
        
        # Setăm exemplul curent
        st.session_state.current_example = {
            "type": example_type,
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
    
    # Afișăm tipul de phishing
    st.header(f"Tip: {st.session_state.current_example['type']}")
    
    # Buton pentru regenerare
    if st.button("Generează alt exemplu", use_container_width=True):
        if "current_example" in st.session_state:
            del st.session_state.current_example
        st.rerun()
    
    if st.session_state.ai_mode:
        st.info("Aceste exemple au fost generate cu ajutorul Inteligenței Artificiale.")
    
    col1, col2 = st.columns(2)
    
    # Modul de afișare depinde de setarea de renderare avansată
    if st.session_state.advanced_rendering:
        # Folosim renderarea HTML pentru un aspect mai realist
        email1_html = render_html_email(st.session_state.items[0]["email"])
        email2_html = render_html_email(st.session_state.items[1]["email"])
        
        with col1:
            st.subheader("Mesaj #1")
            st.markdown(email1_html, unsafe_allow_html=True)
        
        with col2:
            st.subheader("Mesaj #2")
            st.markdown(email2_html, unsafe_allow_html=True)
    else:
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
        
        # Evidențiem elementele de phishing
        phish_idx = correct_idx
        phish_email = st.session_state.items[phish_idx]["email"]
        
        st.subheader("Analiză detaliată a mesajului de phishing:")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Semne de phishing:**")
            signs = []
            
            # Verificăm adresa de email
            sender_email = phish_email["sender_email"]
            if "1" in sender_email or "-" in sender_email or sender_email.count(".") > 2:
                signs.append("Adresă de email suspectă")
            
            # Verificăm subiectul
            subject = phish_email["subject"]
            if "URGENT" in subject or "imediat" in subject.lower() or "acum" in subject.lower():
                signs.append("Ton de urgență în subiect")
            
            # Verificăm corpul
            body = phish_email["body"]
            if "http://" in body or "bit.ly" in body:
                signs.append("Link-uri suspecte")
            
            if "card" in body.lower() or "parola" in body.lower() or "cont" in body.lower():
                signs.append("Solicitare de date personale")
            
            if "urgent" in body.lower() or "imediat" in body.lower():
                signs.append("Presiune de timp")
            
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
