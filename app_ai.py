import streamlit as st
import random
import json
import os
import requests
from datetime import datetime
import time

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
            },
            {
                "type": "Ofertă falsă",
                "real": {
                    "subject": "Promoție de vară la produsele electronice",
                    "body": "Dragi clienți,\n\nVă anunțăm că începând cu data de 15 iunie, toate produsele electronice vor beneficia de reduceri de până la 30%.\n\nPentru mai multe detalii și catalog complet, vizitați magazinul nostru sau www.electroshop.ro.\n\nEchipa ElectroShop"
                },
                "fake": {
                    "subject": "FELICITĂRI! Ai câștigat un iPhone 15!",
                    "body": "Felicitări!\n\nAi fost selectat aleatoriu pentru a primi un iPhone 15 GRATUIT!\n\nPentru a revendica premiul, accesează link-ul: www.winner-claim.xyz/iphone și completează formularul cu datele tale personale și adresa de livrare în 48 de ore.\n\nEchipa Winner"
                },
                "explanation": "Fals: ofertă prea bună pentru a fi adevărată, domeniu suspect (.xyz), solicită date personale. Real: promoție rezonabilă, site oficial, nu solicită date personale."
            },
            {
                "type": "Impersonare CEO",
                "real": {
                    "subject": "Prezentarea trimestrială - feedback",
                    "body": "Bună ziua tuturor,\n\nVă mulțumesc pentru participarea la prezentarea trimestrială de ieri.\n\nVă rog să trimiteți feedback-ul și sugestiile în formularul din intranet până vineri.\n\nCu stimă,\nAna Marinescu\nDirector General\nam@compania.ro"
                },
                "fake": {
                    "subject": "Solicitare urgentă - confidențial",
                    "body": "Salut,\n\nSunt în mijlocul unei întâlniri importante și am nevoie urgent să achiziționez niște carduri cadou pentru un client VIP.\n\nPoți să cumperi 5 carduri Amazon a câte 200 EUR și să-mi trimiți codurile pe acest email?\n\nVoi aproba rambursarea imediat ce mă întorc.\n\nMulțumesc,\nAna Marinescu\nDirector General\nanam_ceo@gmail.com"
                },
                "explanation": "Fals: ton urgent, adresă de email suspectă (gmail personal în loc de domeniul companiei), solicitare neobișnuită de bani/carduri. Real: adresă oficială de email, solicitare profesională normală."
            },
            {
                "type": "Actualizare de securitate",
                "real": {
                    "subject": "Actualizare politică de securitate - acțiune necesară",
                    "body": "Stimate utilizator,\n\nAm actualizat politica noastră de securitate.\n\nVă rugăm să vă autentificați în contul dvs. de pe site-ul nostru www.serviciu-web.ro și să revizuiți noii termeni din secțiunea 'Setări cont'.\n\nEchipa de Securitate\nServiceWeb"
                },
                "fake": {
                    "subject": "URGENT: Actualizare de securitate necesară ACUM",
                    "body": "Atenție!\n\nContul dvs. este expus riscurilor! Trebuie să actualizați imediat parola accesând acest link: http://service-web.security-login.com\n\nIntroduceți parola actuală și setați una nouă în maxim 2 ore sau contul va fi suspendat.\n\nDepartamentul Tehnic"
                },
                "explanation": "Fals: ton alarmist, domeniu fals (service-web.security-login.com), cere direct parola. Real: trimite către site-ul oficial, nu solicită informații sensibile prin email."
            },
            {
                "type": "Suport tehnic fals",
                "real": {
                    "subject": "Confirmare ticket suport #12345",
                    "body": "Bună ziua,\n\nAm înregistrat solicitarea dvs. cu numărul de ticket #12345.\n\nUn specialist va analiza problema și vă va contacta în maxim 24 de ore.\n\nPuteți urmări statusul ticket-ului pe portalul nostru de suport.\n\nEchipa de Suport Tehnic\nsupport@companie.ro"
                },
                "fake": {
                    "subject": "Alerta Virus Detectat pe Dispozitiv",
                    "body": "AVERTISMENT: Am detectat un virus periculos pe dispozitivul dvs!\n\nDatele dvs. sunt în pericol! Sunați ACUM la +40 722 123 456 pentru asistență imediată de la echipa noastră Microsoft.\n\nSau accesați: http://windows-security-center.tech pentru scanare gratuită.\n\nEchipa de Securitate Microsoft"
                },
                "explanation": "Fals: pretinde că este de la Microsoft, număr de telefon suspect, domeniu neoficial, ton alarmist. Real: referire la un ticket specific, nu solicită acțiune urgentă, adresă email oficială."
            },
            {
                "type": "Notificare livrare",
                "real": {
                    "subject": "Comandă #A12345 - În curs de livrare",
                    "body": "Bună ziua,\n\nComanda dvs. #A12345 a fost expediată și va fi livrată în data de 25.06.2023.\n\nPuteți urmări statusul folosind codul de tracking: RO123456789RO pe site-ul nostru www.curier-oficial.ro.\n\nEchipa Livrări\nCurier Oficial"
                },
                "fake": {
                    "subject": "Colet reținut la vamă - Acțiune necesară",
                    "body": "Atenție!\n\nColetul dvs. a fost reținut la vamă datorită unei taxe neplătite de 19,99 EUR.\n\nPentru a evita returnarea, accesați urgent: http://customs-delivery-pay.com și introduceți datele cardului pentru plata taxei.\n\nServiciul Vamal de Curierat"
                },
                "explanation": "Fals: solicită plată online pe un site suspect, nu menționează numărul specific al comenzii, domeniu suspect. Real: include număr de comandă și cod de tracking, trimite către site oficial."
            },
            {
                "type": "Reînnoire abonament",
                "real": {
                    "subject": "Abonamentul dvs. expiră în 7 zile",
                    "body": "Stimate abonat,\n\nVă reamintim că abonamentul dvs. premium va expira pe data de 30.06.2023.\n\nPentru reînnoire, accesați contul dvs. pe www.serviciu-streaming.ro/cont și selectați opțiunea dorită.\n\nVă mulțumim că sunteți alături de noi!\n\nEchipa Serviciu Streaming"
                },
                "fake": {
                    "subject": "ULTIMA ȘANSĂ: Abonamentul dvs. Netflix expiră AZI",
                    "body": "Atenție: Abonamentul dvs. Netflix expiră astăzi!\n\nPentru a evita întreruperea serviciului, actualizați urgent detaliile de plată aici: http://netflix-renew.payment.com\n\nIntroduceți datele cardului pentru reînnoirea automată.\n\nEchipa Netflix"
                },
                "explanation": "Fals: presiune extremă de timp, domeniu fals (netflix-renew.payment.com), solicită direct date de card. Real: oferă notificare din timp, trimite către site-ul oficial, nu solicită date sensibile prin email."
            },
            {
                "type": "Donație falsă",
                "real": {
                    "subject": "Mulțumim pentru interesul față de cauza noastră",
                    "body": "Dragă susținător,\n\nÎți mulțumim pentru interesul arătat față de proiectele noastre.\n\nDacă dorești să contribui, poți face o donație prin site-ul nostru oficial www.ong-salvare.ro/doneaza, unde vei găsi toate metodele de plată disponibile și detalii despre cum vor fi folosite fondurile.\n\nCu recunoștință,\nEchipa ONG Salvare"
                },
                "fake": {
                    "subject": "URGENT: Apel pentru ajutor - Victimele dezastrului",
                    "body": "Dragă om cu suflet mare,\n\nMii de victime ale dezastrului recent au nevoie URGENTĂ de ajutorul tău!\n\nDonează ACUM prin transfer direct în contul: RO11FAKE12345678900 sau folosește link-ul rapid de donație: http://help-disaster-victims.org/donate\n\nFiecare minut contează!\n\nFundația Internațională de Ajutor"
                },
                "explanation": "Fals: ton extrem de urgent, organizație nefamiliară, cont bancar sau link de donație direct în email. Real: direcționează către site-ul oficial, ton profesional, fără presiune."
            },
            {
                "type": "Oportunitate de investiții",
                "real": {
                    "subject": "Invitație: Webinar despre strategii de investiții 2023",
                    "body": "Stimată Doamnă/Stimate Domn,\n\nVă invităm să participați la webinarul nostru despre strategii de investiții pentru 2023, care va avea loc pe data de 15 iulie.\n\nPentru a vă înscrie și a afla mai multe detalii, vizitați: www.banca-investitii.ro/webinare\n\nParticiparea este gratuită pentru clienții noștri.\n\nBanca de Investiții"
                },
                "fake": {
                    "subject": "CONFIDENȚIAL: Oportunitate de investiții cu randament GARANTAT 50%",
                    "body": "Oportunitate EXCLUSIVĂ de investiții!\n\nUn grup select de investitori poate acum accesa o oportunitate UNICĂ cu randament GARANTAT de 50% în doar 3 luni!\n\nLocuri limitate! Transferă minim 1000 EUR în contul: RO99FAKE87654321000 pentru a-ți rezerva poziția.\n\nRăspunde în 24h pentru detalii confidențiale!\n\nGrupul de Investiții Exclusive"
                },
                "explanation": "Fals: promisiune de câștig nerealist de mare, presiune de timp, solicită transfer direct de bani. Real: invitație la un eveniment informativ gratuit, fără solicitare de bani, site oficial."
            },
            {
                "type": "Cupoane și discount-uri",
                "real": {
                    "subject": "Voucher cadou pentru aniversarea colaborării noastre",
                    "body": "Dragă client,\n\nCu ocazia aniversării a 3 ani de când ești clientul nostru, îți oferim un voucher în valoare de 50 RON.\n\nPoți folosi codul ANIV50 la următoarea comandă pe site-ul nostru www.magazin-oficial.ro până la data de 31.12.2023.\n\nEchipa Magazin Oficial"
                },
                "fake": {
                    "subject": "CÂȘTIGĂTOR! Voucher de 500 EUR la Carrefour",
                    "body": "FELICITĂRI! Ai fost selectat pentru a primi un voucher GRATUIT de 500 EUR la Carrefour!\n\nPentru a revendica premiul, completează formularul de la: http://carrefour-vouchers.win cu datele tale personale și numărul cardului pentru verificare.\n\nOfertă validă doar 24 ore!\n\nEchipa Promoții Carrefour"
                },
                "explanation": "Fals: valoare nerealist de mare, domeniu suspect (.win), solicită date de card, presiune de timp extremă. Real: ofertă realistă, cod de voucher direct în email, site oficial, perioadă rezonabilă de valabilitate."
            },
            {
                "type": "Confirmare comandă falsă",
                "real": {
                    "subject": "Confirmare comandă #B78901 - Magazin Online",
                    "body": "Mulțumim pentru comanda dvs.!\n\nComanda #B78901 a fost înregistrată cu succes.\nProduse comandate: Telefon Samsung Galaxy S23\nValoare totală: 3.299 RON\nData livrării estimate: 27.06.2023\n\nPentru detalii complete, accesați contul dvs. pe www.magazin-online.ro\n\nEchipa Magazin Online"
                },
                "fake": {
                    "subject": "Comandă confirmată #XZ12345 - Plată eșuată",
                    "body": "Comandă confirmată #XZ12345\n\nATENȚIE: Plata pentru comanda dvs. de iPhone 14 Pro (2.499 EUR) a eșuat.\n\nPentru a evita anularea, actualizați urgent detaliile de plată aici: http://order-payment-update.shop\n\nComanda va fi anulată automat în 2 ore dacă plata nu este procesată.\n\nDepartamentul Financiar"
                },
                "explanation": "Fals: comandă pe care nu ai făcut-o, presiune de timp, link suspect, solicită date de plată. Real: detalii specifice despre o comandă reală, trimitere către site-ul oficial, nu solicită acțiune urgentă."
            },
            {
                "type": "Probleme cont social media",
                "real": {
                    "subject": "Actualizare termeni și condiții Facebook",
                    "body": "Bună ziua,\n\nVă informăm că am actualizat termenii și condițiile de utilizare.\n\nPuteți consulta noii termeni accesând secțiunea 'Setări cont' > 'Termeni și condiții' din contul dvs. sau vizitând www.facebook.com/terms.\n\nNu este necesară nicio acțiune pentru continuarea utilizării serviciilor noastre.\n\nEchipa Facebook"
                },
                "fake": {
                    "subject": "ALERTĂ: Contul dvs. Facebook va fi dezactivat",
                    "body": "URGENT: Contul dvs. a fost raportat pentru încălcarea regulilor comunității!\n\nContul dvs. va fi dezactivat în 24 de ore dacă nu confirmați identitatea.\n\nPentru verificare rapidă, accesați: http://facebook-verify-account.co și introduceți datele de autentificare.\n\nDepartamentul de Securitate Facebook"
                },
                "explanation": "Fals: domeniu fals (facebook-verify-account.co), ton alarmist, solicită date de autentificare. Real: trimite către site-ul oficial, nu solicită acțiuni urgente, ton profesional."
            },
            {
                "type": "Verificare cont",
                "real": {
                    "subject": "Confirmare adresă de email pentru contul nou",
                    "body": "Bună ziua,\n\nPentru a finaliza înregistrarea contului dvs. pe platforma noastră, vă rugăm să confirmați adresa de email accesând link-ul de mai jos:\n\nhttps://www.platforma-servicii.ro/confirmare?token=abc123\n\nLink-ul este valabil 48 de ore.\n\nDacă nu ați solicitat crearea unui cont, ignorați acest email.\n\nEchipa Platformă Servicii"
                },
                "fake": {
                    "subject": "ULTIMĂ NOTIFICARE: Contul dvs. va fi suspendat",
                    "body": "Contul dvs. este programat pentru suspendare din cauza unor activități suspecte!\n\nTrebuie să vă verificați IMEDIAT contul accesând: http://account-verification-secure.info și să introduceți numele de utilizator, parola și numărul de telefon pentru verificare.\n\nNeconfirmarea în 6 ore va duce la suspendarea definitivă!\n\nEchipa de Securitate"
                },
                "explanation": "Fals: domeniu suspect, solicită multiple date sensibile, presiune extremă de timp, nu menționează numele serviciului. Real: domeniu oficial, link cu token securizat, perioadă rezonabilă, instrucțiuni în caz de eroare."
            },
            {
                "type": "Rambursare falsă",
                "real": {
                    "subject": "Confirmare rambursare comandă #C45678",
                    "body": "Stimate client,\n\nVă informăm că am procesat cererea dvs. de rambursare pentru comanda #C45678.\n\nSuma de 249,99 RON a fost returnată pe cardul folosit la achiziție și va fi vizibilă în contul dvs. în 3-5 zile lucrătoare.\n\nPentru detalii, accesați istoricul comenzilor din contul dvs. pe www.magazin-electronic.ro.\n\nMagazin Electronic"
                },
                "fake": {
                    "subject": "REFUND DISPONIBIL - 329,99 EUR Rambursare fiscală",
                    "body": "Stimate contribuabil,\n\nAvem plăcerea să vă informăm că aveți o RAMBURSARE FISCALĂ în valoare de 329,99 EUR disponibilă!\n\nPentru a primi suma, accesați: http://tax-refund-gov.eu și completați formularul cu datele dvs. bancare pentru transfer direct.\n\nRambursarea expiră în 48 ore!\n\nAdministrația Fiscală"
                },
                "explanation": "Fals: domeniu fals care imită o instituție guvernamentală, sumă mare nejustificată, presiune de timp, solicită date bancare. Real: referință la o comandă specifică, sumă exactă, informație despre procesul standard de rambursare."
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

# Inițializare stare sesiune
if "score" not in st.session_state:
    st.session_state.score = 0
if "total" not in st.session_state:
    st.session_state.total = 0
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.now()
if "enhanced_ui" not in st.session_state:
    st.session_state.enhanced_ui = True
if "answered_types" not in st.session_state:
    st.session_state.answered_types = {}
if "quiz_complete" not in st.session_state:
    st.session_state.quiz_complete = False
if "current_emails" not in st.session_state:
    st.session_state.current_emails = None

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
    st.header("Statistici și Setări")
    st.metric("Scor curent", f"{st.session_state.score}/{st.session_state.total}")
    if st.session_state.total > 0:
        accuracy = (st.session_state.score / st.session_state.total) * 100
        st.progress(accuracy/100, f"Acuratețe: {accuracy:.1f}%")
    
    elapsed_time = (datetime.now() - st.session_state.start_time).total_seconds()
    minutes, seconds = divmod(int(elapsed_time), 60)
    st.info(f"Timp petrecut: {minutes}m {seconds}s")
    
    st.subheader("Progres")
    total_types = len(examples)
    completed_types = len(st.session_state.answered_types)
    st.progress(completed_types/total_types, f"Progres: {completed_types}/{total_types} tipuri")
    
    st.subheader("Setări interfață")
    enhanced_ui = st.toggle("Interfață îmbunătățită", value=st.session_state.enhanced_ui)
    if enhanced_ui != st.session_state.enhanced_ui:
        st.session_state.enhanced_ui = enhanced_ui
    
    if st.button("Resetează tot"):
        st.session_state.score = 0
        st.session_state.total = 0
        st.session_state.current_index = 0
        st.session_state.start_time = datetime.now()
        st.session_state.answered_types = {}
        st.session_state.quiz_complete = False
        st.session_state.current_emails = None
        st.rerun()

# Container principal
main_container = st.container()

# Verificăm dacă quiz-ul a fost completat
if st.session_state.quiz_complete:
    # Afișăm raportul final
    st.header("🎓 Raport Final - Vaccinare Anti-Phishing Completă!")
    
    # Calculăm scorul total și procent
    total_score = st.session_state.score
    total_questions = st.session_state.total
    if total_questions > 0:
        percent_correct = (total_score / total_questions) * 100
    else:
        percent_correct = 0
    
    # Afișăm scorul
    st.subheader(f"Scor final: {total_score}/{total_questions} ({percent_correct:.1f}%)")
    
    # Afișăm timpul petrecut
    elapsed_time = (datetime.now() - st.session_state.start_time).total_seconds()
    minutes, seconds = divmod(int(elapsed_time), 60)
    st.info(f"Timp total: {minutes} minute și {seconds} secunde")
    
    # Afișăm rezultatele pe tipuri de phishing
    st.subheader("Rezultate pe tipuri de phishing:")
    
    # Creăm o listă de dicționare pentru afișare tabel
    results_data = []
    for phish_type, result in st.session_state.answered_types.items():
        results_data.append({
            "Tip de phishing": phish_type,
            "Răspuns corect": "✅" if result["correct"] else "❌",
            "Explicație": result["explanation"]
        })
    
    # Afișăm tabelul
    st.table(results_data)
    
    # Buton pentru restart
    if st.button("Începe un nou test", use_container_width=True):
        st.session_state.score = 0
        st.session_state.total = 0
        st.session_state.current_index = 0
        st.session_state.start_time = datetime.now()
        st.session_state.answered_types = {}
        st.session_state.quiz_complete = False
        st.session_state.current_emails = None
        st.rerun()
        
    # Sfaturi finale
    with st.expander("Cele mai importante semne de phishing"):
        st.markdown("""
        ### Principalele semne de phishing pe care să le cauți:
        
        1. **Ton de urgență și presiune** - Emailurile de phishing creează adesea un sentiment de urgență pentru a te determina să acționezi impulsiv.
        
        2. **URL-uri suspecte** - Verifică întotdeauna adresa URL înainte de a face click, chiar dacă textul vizibil pare legitim.
        
        3. **Solicitări de informații personale** - Companiile legitime nu cer niciodată informații sensibile prin email.
        
        4. **Oferte prea bune pentru a fi adevărate** - Câștiguri neașteptate, reduceri extreme sau oferte incredibile sunt adesea capcane.
        
        5. **Greșeli gramaticale și de ortografie** - Comunicările profesionale sunt de obicei verificate pentru greșeli.
        
        6. **Adrese de email suspecte** - Verifică cu atenție adresa expeditorului, nu doar numele afișat.
        
        7. **Link-uri și atașamente neașteptate** - Fii prudent cu atașamentele pe care nu le așteptai.
        """)
else:
    # Quiz în desfășurare
    with main_container:
        # Verificăm dacă am parcurs toate tipurile sau dacă nu avem emailuri curente
        if st.session_state.current_index >= len(examples) or st.session_state.current_emails is None:
            if len(st.session_state.answered_types) >= len(examples):
                # Am completat toate tipurile de phishing
                st.session_state.quiz_complete = True
                st.rerun()
            
            # Alegem un exemplu care nu a fost încă rezolvat
            remaining_types = [i for i in range(len(examples)) if examples[i]["type"] not in st.session_state.answered_types]
            if remaining_types:
                st.session_state.current_index = random.choice(remaining_types)
            else:
                # Dacă am răspuns la toate, marcăm quiz-ul ca fiind complet
                st.session_state.quiz_complete = True
                st.rerun()
            
            # Obținem exemple pentru tipul curent
            current_example = examples[st.session_state.current_index]
            
            # Pregătim emailurile
            real_email = current_example["real"]
            fake_email = current_example["fake"]
            
            # Pregătim lista cu cele două emailuri și amestecăm ordinea
            emails = [
                {"data": real_email, "is_phish": False},
                {"data": fake_email, "is_phish": True}
            ]
            random.shuffle(emails)
            
            # Salvăm emailurile în sesiune
            st.session_state.current_emails = emails
        
        # Obținem exemplul curent
        current_example = examples[st.session_state.current_index]
        emails = st.session_state.current_emails
        
        # Afișăm tipul de phishing și explicația
        st.header(f"Tip: {current_example['type']}")
        
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
            
            # Adăugăm tipul curent în lista de tipuri la care s-a răspuns
            st.session_state.answered_types[current_example["type"]] = {
                "correct": correct,
                "explanation": current_example["explanation"]
            }
            
            # Afișăm explicația
            st.markdown(f"**Explicație:** {current_example['explanation']}")
            
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
            
            # Buton pentru continuare
            if st.button("Continuă la următorul exemplu", use_container_width=True):
                # Dacă am răspuns la toate tipurile
                if len(st.session_state.answered_types) >= len(examples):
                    st.session_state.quiz_complete = True
                else:
                    # Ștergem emailurile curente pentru a genera altele la următoarea iterație
                    st.session_state.current_emails = None
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
    
    **Tipuri de phishing acoperite:**
    - Email-phishing clasic
    - Spear-phishing (phishing țintit)
    - Fraudă bancară
    - Ofertă falsă
    - Impersonare CEO
    - Actualizare de securitate falsă
    - Suport tehnic fals
    - Notificare de livrare falsă
    - Reînnoire abonament falsă
    - Donație falsă
    - Oportunitate de investiții falsă
    - Cupoane și discount-uri false
    - Confirmare comandă falsă
    - Probleme cont social media false
    - Verificare cont falsă
    - Rambursare falsă (cerere de returnare a banilor)
    """)
    
    feedback = st.text_area("Feedback sau sugestii:")
    if st.button("Trimite feedback"):
        st.success("Mulțumim pentru feedback! Vom lua în considerare sugestiile tale pentru versiunile viitoare.")

# Footer
st.markdown("---")
st.markdown("© 2025 Vaccin Anti-Phishing | Creat în scop educațional")
