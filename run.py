from core import CoreAssembler
from doubleHelix import DoubleHelixAssembler
from substitution import SubstitutionAssembler

BATCH_SIZE = 10
DEFAULT_FILE = "ressource/frag_a.dat"
DEFAULT_WEIGHT = 1

k = 1
plot = False

file_in = input("Enter path to .dat-file: ")
if file_in == '':
    file = DEFAULT_FILE
else:
    file = file_in

file_in = input("Enter min_weight: ")
if file_in == '':
    min_weight = DEFAULT_WEIGHT
else:
    min_weight = int(file_in)

if input("Batch Execute(y/n): ") == 'y':
    k = BATCH_SIZE

if input("Print Plot(y/n): ") == 'y':
    plot = True

if input("Start and run CoreAssembler(y/n): ") == 'y':
    ca = CoreAssembler(plot_flag=plot, min_weight=min_weight, path=file)
    results = ca.run(iterations=k)
    for result in results:
        print(result + ':(' + str(len(result)) + ') ')
    print(" ...finished")

if input("Start and run DoubleHelixAssembler(y/n): ") == 'y':
    dha = DoubleHelixAssembler(plot_flag=plot, min_weight=min_weight, path=file)
    results = dha.run(iterations=k)
    for result in results:
        print(result + ':(' + str(len(result)) + ') ')
    print(" ...finished")

if input("Start and run SubstitutionAssembler(y/n): ") == 'y':
    suba = SubstitutionAssembler(plot_flag=plot, min_weight=min_weight, path=file)
    results = suba.run(iterations=k)
    for result in results:
        print(result + ':(' + str(len(result)) + ') ')
    print(" ...finished")
