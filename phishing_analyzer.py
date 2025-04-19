def analyze_phishing_email(email_data, email_type):
    """
    Analizează un email de phishing și identifică indicatorii de fraudă
    
    Args:
        email_data: Dicționar cu datele emailului
        email_type: Tipul de phishing
        
    Returns:
        dict: Analiză detaliată cu indicatori și explicații
    """
    indicators = []
    
    # Analizarea subiectului
    subject = email_data.get("subject", "").lower()
    if any(word in subject for word in ["urgent", "urgentă", "imediat", "acum", "alertă", "atenție"]):
        indicators.append({
            "tip": "Ton de urgență în subiect",
            "detalii": "Emailurile frauduloase folosesc adesea un ton de urgență pentru a te determina să acționezi impulsiv, fără să analizezi conținutul.",
            "exemplu": email_data.get("subject"),
            "risc": "ridicat"
        })
    
    if subject.isupper() or subject.count("!") > 1:
        indicators.append({
            "tip": "Formatare agresivă în subiect",
            "detalii": "Utilizarea excesivă a majusculelor sau a semnelor de exclamare este o tehnică de manipulare emoțională.",
            "exemplu": email_data.get("subject"),
            "risc": "mediu"
        })
    
    # Analizarea corpului
    body = email_data.get("body", "").lower()
    
    # Verificarea URL-urilor suspecte
    import re
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', body)
    
    for url in urls:
        suspicious = False
        reasons = []
        
        # URL scurtat
        if any(domain in url for domain in ["bit.ly", "tinyurl", "goo.gl", "t.co"]):
            suspicious = True
            reasons.append("URL scurtat care ascunde destinația reală")
        
        # Domeniu similar cu unul legitim dar diferit
        common_domains = ["google", "facebook", "microsoft", "apple", "amazon", "netflix", "paypal", "banca"]
        for domain in common_domains:
            if domain in url and not url.endswith(f".com/{domain}") and not url.endswith(f".ro/{domain}") and domain + "-" in url:
                suspicious = True
                reasons.append(f"Domeniu care imită '{domain}' dar nu este oficial")
        
        # Subdomenii suspecte
        if url.count(".") > 2:
            suspicious = True
            reasons.append("Utilizarea subdomeniilor pentru a masca adresa reală")
        
        # Domenii cu extensii neobișnuite
        suspicious_tlds = ["xyz", "info", "online", "site", "tech", "win", "top"]
        for tld in suspicious_tlds:
            if f".{tld}" in url:
                suspicious = True
                reasons.append(f"Extensie de domeniu neobișnuită (.{tld})")
        
        if suspicious:
            indicators.append({
                "tip": "URL suspect",
                "detalii": "Link-ul conține indicatori de fraudă: " + ", ".join(reasons),
                "exemplu": url,
                "risc": "ridicat"
            })
    
    # Verificarea solicitărilor de informații sensibile
    sensitive_patterns = [
        "parolă", "password", "user", "login", "autentificare", "cont", "card", 
        "pin", "cvv", "bancar", "transfer", "plată", "credit", "verificare"
    ]
    
    if any(pattern in body for pattern in sensitive_patterns):
        indicators.append({
            "tip": "Solicitare de informații sensibile",
            "detalii": "Emailul cere date confidențiale. Companiile legitime nu solicită niciodată informații sensibile prin email.",
            "exemplu": "Extragere context: \"..." + body[max(0, body.find(next((p for p in sensitive_patterns if p in body), ""))-20:min(len(body), body.find(next((p for p in sensitive_patterns if p in body), ""))+50)] + "...\"",
            "risc": "ridicat"
        })
    
    # Verificare limbaj
    if any(word in body for word in ["gratuit", "câștigat", "premiu", "ofertă", "promoție"]) and "verificare" in body:
        indicators.append({
            "tip": "Ofertă prea bună pentru a fi adevărată",
            "detalii": "Promisiunile de câștiguri sau premii neașteptate sunt tactici comune de phishing.",
            "exemplu": "Acest email promite câștiguri sau oferte neobișnuit de avantajoase pentru a te determina să furnizezi informații.",
            "risc": "mediu"
        })
    
    # Recomandări specifice în funcție de tipul de phishing
    recommendations = {
        "Email-phishing clasic": "Verifică întotdeauna adresa expeditorului și nu face click pe link-uri suspecte.",
        "Spear-phishing": "Fii atent la emailurile care par a fi de la persoane cunoscute dar conțin solicitări neobișnuite.",
        "Fraudă bancară": "Băncile nu solicită niciodată informații sensibile prin email. Accesează site-ul bancar direct, nu prin link-uri din email.",
        "Ofertă falsă": "Ofertele prea bune pentru a fi adevărate de obicei nu sunt adevărate. Verifică oferta direct pe site-ul oficial.",
        "Impersonare CEO": "Confirmă telefonic orice solicitare neobișnuită presupus venită de la un superior.",
        "Actualizare de securitate": "Accesează direct site-ul pentru a-ți verifica contul, nu prin link-uri din email.",
        "Suport tehnic fals": "Companiile legitime nu te contactează neanunțat despre probleme tehnice.",
        "Notificare livrare": "Verifică numărul de comandă cu cel din contul tău înainte de a accesa orice link.",
        "Reînnoire abonament": "Verifică statusul abonamentelor direct pe site-ul furnizorului de servicii.",
        "Donație falsă": "Cercetează organizația înainte de a dona și folosește doar site-uri oficiale.",
        "Oportunitate de investiții": "Investițiile legitime nu promit câștiguri garantate sau extraordinare.",
        "Cupoane și discount-uri": "Verifică ofertele pe site-ul oficial al comerciantului.",
        "Confirmare comandă falsă": "Verifică întotdeauna istoricul comenzilor în contul tău înainte de a reacționa.",
        "Probleme cont social media": "Rețelele sociale te notifică despre probleme doar în aplicație sau pe site-ul oficial.",
        "Verificare cont": "Accesează direct site-ul pentru a-ți verifica contul, nu prin link-uri din email.",
        "Rambursare falsa": "Rambursările legitime menționează detalii specifice tranzacției originale."
    }
    
    # Adaugă recomandarea specifică tipului
    if email_type in recommendations:
        tip_specific = {
            "tip": f"Recomandare pentru {email_type}",
            "detalii": recommendations[email_type],
            "exemplu": "",
            "risc": "informativ"
        }
        indicators.append(tip_specific)
    
    return {
        "indicators": indicators,
        "total_risk_score": sum(4 if ind["risc"] == "ridicat" else 2 if ind["risc"] == "mediu" else 1 for ind in indicators if ind["risc"] != "informativ"),
        "primary_risk": next((ind["tip"] for ind in indicators if ind["risc"] == "ridicat"), "N/A")
    }
