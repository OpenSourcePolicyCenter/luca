"""OFX institution FID codes."""

from .types import FinancialInstitution

db = {}

def add(*args):
    fi = FinancialInstitution(*args)
    db[fi.name] = fi

add('Chase Credit Cards', 'https://ofx.chase.com', 'B1', '10898')

add('Delta Community Credit Union',
    'https://appweb.deltacommunitycu.com/ofxroot/directtocore.asp',
    'decu.org', '3328')