"""
Șabloane pentru emailuri realiste ce pot fi folosite în aplicația de antrenament phishing
"""

# Șabloane pentru emailuri legitime
LEGITIMATE_TEMPLATES = {
    "banking": {
        "headers": {
            "sender_name": "Banca Transilvania",
            "sender_email": "notificari@bancatransilvania.ro",
            "logo": "BT",
            "colors": "#0166b1",
            "footer": "© Banca Transilvania S.A. | Toate drepturile rezervate | Bd. Carol I, nr. 17, Cluj-Napoca"
        },
        "subjects": [
            "Confirmare tranzacție #{{transaction_id}}",
            "Informare: Modificări în termenii și condițiile contului dvs.",
            "Extras de cont - perioada {{month}}"
        ],
        "body_templates": [
            """Stimate client,

Vă informăm că s-a înregistrat o tranzacție în valoare de {{amount}} RON de pe cardul dvs. cu terminația {{card_last_4}} în data de {{date}}.

Dacă nu recunoașteți această tranzacție, vă rugăm să contactați serviciul de Asistență Clienți la numărul 0800 80 CARD (2273), disponibil non-stop.

Puteți verifica toate tranzacțiile în aplicația BT24 sau în orice sucursală Banca Transilvania.

Pentru orice alte informații, vă stăm la dispoziție.

Cu stimă,
Echipa Banca Transilvania

-------
Acest email este generat automat. Vă rugăm să nu răspundeți la această adresă.
Pentru confidențialitatea dvs., nu includem link-uri în notificările de tranzacții.
"""
        ]
    },
    "ecommerce": {
        "headers": {
            "sender_name": "eMAG",
            "sender_email": "info@emag.ro",
            "logo": "eMAG",
            "colors": "#ffce00",
            "footer": "SC Dante International SA | J40/372/2002 | CUI 14399840 | Șos. Virtuții, nr. 148, București"
        },
        "subjects": [
            "Comanda #{{order_id}} a fost confirmată",
            "Factură pentru comanda #{{order_id}}",
            "Urmărește livrarea comenzii #{{order_id}}"
        ],
        "body_templates": [
            """Salut {{name}},

Îți mulțumim pentru comanda ta #{{order_id}}!

Detalii comandă:
* Data: {{date}}
* Produse: {{product_list}}
* Valoare totală: {{amount}} RON
* Adresa de livrare: {{address}}
* Metoda de plată: {{payment_method}}

Comanda ta este în curs de procesare și va fi expediată în următoarele 24 de ore.

Poți urmări statusul comenzii tale în contul tău eMAG, secțiunea "Comenzile mele".

Pentru orice întrebări legate de comandă, te rugăm să contactezi departamentul Relații Clienți la numărul 0722.100.123 sau prin email la help@emag.ro.

Cu stimă,
Echipa eMAG

-------
SC Dante International SA
www.emag.ro
"""
        ]
    }
}

