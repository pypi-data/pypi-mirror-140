from proposalsampler.sampling.slambda.tree_editor import TreeEditor
from proposalsampler.sampling.slambda.slambda_synch import ValTableSynch
import tokentranslator.translator.tree.maps as ms

from proposalsampler.sampling.slambda.data.stable import stable_fixed
# from proposalsampler.sampling.slambda.data.stable import stable
from tokentranslator.db_models.model_stable import ModelStable

from functools import reduce


class ValTableSampling():

    '''Generate proposal's (parsed_net) missing vars data
    (init_ventry, vars_terms) with use of value table sampling.

    Inputs:

    - ``parsed_net`` -- proposal parsed net (see parser_general).
    
    - ``init_ventry`` -- entry with part of proposal data
    (from vars_terms or predicate's) whose other part will be
    generated here with sampling.
    (ex: for abelian(X, S_{3}) X will be missed in init_ventry
    and will be generated).
 
    - ``stable`` -- generators of each term
    (see sampling.slambda.data.stable).
    
    - ``stable_fixed`` -- terms, whose sign is always fixed
    (like mid terms)
    
    - ``vars_terms`` -- name of terms that is vars.

    Example:

    for proposal = "abelian(G)\\andsubgroup(H,G,)=>abelian(H)"
    with init vdata =
    {"G": ("(1,2)(3,5)", "(1,5,2,3)"),
     # subgroup_idd: True, abelian_idd: True,
     "idd": str(["s"]), "successors_count": 0},
    where H is not ginven
    => will be generated during sampling.

    '''

    def __init__(self, parsed_net, init_ventry,
                 stable, stable_fixed,
                 mid_terms, vars_terms):
        self.set_parsed_net(parsed_net)
        self.set_init_ventry(init_ventry)
        self.set_stable(stable, stable_fixed)
        self.set_mid_terms(mid_terms)
        self.set_vars_terms(vars_terms)
        self.successes = None

    def set_init_ventry(self, init_ventry):
        self.init_ventry = init_ventry

    def set_parsed_net(self, parsed_net):
        self.parsed_net = parsed_net

    def set_stable(self, stable, stable_fixed):
        self.stable = stable
        self.stable_fixed = stable_fixed

    def set_mid_terms(self, mid_terms):
        self.mid_terms = mid_terms

    def set_vars_terms(self, vars_terms):
        self.vars_terms = vars_terms

    def run(self, editor_out=None):
        if editor_out is None:
            nodes_net, nodes_idds = self.editor_step()
        else:
            nodes_net, nodes_idds = editor_out
        self.nodes_idds = nodes_idds

        successes, vesnet = self.synch_step(nodes_net, nodes_idds)
        json_out = self.net_to_json(vesnet)
        # if successes > 0:
        self.successes = successes
        return(json_out)

    def net_to_json(self, vesnet):
        D = vesnet
        D = ms.set_max_height(D)
        D = ms.set_max_width(D)
        D = ms.set_position(D, [["['s']"]], {"x": 400, "y": 100},
                            lambda dx, level: 10*level,
                            lambda w, level: (w+20)**2+level)

        slambda_converter = ms.convert_node_data_slambda
        net_data = ms.map_net_nx_to_cy(D,
                                       node_data_converter=slambda_converter)
        self.json_out = net_data
        return(self.json_out)

    def synch_step(self, nodes_net, nodes_idds):
        
        '''sample each generator in nodes_idds for each
        collumn in init_ventry, generate result tree
        (from init_ventry to succ_ventry or fail_ventry).'''

        v_synch = ValTableSynch(nodes_net, nodes_idds,
                                self.stable, self.stable_fixed)
        v_synch.init_ventry(self.init_ventry)
        results = v_synch.synch(self.init_ventry, [])
        successes, failures, state = results
        
        return((successes, v_synch.vesnet))

    def editor_step(self):

        '''add slambda data to parsed net predicates and
        vars nodes. Return them as well.

        slambda_nodes_idds is idd for predicates or names for vars,
        can be used to init vtable skeleton:
        self.get_vtable_skeleton(nodes_idds)'''

        D = self.parsed_net

        tree_editor = TreeEditor()
        tree_editor.set_mid_terms(self.mid_terms)
        tree_editor.set_stable_names(list(self.stable.get_stable().keys()))
        tree_editor.set_vars_terms(self.vars_terms)
        tree_editor.set_parsed_net(D)

        slambda_nodes_idds = []

        # add slambda key for each node in D
        # which name exist in stable:
        for node_idd in D.nodes:
            slambda = tree_editor(node_idd)
            if slambda is not None:
                if D.nodes[node_idd]["name"] == "br":
                    left_node_idd = tree_editor.get_successors(node_idd)[0]
                    slambda_nodes_idds.append(left_node_idd)
                else:
                    slambda_nodes_idds.append(node_idd)
        return((D, slambda_nodes_idds))

    def get_vtable_skeleton(self, nodes_idds):
        
        '''Return hat of value table.

        - ``nodes_idds`` -- from self.editor_step'''

        nodes = self.parsed_net.nodes
        get_vtname = (lambda node_idd:
                      nodes[node_idd]["data"]["slambda"]["vtname"])
        get_stname = (lambda node_idd:
                      nodes[node_idd]["data"]["slambda"]["stname"])
        table_skeleton = [(node_idd,
                           get_stname(node_idd))
                          if (get_stname(node_idd) != get_vtname(node_idd))
                          else (get_stname(node_idd), get_stname(node_idd))
                          for node_idd in nodes_idds]
        # remove duplicates:
        f = lambda acc, x: acc+[x] if (x not in [y for y in acc]) else acc
        table_skeleton = list(reduce(f, table_skeleton, []))
        return(table_skeleton)


