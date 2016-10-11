import items


class Armor(items.Item):
    def __init__(self, position, image, cage, world, name, pname, weight, fakename, fakepname, range,
                 defense, slot, **kwargs):
        items.Item.__init__(self, position, image, cage, world, name, pname, weight, fakename, fakepname, range,
                            **kwargs)
        self.defense = defense
        self.slot = slot
        print "kwargs: " + str(kwargs)

    __isarmor__ = True

    def defend(self, damage, damageType):
        return damage * self.defense[damageType]
