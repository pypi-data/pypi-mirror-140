# ios.converters.all
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



# --- imports ---



from ...diff import DiffConvert



# --- converter classes ---



# SYSTEM



class Cvt_Hostname(DiffConvert):
    cmd = "hostname",

    def remove(self, old):
        return "no hostname"

    def update(self, old, upd, new):
        return "hostname " + new



# [NO] SPANNING-TREE ...



class Cvt_NoSTP(DiffConvert):
    cmd = "no-spanning-tree-vlan", None

    def remove(self, old, tag):
        # removing 'no spanning-tree' enables spanning-tree
        return "spanning-tree vlan %d" % tag

    def update(self, old, upd, new, tag):
        # adding 'no spanning-tree' disables spanning-tree
        return "no spanning-tree vlan %d" % tag


class Cvt_STPPri(DiffConvert):
    cmd = "spanning-tree-vlan-priority", None

    def remove(self, old, tag):
        return "no spanning-tree vlan %d priority" % tag

    def update(self, old, upd, new, tag):
        return "spanning-tree vlan %d priority %d" % (tag, new)



# TRACK ...



class Cvt_Track(DiffConvert):
    cmd = "track", None
    ext = "criterion",

    def remove(self, old, obj):
        return "no track %d" % obj

    def update(self, old, upd, new, obj):
        return "track %d %s" % (obj, new["criterion"])


class DiffConvert_Track(DiffConvert):
    context = Cvt_Track.cmd

    def enter(self, obj):
        return "track " + str(obj),


class Cvt_Track_Delay(DiffConvert_Track):
    cmd = "delay",

    def remove(self, old, obj):
        return [*self.enter(obj), " no delay"]

    def update(self, old, upd, new, obj):
        return [*self.enter(obj), " delay " + new]


class Cvt_Track_IPVRF(DiffConvert_Track):
    cmd = "ip-vrf",

    def remove(self, old, obj):
        return [*self.enter(obj), " no ip vrf"]

    def update(self, old, upd, new, obj):
        return [*self.enter(obj), " ip vrf " + new]


class Cvt_Track_IPv6VRF(DiffConvert_Track):
    cmd = "ipv6-vrf",

    def remove(self, old, obj):
        return [*self.enter(obj), " no ipv6 vrf"]

    def update(self, old, upd, new, obj):
        return [*self.enter(obj), " ipv6 vrf " + new]


class Cvt_Track_Obj(DiffConvert_Track):
    cmd = "object", None

    def remove(self, old, obj, sub_obj):
        return [*self.enter(obj), " no object " + sub_obj]

    def update(self, old, upd, new, obj, sub_obj):
        return [*self.enter(obj), " object " + sub_obj]



# VLAN ...



class Cvt_VLAN(DiffConvert):
    cmd = "vlan", None

    def remove(self, old, tag):
        return "no vlan %d" % tag

    def add(self, new, tag):
        return "vlan %d" % tag


class Cvt_VLAN_Name(DiffConvert):
    context = Cvt_VLAN.cmd
    cmd = "name",

    def remove(self, old, tag):
        return "vlan " + str(tag), " no name"

    def update(self, old, upd, new, tag):
        return "vlan " + str(tag), " name " + new



# VRF ...



class Cvt_VRF(DiffConvert):
    cmd = "vrf", None

    def remove(self, old, name):
        return "no vrf definition " + name

    def add(self, new,  name):
        return "vrf definition " + name


class DiffConvert_VRF(DiffConvert):
    context = Cvt_VRF.cmd

    def enter(self, vrf):
        return "vrf definition " + vrf,


class Cvt_VRF_RD(DiffConvert_VRF):
    cmd = "rd",

    def remove(self, old, vrf):
        return [*self.enter(vrf), " no rd " + old]

    def update(self, old, upd, new, vrf):
        l = list(super().enter(vrf))
        if old:
            l.append(" no rd " + old)
        l.append(" rd " + new)
        return l


class Cvt_VRF_RT(DiffConvert_VRF):
    cmd = "route-target", None, None

    def truncate(self, old, rem, new, vrf, dir_, rt):
        return [*self.enter(vrf), " no route-target %s %s" % (dir_, rt)]

    def update(self, old, upd, new, vrf, dir_, rt):
        return [*self.enter(vrf), " route-target %s %s" % (dir_, rt)]


class Cvt_VRF_AF(DiffConvert_VRF):
    cmd = "address-family", None

    def remove(self, old, vrf, af):
        return [*self.enter(vrf), " no address-family " + af]

    def add(self, new, vrf, af):
        return [*self.enter(vrf), " address-family " + af]


class DiffConvert_VRF_AF(DiffConvert_VRF):
    context = DiffConvert_VRF.context + Cvt_VRF_AF.cmd

    def enter(self, vrf, af):
        return [*super().enter(vrf), " address-family " + af]


class Cvt_VRF_AF_RT(DiffConvert_VRF_AF):
    cmd = "route-target", None, None

    def truncate(self, old, rem, new, vrf, af, dir_, rt):
        return [*self.enter(vrf, af), "  no route-target %s %s" % (dir_, rt)]

    def update(self, old, upd, new, vrf, af, dir_, rt):
        return [*self.enter(vrf, af), "  route-target %s %s" % (dir_, rt)]
