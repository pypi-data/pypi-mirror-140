# ios.commands.other
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



# --- imports ---



from deepops import deepsetdefault, deepget
import netaddr

from ..utils import expand_set
from ...config import IndentedContextualCommand



# --- configuration command classes ---



# SYSTEM



class Cmd_Comment(IndentedContextualCommand):
    # we don't really need to match comments as they do nothing but it
    # avoids chugging through the entire list of commands and doing
    # nothing
    match = r"!.*"


class Cmd_Hostname(IndentedContextualCommand):
    match = r"hostname (?P<hostname>\S+)"

    def parse(self, cfg, hostname):
        cfg["hostname"] = hostname



# [NO] SPANNING-TREE ...



class Cmd_NoSTP(IndentedContextualCommand):
    match = r"no spanning-tree vlan (?P<tags>[-0-9,]+)"

    def parse(self, cfg, tags):
        cfg.setdefault(
            "no-spanning-tree-vlan", set()).update(expand_set(tags))


class Cmd_STPPri(IndentedContextualCommand):
    match = r"spanning-tree vlan (?P<tags>[-0-9,]+) priority (?P<pri>\d+)"

    def parse(self, cfg, tags, pri):
        cfg_stp_pri = cfg.setdefault("spanning-tree-vlan-priority", {})
        for tag in expand_set(tags):
            cfg_stp_pri[int(tag)] = int(pri)



# TRACK ...



class Cmd_Track(IndentedContextualCommand):
    match = r"track (?P<obj>\d+)"
    enter_context = "track"

    def parse(self, cfg, obj):
        # if there is no criterion, we're modifying an existing object,
        # which must have already been defined, so we deliberately don't
        # create it with deepsetdefault() but just deepget() it with
        # default_error set, to force an error here, if it doesn't exist
        return deepget(cfg, "track", int(obj), default_error=True)


class CmdContext_Track(IndentedContextualCommand):
    context = "track"


class Cmd_Track_Delay(CmdContext_Track):
    match = r"delay (?P<delay>.+)"

    def parse(self, cfg, delay):
        cfg["delay"] = delay


class Cmd_Track_IPVRF(CmdContext_Track):
    match = r"ip vrf (?P<vrf_name>\S+)"

    def parse(self, cfg, vrf_name):
        cfg["ip-vrf"] = vrf_name


class Cmd_Track_IPv6VRF(CmdContext_Track):
    match = r"ipv6 vrf (?P<vrf_name>\S+)"

    def parse(self, cfg, vrf_name):
        cfg["ipv6-vrf"] = vrf_name


class Cmd_Track_Obj(CmdContext_Track):
    match = r"object (?P<obj>.+)"

    def parse(self, cfg, obj):
        deepsetdefault(cfg, "object", last=set()).add(obj)


class Cmd_TrackRoute(IndentedContextualCommand):
    match = (r"track (?P<obj>\d+)"
           r" (?P<proto>ip|ipv6) route"
           r" (?P<net>[0-9a-fA-F.:]+/\d+|[0-9.]+ [0-9.]+)"
           r" (?P<extra>metric .+|reachability)")
    enter_context = "track"

    def parse(self, cfg, obj, proto, net, extra):
        # the 'net' can be in 'network netmask' or CIDR format, but the
        # netaddr.IPNetwork() object requires a slash between the
        # network and netmask, so we just change the space to a slash
        net = netaddr.IPNetwork(net.replace(" ", "/"))

        # reconstruct a normalised version of the criterion
        criterion = ("%s route %s %s" % (proto, net, extra))

        # create the new track object and store the criterion in it
        t = deepsetdefault(cfg, "track", int(obj))
        t["criterion"] = criterion

        # return the track object for the new context
        return t


class Cmd_TrackOther(IndentedContextualCommand):
    match = r"track (?P<obj>\d+) (?P<other>(interface .+|list .+|stub-object))"
    enter_context = "track"

    def parse(self, cfg, obj, other):
        t = deepsetdefault(cfg, "track", int(obj))
        t["criterion"] = other

        return t



# VLAN ...



class Cmd_VLAN(IndentedContextualCommand):
    match = r"vlan (?P<tag>\d+)"
    enter_context = "vlan"

    def parse(self, cfg, tag):
        # create the VLAN configuration entry, setting an 'exists' key
        # as we might stop other information in here that isn't in the
        # VLAN definition itself in IOS (e.g. STP priority) in future
        v = deepsetdefault(cfg, "vlan", int(tag))
        v["exists"] = True

        return v


class CmdContext_VLAN(IndentedContextualCommand):
    context = "vlan"


class Cmd_VLAN_Name(CmdContext_VLAN):
    match = r"name (?P<name>\S+)"

    def parse(self, cfg, name):
        cfg["name"] = name



# VRF ...



class Cmd_VRF(IndentedContextualCommand):
    match = r"vrf definition (?P<name>\S+)"
    enter_context = "vrf"

    def parse(self, cfg, name):
        return deepsetdefault(cfg, "vrf", name)


class CmdContext_VRF(IndentedContextualCommand):
    context = "vrf"


class Cmd_VRF_RD(CmdContext_VRF):
    match = r"rd (?P<rd>\S+)"

    def parse(self, cfg, rd):
        cfg["rd"] = rd


class Cmd_VRF_RT(CmdContext_VRF):
    match = r"route-target (?P<dir_>import|export|both) (?P<rt>\S+)"

    def parse(self, cfg, dir_, rt):
        if dir_ in { "import", "both" }:
            deepsetdefault(cfg, "route-target", "import", last=set()).add(rt)
        if dir_ in { "export", "both" }:
            deepsetdefault(cfg, "route-target", "export", last=set()).add(rt)


class Cmd_VRF_AF(CmdContext_VRF):
    # "unicast" on the end is effectively ignored
    match = r"address-family (?P<af>ipv4|ipv6)( unicast)?"
    enter_context = "vrf-af"

    def parse(self, cfg, af):
        return deepsetdefault(cfg, "address-family", af)


class CmdContext_VRF_AF(IndentedContextualCommand):
    context = "vrf-af"


class Cmd_VRF_AF_RT(CmdContext_VRF_AF):
    match = r"route-target (?P<dir_>import|export|both) (?P<rt>\S+)"

    def parse(self, cfg, dir_, rt):
        if dir_ in { "import", "both" }:
            deepsetdefault(cfg, "route-target", "import", last=set()).add(rt)
        if dir_ in { "export", "both" }:
            deepsetdefault(cfg, "route-target", "export", last=set()).add(rt)
