"""Apply the WAT 2027 CTA to a server copy while preserving local navigation edits."""
from pathlib import Path

path = Path("templates/navigation.html")
source = path.read_text()
style = """{% load static %}
<style>
#top-header-left-p3.wat-registration-link{display:inline-flex;align-items:center;min-height:32px;padding:5px 12px;border-radius:999px;background:#b50912;color:#fff!important;font-weight:700;text-decoration:none;white-space:nowrap}
#top-header-left-p3.wat-registration-link:hover{background:#93070e}
#ham-but-content .wat-registration-mobile a{display:block;margin:10px 16px;padding:14px 16px;border-radius:10px;background:#b50912;color:#fff;text-align:center;font-weight:700;text-decoration:none}
</style>
"""
if "wat-registration-link" not in source:
    if not source.startswith("{% load static %}\n"):
        raise RuntimeError("navigation header marker not found")
    source = source.replace("{% load static %}\n", style, 1)

old = """<a href="https://docs.google.com/forms/d/e/1FAIpQLSeqelCnUhkOrWtr7UJtpcKxIuBBfNsaRg4_JytT9lJGKqXt8Q/viewform"
               id="top-header-left-p3" target="_blank">Абонирай се</a>"""
new = """<a href="{% url 'wat 2027 registration' %}" id="top-header-left-p3" class="wat-registration-link">Регистрирай се за WAT 2027</a>"""
if old in source:
    source = source.replace(old, new, 1)
if new not in source:
    raise RuntimeError("desktop registration marker not found")

marker = """            <li>
                <a id="contacts" href="{% url 'contacts' %}">
                    <div class="main-element-header">
                        <p>Контакти</p>
                    </div>
                </a>
            </li>
"""
mobile = """            <li class="wat-registration-mobile">
                <a href="{% url 'wat 2027 registration' %}">Регистрирай се за WAT 2027</a>
            </li>
"""
if mobile not in source:
    if marker not in source:
        raise RuntimeError("mobile navigation marker not found")
    source = source.replace(marker, marker + mobile, 1)

path.write_text(source)
print("WAT_NAV_APPLIED")
