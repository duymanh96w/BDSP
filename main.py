from src.data_loader import load_data
from test import Network


if __name__=='__main__':
    num_works, num_shifts, min_num_shifts, shifts = load_data(filename='c1')
    n = Network(num_works, num_shifts, shifts)