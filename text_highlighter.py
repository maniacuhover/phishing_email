def highlight_phishing_indicators(email_text, indicators):
    """
    Evidențiază indicatori de phishing în textul emailului
    
    Args:
        email_text: Textul emailului
        indicators: Lista de indicatori detectați
    
    Returns:
        str: Textul emailului cu evidențieri HTML
    """
    highlighted_text = email_text
    
    # Definim stilurile de evidențiere
    highlight_styles = {
        "ridicat": "background-color: #ffcccc; border-bottom: 2px solid red; padding: 2px;",
        "mediu": "background-color: #fff2cc; border-bottom: 2px solid orange; padding: 2px;",
        "informativ": "background-color: #e6f3ff; border-bottom: 2px solid blue; padding: 2px;"
    }
    
    # Evidențiază URL-uri suspecte
    import re
    for indicator in indicators:
        if indicator["tip"] == "URL suspect" and indicator["exemplu"]:
            url = indicator["exemplu"]
            url_pattern = re.escape(url)
            replacement = f'<span style="{highlight_styles["ridicat"]}" title="URL suspect: {indicator["detalii"]}">{url}</span>'
            highlighted_text = re.sub(url_pattern, replacement, highlighted_text)
    
    # Evidențiază fraze cu ton de urgență
    urgency_words = ["urgent", "imediat", "acum", "alertă", "atenție", "pericol", "expiră", "limitat"]
    for word in urgency_words:
        pattern = r'\b' + word + r'\b'
        replacement = f'<span style="{highlight_styles["mediu"]}" title="Ton de urgență: Poate indica o tentativă de phishing">{word}</span>'
        highlighted_text = re.sub(pattern, replacement, highlighted_text, flags=re.IGNORECASE)
    
    # Evidențiază solicitări de informații sensibile
    sensitive_phrases = [
        "introduceți parola", "confirmați datele", "actualizați informațiile", 
        "verificați contul", "introduceți codul", "datele cardului"
    ]
    
    for phrase in sensitive_phrases:
        if phrase.lower() in highlighted_text.lower():
            pattern = re.escape(phrase)
            replacement = f'<span style="{highlight_styles["ridicat"]}" title="Solicitare informații sensibile: Risc ridicat de phishing">{phrase}</span>'
            highlighted_text = re.sub(pattern, replacement, highlighted_text, flags=re.IGNORECASE)
    
    return highlighted_text
