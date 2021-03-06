"""Usage:
    phyltr subtree taxa [<options>] [<files>]

Replace each tree with the minimal subtree containing the specified taxa.

OPTIONS:

    taxa
        A comma-separated list of leaf taxa to keep in the tree

    files
        A whitespace-separated list of filenames to read treestreams from.
        Use a filename of "-" to read from stdin.  If no filenames are
        specified, the treestream will be read from stdin.
"""

import sys

from phyltr.commands.generic import PhyltrCommand, plumb
import phyltr.utils.phyoptparse as optparse

class Subtree(PhyltrCommand):

    def __init__(self, taxa=None, filename=None, attribute=None, value=None):
        self.attribute = attribute
        self.filename = filename
        self.value = value

        self.by_attribute = False

        if taxa:
            self.taxa = taxa
        elif filename:
            with open(options.filename, "r") as fp:
                self.taxa = [t.strip() for t in fp.readlines()]
            if not self.taxa:
                raise ValueError("Empty file!")
        elif self.attribute and self.value:
            self.taxa = []
        else:
            raise ValueError("Incompatible arguments")


    def process_tree(self, t):
        if self.taxa:
            leaves = [l for l in t.get_leaves() if l.name in self.taxa]
            mrca = leaves[0].get_common_ancestor(leaves[1:])
            t = mrca
        else:
            mrca = list(t.get_monophyletic([self.value], self.attribute))[0]
            assert mrca != t
            t = mrca
        return t

def run():

    # Parse options
    parser = optparse.OptionParser(__doc__)
    parser.add_option('-a', '--attribute', default=None)
    parser.add_option('-f', '--file', dest="filename",
            help='Specifies a file from which to read taxa')
    parser.add_option('-v', '--value', default=None)
    options, files = parser.parse_args()

    if (options.attribute and options.value) or options.filename:
        taxa = []
    else:
        if files:
            taxa = set(files[0].split(","))
            files = files[1:]
        else:
            sys.stderr.write("Must specify either a list of taxa, a file of taxa, or an attribute and value.\n")
            sys.exit(1)

    subtree = Subtree(taxa, options.filename, options.attribute, options.value)
    plumb(subtree, files)
