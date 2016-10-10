class ItemGui(object):
    def __init__(self, actions=(("drop", "drop", False),)):
        self.actions = actions

    def draw(self, font, surface, y, width, player, letter, stack):
        letterImage = font.render(letter, 1, (255, 255, 255))
        nameImage = font.render(player.getitemname(stack[0], False) if len(stack) == 1
                                else str(len(stack)) + " " + player.getitemname(stack[0], True), 1, (255, 255, 255))
        surface.blit(letterImage, (5, y + 32 - letterImage.get_height() // 2))
        surface.blit(stack[0].image.toSurf(), (16, y))
        surface.blit(nameImage, (74, y + 32 - nameImage.get_height() // 2))

    def receiveEvent(self, event):
        pass

    def getHeight(self):
        return 64
