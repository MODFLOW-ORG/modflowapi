"""
Centralized location to store the "data model"/relationship trees for packages
blocks, and input variables that are used by the modflowapi.extensions code
"""

gridshape = {
    "dis": ["nlay", "nrow", "ncol"],
    "disu": [
        "nlay",
        "ncpl",
    ],
}


# Note: HFB variables are not accessible in the memory manager 10/7/2022
pkgvars = {
    "dis": ["top", "bot", "area", "idomain"],
    "chd": [
        "nbound",
        "maxbound",
        "nodelist",
        ("bound", ("head",)),
        "naux",
        "auxname_cst",
        "auxvar",
    ],
    "drn": [
        "nbound",
        "maxbound",
        "nodelist",
        (
            "bound",
            (
                "elev",
                "cond",
            ),
        ),
        "naux",
        "auxname_cst",
        "auxvar",
    ],
    "evt": [
        "nbound",
        "maxbound",
        "nodelist",
        (
            "bound",
            (
                "surface",
                "rate",
                "depth",
            ),
        ),
        # "pxdp:NSEG", "petm:NSEG"
        "naux",
        "auxname_cst",
        "auxvar",
    ],
    "ghb": [
        "nbound",
        "maxbound",
        "nodelist",
        (
            "bound",
            (
                "bhead",
                "cond",
            ),
        ),
        "naux",
        "auxname_cst",
        "auxvar",
    ],
    "ic": ["strt"],
    "npf": ["k11", "k22", "k33", "angle1", "angle2", "angle3", "icelltype"],
    "rch": [
        "maxbound",
        "nbound",
        "nodelist",
        ("bound", ("recharge",)),
        "naux",
        "auxname_cst",
        "auxvar",
    ],
    "riv": [
        "maxbound",
        "nbound",
        "nodelist",
        ("bound", ("stage", "cond", "rbot")),
        "naux",
        "auxname_cst",
        "auxvar",
    ],
    "sto": ["iconvert", "ss", "sy"],
    "wel": [
        "maxbound",
        "nbound",
        "nodelist",
        ("bound", ("q",)),
        "naux",
        "auxname_cst",
        "auxvar",
    ],
    # gwe model
    "cnd": ["alh", "alv", "ath1", "ath2", "atv", "kts"],
    "est": ["porosity", "decay", "cps", "rhos"],
    "cpt": [
        "maxbound",
        "nbound",
        "nodelist",
        ("bound", ("temp",)),
        "naux",
        "auxname_cst",
        "auxvar",
    ],
    "esl": [
        "maxbound",
        "nbound",
        "nodelist",
        ("bound", ("senerrate",)),
        "naux",
        "auxname_cst",
        "auxvar",
    ],
    # gwt model
    "dsp": ["diffc", "alh", "alv", "ath1", "ath2", "atv"],
    "cnc": [
        "maxbound",
        "nbound",
        "nodelist",
        ("bound", ("conc",)),
        "naux",
        "auxname_cst",
        "auxvar",
    ],
    "ist": [
        "cim",
        "thtaim",
        "zetaim",
        "decay",
        "decay_sorbed",
        "bulk_density",
        "distcoef",
    ],
    "mst": ["porosity", "decay", "decay_sorbed", "bulk_density", "distcoef"],
    "src": [
        "maxbound",
        "nbound",
        "nodelist",
        ("bound", ("smassrate",)),
        "naux",
        "auxname_cst",
        "auxvar",
    ],
    # prt model
    "mip": ["porosity", "retfactor", "izone"],
    # exchange model
    "gwf-gwf": ["nexg", "nodem1", "nodem2", "cl1", "cl2", "ihc", "hwva"],
    "gwt-gwt": ["nexg", "nodem1", "nodem2", "cl1", "cl2", "ihc", "hwva"],
    "gwe-gwe": ["nexg", "nodem1", "nodem2", "cl1", "cl2", "ihc", "hwva"],
    # simulation
    "ats": [
        ("maxats", ()),
        "iperats",
        "dt0",
        "dtmin",
        "dtmax",
        "dtadj",
        "dtfailadj",
    ],
    "tdis": [
        "nper",
        "itmuni",
        "kper",
        "kstp",
        "delt",
        "pertim",
        "totim,",
        "perlen",
        "nstp",
        "tsmult",
    ],
    # solution package
    "sln-ims": [
        "mxiter",
        "dvclose",
        "gamma",
        "theta",
        "akappa",
        "amomentum",
        "numtrack",
        "btol",
        "breduc",
        "res_lim",
    ],
    "ims": [
        "niterc",
        "dvclose",
        "rclose",
        "relax",
        "ipc",
        "droptol",
        "north",
        "iscl",
        "iord",
    ],
    "sln-ems": [
        "icnvg",
        "ttsoln",
    ],
}


