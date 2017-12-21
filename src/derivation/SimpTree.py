#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, logging, os, string, sys

# ------------------------------------------------------ #
import SimpNode

# ------------------------------------------------------ #

if not os.path.abspath( __file__ + "/../../../lib/iapyx/src" ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../../../lib/iapyx/src" ) )

from utils import tools

# **************************************** #


class SimpTree( ) :

  ################
  #  ATTRIBUTES  #
  ################
  root              = None # an instance of SimpNode
  descendants_nodes = None # list of descendant nodes
  descendants_trees = None # list of descendant SimpTrees


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, rootObj, edgeList ) :

    self.root              = rootObj
    self.descendants_nodes = []
    self.descendants_trees = []

    self.populate_tree( edgeList )

    #print self.__str__()
    #if self.root.label == "FinalState" :
    #  tools.bp( __name__, inspect.stack()[0][3], "stuff" )


  #############
  #  __STR__  #
  #############
  def __str__( self ) :

    return_str  = ""
    return_str += "\n" 
    return_str += "========================\n"
    return_str += "        SIMPTREE\n"
    return_str += "root : \n"
    return_str += str( self.root ) + "\n"
    return_str += "descendants_nodes :" + "\n"

    for node in self.descendants_nodes :
      return_str += str( node ) + "\n"

    return_str += "========================\n"
    return_str += "\n"

    return return_str


  ###############################
  #  GET DESCENDANTS NODES ALL  #
  ###############################
  def get_descendants_nodes_all( self ) :

    if len( self.descendants_trees ) < 1 :
      return 1

    else :
      count = 0
      for d in self.descendants_trees :
        count += d.get_descendants_nodes_all()

      return count + 1


  ###################
  #  POPULATE TREE  #
  ###################
  # rootObj is a SimpNode
  # edgeList is an array of binary arrays mapping sources to destinations
  def populate_tree( self, edgeList ) :

    # ------------------------------------------ #
    # check if this is a new tree instantiation
    if self.root == None and self.containsFinalStates( edgeList ) :
      self.root = SimpNode.SimpNode( "FinalState", "goal", False )

    # ------------------------------------------ #
    # instantiate descendant nodes
    self.descendants_nodes = self.getDescendants_nodes( edgeList )

    # ------------------------------------------ #
    # remove edges with this root as src
    newEdgeList = self.getNewEdgeList( self.root.label, edgeList )

    # ------------------------------------------ #
    # build SimpTrees for all descendants
    for node in self.descendants_nodes :
      self.descendants_trees.append( SimpTree( node, newEdgeList ) )
      

  ###########################
  #  CONTAINS FINAL STATES  #
  ###########################
  def containsFinalStates( self, edgeList ) :

    flag = False

    for edge in edgeList :
      if edge[0] == "FinalState" :
        flag = True

    return flag


  ############################
  #  GET DEESCENDANTS NODES  #
  ############################
  def getDescendants_nodes( self, edgeList ) :

    # ------------------------------------------ #
    # collect descendant strings
    descList_strs = []
    for edge in edgeList :
      if edge[0] == self.root.label :
        descList_strs.append( edge[1] )

    # ------------------------------------------ #
    # create SimpNode objects for each descendant
    descList_nodes = []
    for desc in descList_strs :
      label    = desc
      data     = label.split( "->" )
      treeType = data[0]

      if "_NOT_" in label :
        isNeg = True
      else :
        isNeg = False

      descList_nodes.append( SimpNode.SimpNode( label, treeType, isNeg ) )

    return descList_nodes


  #######################
  #  GET NEW EDGE LIST  #
  #######################
  def getNewEdgeList( self, srcLabel, oldEdgeList ) :

    newEdgeList = []
    for edge in oldEdgeList :

      if not edge[0] == srcLabel :
        newEdgeList.append( edge )

    return newEdgeList


#########
#  EOF  #
#########
