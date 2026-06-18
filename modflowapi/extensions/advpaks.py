from .pakbase import AdvancedPackage

# Backward compatibility alias; SFR diversions are now handled generically
# by Package._build_advanced_inputs via adv_pkgvars["sfr"]["diversions"].
SfrPackage = AdvancedPackage
