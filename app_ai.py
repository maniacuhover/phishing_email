import streamlit as st
import random
import json
import os
from datetime import datetime, timedelta

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

# Inițializare stare sesiune - IMPORTANT: folosim o structură mai robustă pentru a urmări starea
if "app_state" not in st.session_state:
    st.session_state.app_state = {
        "score": 0,
        "total": 0,
        "start_time": datetime.now(),
        "enhanced_ui": True,
        "answered_types": {},
        "quiz_complete": False,
        "current_example_index": None,
        "current_emails": None,
        "show_result": False,  # Flag pentru a afișa sau nu rezultatul
        "need_new_example": True,  # Flag pentru a genera un nou exemplu
        "phish_positions": []  # Lista pentru a alterna pozițiile de phishing
    }

# Încărcăm exemplele
examples = load_examples()

# Interfață utilizator
st.title("🛡️ Antrenament Anti-Phishing")
st.markdown("""
#### Dezvoltă-ți abilitățile de a identifica atacurile online!
Acest simulator te pregătește să recunoști diverse tipuri de înșelătorii digitale întâlnite frecvent.
""")

# Sidebar cu scor, statistici și setări
with st.sidebar:
    st.header("Statistici și Setări")
    st.metric("Scor curent", f"{st.session_state.app_state['score']}/{st.session_state.app_state['total']}")
    if st.session_state.app_state['total'] > 0:
        accuracy = (st.session_state.app_state['score'] / st.session_state.app_state['total']) * 100
        st.progress(accuracy/100, f"Acuratețe: {accuracy:.1f}%")
    
    elapsed_time = (datetime.now() - st.session_state.app_state['start_time']).total_seconds()
    minutes, seconds = divmod(int(elapsed_time), 60)
    st.info(f"Timp petrecut: {minutes}m {seconds}s")
    
    st.subheader("Progres")
    total_types = len(examples)
    completed_types = len(st.session_state.app_state['answered_types'])
    st.progress(completed_types/total_types, f"Progres: {completed_types}/{total_types} tipuri")
    
    st.subheader("Setări interfață")
    enhanced_ui = st.toggle("Interfață îmbunătățită", value=st.session_state.app_state['enhanced_ui'])
    if enhanced_ui != st.session_state.app_state['enhanced_ui']:
        st.session_state.app_state['enhanced_ui'] = enhanced_ui
    
    # Buton pentru resetare
    if st.button("Resetează tot"):
        # Resetăm complet starea aplicației
        st.session_state.app_state = {
            "score": 0,
            "total": 0,
            "start_time": datetime.now(),
            "enhanced_ui": True,
            "answered_types": {},
            "quiz_complete": False,
            "current_example_index": None,
            "current_emails": None,
            "show_result": False,
            "need_new_example": True,
            "phish_positions": []
        }
        st.rerun()

# Container principal
main_container = st.container()

