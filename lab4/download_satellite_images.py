from io import BytesIO
from math import asinh, floor, pi, radians, tan
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image


ZOOM = 14
TILES_PER_SIDE = 4
OUTPUT = Path(__file__).parent / "satellite_data"
URL = (
    "https://tiles.maps.eox.at/wmts/1.0.0/"
    "s2cloudless-2020_3857/default/g/{z}/{y}/{x}.jpg"
)


def tile_number(latitude, longitude, zoom):
    size = 2**zoom
    x = floor((longitude + 180) / 360 * size)
    y = floor((1 - asinh(tan(radians(latitude))) / pi) / 2 * size)
    return x, y


def download_image(name, latitude, longitude):
    center_x, center_y = tile_number(latitude, longitude, ZOOM)
    start_x = center_x - TILES_PER_SIDE // 2
    start_y = center_y - TILES_PER_SIDE // 2
    mosaic = Image.new("RGB", (256 * TILES_PER_SIDE, 256 * TILES_PER_SIDE))

    for row in range(TILES_PER_SIDE):
        for column in range(TILES_PER_SIDE):
            x = start_x + column
            y = start_y + row
            request = Request(URL.format(z=ZOOM, y=y, x=x), headers={"User-Agent": "ML4space lab"})
            with urlopen(request) as response:
                tile = Image.open(BytesIO(response.read())).convert("RGB")
            mosaic.paste(tile, (column * 256, row * 256))

    path = OUTPUT / f"{name}.png"
    mosaic.save(path)
    print(f"Saved {path} ({mosaic.width} x {mosaic.height})")


OUTPUT.mkdir(exist_ok=True)
download_image("forest_amazon", -3.0, -62.0)
download_image("urban_riyadh", 24.7136, 46.6753)
