# parser$ python3 -m translator.sampling.slambda.tests_slambda

from proposalsampler.sampling.slambda.slambda_single import sampling_of_single_node
from proposalsampler.sampling.slambda.tests_tree_editor import test_set_slambda
# from translator.tree.tests_map import test as test_map
# from translator.sampling.slambda.tree_editor import TreeEditor

from tokentranslator.db_models.model_stable import ModelStable
# from proposalsampler.sampling.slambda.data.stable import stable


def test_slambda_single():

    stable = ModelStable()

    # target proposal:
    # "abelian(G) \\and subgroup(H, G,) => abelian(H)"
    # set slambda data to each node:
    net, nodes = test_set_slambda(22)

    # take idd of subgroup and abelian terms:
    subgroup_idd = [idd for idd in nodes
                    if net.nodes[idd]["data"]["slambda"]["stname"] == "subgroup"][0]
    abelian_idd = [idd for idd in nodes
                   if net.nodes[idd]["data"]["slambda"]["stname"] == "abelian"][0]

    idds = [("subgroup", subgroup_idd),
            ("abelian", abelian_idd)]

    # create value table:
    test_vtable = [

        # both H and G are given
        # => just check target proposal:
        {"H": ("(2,4)(3,5)",),
         "G": ("(2,4)(3,5)", "(2,5,4,3)"),
         "idd": str(["s"]), "successors_count": 0},
        
        # G is not given
        # => must be generating during sampling
        {"H": ("(2,3)(4,5)",),
         subgroup_idd: True, abelian_idd: True,
         "idd": str(["s"]), "successors_count": 0},
        
        # H is not ginven
        # => must be generating during sampling
        {"G": ("(1,2)(3,5)", "(1,5,2,3)"),
         subgroup_idd: True, abelian_idd: True,
         "idd": str(["s"]), "successors_count": 0},
        {"G": ("(1,4)(2,3)", "(1,3)(2,4)"),
         abelian_idd: True, subgroup_idd: True,
         "idd": str(["s"]), "successors_count": 0}]
    
    print("subgroup node:\n")
    print(net.nodes[subgroup_idd])
    print("\nabelian node:\n")
    print(net.nodes[abelian_idd])

    print("\n========= Tests for each entry in vtable ===========\n")
    for entry in test_vtable:
        # FOR print:
        print("\n+++++++++++++ for entry: +++++++++++++")
        print(entry)

        for (pred_name, pred_idd) in idds:
            print("\n------------for " + pred_name + ": ",
                  pred_idd, "------------")
            pred_node_data = net.nodes[pred_idd]["data"]["slambda"]

            # print node args:
            print("from node:")
            print(pred_name + "(", str(pred_node_data["args"][:-1]),
                  ")\n")

            # print node args entry values:
            pred_args = [entry[arg] if (arg in entry
                                        and entry[arg] is not None)
                         else arg
                         for arg in pred_node_data["args"][:-1]]
            pred_out = "None"
            if pred_idd in entry:
                pred_out = entry[pred_idd]
            print("from vtentry:")
            print(pred_name + "(", str(pred_args), ") = ",
                  pred_out, "\n")
            # print(net.nodes[subgroup_idd]["data"]["slambda"])
            # END FOR

            out, msg = sampling_of_single_node(net.nodes[pred_idd],
                                               entry, stable)
            print("out:")
            print(out)
            if out is not None:
                print(len(out))
            print("msg:")
            print(msg)

    print("\ntest_vtable:")
    for entry in test_vtable:
        print(entry, "\n")


def run():
    test_slambda_single()


if __name__ == "__main__":
    run()

