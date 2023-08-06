#
# Copyright (C) 2014-2022 S[&]T, The Netherlands.
#

from __future__ import absolute_import, division, print_function

import argparse
import logging
import multiprocessing
import sys
import os

try:
    from tqdm import tqdm as bar
except ImportError:
    def bar(range, total=None):
        return range

import muninn

from .utils import Processor, create_parser, parse_args_and_run
from .ingest import CheckProductListAction, filter_paths, get_path_expansion_function


class AttachProcessor(Processor):

    def __init__(self, args):
        super(AttachProcessor, self).__init__(args.archive)
        self.path_expansion_function = get_path_expansion_function(args.path_is_stem, args.path_is_enclosing_directory)
        self.use_symlinks = args.link
        self.verify_hash = args.verify_hash
        self.exclude = args.exclude
        self.product_type = args.product_type
        self.keep = args.keep

    def perform_operation(self, archive, path):
        path = os.path.abspath(path.strip())

        # Expand path into multiple files and/or directories that belong to the same product.
        try:
            product_paths = self.path_expansion_function(path)
        except muninn.Error as error:
            logging.error("%s: unable to determine which files or directories belong to product [%s]" % (path, error))
            return 0

        # Discard paths matching any of the user supplied exclude patterns.
        if self.exclude:
            product_paths = filter_paths(product_paths, self.exclude)

        if not product_paths:
            logging.error("%s: path does not match any files or directories" % path)
            return 0

        try:
            properties = archive.attach(product_paths, self.product_type, use_symlinks=self.use_symlinks,
                                        verify_hash=self.verify_hash, use_current_path=self.keep)
        except muninn.Error as error:
            logging.error("%s: unable to attach product [%s]" % (path, error))
            return 0

        return 1


def attach(args):
    processor = AttachProcessor(args)
    with muninn.open(args.archive) as archive:
        if "-" in args.path:
            paths = [path for path in sys.stdin]
        else:
            paths = args.path
        total = len(paths)
        num_success = 0
        if args.parallel:
            if args.processes is not None:
                pool = multiprocessing.Pool(args.processes)
            else:
                pool = multiprocessing.Pool()
            num_success = sum(list(bar(pool.imap(processor, paths), total=total)))
            pool.close()
            pool.join()
        elif total > 1:
            for path in bar(paths):
                num_success += processor.perform_operation(archive, path)
        elif total == 1:
            # don't show progress bar if we attach just one item
            num_success = processor.perform_operation(archive, paths[0])

    return 0 if num_success == total else 1


def main():
    parser = create_parser(description="Attach product to existing metadata entry in a muninn archive.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-s", "--path-is-stem", action="store_true", help="each product path is interpreted as a "
                       "stem; any file or directory of which the name starts with this stem is considered to be part "
                       "of the product")
    group.add_argument("-d", "--path-is-enclosing-directory", action="store_true", help="each product path is "
                       "interpreted as an enclosing directory; the actual product consists of any file or directory "
                       "found inside this enclosing directory; the enclosing directory itself is not considered part "
                       "of the product")
    parser.add_argument("-e", "--exclude", metavar="PATTERN", action="append", help="exclude any files or "
                        "directories whose basename matches PATTERN; *, ?, and [] can be used as wildcards; to match "
                        "a wildcard character literally, include it within brackets, e.g. [?] to match the character ? "
                        "literally")
    parser.add_argument("-t", "--product-type", help="force the product type of products to attach")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-l", "--link", action="store_true", help="attach symbolic links to each product")
    group.add_argument("-k", "--keep", action="store_true", help="attach product, using the current product path if it "
                                                                 "is in the muninn path, otherwise throws an error")
    parser.add_argument("--verify-hash", action="store_true",
                        help="verify the hash of the product after it has been put in the archive")
    parser.add_argument("--parallel", action="store_true", help="use multi-processing to perform attach")
    parser.add_argument("--processes", type=int, help="use a specific amount of processes for --parallel")
    parser.add_argument("archive", metavar="ARCHIVE", help="identifier of the archive to use")
    parser.add_argument("path", metavar="PATH", nargs="+", action=CheckProductListAction,
                        help="products to attach, or \"-\" to read the list of products from standard input")
    return parse_args_and_run(parser, attach)
