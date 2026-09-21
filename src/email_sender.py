import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
from config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
    h1 { color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }
    .paper { background: #f9f9f9; border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 30px; }
    .title { color: #2980b9; font-size: 1.2em; margin-top: 0; }
    .meta { color: #7f8c8d; font-size: 0.9em; margin-bottom: 15px; }
    .pi-box { background: #e8f4f8; border-left: 4px solid #3498db; padding: 10px 15px; margin: 15px 0; border-radius: 0 4px 4px 0; }
    .pi-name { font-weight: bold; color: #2c3e50; }
    .abstract { font-size: 0.95em; color: #444; }
    .links a { display: inline-block; background: #3498db; color: white; text-decoration: none; padding: 8px 15px; border-radius: 4px; font-size: 0.9em; margin-right: 10px; }
    .links a:hover { background: #2980b9; }
</style>
</head>
<body>
    <h1>Daily Mech Interp Drip 💧</h1>
    <p>Here are your curated papers for today, focusing on target faculty in Europe & NA.</p>
    
    {% for item in items %}
    <div class="paper">
        <h2 class="title">{{ item.paper.title }}</h2>
        <div class="meta">Published: {{ item.paper.publication_year }}</div>
        
        <div class="pi-box">
            <strong>Prospective PIs (Faculty/Senior):</strong>
            <ul>
            {% for pi in item.pis %}
                <li>
                    <span class="pi-name">{{ pi.display_name }}</span> 
                    ({{ pi.institution }}, {{ pi.country }}) - 
                    <em>Found {{ pi.paper_count }} paper(s) in DB</em> - 
                    <a href="{{ pi.openalex_id }}">OpenAlex Profile</a>
                </li>
            {% endfor %}
            </ul>
        </div>
        
        <div class="abstract">
            <strong>Abstract:</strong><br>
            {{ item.paper.abstract[:800] }}{% if item.paper.abstract|length > 800 %}...{% endif %}
        </div>
        
        <br>
        <div class="links">
            {% if item.paper.doi %}
            <a href="{{ item.paper.doi }}">Read Paper (DOI)</a>
            {% endif %}
            <a href="{{ item.paper.openalex_id }}">View on OpenAlex</a>
        </div>
    </div>
    {% endfor %}
    
    <p style="text-align: center; color: #999; font-size: 0.8em; margin-top: 40px;">
        Automated by your Agent via GitHub Actions.
    </p>
</body>
</html>
"""

def send_daily_email(items):
    if not items:
        logging.info("No items to send.")
        return False
        
    if not EMAIL_PASSWORD:
        logging.error("No EMAIL_PASSWORD configured. Cannot send email.")
        return False
        
    template = Template(HTML_TEMPLATE)
    html_content = template.render(items=items)
    
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Daily Mech Interp Drip - {len(items)} Papers ({timestamp})"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECIPIENT
    
    part = MIMEText(html_content, 'html')
    msg.attach(part)
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
        server.quit()
        logging.info(f"Successfully sent email to {EMAIL_RECIPIENT}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False
