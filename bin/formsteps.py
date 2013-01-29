"""One-off program to generate tax forms until I learn the workflow."""

import re
import json
from collections import OrderedDict
from decimal import Decimal
from pyPdf import PdfFileWriter, PdfFileReader
from reportlab.pdfgen.canvas import Canvas
from StringIO import StringIO

from luca.forms.us import form_940
from luca.forms.us import form_941

integer_re = re.compile(r'\d+$')
decimal_re = re.compile(r'\d+\.\d+$')

class Form(object):
    def __init__(self):
        self.names = OrderedDict()

    def __setattr__(self, name, value):
        if name != 'names':
            self.names[name] = None
        self.__dict__[name] = value

def ordereddict_with_decimals(pairs):
    o = OrderedDict()
    for key, value in pairs:
        if isinstance(value, unicode) and decimal_re.match(value):
            value = Decimal(value)
        o[key] = value
    return o

form_decoder = json.JSONDecoder(
    object_pairs_hook=ordereddict_with_decimals,
    )

form_encoder = json.JSONEncoder(
    indent=1,
    separators=(',', ': '),
    default=unicode,
    )

if __name__ == '__main__':

    if True:
        jsonpath = 'taxforms/2012-us-Form-940.json'
        pdfpath = '/home/brandon/Downloads/f940.pdf'
        form_module = form_940

    else:
        jsonpath = 'taxforms/2013-01-US-Form-941.json'
        pdfpath = '/home/brandon/Downloads/f941.pdf'
        form_module = form_941

    with open(jsonpath) as f:
        data = form_decoder.decode(f.read())

    form = Form()
    for section, keyvalues in data.items():
        for key, value in keyvalues.items():
            if isinstance(value, float):
                value = Decimal('{:.2f}'.format(value))
            setattr(form, key, value)

    form_module.compute(form)

    data['outputs'] = OrderedDict(
        (name, getattr(form, name)) for name in form.names
        if name not in data['inputs']
        )

    json_string = form_encoder.encode(data)
    with open(jsonpath, 'w') as f:
        f.write(json_string)

    original_form = PdfFileReader(file(pdfpath, 'rb'))

    canvas = Canvas('fields.pdf')
    form_module.draw(form, canvas)
    overlays = PdfFileReader(StringIO(canvas.getpdfdata()))

    output = PdfFileWriter()

    for i in range(overlays.numPages):
        page = original_form.getPage(i)
        overlay = overlays.getPage(i)
        page.mergePage(overlay)
        output.addPage(page)

    with open('output.pdf', 'w') as f:
        output.write(f)
