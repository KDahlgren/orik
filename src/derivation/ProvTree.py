#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import inspect, logging, os, string, sys, time
import pydot

# ------------------------------------------------------ #
# import sibling packages HERE!!!
import DerivTree, GoalNode, RuleNode, FactNode, provTools
import SimpTree

if not os.path.abspath( __file__ + "/../../../lib/iapyx/src" ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../../../lib/iapyx/src" ) )
from utils import tools

# **************************************** #

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
  nodeset       = None
  edgeset       = None
  level         = 0
  serial_nodes   = []
  serial_edges   = []


  #################
  #  CONSTRUCTOR  #
  #################
  def __init__( self, name, parsedResults, cursor ) :
    self.rootname      = name
    self.subtrees      = []
    self.parsedResults = parsedResults
    self.cursor        = cursor


  ###############
  #  COPY TREE  #
  ###############
  def copyTree( self ) :

    newTree               = ProvTree( self.rootname, self.parsedResults, self.cursor )
    newTree.rootname      = self.rootname
    newTree.subtrees      = self.subtrees
    newTree.parsedResults = self.parsedResults
    newTree.cursor        = self.cursor
    newTree.nodeset       = self.nodeset
    newTree.edgeset       = self.edgeset

    return newTree


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


  ###################
  #  POPULATE TREE  #
  ###################
  def populateTree( self, post_eot ) :

    for seedRecord in post_eot :

      logging.debug( " ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^" )
      logging.debug( "           NEW POST RECORD" )
      logging.debug( "seedRecord = " + str( seedRecord ) )

      self.generateProvTree( "post", seedRecord )


  ########################
  #  GENERATE PROV TREE  #
  ########################
  # populates self.subtrees
  # DerivTree Constructor Fields : ( name, rid, treeType, isNeg, provAttMap, record, results, cursor )
  def generateProvTree( self, name, seedRecord ) :
    newSubTree = DerivTree.DerivTree( name, None, "goal", False, None, seedRecord, self.parsedResults, self.level, self.cursor )
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


  ##############################
  #  GENERATE TREE SIMPLIFIED  #
  ##############################
  # output a SimpTree object
  def generate_SimpTree( self ) :

    # ------------------------------------------------ #
    # grab the set of unique edges in the original
    # provenance tree.
    edges = self.getAllUniqueEdges()

    #tools.bp( __name__, inspect.stack()[0][3], "num unique edges = " + str( len(edges) ) )

    # ------------------------------------------------ #
    # model the edges in a SimpTree object.
    simpTree = SimpTree.SimpTree( None, edges )

    return simpTree


  ##########################
  #  GET ALL UNIQUE EDGES  #
  ##########################
  def getAllUniqueEdges( self ) :

    uniqueEdgeList = []

    # ---------------------------------------- #
    # use pydot to prep graph components
    edges = []

    provRootNode = pydot.Node( self.rootname, shape='doublecircle', margin=0 )

    for tree in self.subtrees :
      edges.append( pydot.Edge( provRootNode, provTools.createNode( tree.root ) ) )
      topology = tree.getTopology( )

      # node/edge postprocessing
      topology = self.processTopo( topology )

      edges.extend( topology[1] )

    clean_edgeList = []
    for edge in edges :
      src = edge.get_source()
      src = src.replace( "'", "" )
      src = src.replace( '"', "" )
      src = src.translate( None, string.whitespace )

      des = edge.get_destination()
      des = des.replace( "'", "" )
      des = des.replace( '"', "" )
      des = des.translate( None, string.whitespace )

      clean_edgeList.append( [ src, des ] )

    for e in clean_edgeList :
      if not self.isDuplicate( e, uniqueEdgeList ) :
        uniqueEdgeList.append( e )

    return uniqueEdgeList


  ##################
  #  IS DUPLICATE  #
  ##################
  def isDuplicate( self, edge, edgeList ) :

    flag = False
    for e in edgeList :
      src = e[0]
      des = e[1]

      if src == edge[0] and des == edge[1] :
        flag = True

    return flag

 
  ##################
  #  CREATE GRAPH  #
  ##################
  # save image file, no return value
  def createGraph( self, addNameInfo, fmla_index, iter_count, argDict ) :

    logging.debug( "... running createGraph ..." )
    logging.debug( "subtrees   = " + str( self.subtrees ) )
    logging.debug( "iter_count = " + str( iter_count ) )
  
    graph = pydot.Dot( graph_type = 'digraph', strict=True ) # strict => ignore duplicate edges

    #path  = IMGSAVEPATH + "/provtree_render_" + str(time.strftime("%d-%m-%Y")) + "_" + str( time.strftime( "%H"+"hrs-"+"%M"+"mins-"+"%S" +"secs" )) + "_" + str(iter_count)
    path  = IMGSAVEPATH + "/provtree_render_fmla" + str( fmla_index ) + "_iter" + str(iter_count)

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

    logging.debug( "... in createGraph :"  )
    logging.debug( "nodes : " + str(len(nodes)) )
    for i in range(0,len(nodes)) :
      logging.debug( "node#" + str(i) + " : " + str(nodes[i]) )
    logging.debug( "edges : " + str(len(edges)) )
    for i in range(0,len(edges)) :
      logging.debug( "edge#" + str(i) + " : " + str(edges[i]) )

    # set attributes
    self.nodeset = nodes
    self.edgeset = edges

    # <><><><><><><><><><><><><><><><><><><><><><> #
    # print an audit of tree nodes and edges
    logging.debug( "/////////////////////////" )
    logging.debug( "rootname is " + self.rootname )
    logging.debug( "num subtrees = " + str( len(self.subtrees) ) )
    logging.debug( "num nodes    = " + str( len(nodes) ) )
    logging.debug( "num edges    = " + str( len(edges) ) )

    #edgeCountMap = {}
    #for edge in self.edgeset :
    #  count = 0
    #  for e in self.edgeset :
    #    if e.to_string() == edge.to_string() :
    #      count += 1
    #  edgeCountMap[ edge.to_string() ] = count
    #for edge in edgeCountMap :
    #  print edge + " : " + str( edgeCountMap[edge] )

    #print "-----------------------"

    #countMap = {}
    #for node in self.nodeset :
    #  count = 0
    #  for n in self.nodeset :
    #    if n.to_string() == node.to_string() :
    #      count += 1
    #  countMap[ node.to_string() ] = count
    #for node in countMap :
    #  print node + " : " + str( countMap[node] )

    logging.debug( "/////////////////////////" )
    #tools.bp( __name__, inspect.stack()[0][3], "stophere" )
    # <><><><><><><><><><><><><><><><><><><><><><> #

    # -------------------------------------------------------- #
    # create graph png

    # add nodes :
    for n in nodes :
      graph.add_node( n )
    # add edges
    for e in edges :
      graph.add_edge( e )

    logging.info( "Saving prov tree render to " + str( path ) )
    graph.write_png( path + ".png" )
    #tools.bp( __name__, inspect.stack()[0][3], "sanity check graph before proceeding." )

    # -------------------------------------------------------- #
    # save graph data to file

    if tools.getConfig( argDict[ "settings" ], "DEFAULT", "SERIAL_GRAPH", bool ) == True :

      self.serial_nodes = []
      self.serial_edges = []

      serial_path  = IMGSAVEPATH + "/provtree_graph_data_fmla" + str( fmla_index ) + "_iter" + str(iter_count) + ".txt"
      logging.info( "Saving prov tree graph data to " + str( serial_path ) )

      fo = open( serial_path, "w" )

      fo.write( "[NODES]\n" )
      for n in nodes :
        serial_node = "pydot.Node(" + str( n.get_name() ) + ")\n"
        self.serial_nodes.append( serial_node )
        fo.write( serial_node )

      fo.write( "[EDGES]\n" )
      for e in edges :
        serial_edge = "pydot.Edge(" + str( e.get_source() ) + "," + str( e.get_destination() ) + "\n"
        self.serial_edges.append( serial_edge )
        fo.write( serial_edge )

      fo.close()


  ##################
  #  PROCESS TOPO  #
  ##################
  def processTopo( self, topology ) :

    logging.debug( "topology    = " + str( topology ) )
    logging.debug( "topology[0] = " + str( topology[0] ) )
    logging.debug( "topology[1] = " + str( topology[1] ) )
    for node in topology[0] :
      logging.debug( str( node.get_name() ) )
    for edge in topology[1] :
      logging.debug( "src  = " + str( edge.get_source() ) )
      logging.debug( "dest =" + str( edge.get_destination() ) )

    #topology = self.suppressDomNodes( topology )

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
      if not "goal->dom_" in node.get_name()[1:11] :
        processed_nodeset.append( node )
      else :
        #print "<><><>deleted node " + str( node.get_name() )
        continue

    # edges are pydot objects.
    # get_source and get_destination also pull quotation marks.
    for edge in orig_edgeset :
      sourceNode      = edge.get_source()
      destinationNode = edge.get_destination()
      if not "goal->dom_" in sourceNode[1:11] and not "goal->dom_" in destinationNode[1:11] :
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
    logging.debug( "... running getEdgeSet ..." )
    logging.debug( "subtrees = " + str( self.subtrees ) )

    edgeSet = []

    for tree in self.subtrees :
      edgeSet.append( ( self.rootname, str( tree.root ) ) )
      edgeSet.extend( tree.getTopology_edgeSet() )

    return edgeSet

#########
#  EOF  #
#########
