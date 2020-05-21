import argparse

parser = argparse.ArgumentParser(description='Deliverable for IAPR 2020 project.')

parser.add_argument('-i','--input', default='../data/robot_parcours_1.avi', help='Input video clip, should be .avi')
parser.add_argument('-o','--output', default='../data/robot_parcours_1_out.avi', help='output video clip (path and name), should be .avi')
parser.add_argument('-v','--verbose', action='store_true', default=False, help='Makes processing verbose and displays intermediate figures (execution stops when a figure is open)')

args = parser.parse_args()

print(args.verbose)
print(type(args.verbose))