# Șabloane pentru emailuri de phishing
PHISHING_TEMPLATES = {
    "banking_phish": {
        "headers": {
            "sender_name": "Banca Translivania",  # greșeală subtilă
            "sender_email": "notificari@bancatranslivania-secure.com",  # domeniu fals
            "logo": "BT",
            "colors": "#0166b1",
            "footer": "© Banca Translivania S.A. | Toate drepturile rezervate"
        },
        "subjects": [
            "URGENT: Suspiciune fraudă pe contul dvs. #{{account_id}}",
            "Actualizare de securitate necesară - acționați acum",
            "Cont restricționat - Verificare necesară"
        ],
        "body_templates": [
            """Stimate client,

Am detectat o activitate suspectă pe contul dumneavoastră în data de {{date}}. Pentru siguranța fondurilor dvs., anumite funcționalități au fost temporar restricționate.

Pentru a restabili accesul complet la contul dvs., vă rugăm să verificați identitatea accesând portalul nostru securizat:

➤ [Verificare Securitate](http://verificare-bt.online-secure.com/auth)

În cazul în care nu efectuați verificarea în termen de 24 de ore, contul dvs. va fi suspendat conform politicilor de securitate.

Vă mulțumim pentru înțelegere,
Departamentul de Securitate
Banca Translivania

-------
Acest email este confidențial. Vă rugăm să nu distribuiți acest mesaj.
"""
        ]
    },
    "ecommerce_phish": {
        "headers": {
            "sender_name": "eMAG Servicii Clienți",
            "sender_email": "support@emag-delivery.info",  # domeniu fals
            "logo": "eMAG",
            "colors": "#ffce00",
            "footer": "Departamentul de Livrări eMAG"
        },
        "subjects": [
            "URGENT: Problemă cu livrarea comenzii #{{order_id}}",
            "Actualizare necesară pentru livrarea comenzii dvs.",
            "Confirmare adresă pentru livrarea pachetului"
        ],
        "body_templates": [
            """Dragă client,

Vă informăm că pachetul dumneavoastră cu numărul de comandă #{{order_id}} nu a putut fi livrat din cauza unor informații incomplete.

Pentru a evita returnarea pachetului la depozit, vă rugăm să confirmați urgent adresa de livrare și detaliile de contact accesând link-ul de mai jos:

➤ [Confirmare Adresă Livrare](http://emag-delivery.info/confirm/{{order_id}})

Notă: Pentru a vă verifica identitatea, veți fi rugat să furnizați câteva informații de securitate.

Dacă nu confirmați adresa în 48 de ore, pachetul va fi returnat la expeditor și veți fi taxat cu costurile de retur.

Cu stimă,
Echipa de Livrări eMAG

-------
Răspundeți rapid pentru a evita întârzieri suplimentare!
"""
        ]
    }
}

def generate_realistic_email(template_type, is_phishing=False):
    """
    Generează un email realist bazat pe șabloane predefinite
    
    Args:
        template_type: Tipul de email (banking, ecommerce, etc.)
        is_phishing: Dacă email-ul ar trebui să fie phishing sau legitim
    
    Returns:
        dict: Un email complet generat
    """
    import random
    import datetime
    
    # Alegem șablonul corespunzător
    templates = PHISHING_TEMPLATES if is_phishing else LEGITIMATE_TEMPLATES
    template_key = f"{template_type}_phish" if is_phishing else template_type
    
    # Verificăm dacă șablonul există
    if template_key not in templates:
        # Folosim un șablon implicit
        template_key = list(templates.keys())[0]
    
    template = templates[template_key]
    
    # Generăm datele variabile
    variables = {
        "transaction_id": f"TX{random.randint(10000, 99999)}",
        "order_id": f"{random.randint(100000, 999999)}",
        "account_id": f"*****{random.randint(1000, 9999)}",
        "card_last_4": f"{random.randint(1000, 9999)}",
        "amount": f"{random.randint(50, 5000)}.{random.randint(0, 99):02d}",
        "date": datetime.datetime.now().strftime("%d.%m.%Y"),
        "month": datetime.datetime.now().strftime("%B %Y"),
        "name": "Alexandru Popescu",
        "product_list": "Laptop ASUS, Mouse wireless, Căști audio",
        "address": "Strada Exemplu, nr. 123, București",
        "payment_method": random.choice(["Card", "Ramburs", "Transfer bancar"])
    }
    
    # Alegem un subiect și un corp aleator
    subject_template = random.choice(template["subjects"])
    body_template = random.choice(template["body_templates"])
    
    # Înlocuim variabilele
    subject = subject_template
    body = body_template
    
    for key, value in variables.items():
        placeholder = "{{" + key + "}}"
        subject = subject.replace(placeholder, str(value))
        body = body.replace(placeholder, str(value))
    
    # Construim emailul complet
    email = {
        "subject": subject,
        "body": body,
        "sender": template["headers"]["sender_name"],
        "sender_email": template["headers"]["sender_email"],
        "logo": template["headers"]["logo"],
        "colors": template["headers"]["colors"],
        "footer": template["headers"]["footer"],
        "date": datetime.datetime.now().strftime("%d.%m.%Y, %H:%M")
    }
    
    return email
