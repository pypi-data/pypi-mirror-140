# from proposalsampler.sampling.slambda.data.stable import sign_module_name
from proposalsampler.sampling.slambda.data.gens.algebra.groups import subgroups 
from proposalsampler.sampling.slambda.data.gens.algebra.groups import abelian
import random

from copy import deepcopy

import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
# logger = logging.getLogger('tests.tester.gen_1d')

# if using directly uncoment that:

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('slambda_single')
logger.setLevel(level=log_level)


def sampling_of_single_node(node, ventry, stable):
    
    '''
    If node has no "mem_sign" key, it will
    be added (for memorization of generated signs).

    If ventry is not complite with node name
    or args, it will be (with None values).

    Return either list of successful samples (entries)
    (for entry sign) or failure (None).

    For ``rand`` signature type failure means no results
    after N samples.

    If failure, ``failure_statuses`` for node["name"]
    will be added as description of cause.'''

    node_data = node["data"]["slambda"]

    # print("node_data:")
    # print(node_data)
    if not stable.has_predicate(node_data["stname"]):
        # if node_data["stname"] not in stable:
        print("no generator for: ", node_data["stname"])

    # if node not exist yet in vtentry,
    # add it:
    if node_data["vtname"] not in ventry:
        ventry[node_data["vtname"]] = None

    # if node args not exist in ventry:
    # add it:
    for arg in node_data["args"]:
        if arg not in ventry:
            ventry[arg] = None

    # collect node.sign to work with:
    # (ex: for node["args"] = [X, Y] and node["name"] = f
    #  and sign [X, Y, Out], collect [None, 1, True],
    #  where values taken from ventry):
    target_attrs = [arg for arg in node_data["args"]]
    target_sign_val = [ventry[arg]
                       for arg in node_data["args"]]
    target_sign = [True if ventry[arg] is not None
                   else False for arg in node_data["args"]]
    '''
    target_attrs.append(node_data["vtname"])
    target_sign_val.append(ventry[node_data["vtname"]])
    target_sign.append(True
                       if (ventry[node_data["vtname"]]
                           is not None)
                       else False)
    '''
    target_attrs = tuple(target_attrs)
    target_sign_val = tuple(target_sign_val)
    target_sign = tuple(target_sign)
    logger.debug("target_attrs:")
    logger.debug(target_attrs)
    logger.debug("target_sign_val:")
    logger.debug(target_sign_val)
    logger.debug("target_sign:")
    logger.debug(target_sign)

    # memorization:
    if "mem_sign" not in node_data:
        node_data["mem_sign"] = {}

    # if there is previus results
    # use it:
    if target_sign_val in node_data["mem_sign"]:
        mem_sign = node_data["mem_sign"][target_sign_val]

        if mem_sign is None:
            msg = "failure found in mem_sign"
            return((None, msg))
        else:
            n_entries = [create_new_entry(node_data, target_attrs,
                                          sign_value, ventry)
                         for sign_value in node_data["mem_sign"][target_sign_val]]
            return((n_entries, None))

    # if there is none, generate new:

    # generate new samples with use
    # of sign generators (for target_sign_val):
    if not stable.has_signature(node_data["stname"], target_sign):
        # if target_sign not in stable[node_data["stname"]]:
        msg = ("no such signature for: " + node_data["stname"]
               + " " + str(target_sign))
        print(msg)
        logger.debug("available signs for node ", node_data["stname"])
        logger.debug(stable.get_signatures(node_data["stname"]))
        # logger.debug(stable[node_data["stname"]])
        # ventry["failure_statuses"][node_data["name"]] = msg
        return((None, msg))
    else:
        target_sign_stdata = stable.get_data(node_data["stname"],
                                             target_sign)
        # target_sign_stdata = stable[node_data["stname"]][target_sign]

        # exec(target_sign_stdata['code'])
        # gen = locals()[target_sign_stdata['func_name']]

        slambda_globals = {}
        slambda_locals = {}
        
        exec(target_sign_stdata['code'],
             slambda_globals, slambda_locals)
        slambda_globals.update(slambda_locals)
        
        '''
        # secure:
        exec(target_sign_stdata['code'],
             {'__builtins__': 
              {'print': print,
               'globals': globals,
               'locals': locals},
              
              'subgroups': subgroups,
              'abelian': abelian,
              'random': random},
             slambda_locals)
        '''
        gen = slambda_locals[target_sign_stdata['func_name']]
        '''
        # get generator from:
        # (like groups.sub_X_y_out)
        gen = eval(sign_module_name+target_sign_stdata["func_name"])
        '''
        _type = target_sign_stdata["gen_type"]
        print("slambda_globals:")
        print(slambda_globals)
        print("slambda_locals:")
        print(slambda_locals)
        # print("locals:")
        # print(locals())
        # print("globals:")
        # print(globals())
        if _type == "det":
            print("slambda_locals1:")
            print(slambda_locals)

            tmp_glob = {'__builtins__': None,
                        'gen': gen,
                        'target_sign_val': target_sign_val}
            
            ### tmp_glob.update(slambda_locals)
            print("tmp_glob1:")
            print(tmp_glob)

            # if result is determent:
            # cmd = compile('gen(target_sign_val)', '<string>', 'exec',
            #               0, 1)
            res = eval('gen(target_sign_val)',
                       tmp_glob)
            # slambda_locals.copy()
            # res = gen(target_sign_val)
            if res is not None:
                n_entry = create_new_entry(node_data, target_attrs,
                                           res, ventry)
                node_data["mem_sign"][target_sign_val] = [res]
                return(([n_entry], None))
            else:
                # failure:
                node_data["mem_sign"][target_sign_val] = None
                msg = ("wrong value,"
                       + " ")
                # ventry["failure_statuses"][node_data["name"]] = msg
                return((None, msg))

        elif _type == "rand":
            # if result is random:
            res_success = []
            previus_states = []
            N = target_sign_stdata["count_of_samples"]
            for step in range(N):
                print("slambda_locals2:")
                print(slambda_locals)
                tmp_glob = {'__builtins__': None,
                            'gen': gen,
                            'target_sign_val': target_sign_val,
                            'previus_states': previus_states}
                ### tmp_glob.update(slambda_locals)
                print("tmp_glob2:")
                print(tmp_glob)
                # cmd = compile('gen(target_sign_val, previus_states)',
                #               '<string>', 'exec',0 , 1)
                res, previus_states = eval('gen(target_sign_val, previus_states)',
                                           tmp_glob)
                # slambda_locals.copy()
                # res, previus_states = gen(target_sign_val, previus_states)
                if previus_states is None:
                    # states empty:
                    break
                if res is not None:
                    res_success.append(res)

            # if there is some results:
            if len(res_success) > 0:
                n_entries = [create_new_entry(node_data, target_attrs,
                                              sign_value, ventry)
                             for sign_value in res_success]
                node_data["mem_sign"][target_sign_val] = res_success
                return((n_entries, None))
            else:
                # failure:
                node_data["mem_sign"][target_sign_val] = None
                msg = ("rand count achived,"
                       + " no results")
                # ventry["failure_statuses"][node_data["name"]] = msg
                return((None, msg))


def create_new_entry(node_data, sign, sign_values, parent_entry):
    n_entry = deepcopy(parent_entry)
    print("sign:")
    print(sign)
    print("n_entry:")
    print(n_entry)
    print("sign_values:")
    print(sign_values)
    for idx, attr in enumerate(sign):
        n_entry[attr] = sign_values[idx]

    # if ventry has no attribute checked_nodes
    # add it:
    if "checked_nodes" not in n_entry:
        n_entry["checked_nodes"] = [node_data["vtname"]]
    else:
        n_entry["checked_nodes"].append(node_data["vtname"])

    n_entry["parent_idd"] = parent_entry["idd"]
    n_entry["idd"] = str((eval(parent_entry["idd"])
                          + [parent_entry["successors_count"]]))
    parent_entry["successors_count"] += 1
    n_entry["successors_count"] = 0
    return(n_entry)