# Verificăm dacă quiz-ul a fost completat
if st.session_state.app_state['quiz_complete']:
    # Afișăm raportul final
    st.header("🎓 Raport Final - Antrenament Complet!")
    
    # Calculăm scorul total și procent
    total_score = st.session_state.app_state['score']
    total_questions = st.session_state.app_state['total']
    if total_questions > 0:
        percent_correct = (total_score / total_questions) * 100
    else:
        percent_correct = 0
    
    # Afișăm scorul
    st.subheader(f"Scor final: {total_score}/{total_questions} ({percent_correct:.1f}%)")
    
    # Afișăm timpul petrecut
    elapsed_time = (datetime.now() - st.session_state.app_state['start_time']).total_seconds()
    minutes, seconds = divmod(int(elapsed_time), 60)
    st.info(f"Timp total: {minutes} minute și {seconds} secunde")
    
    # Afișăm rezultatele pe tipuri de phishing
    st.subheader("Rezultate pe tipuri de phishing:")
    
    # Creăm o listă de dicționare pentru afișare tabel
    results_data = []
    for phish_type, result in st.session_state.app_state['answered_types'].items():
        results_data.append({
            "Tip de phishing": phish_type,
            "Răspuns corect": "✅" if result["correct"] else "❌",
            "Explicație": result["explanation"]
        })
    
    # Afișăm tabelul
    st.table(results_data)
    
    # Buton pentru restart
    if st.button("Începe un nou test", use_container_width=True):
        # Resetăm starea aplicației dar păstrăm preferințele UI
        enhanced_ui = st.session_state.app_state['enhanced_ui']
        st.session_state.app_state = {
            "score": 0,
            "total": 0,
            "start_time": datetime.now(),
            "enhanced_ui": enhanced_ui,
            "answered_types": {},
            "quiz_complete": False,
            "current_example_index": None,
            "current_emails": None,
            "show_result": False,
            "need_new_example": True,
            "phish_positions": []
        }
        st.rerun()
        
    # Sfaturi finale
    with st.expander("Cele mai importante semne de phishing"):
        st.markdown("""
        ### Principalele semne de phishing pe care să le cauți:
        
        1. **URL-uri suspecte** - Verifică întotdeauna adresa URL înainte de a face click. Plasează cursorul peste link pentru a vedea adresa reală. Domenii suspicioase conțin:
           - Domenii care imită branduri (de ex: arată similar dar au erori minore de scriere)
           - Extensii neobișnuite (.xyz, .info, .co în loc de .com)
           - Subdomenii ciudate (de ex: netflix.domeniu-suspect.com)
        
        2. **Ton de urgență și presiune** - Mesajele care creează un sentiment de urgență ("Acum", "Urgent", "Imediat"):
           - Avertismente de blocare/suspendare a contului
           - Limite de timp artificiale ("Doar 24 ore", "Expiră azi")
           - Oferte limitate ("Ultimele 2 produse")
        
        3. **Solicitări de informații sensibile** - Companiile legitime nu cer niciodată:
           - Parole sau PIN-uri complete
           - Detalii complete ale cardului
           - Coduri de securitate prin email
        
        4. **Oferte prea bune pentru a fi adevărate**:
           - Câștiguri neașteptate la loterii la care nu ai participat
           - Produse gratuite de valoare mare
           - "Taxe de procesare" pentru premii mari
        
        5. **Verifică adresa expeditorului**:
           - Nu te baza doar pe numele afișat
           - Verifică întregul domeniu al adresei (după @)
           - Companiile folosesc domenii corporative, nu servicii gratuite de email
        
        6. **Greșeli și inconsistențe**:
           - Erori gramaticale și de ortografie
           - Formatare slabă sau inconsistentă
           - Logo-uri de calitate scăzută sau distorsionate
        
        7. **Contactează direct compania**:
           - În caz de dubii, nu folosi linkurile din email
           - Deschide un browser nou și vizitează site-ul oficial
           - Contactează compania prin canalele oficiale
        """)
