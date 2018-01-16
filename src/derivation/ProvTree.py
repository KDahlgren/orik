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
import GoalNode, RuleNode, FactNode

if not os.path.abspath( __file__ + "/../../../lib/iapyx/src" ) in sys.path :
  sys.path.append( os.path.abspath( __file__ + "/../../../lib/iapyx/src" ) )

from utils import tools

# **************************************** #

IMGSAVEPATH = os.path.abspath( os.getcwd() ) + "/data"

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
  # parents       : [ ProvTree ]. the ProvTree object instances connected to
  #                               this tree. None iff root is "FinalState".
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
                      argDict         = {} ) :

    # dictionary of the execution arguments
    self.argDict = argDict

    # list of descendant ProvTree objects
    self.descendants = []

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

    if not self.rootname == "FinalState" :
      self.parents.append( parent )

    logging.debug( "==================================" )
    logging.debug( "       CREATING NEW PROV TREE" )
    logging.debug( "self.rootname        = " + str( self.rootname ) )
    logging.debug( "self.final_state_ptr = " + str( self.final_state_ptr ) )
    logging.debug( "self.parsedResults   = " + str( self.parsedResults ) )
    logging.debug( "self.cursor          = " + str( self.cursor ) )
    logging.debug( "self.db_id           = " + str( self.db_id ) )
    logging.debug( "self.treeType        = " + str( self.treeType ) )
    logging.debug( "self.isNeg           = " + str( self.isNeg ) )
    logging.debug( "self.provAttMap      = " + str( self.provAttMap ) )
    logging.debug( "self.record          = " + str( self.record ) )
    logging.debug( "self.eot             = " + str( self.eot ) )
    logging.debug( "self.parents         = " + str( self.parents ) )
    logging.debug( "self                 = " + str( self        ) )
    logging.debug( "==================================" )

    # for qa testing :
    if self.rootname == "__KD__TESTNODE__KD__" :
      self.generate_tree()
      return None

    # -------------------------------- #
    # CASE : node is the FinalState 
    #        root

    if rootname == "FinalState" :

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
      self.generate_subtree()

      if self.final_state_ptr :
        self.final_state_ptr.node_str_to_object_map[ self.__str__() ] = self # add this node to the final state map

    # -------------------------------- #
    if not self.rootname == "__TestNode__" :  # for qa tests

      # generate graph meta data
      self.generate_graph_data()


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
    graph_save_path = IMGSAVEPATH + "/provtree_render_fmla" + str( fmla_index ) + "_iter" + str(iter_count)
    if additional_str :
      graph_save_path += additional_str

    for n in self.nodeset_pydot :
      graph.add_node( n )

    for e in self.edgeset_pydot :
      graph.add_edge( e )

    logging.info( "Saving prov tree render to " + str( graph_save_path + ".png" ), )
    graph.write_png( graph_save_path + ".png" )
    logging.debug( "...done." )

    # -------------------------------- #
    # generate stats about the graph

    graph_stats                = {}
    graph_stats[ "num_nodes" ] = len( self.nodeset_pydot )
    graph_stats[ "num_edges" ] = len( self.edgeset_pydot )

    try :
      if tools.getConfig( self.argDict[ "settings" ], "DEFAULT", "SERIAL_GRAPH", bool ) == True :
        self.save_serial_graph( fmla_index, iter_count, additional_str )
    except KeyError :
      logging.info( "not outputting graph data." )

    return graph_stats


  #######################
  #  SAVE SERIAL GRAPH  #
  #######################
  # save the nodes and edges of the graph to file.
  def save_serial_graph( self, fmla_index, iter_count, additional_str ) :

      serial_path  = IMGSAVEPATH + "/provtree_graph_data_fmla" + str( fmla_index ) + "_iter" + str(iter_count) + "_" + additional_str + ".txt"
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
            sys.exit( "blah" )

          # CASE : no wildcards in the trigger record
          else :
            goalName    = self.curr_node.descendant_meta[ prov_rid ][ "goalName" ]
            polarity    = None
            subtreeType = "rule"

            # do not create another ProvTree for the descendant if the descendant already exists.
            # just update the existing node's parents.
            # keep the meta data for when generating graph edges, though.
            if self.already_incorporated_into_graph( goalName, polarity, trig_rec, subtreeType ) :

              # get descendant meta
              descendant_node_str = self.get_node_string( goalName, polarity, trig_rec, subtreeType )
              existing_descendant = self.final_state_ptr.node_str_to_object_map[ descendant_node_str ]

              # update parents of existing descendant
              if existing_descendant.treeType == "rule" :
                pass # not applicable on rules because rules can have only one parent.
              else :
                existing_descendant.parents.append( self )

            else :
  
              goalName    = self.curr_node.descendant_meta[ prov_rid ][ "goalName"    ]
              triggerData = self.curr_node.descendant_meta[ prov_rid ][ "triggerData" ]
  
              for record in triggerData :
  
                new_subtree = ProvTree( rootname        = goalName, \
                                        final_state_ptr = self.final_state_ptr, \
                                        parsedResults   = self.parsedResults, \
                                        cursor          = self.cursor, \
                                        db_id           = prov_rid, \
                                        treeType        = "rule", \
                                        record          = record, \
                                        parent          = self, \
                                        eot             = self.eot )
  
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

        else :

          treeType      = d_meta[ "treeType" ]
          node_name     = d_meta[ "node_name" ]
          triggerRecord = d_meta[ "triggerRecord" ]
          polarity      = d_meta[ "polarity" ]
  
          if polarity == "notin" :
            isNeg = True
          else :
            isNeg = False
  
          # CASE : spawn a goal
          if treeType == "goal" :
            new_subtree = ProvTree( rootname        = node_name, \
                                    final_state_ptr = self.final_state_ptr, \
                                    parsedResults   = self.parsedResults, \
                                    cursor          = self.cursor, \
                                    treeType        = "goal", \
                                    record          = triggerRecord, \
                                    isNeg           = isNeg, \
                                    parent          = self, \
                                    eot             = self.eot )
  
          # CASE : spawn a fact
          elif treeType == "fact" :
            new_subtree = ProvTree( rootname        = node_name, \
                                    final_state_ptr = self.final_state_ptr, \
                                    parsedResults   = self.parsedResults, \
                                    cursor          = self.cursor, \
                                    treeType        = "fact", \
                                    record          = triggerRecord, \
                                    isNeg           = isNeg, \
                                    parent          = self, \
                                    eot             = self.eot )
  
          # CASE : wtf??? 
          else :
            tools.bp( __name__, inspect.stack()[0][3], "  FATAL ERROR : treeType not recognized '" + treeType + "'" )
  
          self.descendants.append( new_subtree )

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
    logging.debug( "  ALREADY INCORPORATED INTO GRAPH : self.final_state_ptr.node_str_to_object_map = " + \
                      str( self.final_state_ptr.node_str_to_object_map ) )

    flag = False

    if subtreeType == "rule" :
      rule_str_to_check = self.get_node_string( goalName, polarity, trig_rec, subtreeType )
      if rule_str_to_check in self.final_state_ptr.node_str_to_object_map :
        flag = True

    elif subtreeType == "goal" :
      goal_str_to_check = self.get_node_string( goalName, polarity, trig_rec, subtreeType )
      if goal_str_to_check in self.final_state_ptr.node_str_to_object_map :
        flag = True

    elif subtreeType == "fact" :
      fact_str_to_check = self.get_node_string( goalName, polarity, trig_rec, subtreeType )
      if fact_str_to_check in self.final_state_ptr.node_str_to_object_map :
        flag = True

    else :
      tools.bp( __name__, inspect.stack()[0][3], "  FATAL ERROR : unrecognized descendant type '" + subtreeType + "'" )

    logging.debug( "  ALREADY INCORPORATED INTO GRAPH : ...done." )

    return flag


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
      self.curr_node = GoalNode.GoalNode( name          = self.rootname, \
                                          isNeg         = self.isNeg, \
                                          record        = self.record, \
                                          parsedResults = self.parsedResults, \
                                          cursor        = self.cursor )

    # -------------------------------- #
    # CASE : rule node

    elif self.treeType == "rule" :
      self.curr_node = RuleNode.RuleNode( rid           = self.db_id, \
                                          name          = self.rootname, \
                                          record        = self.record, \
                                          parsedResults = self.parsedResults, \
                                          cursor        = self.cursor )

    # -------------------------------- #
    # CASE : fact node
    elif self.treeType == "fact" :
      self.curr_node = FactNode.FactNode( name          = self.rootname, \
                                          isNeg         = self.isNeg, \
                                          record        = self.record, \
                                          parsedResults = self.parsedResults, \
                                          cursor        = self.cursor )

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
                                         parent          = self ) )


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
