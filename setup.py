#!/usr/bin/env python

# based on https://github.com/KDahlgren/pyLDFI/blob/master/setup.py

import os, sys, time


##########
#  MAIN  #
##########
def main() :
  print "Running orik setup with args : \n" + str(sys.argv)

  # clean any existing libs
  os.system( "make clean" )

  # download submodules
  os.system( "make get-submodules" )

  os.system( "make c4" )
  os.system( "make iapyx" )


##############################
#  MAIN THREAD OF EXECUTION  #
##############################
if __name__ == "__main__" :
  main()


#########
#  EOF  #
#########
