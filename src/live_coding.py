import csv

file_path = 'PiE/bleatcode/static/desc.csv'
delimiter = '|'
carrier_return = "+-="


sheep_names = []
sheep_descs = []
sheep_bases = []
sheep_tests = []

#create an empty 2-D array
#rows, cols = (0,0)
#arr = [[0 for i in range(cols)] for j in range(rows)]

#read from csv file
with open(file_path, newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=delimiter)
    for row in spamreader:
        sheep_names.append(row[0])
        sheep_descs.append(row[1])
        sheep_bases.append(row[2])
        sheep_tests.append(row[3])


#csv file is now in each for loop

#replace
sheep_bases = [s.replace(carrier_return, "\n") for s in sheep_bases]
sheep_descs = [s.replace(carrier_return, "\n") for s in sheep_descs]

print(sheep_descs)