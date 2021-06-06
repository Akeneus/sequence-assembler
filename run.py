from core import CoreAssambler
from doubleHelix import DoubleHelixAssambler
from substitution import SubstitutionAssambler

ca = CoreAssambler()
ca.run()

dha = DoubleHelixAssambler()
dha.run()

suba = SubstitutionAssambler()
suba.run()
