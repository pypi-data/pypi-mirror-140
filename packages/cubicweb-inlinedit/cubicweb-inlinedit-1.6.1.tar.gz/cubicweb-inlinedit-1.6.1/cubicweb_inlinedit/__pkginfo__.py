# pylint: disable=W0622
"""cubicweb-inlinedit application packaging information"""

modname = "inlinedit"
distname = "cubicweb-inlinedit"

numversion = (1, 6, 1)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
author = "LOGILAB S.A. (Paris, FRANCE)"
author_email = "contact@logilab.fr"
description = "Extension of the `reledit` builtin feature"
web = "https://forge.extranet.logilab.fr/cubicweb/cubes/%s" % distname

__depends__ = {"cubicweb": ">= 3.30.0, <3.32", "cwtags": "<1.2.3"}

__recommends__ = {}

classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python",
    "Programming Language :: JavaScript",
]