class Sampler():
    '''
    Giving parsed net from proposal and init value entry,
    will try to produce remained args.
    '''
    def __init__(self):

        self.mid_terms = ["clause_where", "clause_for", "clause_into",
                          "def_0", "in_0",
                          "if", "if_only", "if_def",
                          "clause_or", "conj"]
        self.vars_terms = ["set", "var"]
        self.parsed_net = None
        self.init_ventry = None

        self.stable = ModelStable()
        
        self.gen = ValTableSampling(None, None,
                                    self.stable, stable_fixed,
                                    self.mid_terms, self.vars_terms)

    def set_parsed_net(self, parsed_net):
        self.parsed_net = parsed_net
        self.gen.parsed_net = parsed_net

    def set_init_ventry(self, init_ventry):
        self.init_ventry = init_ventry

    def get_parsed_net(self):
        if self.gen.parsed_net is not None:
            return(self.gen.parsed_net)
        else:
            return(self.parsed_net)

    def get_vtable_skeleton(self):
        net_out, nodes_idds = self.editor_step()
        return(self.gen.get_vtable_skeleton(nodes_idds))

    def get_stable(self):
        return(self.gen.stable.get_stable())

    def editor_step(self):

        '''fill slambda data for self.gen.parsed_net
        and skeleton for vtable.'''

        if self.parsed_net is None:
            raise(BaseException("use sampler.set_parsed_net first"))
        return(self.gen.editor_step())

    def get_successors(self):
        return(self.gen.successes)

    def run(self):
        if self.parsed_net is None:
            raise(BaseException("use sampler.set_parsed_net first"))
        if self.init_ventry is None:
            raise(BaseException("use sampler.set_init_ventry first"))

        self.gen = ValTableSampling(self.parsed_net.copy(),
                                    self.init_ventry.copy(),
                                    self.stable, stable_fixed,
                                    self.mid_terms, self.vars_terms)

        out = self.gen.run()
        # print("\nsampling json (for cy) result:")
        # print(out)

        print("\nsampling successors:")
        print(self.gen.successes)
        # TODO: bug with parsed_net
        return(out)
