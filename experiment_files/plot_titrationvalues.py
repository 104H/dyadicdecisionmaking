import sys
import os
import json
import numpy as np
import matplotlib.pyplot as plt
   

def get_input():

    try:
        pair_id = int(sys.argv[1])
    except:
        print('Please enter a number as pair id:')
        pair_id = input()
        
    chamber = []
    if chamber == []:
        print("Enter chamber number (1 or 2):")
        chamber = input()
    elif chamber != 1 & chamber != 2:
        print("Wrong! Enter chamber number (1 or 2):")
        chamber = input()
    else:
        print("You already entered a chamber number! You entered:" + chamber)
        
    return pair_id, chamber
    

def get_titrationvalues(pair_id, chamber):

    filename = 'data_chamber' + str(chamber) + '.json'
    
    cur_path = os.getcwd()
    path = os.path.join(cur_path, 'data', str(pair_id), filename)
    
    if not os.path.exists(path):
        print('Error: No such file or directory for pair id ' + str(pair_id) + ' and chamber ' + str(chamber) + '!')
        sys.exit(0)
    else:
        # read file
        with open(path, 'r') as myfile:
            data = json.load(myfile)

    return data['threshold_list']
    
    
def plot_titrationvalues(values):

    x = np.arange(1, len(values)+1)
    
    ax = plt.plot(x, values)
    
    plt.xlabel('trial')
    plt.ylabel('titralion value')
    plt.show()
    
        
def main():
    pair_id, chamber = get_input()
    values = get_titrationvalues(pair_id, chamber)
    plot_titrationvalues(values)
   
   
if __name__ == "__main__":
    main()