adv_pkgvars = {
    "sfr": {
        "packagedata": [
            "maxbound",
            (
                "ifno:range:maxbound",
                "nodelist",
                "length",
                "width",
                "slope",
                "strtop",
                "bthick",
                "hk",
                "rough",
                "nconnreach",
                "ustrf",
                "ndiv",
            ),
        ],
        "diversions": [
            "ndiv:count_nonzero:ndiv",
            (
                "ifno:where_idx:ndiv",
                "idv:where_val:ndiv",
                "divreach",  # iconr
            ),
        ],
        "perioddata": [
            "maxbound",
            "nbound",
            (
                "bound",
                ("ifno", "sfrsetting", "setting_0", "setting_1"),
            ),
        ],
    },
    "uzf": {
        "packagedata": [
            "maxbound",
            (
                "ifno:range:maxbound",
                "nodelist",
                "landflag",
                "ivertcon",
                "surfdep",
                "vks",
                "thtr",
                "thts",
                "thti",
                "eps",
            ),
        ],
        "perioddata": [
            "maxbound",
            "nbound",
            ("bound", ("ifno:range:maxbound", "finf", "pet", "extdp", "extwc", "ha", "hroot", "rootact")),
        ],
    },
    "lak": {
        "packagedata": ["nlakes", ("ifno:range:nlakes", "strt", "nlakeconn")],
    },
    "maw": {"packagedata": ["nmawwells", ("ifno:range:nmawwells", "radius", "bot", "strt", "ngwfnodes")]},
}


def get_package_class(pkg_type):
    """
    Return the Package subclass used to represent instances of the given
    package type.

    Package is now a single composite implementation -- the var kinds it
    exposes (array/list/scalar/advanced) are determined by pkgvars/adv_pkgvars,
    not by subclass. ArrayPackage/ListPackage/ScalarPackage/AdvancedPackage are
    behaviorally identical, empty subclasses of Package kept only so that
    isinstance(pkg, ArrayPackage) etc. still resolves as it did pre-refactor.
    This mapping is a backwards-compatibility shim, not a real taxonomy, and
    is slated for removal (along with the subclasses) in the next major
    version.
    """
    from .pakbase import AdvancedPackage, ArrayPackage, ListPackage, ScalarPackage

    pkg_type_classes = {
        "dis": ArrayPackage,
        "chd": ListPackage,
        "drn": ListPackage,
        "evt": ListPackage,
        "ghb": ListPackage,
        "ic": ArrayPackage,
        "npf": ArrayPackage,
        "rch": ListPackage,
        "riv": ListPackage,
        "sto": ArrayPackage,
        "wel": ListPackage,
        # exchanges
        "gwf-gwf": ListPackage,
        "gwt-gwt": ListPackage,
        "gwe-gwe": ListPackage,
        # advanced
        "sfr": AdvancedPackage,
        "uzf": AdvancedPackage,
        "lak": AdvancedPackage,
        "maw": AdvancedPackage,
        # gwt
        "dsp": ArrayPackage,
        "cnc": ListPackage,
        "ist": ArrayPackage,
        "mst": ArrayPackage,
        "src": ListPackage,
        # gwe
        "cnd": ArrayPackage,
        "est": ArrayPackage,
        "cpt": ListPackage,
        "esl": ListPackage,
        # prt
        "mip": ArrayPackage,
        # sim-level pkgs
        "tdis": ScalarPackage,
        "ats": ListPackage,
    }
    return pkg_type_classes.get(pkg_type, AdvancedPackage)
