import streamlit as st
import random
import json
import os
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
            },
            {
                "type": "Coș cadou Paște",
                "real": {
                    "subject": "Ofertă specială de Paște - Lindt Romania",
                    "body": "Dragi clienți,\n\nCu ocazia sărbătorilor pascale, vă oferim reduceri de 15% la toate produsele noastre de ciocolată.\n\nVizitați magazinul nostru sau accesați www.lindt.ro/paste pentru a vedea ofertele.\n\nVă dorim Sărbători Fericite!\nEchipa Lindt România"
                },
                "fake": {
                    "subject": "🐰 CADOU GRATUIT - Coș de Paște Lindt pentru tine!",
                    "body": "Felicitări! Ai fost selectat să primești un coș de Paște Lindt GRATUIT!\n\nPentru a-ți revendica coșul cadou, completează chestionarul nostru scurt (30 de secunde) și plătește doar taxa de livrare 4,99 lei:\n\nhttp://lindt-easter-gift.com/claim\n\nOfertă valabilă doar azi!\nEchipa Promoții de Paște"
                },
                "explanation": "Fals: domeniu fals care imită brandul Lindt, ofertă prea bună pentru a fi adevărată (cadou 'gratuit' dar cere taxă), presiune de timp. Real: site oficial, reducere rezonabilă, nu solicită date personale."
            },
            {
                "type": "Vouchere și cupoane",
                "real": {
                    "subject": "Voucher cadou pentru aniversarea colaborării noastre",
                    "body": "Dragă client,\n\nCu ocazia aniversării a 3 ani de când ești clientul nostru, îți oferim un voucher în valoare de 50 RON.\n\nPoți folosi codul ANIV50 la următoarea comandă pe site-ul nostru www.magazin-oficial.ro până la data de 31.12.2023.\n\nEchipa Magazin Oficial"
                },
                "fake": {
                    "subject": "IMPORTANT: Voucher KAUFLAND de 250 EUR - Sondaj Clienți",
                    "body": "Stimați clienți Kaufland,\n\nSărbătorim 15 ani în România și oferim 100 vouchere de 250 EUR!\n\nPentru a obține voucher-ul, completează un scurt sondaj (2 minute) și introduceți datele dvs. pentru validare:\n\nhttp://kaufland-voucher.online/ro\n\nPrimii 100 de participanți vor primi voucherul direct pe email.\nEchipa Kaufland România"
                },
                "explanation": "Fals: domeniu suspect (.online), valoare nerealist de mare a voucherului, urgență (primii 100), solicită date personale. Real: ofertă realistă de valoare moderată, cod de voucher furnizat direct în email."
            },
            {
                "type": "Impersonare CEO",
                "real": {
                    "subject": "Prezentarea trimestrială - feedback",
                    "body": "Bună ziua tuturor,\n\nVă mulțumesc pentru participarea la prezentarea trimestrială de ieri.\n\nVă rog să trimiteți feedback-ul și sugestiile în formularul din intranet până vineri.\n\nCu stimă,\nAna Marinescu\nDirector General\nam@compania.ro"
                },
                "fake": {
                    "subject": "Solicitare discretă - te rog răspunde imediat",
                    "body": "Salut,\n\nMă aflu într-o întâlnire confidențială și nu pot vorbi la telefon. Avem nevoie urgent de niște carduri cadou Google Play pentru un client important.\n\nPoți să cumperi 5 carduri a câte 200 EUR și să-mi trimiți codurile pe WhatsApp la nr +40755123456? Voi aproba rambursarea astăzi.\n\nSunt presată de timp, te rog confirmă în 15 minute.\n\nMulțumesc,\nAna Marinescu\nDirector General\nana.marinescu.ceo@gmail.com"
                },
                "explanation": "Fals: adresă de email personală (gmail) în loc de domeniul companiei, solicitare urgentă de bani/carduri, cerere de comunicare pe alt canal, presiune extremă de timp. Real: adresă oficială de email, solicitare profesională normală."
            },
            {
                "type": "Actualizare de securitate",
                "real": {
                    "subject": "Actualizare politică de securitate - acțiune necesară",
                    "body": "Stimate utilizator,\n\nAm actualizat politica noastră de securitate.\n\nVă rugăm să vă autentificați în contul dvs. de pe site-ul nostru www.serviciu-web.ro și să revizuiți noii termeni din secțiunea 'Setări cont'.\n\nEchipa de Securitate\nServiceWeb"
                },
                "fake": {
                    "subject": "⚠ ALERTA DE SECURITATE: Contul dvs. a fost COMPROMIS",
                    "body": "URGENT - Acțiune Imediată Necesară!\n\nAm detectat o încercare de acces neautorizat la contul dvs!\n\nPentru a preveni pierderea accesului, trebuie să vă verificați contul în următoarele 2 ore accesând:\n\nhttp://account-security-verification.com/verify\n\nVeți avea nevoie de parola actuală și detaliile cardului de credit pentru verificare.\n\nEchipa de Securitate"
                },
                "explanation": "Fals: ton extrem de alarmist, domeniu generic, solicitare de informații sensibile (parolă și card), presiune extremă de timp. Real: ton profesional, trimitere către site-ul oficial, nu solicită date sensibile prin email."
            },
            {
                "type": "Felicitare electronică falsă",
                "real": {
                    "subject": "O felicitare virtuală pentru tine",
                    "body": "Dragă prieten,\n\nȚi-am trimis o felicitare virtuală pentru a sărbători prietenia noastră.\n\nO poți vizualiza accesând www.ecards-official.com/view/card/12345 - nu este necesară nicio înregistrare sau descărcare.\n\nCu drag,\nAndreea"
                },
                "fake": {
                    "subject": "Cineva ți-a trimis o FELICITARE SPECIALĂ! 💌",
                    "body": "Cineva special s-a gândit la tine!\n\nUn prieten ți-a trimis o felicitare personalizată. Pentru a o vedea, descarcă atașamentul sau accesează:\n\nhttp://special-ecards.co/view?id=12345\n\nNOTĂ: Felicitarea va expira în 24 de ore, grăbește-te să o vezi!\n\nEchipa Special E-Cards"
                },
                "explanation": "Fals: expeditor necunoscut, presiune de timp, solicitare de descărcare de atașamente, domeniu suspect (.co). Real: domeniu clar, fără presiune de timp, menționează explicit că nu este necesară descărcarea sau înregistrarea."
            },
            {
                "type": "Fraudă cu suport tehnic",
                "real": {
                    "subject": "Confirmare ticket suport #12345",
                    "body": "Bună ziua,\n\nAm înregistrat solicitarea dvs. cu numărul de ticket #12345.\n\nUn specialist va analiza problema și vă va contacta în maxim 24 de ore.\n\nPuteți urmări statusul ticket-ului pe portalul nostru de suport.\n\nEchipa de Suport Tehnic\nsupport@companie.ro"
                },
                "fake": {
                    "subject": "⚠ ALERTĂ CRITICĂ: Virus detectat pe dispozitivul dvs",
                    "body": "AVERTISMENT DE SECURITATE MICROSOFT!\n\nAm detectat activitate suspectă pe dispozitivul dvs. Virușii detectați:\n- Trojan.BTC-Miner\n- Spyware.KeyLogger\n\nDatele și conturile dvs. bancare sunt în PERICOL IMINENT!\n\nSunați ACUM la numărul dedicat: +40721000123 pentru asistență imediată, sau accesați:\nhttp://windows-security-center.tech\n\nNeintervenția în 3 ore poate duce la PIERDEREA TOTALĂ A DATELOR!\n\nEchipa de Securitate Microsoft"
                },
                "explanation": "Fals: ton extrem de alarmist, număr de telefon suspect, domeniu fals, presiune extremă de timp, exagerarea consecințelor. Real: ton profesional, referire la un număr de ticket specific."
            },
            {
                "type": "Notificare livrare falsă",
                "real": {
                    "subject": "Comandă #A12345 - În curs de livrare",
                    "body": "Bună ziua,\n\nComanda dvs. #A12345 a fost expediată și va fi livrată în data de 25.06.2023.\n\nPuteți urmări statusul folosind codul de tracking: RO123456789RO pe site-ul nostru www.fan-courier.ro.\n\nEchipa Livrări\nFan Courier"
                },
                "fake": {
                    "subject": "⚠️ IMPORTANT: Coletul dvs. necesită confirmare de adresă",
                    "body": "Stimate client,\n\nAvem un colet pentru dvs, dar livrarea a eșuat din cauza unei adrese incomplete.\n\nPentru a reprograma livrarea, vă rugăm să confirmați adresa folosind link-ul de mai jos:\n\nhttp://delivery-address-confirm.co/form\n\nVa trebui să plătiți o taxă de reprogramare de 3,99 lei cu cardul.\n\nDacă nu confirmați în 48h, coletul va fi returnat expeditorului.\n\nServiciul de Livrări"
                },
                "explanation": "Fals: nu specifică numele companiei de curierat, nu menționează nicio referință la comandă, solicită taxă de reprogramare, domeniu suspect, solicită date de card. Real: include număr de comandă și cod de tracking specific, trimite către site-ul oficial al companiei de curierat."
            },
            {
                "type": "Sondaj fals cu premii",
                "real": {
                    "subject": "Invitație: Participă la studiul nostru anual de satisfacție",
                    "body": "Dragă client,\n\nTe invităm să participi la studiul nostru anual privind satisfacția clienților. Completarea durează aproximativ 5 minute.\n\nParticipanții vor intra automat într-o tragere la sorți pentru un voucher de 300 RON.\n\nPoți accesa chestionarul pe site-ul nostru oficial: www.companie.ro/sondaj\n\nÎți mulțumim pentru feedback!\nEchipa de Relații Clienți"
                },
                "fake": {
                    "subject": "🎁 FELICITĂRI! Ai fost selectat pentru premiul Samsung!",
                    "body": "FELICITĂRI!\n\nDistozitivul tău a fost selectat aleatoriu pentru a câștiga un nou Samsung Galaxy S23 Ultra!\n\nPentru a revendica premiul, trebuie doar să participi la sondajul nostru scurt (3 întrebări) și să plătești taxa de procesare de doar 9,99 lei:\n\nhttp://samsung-winner-survey.com/claim\n\nAu mai rămas doar 2 telefoane! Grăbește-te!\n\nEchipa Promoții Samsung"
                },
                "explanation": "Fals: ofertă nerealistă, domeniu fals care imită brandul Samsung, urgență artificială ('doar 2 telefoane rămase'), solicită taxă pentru un premiu 'câștigat'. Real: ofertă rezonabilă, site oficial, explicație clară a procesului."
            },
            {
                "type": "Reînnoire abonament",
                "real": {
                    "subject": "Abonamentul dvs. expiră în 7 zile",
                    "body": "Stimate abonat,\n\nVă reamintim că abonamentul dvs. premium va expira pe data de 30.06.2023.\n\nPentru reînnoire, accesați contul dvs. pe www.serviciu-streaming.ro/cont și selectați opțiunea dorită.\n\nVă mulțumim că sunteți alături de noi!\n\nEchipa Serviciu Streaming"
                },
                "fake": {
                    "subject": "⚠️ URGENT: Abonamentul dvs. Netflix a fost SUSPENDAT",
                    "body": "Stimate client Netflix,\n\nAbonamentul dvs. a fost SUSPENDAT din cauza unei probleme de plată!\n\nPentru a evita pierderea permanentă a contului și a istoricului de vizionare, trebuie să actualizați URGENT informațiile de plată în următoarele 12 ore:\n\nhttp://netflix-account-billing.co/reactivate\n\nVă vom debita doar 1,99 EUR pentru verificare.\n\nEchipa de Facturare Netflix"
                },
                "explanation": "Fals: ton alarmist, domeniu fals (.co în loc de .com), solicitare de plată pentru 'verificare', presiune extremă de timp. Real: notificare cu mult timp înainte, trimitere către site-ul oficial, fără presiune sau amenințări."
            },
            {
                "type": "Oportunitate de investiții",
                "real": {
                    "subject": "Invitație: Webinar despre strategii de investiții 2023",
                    "body": "Stimată Doamnă/Stimate Domn,\n\nVă invităm să participați la webinarul nostru despre strategii de investiții pentru 2023, care va avea loc pe data de 15 iulie.\n\nPentru a vă înscrie și a afla mai multe detalii, vizitați: www.banca-investitii.ro/webinare\n\nParticiparea este gratuită pentru clienții noștri.\n\nBanca de Investiții"
                },
                "fake": {
                    "subject": "🔐 CONFIDENȚIAL: Oportunitate unică de investiție - Randament 200%",
                    "body": "Stimate investitor,\n\nVă contactez pentru a vă oferi acces la o oportunitate de investiție ULTRA-EXCLUSIVĂ disponibilă doar pentru 10 investitori selectați cu atenție.\n\nInvestiția oferă un randament GARANTAT de 200% în doar 4 luni prin tehnologia noastră avansată de tranzacționare crypto.\n\nPentru a vă rezerva locul, este necesară o investiție minimă de 5000 EUR prin transfer în contul nostru securizat: RO29CRYP12345678900\n\nRăspundeți în 24h sau sunați la: +40755987654\n\nPartenerul dvs. de investiții,\nDr. Alexandru Profit\nCrypto Investment Group"
                },
                "explanation": "Fals: randament nerealist de mare, presiune de timp, solicitare de transferuri directe, lipsă de detalii concrete despre investiție, tonul exclusivist și secretos. Real: invitație la un eveniment informativ, fără solicitare de bani, prezentarea clară a companiei."
            },
            {
                "type": "Confirmare comandă falsă",
                "real": {
                    "subject": "Confirmare comandă #B78901 - Magazin Online",
                    "body": "Mulțumim pentru comanda dvs.!\n\nComanda #B78901 a fost înregistrată cu succes.\nProduse comandate: Telefon Samsung Galaxy S23\nValoare totală: 3.299 RON\nData livrării estimate: 27.06.2023\n\nPentru detalii complete, accesați contul dvs. pe www.magazin-online.ro\n\nEchipa Magazin Online"
                },
                "fake": {
                    "subject": "Comandă Apple confirmată #APL78432 - Acțiune necesară",
                    "body": "Comandă Apple confirmată\nNr. comandă: APL78432\n\nProduse: MacBook Pro 16\" 2023\nValoare: 12,499 RON\n\nATENȚIE: Am detectat o problemă cu metoda dvs. de plată. Plata nu a putut fi procesată.\n\nPentru a evita anularea comenzii, actualizați urgent detaliile cardului:\n\nhttp://apple-order-payment.net/confirm\n\nComanda va fi anulată automat în 4 ore dacă problema nu este rezolvată.\n\nDepartamentul Comenzi Apple"
                },
                "explanation": "Fals: comandă pe care probabil nu ai făcut-o, valoare foarte mare, domeniu fals care imită Apple, presiune de timp, solicită actualizarea datelor cardului. Real: detalii specifice despre comandă, trimitere către site-ul oficial, nu solicită acțiune urgentă."
            },
            {
                "type": "Probleme cont social media",
                "real": {
                    "subject": "Actualizare termeni și condiții Facebook",
                    "body": "Bună ziua,\n\nVă informăm că am actualizat termenii și condițiile de utilizare.\n\nPuteți consulta noii termeni accesând secțiunea 'Setări cont' > 'Termeni și condiții' din contul dvs. sau vizitând www.facebook.com/terms.\n\nNu este necesară nicio acțiune pentru continuarea utilizării serviciilor noastre.\n\nEchipa Facebook"
                },
                "fake": {
                    "subject": "⚠️ URGENT: Contul dvs. de Instagram va fi ȘTERS în 24h",
                    "body": "AVERTISMENT FINAL\n\nContul dvs. de Instagram a fost raportat pentru încălcarea drepturilor de autor și a regulilor comunității!\n\nContul dvs. va fi ȘTERS PERMANENT în 24 de ore dacă nu contestați acuzațiile.\n\nPentru a verifica identitatea și a păstra contul, accesați:\n\nhttp://instagram-copyright-verify.com\n\nVa trebui să vă conectați cu numele de utilizator și parola pentru verificare.\n\nEchipa de Securitate Instagram"
                },
                "explanation": "Fals: ton foarte alarmist, amenințare cu ștergerea contului, domeniu fals, solicitare de date de autentificare. Real: ton profesional, trimitere către site-ul oficial, fără presiune sau amenințări."
            },
            {
                "type": "Verificare cont",
                "real": {
                    "subject": "Confirmare adresă de email pentru contul nou",
                    "body": "Bună ziua,\n\nPentru a finaliza înregistrarea contului dvs. pe platforma noastră, vă rugăm să confirmați adresa de email accesând link-ul de mai jos:\n\nhttps://www.platforma-servicii.ro/confirmare?token=abc123\n\nLink-ul este valabil 48 de ore.\n\nDacă nu ați solicitat crearea unui cont, ignorați acest email.\n\nEchipa Platformă Servicii"
                },
                "fake": {
                    "subject": "⚠️ ACȚIUNE NECESARĂ: Verificare de securitate cont Google",
                    "body": "Alertă de Securitate Google\n\nAm detectat o încercare de conectare neobișnuită la contul dvs. Google din Jakarta, Indonezia.\n\nDacă nu ați fost dvs., contul dvs. este în PERICOL IMINENT!\n\nVerificați-vă imediat contul și schimbați parola accesând:\n\nhttp://google-account-security.co/verify\n\nVeți avea nevoie de parola actuală și un nou cod de securitate care va fi trimis pe telefonul dvs.\n\nNeluarea de măsuri în 12 ore va duce la BLOCAREA CONTULUI.\n\nEchipa de Securitate Google"
                },
                "explanation": "Fals: ton alarmist, domeniu fals, solicitare de parolă actuală, crearea unui sentiment de panică prin menționarea unei locații îndepărtate, presiune de timp. Real: ton neutru, domeniu oficial, utilizarea unui token de securitate, explicație clară a pașilor următori."
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
if "phish_positions" not in st.session_state:
    # Vom folosi această variabilă pentru a alterna poziția emailurilor de phishing
    st.session_state.phish_positions = []

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
        st.session_state.phish_positions = []
        st.rerun()

# Container principal
main_container = st.container()

# Verificăm dacă quiz-ul a fost completat
if st.session_state.quiz_complete:
    # Afișăm raportul final
    st.header("🎓 Raport Final - Antrenament Complet!")
    
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
        st.session_state.phish_positions = []
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
            
            # Funcție pentru a genera emailuri în mod dinamic
            def generate_dynamic_emails(example_type, example_data):
                """
                Generează emailuri dinamice bazate pe șabloane sau AI
                """
                try:
                    # Opțional, încearcă să folosești AI dacă este disponibil
                    # Încearcă să folosești OpenAI (nu-l vom implementa aici pentru că necesită chei API)
                    # În cazul eșecului, folosește datele locale
                    
                    # Simulăm diverse variații
                    real_email = example_data["real"].copy()
                    fake_email = example_data["fake"].copy()
                    
                    # Adăugăm variații aleatorii pentru a face emailurile mai realiste
                    current_date = datetime.now().strftime("%d.%m.%Y")
                    tomorrow = (datetime.now() + datetime.timedelta(days=1)).strftime("%d.%m.%Y")
                    
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
            if not st.session_state.phish_positions:
                # Dacă lista e goală, generăm o secvență semi-aleatoare pentru toată sesiunea
                # Asigurăm un echilibru între stânga și dreapta
                positions = []
                for i in range(len(examples) // 2):
                    positions.extend([True, False])  # True = phishing pe stânga
                random.shuffle(positions)
                st.session_state.phish_positions = positions
            
            # Extragem poziția pentru exemplul curent și o eliminăm din listă
            if st.session_state.phish_positions:
                phishing_on_left = st.session_state.phish_positions.pop(0)
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
