from art_export import ArtExporter
import json

class ArtemisExporter(ArtExporter):
    format_name = 'Artemis screen dump'
    format_description = """
Artemis screen dump format.
Assumes single frame, single layer document.

Attempts to figure out the screen mode from width and height.
If you are using a different palette from the default,
it will also be saved as the closest equivalent ink.
    """
    file_extension = 'sda'
    def run_export(self, out_filename, options):

        # Determine image mode
        modes = [[20,25], [40,25], [80,25], [80,50],
                 [40,50], [24,15], [16,10]]
        try: mode = modes.index([self.art.width,self.art.height])
        except: mode = 1    # Assume mode 1 if we can't figure it out

        outjson = {'v':1, 'mode': mode, 'ink':[], 'data': []}

        # Save the art
        for y in range(self.art.height):
            for x in range(self.art.width):
                char, fg, bg, xform = self.art.get_tile_at(0, 0, x, y)
                if fg == 0 or bg == 0:
                    outjson['data'].append(None)
                else:
                    outjson['data'].append([char, fg-1, bg-1])

        # If palette name isn't "artemis", try to save it as ink
        if self.art.palette.name != "artemis":
            for c in self.art.palette.colors[1:]:
                outjson['ink'].append([
                    round(c[0]/63.75),
                    round(c[1]/63.75),
                    round(c[2]/63.75)
                ])
        else:
            del outjson['ink']

        outfile = open(out_filename, 'w', encoding='utf-8')
        outfile.write(json.dumps(outjson, separators=(',', ':')))
        outfile.close()
        return True
