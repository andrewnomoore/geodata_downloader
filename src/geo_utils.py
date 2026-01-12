import geopandas as gpd
from pathlib import Path
from shapely.wkt import loads
from .exceptions import WKTError

def is_wkt(text: str) -> bool:
    """Check if the input string is in WKT format."""
    try:
        loads(text)
        return True
    except Exception:
        return False

def to_openeo_wkt(aoi: Path | str | None) -> str | None:
    """Returns WKT coordinates of area extent"""
    if aoi is None:
        return None

    if isinstance(aoi, str):
        if is_wkt(aoi):
            return aoi
        else:
            try:
                gdf = gpd.read_file(aoi)
                return gdf.unary_union.wkt
            except Exception as e:
                raise WKTError(e)

    try:
        gdf = gpd.read_file(aoi)
        return gdf.unary_union.wkt
    except Exception as e:
        raise WKTError(e)

def geojson_to_shapefile(geojson_path: Path | str, shapefile_path: Path | str | None = None, force_crs: str | int | None = None,) -> Path:
    """Convert a .geojson file to an ESRI Shapefile (.shp).

    Parameters
    ----------
    geojson_path : Path | str
        Path to the input .geojson file.
    shapefile_path : Path | str | None, optional
        Desired output .shp path or a directory. If None, writes next to the
        input with the same stem and a .shp suffix.
    force_crs : str | int | None, optional
        CRS to set when the input has no CRS. Examples: "EPSG:4326" or 4326.

    Returns
    -------
    Path
        Path to the written .shp file.
    """
    input_path = Path(geojson_path)
    if shapefile_path is None:
        output_path = input_path.with_suffix(".shp")
    else:
        output_candidate = Path(shapefile_path)
        if output_candidate.suffix.lower() == "":
            # Treat as directory; create filename from input stem
            output_path = output_candidate / f"{input_path.stem}.shp"
        elif output_candidate.suffix.lower() != ".shp":
            # If a non-.shp file was provided, coerce to .shp
            output_path = output_candidate.with_suffix(".shp")
        else:
            output_path = output_candidate

    output_path.parent.mkdir(parents=True, exist_ok=True)

    gdf = gpd.read_file(input_path)

    if gdf.crs is None and force_crs is not None:
        gdf = gdf.set_crs(force_crs)

    gdf.to_file(output_path, driver="ESRI Shapefile")

    return output_path
