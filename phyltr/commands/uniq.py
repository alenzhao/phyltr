"""Usage:
    phyltr uniq [<options>] [<files>]

Merge all sets of trees with identical topologies in a tree stream into
single trees.  The branch lengths of the merged trees are computed from those
of all the trees with that topology.  Mean lengths are used by default.

OPTIONS:

    -l, --length
        Specifies the method used to compute branch lengths when trees with
        identical topologies are merged.  Must be one of: "max", "mean",
        "median", or "min".  Default is mean.
    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import itertools

import phyltr.utils.phyoptparse as optparse
from phyltr.commands.generic import PhyltrCommand, plumb

class Uniq(PhyltrCommand):

    def __init__(self, lengths):
        self.lengths = lengths

        self.topologies = {}

    def process_tree(self, t):
        # Compare this tree to all topology exemplars.  If we find a match,
        # add it to the record and move on to the next tree.
        for exemplar in self.topologies:
            if t.robinson_foulds(exemplar)[0] == 0.0:
                self.topologies[exemplar].append(t)
                break
        else:
            self.topologies[t] = [t]

        return None
       
    def postprocess(self):
        for equ_class in self.topologies.values():
            for nodes in itertools.izip(*[t.traverse() for t in equ_class]):
                dists = [n.dist for n in nodes]
                if self.lengths == "max":
                    dist = max(dists)
                elif self.lengths == "mean":
                    dist = sum(dists) / len(dists)
                elif self.lengths == "median":
                    dists.sort()
                    l = len(dists)
                    if l % 2 == 0:
                        dist = 0.5*(dists[l/2]+dists[l/2-1])
                    else:
                        dist = dists[l/2]
                elif self.lengths == "min":
                    dist = min(dists)
                nodes[0].dist = dist
            yield equ_class[0]
def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-l', '--lengths', action="store", dest="lengths", default="mean")
    options, files = parser.parse_args()

    uniq = Uniq(options.lengths)
    plumb(uniq, files)
