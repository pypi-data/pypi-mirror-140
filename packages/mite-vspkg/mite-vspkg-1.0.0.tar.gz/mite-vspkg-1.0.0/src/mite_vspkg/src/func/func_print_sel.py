def pkgs_raw(packages):
    pkgs_raw_str = ""
    for package in packages:
        pkgs_raw_str += str(package) + "\n"
    print(pkgs_raw_str)


def pkgs_traits(packages, traits_to_print):
    pkgs_traits_str = ""
    for package in packages:
        pkgs_traits_str += "\n"
        for trait in traits_to_print:
            if trait in package:
                pkgs_traits_str += "%s: %s\n" % (trait, package[trait])
    print(pkgs_traits_str)
