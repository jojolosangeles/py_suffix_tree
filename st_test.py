from suffix_tree.test.verify_tree import verify_tree, debug_on
from suffix_tree.tree_builder import TreeBuilder

def testit(s, debugOn=False):
  debug_on(debugOn)
  print(f"BUILDING TREE for {s}")
  tb = TreeBuilder(s)
  tb.debugOn = debugOn
  tb.process_all_values()
  if debugOn:
    print(f"DONE, nodeStore is:")
    print(f"{tb.nodeStore}")
    print("Now try verifying")
  verify_tree(tb.nodeStore, s)
  verify_tree(tb.nodeStore, s)
  verify_tree(tb.nodeStore, s)

if __name__ == "__main__":
  testit("eee")