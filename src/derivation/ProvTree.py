#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, os, sys, time
import pydot

# ------------------------------------------------------ #
# import sibling packages HERE!!!
import DerivTree, GoalNode, RuleNode, FactNode, provTools

if not os.path.abspath( __file__ + "/../.." ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/.." ) )
from utils import tools

# **************************************** #

DEBUG       = tools.getConfig( "DERIVATION", "PROVTREE_DEBUG", bool )
IMGSAVEPATH = os.path.abspath( os.getcwd() ) + "/data"

# --------------------------------------------------- #

class ProvTree( ) :

  #############
  #  ATTRIBS  #
  #############
  rootname      = None
  subtrees      = None
  parsedResults = None
  cursor        = None


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, name, parsedResults, cursor ) :
    self.rootname      = name
    self.subtrees      = []
    self.parsedResults = parsedResults
    self.cursor        = cursor


  ######################
  #  IS ULTIMATE GOAL  #
  ######################
  # a convenience function
  # a provenance tree will never not be rooted
  # at "FinalState"
  def isFinalState( self ) :
    if self.rootname == "FinalState" :
      return True
    else :
      return False


  #############
  #  IS LEAF  #
  #############
  # a convenience function
  # a non-empty provenance tree will never be a leaf.
  def isLeaf( self ) :
    return False


  ########################
  #  GENERATE PROV TREE  #
  ########################
  # populates self.subtrees
  # DerivTree Constructor Fields : ( name, rid, treeType, isNeg, provAttMap, record, results, cursor )
  def generateProvTree( self, name, seedRecord ) :
    newSubTree = DerivTree.DerivTree( name, None, "goal", False, None, seedRecord, self.parsedResults, self.cursor )
    self.subtrees.append( newSubTree )


  #################
  #  MERGE TREES  #
  #################
  # old_provTree := a ProvTree instance
  def mergeTrees( self, old_provTree ) :

    # define structure of the new merged tree
    merged_name          = self.rootname
    merged_subtrees      = self.subtrees.extend( old_provTree.subtrees )
    merged_parsedResults = self.parsedResults.extend( old_provTree.parsedResults )
    merged_cursor        = self.cursor

    # instantiate new ProvTree
    provTree_merged = ProvTree( self.rootname, merged_name, merged_parsedResults, merged_cursor )

    # manually construct subtrees for new merged instance
    provTree_merged.subtrees = merged_subtrees

    sys.exit( "provTree_merged.subtrees = " + str(provTree_merged.subtrees) )

    return provTree_merged

 
  ##################
  #  CREATE GRAPH  #
  ##################
  # input list of prov trees (DerivTree instances)
  # save image file, no return value
  def createGraph( self, addNameInfo, iter_count ) :

    if DEBUG :
      print "... running createGraph ..."
      print "subtrees   = " + str( self.subtrees )
      print "iter_count = " + str( iter_count )
  
    graph = pydot.Dot( graph_type = 'digraph', strict=True ) # strict => ignore duplicate edges

    #path  = IMGSAVEPATH + "/provtree_render_" + str(time.strftime("%d-%m-%Y")) + "_" + str( time.strftime( "%H"+"hrs-"+"%M"+"mins-"+"%S" +"secs" )) + "_" + str(iter_count)
    path  = IMGSAVEPATH + "/provtree_render_" + str(iter_count)

    # example: add "_buggyGraph" to the end of the name
    if addNameInfo :
      path += "_" + addNameInfo

    nodes = []
    edges = []

    # add prov tree root
    provRootNode = pydot.Node( self.rootname, shape='doublecircle', margin=0 )
    nodes.append( provRootNode )

    for tree in self.subtrees :
      edges.append( pydot.Edge( provRootNode, provTools.createNode( tree.root ) ) )
      topology = tree.getTopology( )

      # node/edge postprocessing
      topology = self.processTopo( topology )

      nodes.extend( topology[0] )
      edges.extend( topology[1] )

    if DEBUG :
      print "... in createGraph :" 
      print "nodes : " + str(len(nodes))
      for i in range(0,len(nodes)) :
        print "node#" + str(i) + " : " + str(nodes[i])
      print "edges : " + str(len(edges))
      for i in range(0,len(edges)) :
        print "edge#" + str(i) + " : " + str(edges[i])
  
    # create graph
    # add nodes :
    for n in nodes :
      graph.add_node( n )
    # add edges
    for e in edges :
      graph.add_edge( e )

    print "Saving prov tree render to " + str(path)
    graph.write_png( path + ".png" )


  ##################
  #  PROCESS TOPO  #
  ##################
  def processTopo( self, topology ) :

    #print "topology    = " + str( topology )
    #print "topology[0] = " + str( topology[0] )
    #print "topology[1] = " + str( topology[1] )
    #for node in topology[0] :
    #  print str( node.get_name() )
    #for edge in topology[1] :
    #  print "src  = " + str( edge.get_source() )
    #  print "dest =" + str( edge.get_destination() )

    topology = self.suppressDomNodes( topology )

    return topology


  ########################
  #  SUPPRESS DOM NODES  #
  ########################
  def suppressDomNodes( self, topology ) :

    processed_nodeset = []
    processed_edgeset = []

    orig_nodeset = topology[0]
    orig_edgeset = topology[1]

    # nodes are pydot objects.
    # get_name also pulls quotation marks.
    for node in orig_nodeset :
      if not "dom_" in node.get_name()[1:5] :
        processed_nodeset.append( node )
      else :
        #print "<><><>deleted node " + str( node.get_name() )
        continue

    # edges are pydot objects.
    # get_source and get_destination also pull quotation marks.
    for edge in orig_edgeset :
      sourceNode      = edge.get_source()
      destinationNode = edge.get_destination()
      if not "dom_" in sourceNode[1:5] and not "dom_" in destinationNode[1:5] :
        processed_edgeset.append( edge )
      else :
        #print "<><><>deleted edge (" + sourceNode + "," + destinationNode + ")"
        continue

    return ( processed_nodeset, processed_edgeset )


  ##################
  #  GET EDGE SET  #
  ##################
  # grab the complete list of edges for a prov tree
  # use for equality comparisons
  def getEdgeSet( self ) :
    if DEBUG :
      print "... running getEdgeSet ..."
      print "subtrees = " + str( self.subtrees )

    edgeSet = []

    for tree in self.subtrees :
      edgeSet.append( ( self.rootname, str( tree.root ) ) )
      edgeSet.extend( tree.getTopology_edgeSet() )

    return edgeSet

#########
#  EOF  #
#########
