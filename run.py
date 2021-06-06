from core import CoreAssembler
from doubleHelix import DoubleHelixAssembler
from substitution import SubstitutionAssembler

k = 1

if input("Batch Execute(y/n): ") == 'y':
    k = 10

if input("Start and run CoreAssembler(y/n): ") == 'y':
    ca = CoreAssembler()
    result = ca.run(iterations=k)
    print(result + ':(' + str(len(result)) + ')')
    print(" ...finished")

if input("Start and run DoubleHelixAssembler(y/n): ") == 'y':
    dha = DoubleHelixAssembler()
    result = dha.run(iterations=k)
    print(result + ':(' + str(len(result)) + ')')
    print(" ...finished")

if input("Start and run SubstitutionAssembler(y/n): ") == 'y':
    suba = SubstitutionAssembler()
    result = suba.run(iterations=k)
    print(result + ':(' + str(len(result)) + ')')
    print(" ...finished")
