from art_export import ArtExporter
import json

class ArtemisExporter(ArtExporter):
    format_name = 'Artemis screen dump'
    format_description = """
Artemis screen dump format.
Assumes single frame, single layer document.
    """
    file_extension = 'sda'
    def run_export(self, out_filename, options):
        outjson = []
        for y in range(self.art.height):
            for x in range(self.art.width):
                char, fg, bg, xform = self.art.get_tile_at(0, 0, x, y)
                outjson.append([char, fg-1, bg-1])

        outfile = open(out_filename, 'w', encoding='utf-8')
        outfile.write(json.dumps(outjson, separators=(',', ':')))
        outfile.close()
        return True
