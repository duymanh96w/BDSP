import os


def load_data(data_dir='./src/data/problems/', filename='t1'):
    with open(data_dir + filename) as f:
        data = f.readlines()
    
    num_works, num_shifts, min_num_shifts = [int(d) for d in data[0][:-1].split()]
    shifts = []
    for i in range(1, len(data)):
        s = [int(d) for d in data[i][:-1].split()]
        shifts.append(s)
    
    return num_works, num_shifts, min_num_shifts, shifts
