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
    body = email_data.get("body", "").replace("\n", "<br>") if "<br>" not in email_data.get("body", "") else email_data.get("body", "")
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
    
    # Construim corpul emailului cu suport pentru HTML
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
    
    <!-- Overlay tooltip JS -->
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const highlights = document.querySelectorAll('[title]');
        highlights.forEach(el => {
            el.style.position = 'relative';
            el.addEventListener('mouseover', function() {
                const tooltip = document.createElement('div');
                tooltip.innerText = this.getAttribute('title');
                tooltip.style.position = 'absolute';
                tooltip.style.bottom = '100%';
                tooltip.style.left = '0';
                tooltip.style.backgroundColor = '#333';
                tooltip.style.color = 'white';
                tooltip.style.padding = '5px 10px';
                tooltip.style.borderRadius = '4px';
                tooltip.style.fontSize = '12px';
                tooltip.style.zIndex = '1000';
                tooltip.style.whiteSpace = 'nowrap';
                this.appendChild(tooltip);
            });
            
            el.addEventListener('mouseout', function() {
                const tooltip = this.querySelector('div');
                if (tooltip) tooltip.remove();
            });
        });
    });
    </script>
    """
    
    # Combinăm toate componentele
    html = header_html + body_html + footer_html
    
    return html