else:
    # Quiz în desfășurare
    with main_container:
        # GENERARE NOUĂ - verificăm dacă avem nevoie de un nou exemplu
        if st.session_state.app_state['need_new_example']:
            # Verificăm dacă am parcurs toate tipurile
            if len(st.session_state.app_state['answered_types']) >= len(examples):
                # Am completat toate tipurile de phishing
                st.session_state.app_state['quiz_complete'] = True
                st.rerun()
                
            # Alegem un exemplu care nu a fost încă rezolvat
            remaining_indices = [i for i in range(len(examples)) 
                               if examples[i]["type"] not in st.session_state.app_state['answered_types']]
            
            if not remaining_indices:
                # Dacă am răspuns la toate, marcăm quiz-ul ca fiind complet
                st.session_state.app_state['quiz_complete'] = True
                st.rerun()
            
            # Alegem aleatoriu un exemplu din cele rămase
            current_index = random.choice(remaining_indices)
            st.session_state.app_state['current_example_index'] = current_index
            
            # Obținem exemplul curent
            current_example = examples[current_index]
            
            # Funcție pentru a genera emailuri în mod dinamic
            def generate_dynamic_emails(example_type, example_data):
                """
                Generează emailuri dinamice bazate pe șabloane
                """
                try:
                    # Simulăm diverse variații
                    real_email = example_data["real"].copy()
                    fake_email = example_data["fake"].copy()
                    
                    # Adăugăm variații aleatorii pentru a face emailurile mai realiste
                    current_date = datetime.now().strftime("%d.%m.%Y")
                    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
                    
                    # Variații pentru emailul real
                    if "data" in real_email["body"]:
                        real_email["body"] = real_email["body"].replace("25.06.2023", current_date)
                    if "30.06.2023" in real_email["body"]:
                        real_email["body"] = real_email["body"].replace("30.06.2023", tomorrow)
                    
                    # Variații pentru emailul fals - facem să pară mai legitim dar păstrăm caracteristicile de phishing
                    fake_subject = fake_email["subject"]
                    
                    # Rotație a formulărilor urgente pentru a face phishing-ul mai greu de detectat
                    urgent_terms = ["URGENT", "IMPORTANT", "ACȚIUNE NECESARĂ", "ATENȚIE", "ALERTĂ"]
                    warning_symbol = ["⚠️", "🚨", "❗", "⛔", "🔴"]
                    
                    if any(term in fake_subject for term in urgent_terms):
                        # Înlocuim un termen urgent cu altul pentru a varia
                        for term in urgent_terms:
                            if term in fake_subject:
                                new_term = random.choice([t for t in urgent_terms if t != term])
                                fake_email["subject"] = fake_subject.replace(term, new_term)
                                break
                    
                    # Adăugă simboluri de avertizare dacă nu există deja
                    if not any(symbol in fake_subject for symbol in warning_symbol) and random.random() > 0.5:
                        fake_email["subject"] = f"{random.choice(warning_symbol)} {fake_email['subject']}"
                    
                    # Înlocuiește datele în corpul emailului fals pentru a părea actual
                    if "24h" in fake_email["body"]:
                        hours = random.choice(["12h", "24h", "48h", "6h"])
                        fake_email["body"] = fake_email["body"].replace("24h", hours)
                    
                    # Variază linkurile
                    if "http://" in fake_email["body"]:
                        domains = [
                            "secure-verification.com", 
                            "account-confirm.co", 
                            "security-check.net", 
                            "client-verification.info",
                            "quick-verify.xyz"
                        ]
                        # Găsim și înlocuim un URL
                        parts = fake_email["body"].split("http://")
                        if len(parts) > 1:
                            domain_parts = parts[1].split("/", 1)
                            if domain_parts:
                                new_domain = random.choice(domains)
                                if len(domain_parts) > 1:
                                    parts[1] = f"{new_domain}/{domain_parts[1]}"
                                else:
                                    parts[1] = f"{new_domain}"
                                fake_email["body"] = "http://".join(parts)
                    
                    return real_email, fake_email
                    
                except Exception as e:
                    # În caz de eșec, returnăm datele originale
                    return example_data["real"], example_data["fake"]
            
            # Generăm emailurile pentru exemplul curent
            real_email, fake_email = generate_dynamic_emails(current_example["type"], current_example)
            
            # Decidem poziția emailului de phishing (alternată sau aleatoare)
            if not st.session_state.app_state['phish_positions']:
                # Dacă lista e goală, generăm o secvență semi-aleatoare pentru toată sesiunea
                # Asigurăm un echilibru între stânga și dreapta
                positions = []
                for i in range(len(examples) // 2):
                    positions.extend([True, False])  # True = phishing pe stânga
                random.shuffle(positions)
                st.session_state.app_state['phish_positions'] = positions
            
            # Extragem poziția pentru exemplul curent
            if st.session_state.app_state['phish_positions']:
                phishing_on_left = st.session_state.app_state['phish_positions'].pop(0)
            else:
                # Fallback la aleatoriu dacă lista e goală
                phishing_on_left = random.choice([True, False])
            
            # Pregătim lista cu cele două emailuri în funcție de poziția decidcă
            if phishing_on_left:
                emails = [
                    {"data": fake_email, "is_phish": True},
                    {"data": real_email, "is_phish": False}
                ]
            else:
                emails = [
                    {"data": real_email, "is_phish": False},
                    {"data": fake_email, "is_phish": True}
                ]
            
            # Salvăm emailurile în sesiune
            st.session_state.app_state['current_emails'] = emails
            st.session_state.app_state['need_new_example'] = False
            st.session_state.app_state['show_result'] = False
        
        # Obținem exemplul și emailurile curente din starea sesiunii
        current_index = st.session_state.app_state['current_example_index']
        current_example = examples[current_index]
        emails = st.session_state.app_state['current_emails']
        
        # Afișăm tipul de phishing
        st.header(f"Tip: {current_example['type']}")
        
        # Afișăm emailurile
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Mesaj #1")
            if st.session_state.app_state['enhanced_ui']:
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
            if st.session_state.app_state['enhanced_ui']:
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
        
        # Dacă nu am afișat încă rezultatul, arătăm butoanele de selecție
        if not st.session_state.app_state['show_result']:
            # Secțiunea de decizie
            choice = st.radio("Care dintre mesaje crezi că este phishing?", ["Mesaj #1", "Mesaj #2"])
            idx = 0 if choice == "Mesaj #1" else 1
            
            # Verificare răspuns
            if st.button("Verifică răspunsul", use_container_width=True):
                st.session_state.app_state['total'] += 1
                correct = emails[idx]["is_phish"]
                
                if correct:
                    st.session_state.app_state['score'] += 1
                
                # Adăugăm tipul curent în lista de tipuri la care s-a răspuns
                st.session_state.app_state['answered_types'][current_example["type"]] = {
                    "correct": correct,
                    "explanation": current_example["explanation"]
                }
                
                # Setăm flag-ul pentru afișarea rezultatului
                st.session_state.app_state['show_result'] = True
                st.rerun()  # Reîncărcăm pentru a afișa rezultatul
        
        # Afișăm rezultatul dacă flag-ul este setat
        if st.session_state.app_state['show_result']:
            # Verificăm dacă răspunsul a fost corect
            correct = st.session_state.app_state['answered_types'][current_example["type"]]["correct"]
            
            if correct:
                st.success("✅ Corect! Ai identificat corect mesajul de phishing.")
            else:
                st.error("❌ Greșit! Acesta nu era mesajul de phishing.")
            
            # Afișăm explicația
            st.markdown(f"**Explicație:** {current_example['explanation']}")
            
            # Afișăm care era răspunsul corect
            correct_idx = 0 if emails[0]["is_phish"] else 1
            st.info(f"Răspunsul corect era: Mesaj #{correct_idx + 1}")
            
            # Evidențiem elementele de phishing - identificare detaliată a semnelor
            phish_idx = 0 if emails[0]["is_phish"] else 1
            phish_email = emails[phish_idx]["data"]
            
            st.subheader("Elemente de înșelătorie în mesajul phishing:")
            
            # Colorăm diferit zonele suspecte din mesajul de phishing
            phish_subject = phish_email["subject"]
            phish_body = phish_email["body"]
            
            # Funcție pentru evidențierea elementelor suspecte
            def highlight_suspicious(text, suspicious_elements):
                highlighted = text
                for element in suspicious_elements:
                    if element.lower() in text.lower():
                        # Căutăm elementul exact ținând cont de majuscule/minuscule
                        start_idx = text.lower().find(element.lower())
                        end_idx = start_idx + len(element)
                        actual_text = text[start_idx:end_idx]
                        highlighted = highlighted.replace(actual_text, f"<span style='color: red; font-weight: bold;'>{actual_text}</span>")
                return highlighted
            
            # Elemente suspecte în subiect
            subject_suspicious = ["URGENT", "ALERTĂ", "IMPORTANT", "imediat", "ACUM", "❗", "⚠️", "🚨"]
            highlighted_subject = highlight_suspicious(phish_subject, subject_suspicious)
            
            # Elemente suspecte în corp
            body_suspicious = [
                "http://", "accesați:", "click aici", "link",
                "parolă", "card", "cont", "autentificare", "verificare", 
                "urgent", "imediat", "acum", "expiră", "pericol", "blocat", "suspendat", "șters",
                "gratuit", "câștigat", "premiu", "taxă", "plătiți doar"
            ]
            highlighted_body = highlight_suspicious(phish_body, body_suspicious)
            
            # Afișăm versiunea evidențiată
            st.markdown(f"""
            <div style="border: 2px solid red; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
                <h4 style="color: red;">Subiect suspect:</h4>
                <p>{highlighted_subject}</p>
                
                <h4 style="color: red;">Corp suspect:</h4>
                <p style="white-space: pre-line;">{highlighted_body.replace('\\n', '<br>')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Analiza detaliată și explicațiile
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Ce să verifici:**")
                
                # Analiză adaptată pentru fiecare tip de phishing
                checks = []
                
                # URL-uri suspecte
                if "http://" in phish_body or "www." in phish_body:
                    checks.append("**URL-uri suspecte** - Verifică întotdeauna adresa URL completă înainte de a face click. Nu te lăsa păcălit de domenii care imită branduri cunoscute.")
                
                # Ton de urgență
                if any(term.lower() in phish_subject.lower() or term.lower() in phish_body.lower() 
                       for term in ["urgent", "imediat", "acum", "blocat", "pericol", "expiră"]):
                    checks.append("**Presiune psihologică** - Mesajele legitime rareori creează panică sau urgență extremă.")
                
                # Solicitări de date personale
                if any(term.lower() in phish_body.lower() 
                       for term in ["parolă", "card", "cont", "autentificare", "verificare", "datele", "cod"]):
                    checks.append("**Solicitare de date sensibile** - Instituțiile legitime nu cer parole sau date de card prin email.")
                
                # Oferte prea bune
                if any(term.lower() in phish_subject.lower() or term.lower() in phish_body.lower() 
                       for term in ["gratuit", "câștigat", "premiu", "free", "cadou"]):
                    checks.append("**Ofertă prea bună** - Ofertele nerealist de avantajoase sunt de obicei capcane.")
                
                # Adresă expeditor
                if "@gmail.com" in phish_body or "@yahoo.com" in phish_body:
                    checks.append("**Adresă de email suspectă** - Companiile folosesc emailuri corporative, nu servicii gratuite.")
                
                # Alte elemente tipice de înșelătorie
                if "taxă" in phish_body.lower() or "plată" in phish_body.lower():
                    checks.append("**Taxă de procesare** - Solicitarea unei taxe mici pentru a primi un premiu mare este o tactică comună de fraudă.")
                
                # Dacă nu am găsit elemente specifice, adăugăm sfaturi generale
                if not checks:
                    checks = [
                        "**Verifică adresa expeditorului** - Asigură-te că domeniul aparține companiei legitime",
                        "**Analizează limbajul** - Mesajele de phishing au adesea un ton diferit de comunicările oficiale",
                        "**Verifică linkurile** - Plasează mouse-ul peste ele fără a da click pentru a vedea destinația reală"
                    ]
                
                for check in checks:
                    st.markdown(f"- {check}")
            
            with col2:
                st.markdown("**Cum să te protejezi:**")
                st.markdown("""
                - Contactează direct compania sau serviciul prin canalele oficiale
                - Verifică independent linkurile și domeniul expeditorului
                - Nu introduce date personale sau de autentificare ca răspuns la emailuri
                - Activează autentificarea în doi factori unde este posibil
                - Folosește un manager de parole pentru a evita reutilizarea acestora
                """)
            
            # Buton pentru continuare
            if st.button("Continuă la următorul exemplu", use_container_width=True):
                # Resetăm flag-urile pentru a genera un nou exemplu
                st.session_state.app_state['need_new_example'] = True
                st.session_state.app_state['show_result'] = False
                st.rerun()

# Informații educaționale în partea de jos
with st.expander("Sfaturi pentru detectarea phishing-ului"):
    st.markdown("""
    ### 7 Metode pentru a identifica mesajele de phishing:
    
    1. **Verifică adresa expeditorului** - Nu te baza doar pe numele afișat. Verifică întregul domeniu (după @).
    
    2. **Analizează linkurile** - Plasează cursorul peste link pentru a vedea adresa reală. Link-urile legitime duc de obicei la domeniul oficial al companiei.
    
    3. **Fii atent la tonul urgent** - Mesajele care creează un sentiment de urgență ("acționează acum", "urgent", "cont blocat") sunt adesea înșelătorii.
    
    4. **Verifică greșelile** - Comunicările oficiale sunt de obicei verificate pentru greșeli gramaticale și de ortografie.
    
    5. **Nu oferi informații sensibile** - Companiile legitime nu cer niciodată parole, PIN-uri sau detalii complete de card prin email.
    
    6. **Evaluează ofertele** - Ofertele prea bune pentru a fi adevărate, câștiguri neașteptate, produse gratuite de valoare mare sunt adesea capcane.
    
    7. **Folosește verificarea independentă** - Dacă ai dubii, contactează direct compania prin site-ul oficial sau numărul de telefon cunoscut.
    """)

with st.expander("Exemple de escrocherii recente"):
    st.markdown("""
    ### Tactici actuale de phishing întâlnite frecvent:
    
    **Coșuri cadou false de sărbători**:
    Escrocii promit coșuri cadou de la branduri cunoscute (Lindt, Ferrero, etc.) în schimbul completării unui chestionar. În realitate, aceștia colectează date personale sau solicită o "taxă de procesare" pentru premiul inexistent.
    
    **Vouchere false de la retaileri**:
    Mesaje care oferă vouchere valoroase de la magazine populare (Kaufland, Lidl, etc.). Utilizatorii sunt direcționați către site-uri false unde li se cer date personale și de card.
    
    **Felicitări electronice periculoase**:
    Emailuri care par a conține felicitări personalizate, dar care conțin link-uri către site-uri de phishing sau atașamente cu malware.
    
    **Falsificări de brand pentru cosmetice/produse populare**:
    Imitații de campanii de la branduri cunoscute care oferă "giveaway-uri" sau mostre gratuite în schimbul unor "costuri de livrare" minime.
    
    **Notificări false despre pachete**:
    Mesaje care pretind că un colet nu poate fi livrat din cauza unei adrese incomplete sau a unei taxe neplătite, solicitând date personale și de plată.
    """)

with st.expander("Despre acest proiect"):
    st.markdown("""
    Acest simulator de phishing a fost creat în scop educațional pentru a ajuta utilizatorii să recunoască diversele tipuri de înșelătorii digitale.
    
    Aplicația nu colectează, stochează sau procesează niciun fel de date personale.
    
    Toate exemplele sunt create pentru educare și nu reprezintă comunicări reale.
    
    **Tipuri de phishing incluse în simulator:**
    - Email-phishing clasic
    - Spear-phishing (phishing țintit)
    - Fraudă bancară
    - Coș cadou Paște
    - Vouchere și cupoane false
    - Impersonare CEO (frauda "șefului")
    - Actualizare de securitate falsă
    - Felicitare electronică falsă
    - Fraudă cu suport tehnic
    - Notificare livrare falsă
    - Sondaj fals cu premii
    - Reînnoire abonament falsă
    - Oportunitate de investiții falsă
    - Confirmare comandă falsă
    - Probleme cont social media false
    - Verificare cont falsă
    """)
    
    feedback = st.text_area("Feedback sau sugestii:")
    if st.button("Trimite feedback"):
        st.success("Mulțumim pentru feedback! Vom lua în considerare sugestiile tale pentru îmbunătățiri viitoare.")

# Footer
st.markdown("---")
st.markdown("© 2025 Simulator Anti-Phishing | Creat în scop educațional")
