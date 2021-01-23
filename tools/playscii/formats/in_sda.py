
from art_import import ArtImporter
import json

class ArtemisImporter(ArtImporter):

    format_name = 'Artemis Screen Dump'
    format_description = """
Artemis screen dump format.
    """

    def run_import(self, in_filename, options={}):
        self.set_art_charset('artemis')
        self.set_art_palette('artemis')

        with open(in_filename) as f:
            data = json.load(f)

        # determine size from mode
        modes = [[20,25], [40,25], [80,25], [80,50],
                 [40,50], [24,15], [16,10]]
        [xsize, ysize] = modes[data['mode']]
        self.resize(xsize, ysize)

        cell_iterator = iter(data['data'])
        for ypos in range(ysize):
            for xpos in range(xsize):
                cell = next(cell_iterator)
                if cell == None:
                    self.art.set_tile_at(0, 0, xpos, ypos, 0, 0, 0)
                else:
                    self.art.set_tile_at(0, 0, xpos, ypos, cell[0], cell[1]+1, cell[2]+1)

        return True
