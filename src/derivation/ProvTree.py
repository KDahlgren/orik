#!/usr/bin/env python

# **************************************** #

#############
#  IMPORTS  #
#############
# standard python packages
import ConfigParser, copy, inspect, logging, os, string, sys, time
import pydot

# ------------------------------------------------------ #
# import sibling packages HERE!!!
import GoalNode, RuleNode, FactNode

if not os.path.abspath( __file__ + "/../../../lib/iapyx/src" ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../../../lib/iapyx/src" ) )

from utils import tools

# **************************************** #


# --------------------------------------------------- #

class ProvTree( object ) :

  #################
  #  CONSTRUCTOR  #
  #################
  # rootname      : string.       name of the relation at this root node.
  # parsedResults : dictionary.   contains all evaluation results keyed on relation names.
  # cursor        : object.       pointer to the IR database instance.
  # db_id         : integer.      identifier for rules/facts in the IR database.
  # treeType      : string.       "goal" | "rule" | "fact"
  # isNeg         : bool.         is this goal/fact negative?
  # provAttMap    : dictionary.   maps goal attributes to data from evaluation records.
  # record        : array.        a tuple of data from the evaluation results for some 
  #                               relation (hopefully this relation).
  # eot           : integer.      the eot for this execution.
  # parent        : ProvTree.     the ProvTree object instance connected to
  #                               this tree. None iff root is "FinalState".
  # argDict       : dictionary.   dictionary of the commandline/execution parameters/inputs.
  # pre_prov_recs : dictionary.   dictionary of arrays containing all previously considered 
  #                               provenance records per relation.            
  def __init__( self, rootname        = None, \
                      final_state_ptr = None, \
                      parsedResults   = {},   \
                      cursor          = None, \
                      db_id           = None, \
                      treeType        = None, \
                      isNeg           = None, \
                      provAttMap      = {},   \
                      record          = [],   \
                      eot             = 0,    \
                      parent          = None, \
                      argDict         = {},   \
                      img_save_path   = os.path.abspath( os.getcwd() ) + "/" , \
                      prev_prov_recs  = {} ) :

    self.img_save_path = img_save_path + argDict[ "data_save_path" ]
    if not os.path.isdir( self.img_save_path ) :
      raise Exception( "Image save path '" + self.img_save_path + "' does not exist. aborting." )

    # uninteresting boolean. indicates whether or not 
    # the provenance tree rooted at this node is interesting.
    # all provenance trees are initially interesting.
    # provenance trees become uninteresting if all descendant
    # provenance trees are uninteresting.
    self.uninteresting = False

    # dictionary of the execution arguments
    self.argDict = argDict

    # list of descendant ProvTree objects
    self.descendants = []

    # list of all descendant ProvTree objects
    self.all_descendant_objs = []

    # list of parent ProvTree objects
    self.parents = []

    # list of nodes in this ProvTree as pydot objects
    self.nodeset_pydot = []
    self.edgeset_pydot = []

    # list of nodes in this ProvTree in serialized format
    self.nodeset_pydot_str = []
    self.edgeset_pydot_str = []

    # the node object for the root of this ProvTree
    self.curr_node = None

    # FinalState also maintians a map of node names to object pointers.
    self.node_str_to_object_map = {}

    # set data from inputs
    self.rootname        = rootname
    self.final_state_ptr = final_state_ptr
    self.parsedResults   = parsedResults
    self.cursor          = cursor
    self.db_id           = db_id
    self.treeType        = treeType
    self.isNeg           = isNeg
    self.provAttMap      = provAttMap
    self.record          = record
    self.eot             = eot
    self.prev_prov_recs  = prev_prov_recs

    if not self.rootname == "FinalState" :
      self.parents.append( parent )

    logging.debug( "==================================" )
    logging.debug( "       CREATING NEW PROV TREE" )
    logging.debug( "self.rootname        = " + str( self.rootname ) )
    logging.debug( "self.final_state_ptr = " + str( self.final_state_ptr ) )
    #logging.debug( "self.parsedResults   = " + str( self.parsedResults ) )
    logging.debug( "self.cursor          = " + str( self.cursor ) )
    logging.debug( "self.db_id           = " + str( self.db_id ) )
    logging.debug( "self.treeType        = " + str( self.treeType ) )
    logging.debug( "self.isNeg           = " + str( self.isNeg ) )
    logging.debug( "self.provAttMap      = " + str( self.provAttMap ) )
    logging.debug( "self.record          = " + str( self.record ) )
    logging.debug( "self.eot             = " + str( self.eot ) )
    logging.debug( "self.parents         = " + str( self.parents ) )
    logging.debug( "self                 = " + str( self ) )
    #logging.debug( "self.prev_prov_recs  = " + str( self.prev_prov_recs ) )
    if False :
    #if not self.rootname == "FinalState" and self.final_state_ptr :
      logging.debug( "self.final_state_ptr.node_str_to_object_map = \n" + str( self.final_state_ptr.node_str_to_object_map ) )
      logging.debug( "==================================" )
    else :
      logging.debug( "==================================" )

    # for qa testing :
    if self.rootname == "__KD__TESTNODE__KD__" :
      self.generate_tree()
      return None

    # -------------------------------- #
    # CASE : node is the FinalState 
    #        root

    if self.rootname == "FinalState" :

      # set the final_state_ptr
      self.final_state_ptr = self
      logging.debug( "  set final_state_ptr to '" + str( self.final_state_ptr ) + "'" )

      # generate first level of nodes ( all post nodes )
      self.generate_tree()

    # -------------------------------- #
    # CASE : node is not the FinalState
    #        root

    else :
      self.generate_curr_node()
      if self.final_state_ptr :
        self.final_state_ptr.node_str_to_object_map[ self.__str__() ] = self # add this node to the final state map
        logging.debug( "  added '" + self.__str__() + "' to final_state_ptr.node_str_to_object_map" )
      self.generate_subtree()

    # -------------------------------- #
    # simplify by pruning uninteresting
    # branches

    try :
      TREE_SIMPLIFY = tools.getConfig( self.argDict[ "settings" ], "DEFAULT", "TREE_SIMPLIFY", bool )
    except ConfigParser.NoOptionError :
      TREE_SIMPLIFY = False
      logging.warning( "WARNING : no 'TREE_SIMPLIFY' defined in 'DEFAULT' section of " + \
                       self.argDict[ "settings" ] + "...running with TREE_SIMPLIFY==False." )
    logging.debug( "  PROV TREE : using TREE_SIMPLIFY = " + str( TREE_SIMPLIFY ) )
    if TREE_SIMPLIFY :
      self.tree_simplify()

    # -------------------------------- #
    if not self.rootname == "__TestNode__" :  # for qa tests

      if self.treeType == "goal" :
        logging.debug( "+>>>name=" + self.rootname )
        logging.debug( "self.curr_node.descendant_meta = " +str( self.curr_node.descendant_meta ) )

      # generate graph meta data for interesing nodes only
      if TREE_SIMPLIFY and not self.uninteresting :
        print "><><><>< HERERE"
        self.generate_graph_data()
      elif TREE_SIMPLIFY and self.uninteresting :
        logging.debug( "skipping generate_graph_data." )
      else :
        self.generate_graph_data()


  ###################
  #  TREE SIMPLIFY  #
  ###################
  # removes uninteresting descendants.
  # if all descendants are uninteresting,
  # then removes all descendants and sets
  # self.uninteresting as True.
  def tree_simplify( self ) :

    logging.debug( "  TREE SIMPLIFY : running process..." )
    logging.debug( "  TREE SIMPLIFY :  self.curr_node            => " + str( self.curr_node ) )
    logging.debug( "  TREE SIMPLIFY :  self.descendants()        => " + str( self.descendants ) )
    logging.debug( "  TREE SIMPLIFY :  len( self.descendants() ) => " + str( len( self.descendants ) ) )
    for d in self.descendants :
      logging.debug( "  TREE SIMPLIFY :   d = " + str( d ) )
    if not self.treeType == "fact" :
      logging.debug( "  TREE SIMPLIFY :  self.curr_node.descendant_meta() => " + str( self.curr_node.descendant_meta ) )
      logging.debug( "  TREE SIMPLIFY :  len( self.curr_node.descendant_meta() ) => " + str( len( self.curr_node.descendant_meta ) ) )
      for d in self.curr_node.descendant_meta :
        logging.debug( "  TREE SIMPLIFY :   d = " + str( d ) )

    if self.i_am_uninteresting() :
      self.wipe_all_descendants()
      self.uninteresting = True
    else :
      self.wipe_uninteresting_descendants()

    logging.debug( "  TREE SIMPLIFY :  self.i_am_uninteresting() => " + str( self.i_am_uninteresting() ) )
    logging.debug( "  TREE SIMPLIFY :  self.uninteresting()      => " + str( self.uninteresting ) )

    logging.debug( "  TREE SIMPLIFY : ...done." )


  ####################################
  #  WIPE UNINTERESTING DESCENDANTS  #
  ####################################
  # delete only uninteresting descendants from 
  # the descendant list.
  def wipe_uninteresting_descendants( self ) :

    logging.debug( "  WIPE UNINTERESTING DESCENDANTS : running process..." )
    logging.debug( "  WIPE UNINTERESTING DESCENDANTS : self.curr_node          = " + str( self.curr_node ) )
    logging.debug( "  WIPE UNINTERESTING DESCENDANTS : len( self.descendants ) = " + str( len( self.descendants ) ) )
    logging.debug( "  WIPE UNINTERESTING DESCENDANTS : self.descendants        : " )
    for d in self.descendants :
      logging.debug( d )

    if len( self.descendants ) < 1 :
      pass

    else :

      # -------------------------------------------------- #
      # gather all indexes for uninteresting descendants

      uninteresting_descendant_indexes = []
      for i in range( 0, len( self.descendants ) ) :
        if self.descendants[ i ].uninteresting == True :
          uninteresting_descendant_indexes.append( i )

      logging.debug( "  WIPE UNINTERESTING DESCENDANTS : " + \
                     "uninteresting_descendant_indexes = " + \
                     str( uninteresting_descendant_indexes ) )

      # -------------------------------------------------- #
      # perform descendant deletions
      # be sure to do the deletes in reverse order!

      if len( uninteresting_descendant_indexes ) >= 1 :
        deleted_descendant_meta = []
        for index in uninteresting_descendant_indexes[::-1] :
          if self.treeType == "goal" :
            logging.debug( "  WIPE UNINTERESTING : deleting descendant (1) : " + \
                           str( self.descendants[ index ] ) + \
                           ", rid = " + str( self.descendants[ index ].curr_node.rid ) )
            deleted_descendant_meta.append( [ self.descendants[ index ].curr_node.rid, self.descendants[ index ].curr_node.record ] )
          else :
            logging.debug( "  WIPE UNINTERESTING : deleting descendant (2) : " + \
                           str( self.descendants[ index ] ) )
            deleted_descendant_meta.append( [ self.descendants[ index ].curr_node.treeType, self.descendants[ index ].curr_node.isNeg, self.descendants[ index ].curr_node.record, self.descendants[ index ].curr_node.name ] )
          del self.descendants[ index ]
          logging.debug( "  WIPE UNINTERESTING : self.descendants:" )
          for d in self.descendants :
            logging.debug( "    " + str( d ) )

        # -------------------------------------------------- #
        # perform descendant meta deletions

        logging.debug( "  WIPE UNINTERESTING DESCENDANTS : self.curr_node.descendant_meta = " + \
                       str( self.curr_node.descendant_meta ) )
        logging.debug( "  WIPE UNINTERESTING DESCENDANTS : deleted_descendant_meta = " + str( deleted_descendant_meta ) )

        if self.treeType == "goal" :
          for ddm in deleted_descendant_meta :
            rid    = ddm[ 0 ]
            record = ddm[ 1 ]
            for cndm in self.curr_node.descendant_meta :
              logging.debug( "  WIPE UNINTERESTING DESCENDANTS : considering " + \
                             "self.curr_node.descendant_meta[ " + \
                             str( cndm ) + " ] = " + \
                             str( self.curr_node.descendant_meta[ cndm ] ) )
              logging.debug( "  WIPE UNINTERESTING DESCENDANTS : " + str( cndm ) + \
                             " == " + str( rid ) + " = " + str( cndm == rid ) )
              if cndm == rid :
                tmp_meta        = copy.deepcopy( self.curr_node.descendant_meta[ cndm ] )
                tmp_triggerData = tmp_meta[ "triggerData" ]
                new_triggerData = []
                for trig in tmp_triggerData :
                  if not trig == record :
                    new_triggerData.append( trig )
                tmp_meta[ "triggerData" ] = new_triggerData
                self.curr_node.descendant_meta[ cndm ] = copy.deepcopy( tmp_meta )
        else :
          tmp_descendant_meta = []
          for cndm in self.curr_node.descendant_meta :
            flag = False
            for ddm in deleted_descendant_meta :
              if self.structures_are_equal( cndm, ddm ) :
                flag = True
            if not flag : # cndm does not appear in ddm list
              tmp_descendant_meta.append( cndm )
              logging.debug( "  WIPE ALL UNINTERESTING DESCENDANTS : added " + str( cndm ) + " to tmp_descendant_meta"  )

          self.curr_node.descendant_meta = copy.deepcopy( tmp_descendant_meta )

      logging.debug( "  WIPE UNINTERESTING DESCENDANTS : deleted " + \
                     str( len( uninteresting_descendant_indexes ) ) + " descendants" )
      logging.debug( "  WIPE UNINTERESTING DESCENDANTS : remaining len( self.descendants ) = " + \
                     str( len( self.descendants ) ) )
      for d in self.descendants :
        logging.debug( "  WIPE UNINTERESTING DESCENDANTS : d = " + str( d ) )
      logging.debug( "  WIPE UNINTERESTING DESCENDANTS : remaining len( self.curr_node.descendant_meta ) = " + \
                     str( len( self.curr_node.descendant_meta ) ) )
      for d in self.curr_node.descendant_meta :
        logging.debug( "  WIPE UNINTERESTING DESCENDANTS : d = " + str( d ) )

    logging.debug( "  WIPE UNINTERESTING DESCENDANTS : ...done." )


  ##########################
  #  STRUCTURES ARE EQUAL  #
  ##########################
  def structures_are_equal( self, cndm, ddm ) :

    cndm_treeType = cndm[ "treeType" ]
    if cndm[ "polarity" ] == "" :
      cndm_isNeg = False
    else :
      cndm_isNeg = True
    cndm_record   = cndm[ "triggerRecord" ]
    cndm_name     = cndm[ "node_name" ]
    logging.debug( "  STRUCTURES ARE EQUAL : cndm_treeType = " + cndm_treeType )
    logging.debug( "  STRUCTURES ARE EQUAL : cndm_isNeg    = " + str( cndm_isNeg ) )
    logging.debug( "  STRUCTURES ARE EQUAL : cndm_record   = " + str( cndm_record ) )
    logging.debug( "  STRUCTURES ARE EQUAL : cndm_name     = " + cndm_name )

    ddm_treeType = ddm[ 0 ]
    ddm_isNeg    = ddm[ 1 ]
    ddm_record   = ddm[ 2 ]
    ddm_name     = ddm[ 3 ]
    logging.debug( "  STRUCTURES ARE EQUAL : ddm_treeType = " + ddm_treeType )
    logging.debug( "  STRUCTURES ARE EQUAL : ddm_isNeg    = " + str( ddm_isNeg ) )
    logging.debug( "  STRUCTURES ARE EQUAL : ddm_record   = " + str( ddm_record ) )
    logging.debug( "  STRUCTURES ARE EQUAL : ddm_name     = " + ddm_name )

    if cndm_treeType == ddm_treeType and \
       cndm_isNeg    == ddm_isNeg    and \
       cndm_record   == ddm_record   and \
       cndm_name     == ddm_name :
      return True
    else :
      return False


  ##########################
  #  WIPE ALL DESCENDANTS  #
  ##########################
  # set descendant list to empty
  def wipe_all_descendants( self ) :
    logging.debug( "  WIPE ALL DESCENDANTS : running process..." )

    logging.debug( "  WIPE ALL DESCENDANTS : len( self.descendants ) = " + str( len( self.descendants ) ) )
    self.descendants               = copy.deepcopy( [] )
    logging.debug( "  WIPE ALL DESCENDANTS : len( self.descendants ) = " + str( len( self.descendants ) ) )

    if not self.treeType == "fact" :
      logging.debug( "  WIPE ALL DESCENDANTS : len( self.curr_node.descendant_meta ) = " + \
                     str( len( self.curr_node.descendant_meta ) ) )
      self.curr_node.descendant_meta = copy.deepcopy( [] )
      logging.debug( "  WIPE ALL DESCENDANTS : len( self.curr_node.descendant_meta ) = " + \
                     str( len( self.curr_node.descendant_meta ) ) )

    logging.debug( "  WIPE ALL DESCENDANTS : ...done." )



  ########################
  #  I AM UNINTERESTING  #
  ########################
  # a prov tree is uninteresting if all immediate descendants
  # are uninteresting.
  def i_am_uninteresting( self ) :

    logging.debug( "  I AM UNINTERESTING : running process..." )

    # facts are only as interesting as they are uninteresting.
    if self.treeType == "fact" :
      logging.debug( "  I AM UNINTERESTING : fact, returning " + str( self.uninteresting ) )
      return self.uninteresting

    # goals and rules are uninteresting if they have no descendants
    elif len( self.descendants ) < 1 :
      logging.debug( "  I AM UNINTERESTING : len( self.descendants ) < 1 is true:" + str( len( self.descendants ) ) )
      logging.debug( "  I AM UNINTERESTING : returning True" )
      return True

    else :
      num_uninteresting_descendants = 0 # optimism!
      for d in self.descendants :
        if d.uninteresting :
          num_uninteresting_descendants += 1
      logging.debug( "  I AM UNINTERESTING : num_uninteresting_descendants = " + str( num_uninteresting_descendants ) )
      if num_uninteresting_descendants == len( self.descendants ) :
        logging.debug( "  I AM UNINTERESTING : returning True" )
        return True
      else :
        logging.debug( "  I AM UNINTERESTING : returning False" )
        return False


  #########
  #  STR  #
  #########
  def __str__( self ) :

    if self.curr_node :
      return self.curr_node.__str__()

    else :
      return self.rootname + " : curr_node not set."


  ########################
  #  CREATE PYDOT GRAPH  #
  ########################
  # generate the pydot graph visualization and
  # return a dictionary of stats.
  # observe the FinalState prov tree contains the
  # nodeset_pydot and edgeset_pydot structures.
  # only call this function on a FinalState ProvTree
  def create_pydot_graph( self, fmla_index, iter_count, additional_str ) :

    if not self.rootname == "FinalState" :
      tools.bp( __name__, inspect.stack()[0][3], "  FATAL ERROR : calling create_pydot_graph on non-FinalState. aborrting." )

    # -------------------------------- #
    # generate and output pydot graph

    #graph           = pydot.Dot( graph_type = 'digraph', strict=True ) # strict => ignore duplicate edges
    graph           = pydot.Dot( graph_type = 'digraph' ) # strict => ignore duplicate edges
    graph_save_path = self.img_save_path + "/provtree_render_fmla" + str( fmla_index ) + "_iter" + str(iter_count)
    if additional_str :
      graph_save_path += additional_str

    for n in self.nodeset_pydot :
      logging.debug( "  CREATE PYDOT GRAPH : adding node " + n.get_name() + " to nodeset"  )
      graph.add_node( n )

    for e in self.edgeset_pydot :
      logging.debug( "  CREATE PYDOT GRAPH : adding edge (" + e.get_source() + ", " + e.get_destination() + ") to nodeset"  )
      graph.add_edge( e )

    logging.info( "Saving prov tree render to " + str( graph_save_path + ".png" ), )
    graph.write_png( graph_save_path + ".png" )
    logging.debug( "...done." )

    # -------------------------------- #
    # generate stats about the graph

    graph_stats                = {}
    graph_stats[ "num_nodes" ] = len( self.nodeset_pydot )
    graph_stats[ "num_edges" ] = len( self.edgeset_pydot )

    #try :
    if tools.getConfig( self.argDict[ "settings" ], "DEFAULT", "SERIAL_GRAPH", bool ) == True :
      self.save_serial_graph( fmla_index, iter_count, additional_str )
    #except KeyError :
    #  logging.info( "not outputting graph data." )

    return graph_stats


  #######################
  #  SAVE SERIAL GRAPH  #
  #######################
  # save the nodes and edges of the graph to file.
  def save_serial_graph( self, fmla_index, iter_count, additional_str ) :

      if additional_str :
        serial_path  = self.img_save_path + "/provtree_graph_data_fmla" + str( fmla_index ) + "_iter" + str(iter_count) + "_" + additional_str + ".txt"
      else :
        serial_path  = self.img_save_path + "/provtree_graph_data_fmla" + str( fmla_index ) + "_iter" + str(iter_count) + ".txt"
      logging.info( "Saving prov tree graph data to " + str( serial_path ), )

      fo = open( serial_path, "w" )

      fo.write( "[NODES]\n" )
      for n in self.final_state_ptr.nodeset_pydot_str :
        fo.write( n + "\n" )

      fo.write( "[EDGES]\n" )
      for e in self.final_state_ptr.edgeset_pydot_str :
        fo.write( e + "\n" )

      fo.close()

      logging.debug( "...done." )


  #########################
  #  GENERATE GRAPH DATA  #
  #########################
  # generate the data necessary to represent this ProvTree
  # in a pydot graph.
  def generate_graph_data( self ) :

    logging.debug( "  GENERATE GRAPH DATA : running process..." )
    logging.debug( "  GENERATE GRAPH DATA : self          = " + str( self ) )
    logging.debug( "  GENERATE GRAPH DATA : self.rootname = " + self.rootname )
    logging.debug( "  GENERATE GRAPH DATA : self.treeType = " + self.treeType )

    # -------------------------------- #
    # build node
    this_node_pydot     = self.create_pydot_node( self.__str__(), self.curr_node.treeType )
    this_node_pydot_str = self.get_pydot_str( this_node_pydot )

    logging.debug( "  GENERATE GRAPH DATA : this_node_pydot_str = " + this_node_pydot_str )

    # add to final_state accumulation structure
    self.final_state_ptr.nodeset_pydot.append( this_node_pydot )
    self.final_state_ptr.nodeset_pydot_str.append( this_node_pydot_str )

    # -------------------------------- #
    # handle FinalState

    if self.rootname == "FinalState" :

      for d in self.descendants :

        goalName = d.rootname
        rec      = d.record

        descendant_str        = "goal->" + goalName + "(" + str( rec ) + ")"
        descendant_node_pydot = self.create_pydot_node( descendant_str, "goal" )
        this_edge_pydot       = self.create_pydot_edge( this_node_pydot, descendant_node_pydot )
        this_edge_pydot_str   = self.get_pydot_str( this_edge_pydot )

        logging.debug( "  GENERATE GRAPH DATA : adding this_edge_pydot_str = " + this_edge_pydot_str )

        self.final_state_ptr.edgeset_pydot.append( this_edge_pydot )
        self.final_state_ptr.edgeset_pydot_str.append( this_edge_pydot_str )

    else :

      # -------------------------------- #
      # build edges
      # use descendant meta data to build pydot edges 
      # between the current node and descendant nodes 
      # w/o requiring the generation of ProvTree objects 
      # for the descendants.

      # CASE : this is a goal node
      #        spawn rules only.
      if self.treeType == "goal" :

        logging.debug( "-------------------------------------------------------------------------------" )
        logging.debug( "  GENERATE GRAPH DATA : not a final state. using curr_node.descendant_meta:" )
        for prov_id in self.curr_node.descendant_meta :
          d_meta = self.curr_node.descendant_meta[ prov_id ]
          logging.debug( "  GENERATE GRAPH DATA : d_meta = " + str( d_meta ) )
        logging.debug( "-------------------------------------------------------------------------------" )


        for prov_id in self.curr_node.descendant_meta :
          d_meta = self.curr_node.descendant_meta[ prov_id ]
          logging.debug( "  GENERATE GRAPH DATA : d_meta = " + str( d_meta ) )

          goalName    = d_meta[ "goalName" ]
          triggerData = d_meta[ "triggerData" ]

          # need one rule descendant per provenance trigger
          for rec in triggerData :

            descendant_str        = "rule->" + goalName + "(" + str( rec ) + ")"
            descendant_node_pydot = self.create_pydot_node( descendant_str, "goal" )
            this_edge_pydot       = self.create_pydot_edge( this_node_pydot, descendant_node_pydot )
            this_edge_pydot_str   = self.get_pydot_str( this_edge_pydot )

            self.final_state_ptr.edgeset_pydot.append( this_edge_pydot )
            self.final_state_ptr.edgeset_pydot_str.append( this_edge_pydot_str )

            logging.debug( "  GENERATE GRAPH DATA : adding this_edge_pydot_str = " + this_edge_pydot_str )

      # CASE : this is a rule node
      #        spawn goals or facts only.
      elif self.treeType == "rule" :

        logging.debug( "-------------------------------------------------------------------------------" )
        logging.debug( "  GENERATE GRAPH DATA : not a final state. using curr_node.descendant_meta:" )
        for d_meta in self.curr_node.descendant_meta :
          logging.debug( "  GENERATE GRAPH DATA : d_meta = " + str( d_meta ) )
        logging.debug( "-------------------------------------------------------------------------------" )

        for d_meta in self.curr_node.descendant_meta :
          logging.debug( "  GENERATE GRAPH DATA : d_meta = " + str( d_meta ) )

          descendant_goalName      = d_meta[ "node_name" ]
          descendant_polarity      = d_meta[ "polarity" ]
          descendant_triggerRecord = d_meta[ "triggerRecord" ]
          descendant_treeType      = d_meta[ "treeType" ]

          if descendant_treeType == "goal" :
            if descendant_polarity == "notin" :
              descendant_str = "goal->" + "_NOT_" + descendant_goalName + "(" + str( descendant_triggerRecord ) + ")"
            else :
              descendant_str = "goal->" + descendant_goalName + "(" + str( descendant_triggerRecord ) + ")"
            descendant_node_pydot = self.create_pydot_node( descendant_str, "goal" )

            # need this shit in both locations???
            this_edge_pydot     = self.create_pydot_edge( this_node_pydot, descendant_node_pydot )
            this_edge_pydot_str = self.get_pydot_str( this_edge_pydot )
            self.final_state_ptr.edgeset_pydot.append( this_edge_pydot )
            self.final_state_ptr.edgeset_pydot_str.append( this_edge_pydot_str )

            logging.debug( "  GENERATE GRAPH DATA : adding this_edge_pydot_str = " + this_edge_pydot_str )

          else : # is a fact
            if descendant_polarity == "notin" :
              descendant_str = "fact->" + "_NOT_" + descendant_goalName + "(" + str( descendant_triggerRecord ) + ")"
            else :
              descendant_str = "fact->" + descendant_goalName + "(" + str( descendant_triggerRecord ) + ")"
            descendant_node_pydot = self.create_pydot_node( descendant_str, "fact" )

            this_edge_pydot     = self.create_pydot_edge( this_node_pydot, descendant_node_pydot )
            this_edge_pydot_str = self.get_pydot_str( this_edge_pydot )
            self.final_state_ptr.edgeset_pydot.append( this_edge_pydot )
            self.final_state_ptr.edgeset_pydot_str.append( this_edge_pydot_str )
            logging.debug( "  GENERATE GRAPH DATA : adding this_edge_pydot_str = " + this_edge_pydot_str )

    logging.debug( "  GENERATE GRAPH DATA : ...done." )


  ######################
  #  GENERATE SUBTREE  #
  ######################
  # spawn prov trees on descendant nodes
  # do not generate new subtrees from descendants if the descendant 
  # already exists in the graph
  def generate_subtree( self ) :

    # -------------------------------- #
    # CASE : this tree is a goal. 
    #        goals spawn rules only.
    #
    # node descendant meta :
    # { prov_rid : { goalName    : <string>,
    #                triggerData : <array of strings/ints> }, ... }

    if self.treeType == "goal" :

      # iterate over provenance rules
      for prov_rid in self.curr_node.descendant_meta :

        # iterate over the trigger records from the provenance
        for trig_rec in self.curr_node.descendant_meta[ prov_rid ][ "triggerData" ] :

          # CASE : yes wildcards in the trigger record
          if self.is_wildcard_record( trig_rec ) :
            raise Exception( "Holy shit, you've got wildcards in the trigger record. aborting." )

          # CASE : no wildcards in the trigger record
          else :
            goalName    = self.curr_node.descendant_meta[ prov_rid ][ "goalName" ]
            polarity    = None
            subtreeType = "rule"

            # update list of previously considered provenance records
            if goalName in self.prev_prov_recs :
              self.prev_prov_recs[ goalName ].append( trig_rec )
            else :
              self.prev_prov_recs[ goalName ] = [ trig_rec ]
            #logging.debug( "  GENERATE SUBTREE : added '" + str( trig_rec ) + "' to prev_prov_recs:\n" + str( self.prev_prov_recs ) )

            # do not create another ProvTree for the descendant if the descendant already exists.
            # just update the existing node's parents.
            # keep the meta data for when generating graph edges, though.
            if self.already_incorporated_into_graph( goalName, polarity, trig_rec, subtreeType ) :

              # get descendant meta
              descendant_node_str = self.get_node_string( goalName, polarity, trig_rec, subtreeType )
              existing_descendant = self.final_state_ptr.node_str_to_object_map[ descendant_node_str ]

              # add to all descendants
              self.all_descendant_objs.append( self.get_already_incorporated_ptr( goalName, \
                                                                                  polarity, \
                                                                                  trig_rec, \
                                                                                  subtreeType ) )

              # update parents of existing descendant
              if existing_descendant.treeType == "rule" :
                pass # not applicable on rules because rules can have only one parent.
              else :
                existing_descendant.parents.append( self )

            else :
  
              #goalName    = self.curr_node.descendant_meta[ prov_rid ][ "goalName"    ]
              #triggerData = self.curr_node.descendant_meta[ prov_rid ][ "triggerData" ]
  
              #for record in triggerData :
  
              new_subtree = ProvTree( rootname        = goalName, \
                                      final_state_ptr = self.final_state_ptr, \
                                      parsedResults   = self.parsedResults, \
                                      cursor          = self.cursor, \
                                      db_id           = prov_rid, \
                                      treeType        = "rule", \
                                      record          = trig_rec, \
                                      parent          = self, \
                                      argDict         = self.argDict, \
                                      prev_prov_recs  = {}, \
                                      eot             = self.eot )
                                      #prev_prov_recs  = self.prev_prov_recs )
 
              self.all_descendant_objs.append( new_subtree )
              self.descendants.append( new_subtree )


    # -------------------------------- #
    # CASE : this tree is a rule. 
    #        rules spawn goals or facts.
    #
    # node descendant meta :
    # [ { 'treeType'      : "goal" | "fact",
    #     'node_name'     : <string>,
    #     'triggerRecord' : <string>,
    #     'polarity'      : "notin" | "",
    #   }, ... ]

    elif self.treeType == "rule" :

      logging.debug( "  GENERATE SUBTREE : self.rootname = " + self.rootname )

      tmp_curr_node_descendant_meta = []
      for d_meta in self.curr_node.descendant_meta :

        logging.debug( "  GENERATE SUBTREE : d_meta = " + str( d_meta ) )

        goalName    = d_meta[ "node_name" ]
        polarity    = d_meta[ "polarity" ]
        subtreeType = d_meta[ "treeType" ]
        trig_rec    = d_meta[ "triggerRecord" ]

        # do not create another ProvTree for the descendant if the descendant already exists.
        # just update the existing node's parents.
        # keep the meta data for when generating graph edges, though.
        if self.already_incorporated_into_graph( goalName, polarity, trig_rec, subtreeType ) :

          # get descendant meta
          descendant_node_str = self.get_node_string( goalName, polarity, trig_rec, subtreeType )
          existing_descendant = self.final_state_ptr.node_str_to_object_map[ descendant_node_str ]

          # update parents of existing descendant
          existing_descendant.parents.append( self )

          # add the pointer to the set of actual_descendants
          self.all_descendant_objs.append( self.get_already_incorporated_ptr( goalName, \
                                                                              polarity, \
                                                                              trig_rec, \
                                                                              subtreeType ) )

        else :

          if polarity == "notin" :
            isNeg = True
          else :
            isNeg = False
  
          # CASE : spawn a goal
          if subtreeType == "goal" :
            new_subtree = ProvTree( rootname        = goalName, \
                                    final_state_ptr = self.final_state_ptr, \
                                    parsedResults   = self.parsedResults, \
                                    cursor          = self.cursor, \
                                    treeType        = "goal", \
                                    record          = trig_rec, \
                                    isNeg           = isNeg, \
                                    parent          = self, \
                                    argDict         = self.argDict, \
                                    eot             = self.eot, \
                                    prev_prov_recs  = self.prev_prov_recs )
  
          # CASE : spawn a fact
          elif subtreeType == "fact" :
            new_subtree = ProvTree( rootname        = goalName, \
                                    final_state_ptr = self.final_state_ptr, \
                                    parsedResults   = self.parsedResults, \
                                    cursor          = self.cursor, \
                                    treeType        = "fact", \
                                    record          = trig_rec, \
                                    isNeg           = isNeg, \
                                    parent          = self, \
                                    argDict         = self.argDict, \
                                    prev_prov_recs  = {}, \
                                    eot             = self.eot )
  
          # CASE : wtf??? 
          else :
            tools.bp( __name__, inspect.stack()[0][3], "  FATAL ERROR : treeType not recognized '" + treeType + "'" )
  
          self.all_descendant_objs.append( new_subtree )
          self.descendants.append( new_subtree )
          tmp_curr_node_descendant_meta.append( d_meta ) # collects all not already incorporated nodes

      # remove already incorporated nodes from curr_node meta data, too
      # removes recursive paths.
      #self.curr_node.descendant_meta = copy.deepcopy( tmp_curr_node_descendant_meta )

    # -------------------------------- #
    # CASE : this tree is a fact. 
    #        facts spawn nothing.

    else :
      pass



  ########################
  #  IS WILDCARD RECORD  #
  ########################
  # check if the input record contains a wildcard.
  # return boolean.
  def is_wildcard_record( self, trig_rec ) :
    logging.debug( "  IS WILDCARD RECORD : trig_rec = " + str( trig_rec ) )

    if "_" in trig_rec :
      logging.debug( "  IS WILDCARD RECORD : returning True" )
      return True
    else :
      logging.debug( "  IS WILDCARD RECORD : returning False" )
      return False


  #####################################
  #  ALREADY INCORPORATED INTO GRAPH  #
  #####################################
  # check if the descendant node already exists in the graph
  def already_incorporated_into_graph( self, goalName, polarity, trig_rec, subtreeType ) :

    logging.debug( "  ALREADY INCORPORATED INTO GRAPH : running process..." )
    logging.debug( "  ALREADY INCORPORATED INTO GRAPH : goalName    = " + goalName )
    logging.debug( "  ALREADY INCORPORATED INTO GRAPH : polarity    = " + str( polarity ) )
    logging.debug( "  ALREADY INCORPORATED INTO GRAPH : trig_rec    = " + str( trig_rec ) )
    logging.debug( "  ALREADY INCORPORATED INTO GRAPH : subtreeType = " + subtreeType )
    #logging.debug( "  ALREADY INCORPORATED INTO GRAPH : self.final_state_ptr.node_str_to_object_map = " + \
    #                  str( self.final_state_ptr.node_str_to_object_map ) )

    flag = False

    if subtreeType == "rule" :
      rule_str_to_check = self.get_node_string( goalName, polarity, trig_rec, subtreeType )
      logging.debug( "  ALREADY INCORPORATED INTO GRAPH : rule_str_to_check = " + rule_str_to_check )
      if rule_str_to_check in self.final_state_ptr.node_str_to_object_map :
        flag = True

    elif subtreeType == "goal" :
      goal_str_to_check = self.get_node_string( goalName, polarity, trig_rec, subtreeType )
      logging.debug( "  ALREADY INCORPORATED INTO GRAPH : goal_str_to_check = " + goal_str_to_check )
      if goal_str_to_check in self.final_state_ptr.node_str_to_object_map :
        flag = True

    elif subtreeType == "fact" :
      fact_str_to_check = self.get_node_string( goalName, polarity, trig_rec, subtreeType )
      logging.debug( "  ALREADY INCORPORATED INTO GRAPH : fact_str_to_check = " + fact_str_to_check )
      if fact_str_to_check in self.final_state_ptr.node_str_to_object_map :
        flag = True

    else :
      tools.bp( __name__, inspect.stack()[0][3], "  FATAL ERROR : unrecognized descendant type '" + subtreeType + "'" )

    logging.debug( "  ALREADY INCORPORATED INTO GRAPH : returning " + str( flag ) )

    return flag


  ##################################
  #  GET ALREADY INCORPORATED PTR  #
  ##################################
  # check if the descendant node already exists in the graph
  def get_already_incorporated_ptr( self, goalName, polarity, trig_rec, subtreeType ) :

    logging.debug( "  ALREADY INCORPORATED PTR : running process..." )
    logging.debug( "  ALREADY INCORPORATED PTR : goalName    = " + goalName )
    logging.debug( "  ALREADY INCORPORATED PTR : polarity    = " + str( polarity ) )
    logging.debug( "  ALREADY INCORPORATED PTR : trig_rec    = " + str( trig_rec ) )
    logging.debug( "  ALREADY INCORPORATED PTR : subtreeType = " + subtreeType )

    if subtreeType == "goal" or subtreeType == "rule" or subtreeType == "fact" :
      existing_str = self.get_node_string( goalName, polarity, trig_rec, subtreeType )
      logging.debug( "  ALREADY INCORPORATED PTR : existing_str = " + existing_str )
      return self.final_state_ptr.node_str_to_object_map[ existing_str ]

    else :
      tools.bp( __name__, inspect.stack()[0][3], "  FATAL ERROR : unrecognized descendant type '" + subtreeType + "'" )


  #####################
  #  GET NODE STRING  #
  #####################
  # derive the expected string for the node
  def get_node_string( self, goalName, polarity, trig_rec, subtreeType ) :

    if subtreeType == "rule" :
      node_str = "rule->" + goalName + "(" + str( trig_rec ) + ")"

    elif subtreeType == "goal" :
      if polarity == "notin" :
        node_str = "goal->" + "_NOT_" + goalName + "(" + str( trig_rec ) + ")" 
      else :
        node_str = "goal->" + goalName + "(" + str( trig_rec ) + ")" 

    elif subtreeType == "fact" :
      if polarity == "notin" :
        node_str = "fact->" + "_NOT_" + goalName + "(" + str( trig_rec ) + ")" 
      else :
        node_str = "fact->" + goalName + "(" + str( trig_rec ) + ")" 

    else :
      tools.bp( __name__, inspect.stack()[0][3], "  FATAL ERROR : unrecognized descendant type '" + subtreeType + "'" )

    return node_str



  ########################
  #  GENERATE CURR NODE  #
  ########################
  # generate the current node for the root of this ProvTree.
  def generate_curr_node( self ) :

    logging.debug( "  GENERATE CURR NODE : running process..." )
    logging.debug( "    name     = " + self.rootname )
    logging.debug( "    isNeg    = " + str( self.isNeg ) )
    logging.debug( "    treeType = " + self.treeType )

    # -------------------------------- #
    # CASE : goal node

    if self.treeType == "goal" :
      self.curr_node = GoalNode.GoalNode( name           = self.rootname, \
                                          isNeg          = self.isNeg, \
                                          record         = self.record, \
                                          parsedResults  = self.parsedResults, \
                                          cursor         = self.cursor, \
                                          prev_prov_recs = self.prev_prov_recs )

    # -------------------------------- #
    # CASE : rule node

    elif self.treeType == "rule" :
      self.curr_node = RuleNode.RuleNode( rid           = self.db_id, \
                                          name          = self.rootname, \
                                          record        = self.record, \
                                          parsedResults = self.parsedResults, \
                                          cursor        = self.cursor, \
                                          argDict       = self.argDict )

    # -------------------------------- #
    # CASE : fact node
    elif self.treeType == "fact" :
      self.curr_node = FactNode.FactNode( name          = self.rootname, \
                                          isNeg         = self.isNeg, \
                                          record        = self.record, \
                                          parsedResults = self.parsedResults, \
                                          cursor        = self.cursor )
      logging.debug( "+>>> self.curr_node.uninteresting = " + str( self.curr_node.uninteresting ) )
      if self.curr_node.uninteresting == True :
        self.uninteresting = True

    # -------------------------------- #
    else :
      tools.bp( __name__, inspect.stack()[0][3], "  GENERATE CURR NODE : FATAL ERROR : unrecognized tree type '" + self.treeType + "'" )

    logging.debug( "  GENERATE CURR NODE : ...done." )


  ###################
  #  GENERATE TREE  #
  ###################
  # generate a tree given the parsed results.
  # should only run on node FinalState
  def generate_tree( self ) :

    # -------------------------------- #
    # create the current node.

    self.curr_node = GoalNode.GoalNode( name          = self.rootname, \
                                        isNeg         = False, \
                                        parsedResults = self.parsedResults, \
                                        cursor        = self.cursor )

    # -------------------------------- #
    # create the descendant node(s)

    post_eot = self.get_post_eot()

    # break early if no post records at eot.
    if not len( post_eot ) > 0 :
      tools.bp( __name__, inspect.stack()[0][3], "  GENERATE TREE : FATAL ERROR : no eot post records. aborting." )

    for rec in post_eot :
      self.descendants.append( ProvTree( rootname        = "post",             \
                                         final_state_ptr = self.final_state_ptr, \
                                         parsedResults   = self.parsedResults, \
                                         cursor          = self.cursor,        \
                                         db_id           = None,               \
                                         treeType        = "goal",             \
                                         isNeg           = False,              \
                                         provAttMap      = {},                 \
                                         record          = rec,                 \
                                         eot             = self.eot,           \
                                         parent          = self, \
                                         argDict         = self.argDict, \
                                         prev_prov_recs  = self.prev_prov_recs ) )


  ##################
  #  GET POST EOT  #
  ##################
  # extract the post results for eot only.
  # return as a list.
  def get_post_eot( self ) :

    logging.debug( "  GET POST EOT : running process..." )
    logging.debug( "  GET POST EOT : eot = " + str( self.eot ) )

    post_eot = []

    try :
      for rec in self.parsedResults[ "post" ] :
 
        logging.debug( "  GET POST EOT : rec = " + str( rec ) )
 
        # collect eot post records only
        if int( rec[-1] ) == int( self.eot ) :
          post_eot.append( rec )

    except KeyError :
      logging.info( "  GET POST EOT : no eot post records." )

    logging.debug( "  GET POST EOT : post_eot = " + str( post_eot ) )

    return post_eot


  #######################
  #  CREATE PYDOT NODE  #
  #######################
  # return a pydot node
  def create_pydot_node( self, node_str, node_type ) :
  
    if node_type == "goal" :
      thisNode = pydot.Node( node_str, shape='oval' )
  
    elif node_type == "rule" :
      thisNode = pydot.Node( node_str, shape='box' )
  
    elif node_type == "fact" :
      thisNode = pydot.Node( node_str, shape='cylinder' )
  
    else :
      sys.exit( "********************\n********************\n \
                FATAL ERROR in file " + __name__ + \
                " in function " + \
                inspect.stack()[0][3] + \
                " :\nUnrecognized treeType" + \
                str( node_type ) )
  
    return thisNode


  #######################
  #  CREATE PYDOT EDGE  #
  #######################
  # return a pydot edge
  def create_pydot_edge( self, src_pydot_node, dest_pydot_node ) :
    return pydot.Edge( src_pydot_node, dest_pydot_node )


  ###################
  #  GET PYDOT STR  #
  ###################
  # generate an informative string 
  # version of the input pydot object
  def get_pydot_str( self, pydot_obj ) :

    if type( pydot_obj ) is pydot.Node :
      return "pydot.Node(" + pydot_obj.get_name() + ")"
    else :
      return "pydot.Edge(" + pydot_obj.get_source() + "," + pydot_obj.get_destination() + ")"



#########
#  EOF  #
#########
