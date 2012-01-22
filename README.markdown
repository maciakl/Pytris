PyTris: Python Tetris
===

PyTris is a Tetris clone written entirely in Python. The game leverages the PyGame framework for 2D graphics generation. 

Design and Implementation Details
---

I have described the design and implementation process on my blog. You can read the related articles here:

  - [Design Document](http://www.terminally-incoherent.com/blog/2007/10/20/designing-a-tetris-clone-part-1/)
  - [Implementation and Post Mortem](http://www.terminally-incoherent.com/blog/2010/06/24/designing-a-tetris-clone-part-2/)

Dependencies
---

  - [PyGame](http://pygame.org/) (not included)


Known Issues
---

There is a persistent bug that is triggered when the game is forced to remove two non-contiguous lines. It slightly scrambles block positions when it drops the lines down.