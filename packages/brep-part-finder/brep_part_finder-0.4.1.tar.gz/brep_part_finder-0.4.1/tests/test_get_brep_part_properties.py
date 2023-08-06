import unittest
import brep_part_finder as bpf


class TestShape(unittest.TestCase):
    def setUp(self):

        self.brep_part_properties = bpf.get_brep_part_properties(
            "examples/ball_reactor.brep"
        )

    def test_number_of_parts(self):
        """Checks that all 8 of the solids in the Brep result in an entry"""

        assert len(self.brep_part_properties) == 8

    def test_dict_keys_exist(self):
        """Checks each Brep solid entry has the correct keys"""

        for entry in self.brep_part_properties.keys():
            assert "Center.x" in self.brep_part_properties[entry].keys()
            assert "Center.y" in self.brep_part_properties[entry].keys()
            assert "Center.z" in self.brep_part_properties[entry].keys()
            assert "Volume" in self.brep_part_properties[entry].keys()
            assert "BoundingBox.xmin" in self.brep_part_properties[entry].keys()
            assert "BoundingBox.ymin" in self.brep_part_properties[entry].keys()
            assert "BoundingBox.zmin" in self.brep_part_properties[entry].keys()
            assert "BoundingBox.xmax" in self.brep_part_properties[entry].keys()
            assert "BoundingBox.ymax" in self.brep_part_properties[entry].keys()
            assert "BoundingBox.zmax" in self.brep_part_properties[entry].keys()

    def test_dict_keys_are_correct_type(self):
        """Checks each Brep solid entry has the correct type"""

        for entry in self.brep_part_properties.keys():
            assert isinstance(self.brep_part_properties[entry]["Center.x"], float)
            assert isinstance(self.brep_part_properties[entry]["Center.y"], float)
            assert isinstance(self.brep_part_properties[entry]["Center.z"], float)
            assert isinstance(self.brep_part_properties[entry]["Volume"], float)
            assert isinstance(
                self.brep_part_properties[entry]["BoundingBox.xmin"], float
            )
            assert isinstance(
                self.brep_part_properties[entry]["BoundingBox.ymin"], float
            )
            assert isinstance(
                self.brep_part_properties[entry]["BoundingBox.zmin"], float
            )
            assert isinstance(
                self.brep_part_properties[entry]["BoundingBox.xmax"], float
            )
            assert isinstance(
                self.brep_part_properties[entry]["BoundingBox.ymax"], float
            )
            assert isinstance(
                self.brep_part_properties[entry]["BoundingBox.zmax"], float
            )

    def test_volumes_are_positive(self):
        """Checks each Brep solid entry has a positive value for the volume"""

        for entry in self.brep_part_properties.keys():
            assert self.brep_part_properties[entry]["Volume"] > 0.0
