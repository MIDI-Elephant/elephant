#!/usr/bin/python3

import sys, getopt

print(f"Before main, argv={sys.argv}")
sys.argv.pop(0)
print(f"Before main, arger pop, argv={sys.argv}")


def main(argv):
   inputfile = ''
   outputfile = ''
   print(f"In main, argv={argv}")
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print('test.py -i <inputfile> -o <outputfile>')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print('test.py -i <inputfile> -o <outputfile>')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg

   print(f"Input file is {inputfile}")
   print(f"Output file is {outputfile}")

if __name__ == "__main__":
   main(sys.argv[1:])
