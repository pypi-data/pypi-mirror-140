# pygame-builder
 
### Introduction
Use this package to create a game in python in just a few lines of code. Built on top of Pygame, this module is perfect for beginners looking to make their first game. Experts may also find this useful when trying to save time. Enjoy!

### Code Format
```Python
from pygame_builder import Pygame, Element, Image

with Pygame(backgroundImage = image, size = [480, 270], windowCaption = "Pygame", fps = 60, backgroundColour = (0, 0, 0), backgroundSound = None) as pg:
    element = Element(image, screen : pygame.Surface, centerPosition = [0, 0], speed = [0, 0])
    pg.add(element)
    pg.loop(lambda : element.bouncingAnimation())
```

### Example
```Python
from pygame_builder import Pygame, Element, Image

ballGif = "/path/to/ball.gif"

with Pygame() as pg:
    ball = Element(Image(ballGif), pg, pg.getScreenCenter(), [2, 2])
    pg.add(ball)
    pg.loop(lambda : ball.bouncingAnimation())
```