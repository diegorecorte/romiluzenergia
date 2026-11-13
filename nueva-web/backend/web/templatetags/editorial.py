from django import template
from django.template.defaultfilters import urlize,linebreaksbr
from django.utils.html import format_html,format_html_join
register=template.Library()
@register.filter
def editorial(value):
    blocks=[]
    for block in str(value).split('\n\n'):
        block=block.strip()
        if not block:continue
        if block.startswith('## '):blocks.append(format_html('<h2>{}</h2>',block[3:]))
        else:blocks.append(format_html('<p>{}</p>',linebreaksbr(urlize(block,autoescape=True),autoescape=True)))
    return format_html_join('\n','{}',((block,) for block in blocks))
