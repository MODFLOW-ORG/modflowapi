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
        "maxats",
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
}


def get_package_type(pkg_type):
    from .advpaks import LakPackage, SfrPakage, UzfPackage
    from .pakbase import AdvancedPackage, ArrayPackage, ListPackage, ScalarPackage

    pkg_types = {
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
        # advanced
        "sfr": SfrPakage,
        "uzf": UzfPackage,
        "lak": LakPackage,
        # "maw": None,
        # "csub": None,
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
        # sim_level pkgs
        "tdis": ScalarPackage,
        "ats": ListPackage,
    }
    if pkg_type in pkg_types:
        return pkg_types[pkg_type]
    else:
        return AdvancedPackage
