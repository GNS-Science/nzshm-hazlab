from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

import xmltodict

from openquake.hazardlib import nrml, sourceconverter

def parse_rupture_sections(rupture_sections_ffp: Path):
    """
    Parses the rupture sections in the
    file into a dictionary
    """
    with rupture_sections_ffp.open("r") as f:
        doc = xmltodict.parse(f.read())

    doc = doc["nrml"]["geometryModel"]
    sections = {}
    for section in doc["section"]:
        id = int(section["@id"])
        cur_positions = []
        for line_string in section["kiteSurface"]["profile"]:
            cur_positions.append(
                np.asarray(
                    [
                        float(cur_value)
                        for cur_value in line_string["gml:LineString"][
                            "gml:posList"
                        ].split()
                    ]
                ).reshape(2, 3)
            )

        sections[id] = np.concatenate(cur_positions, axis=0)

    return sections

if __name__ == '__main__':
    ffp = Path("/home/chrisdc/tmp/read_rupture_surfaces/U2NhbGVkSW52ZXJzaW9uU29sdXRpb246MTIwNjcy-ruptures_sections.xml")
    section_ids = [0, 19]
    mesh_spacing = 4

    cv = sourceconverter.SourceConverter(rupture_mesh_spacing=mesh_spacing)
    sm = list(nrml.read_source_models([str(ffp)], cv))[0]

    # Load the sections manually
    sections = parse_rupture_sections(ffp)

    # Create some plots
    for cur_id in section_ids:
        section_coords = sections[cur_id]

        oq_surface = sm.sections[str(cur_id)]
        oq_mesh_coords = oq_surface.mesh.array

        # Create a plot
        fig = plt.figure(figsize=(16, 10))

        plt.scatter(section_coords[:, 0], section_coords[:, 1], c="b", s=20)

        plt.scatter(oq_mesh_coords[0].ravel(), oq_mesh_coords[1].ravel(), c="r", s=10)

        plt.title(f"Section {cur_id}")
        plt.tight_layout()
        plt.show()
        plt.close()