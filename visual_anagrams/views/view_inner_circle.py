from PIL import Image
import numpy as np

import torch
import torchvision.transforms.functional as TF

from .permutations import make_inner_circle_perm
from .view_permute import PermuteView

class InnerCircleView(PermuteView):
    '''
    Implements an "inner circle" view, where a circle inside the image spins
    but the border stays still. Inherits from `PermuteView`, which implements
    the `view` and `inverse_view` functions as permutations. We just make
    the correct permutation here, and implement the `make_frame` method
    for animation
    '''
    def __init__(self):
        '''
        Make the correct "inner circle" permutations and pass it to the
        parent class constructor.
        '''
        self.perm_64 = make_inner_circle_perm(im_size=64, r=24)
        self.perm_256 = make_inner_circle_perm(im_size=256, r=96)
        self.perm_1024 = make_inner_circle_perm(im_size=1024, r=384)

        super().__init__(self.perm_64, self.perm_256, self.perm_1024)

    def make_frame(self, im, t):
        im_size = im.size[0]
        frame_size = int(im_size * 1.5)
        theta = -t * 180
        r = int(im_size / 8 * 3)    # TODO: Hardcoded

        # Convert to tensor
        im = torch.tensor(np.array(im) / 255.).permute(2,0,1)

        # Get mask of circle
        coords = torch.arange(0, im_size) - im_size / 2.
        xx, yy = torch.meshgrid(coords, coords)
        mask = xx**2 + yy**2 < r**2
        mask = torch.stack([mask]*3).float()

        # Get rotate image
        im_rotated = TF.rotate(im, theta)

        # Composite rotated circle + border together
        im = im * (1 - mask) + im_rotated * mask

        # Convert back to PIL
        im = Image.fromarray((np.array(im.permute(1,2,0)) * 255.).astype(np.uint8))

        # Paste on to canvas
        frame = Image.new('RGB', (frame_size, frame_size), (255, 255, 255))
        frame.paste(im, ((frame_size - im_size) // 2, (frame_size - im_size) // 2))

        return frame

