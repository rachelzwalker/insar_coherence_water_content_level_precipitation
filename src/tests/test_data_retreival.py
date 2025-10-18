import unittest
import os
import asf_search as asf

from src.DataRetrieval import DataRetrieval

aoi = 'POLYGON((-2.0395 53.5805,-2.0389 53.4645,-1.8289 53.4657,-1.8305 53.5834,-2.0395 53.5805))'
start = '2019-12-26'
end = '2019-12-31'

opts = {
    'platform': asf.PLATFORM.SENTINEL1,
    'start': start,
    'end': end,
    'beamMode': asf.BEAMMODE.IW,
    'flightDirection': asf.FLIGHT_DIRECTION.ASCENDING,
    'relativeOrbit': 132
}

granule_1 = 'S1B_IW_SLC__1SDV_20180402T174910_20180402T174937_010308_012C0D_BC27'

current_directory = os.getcwd()
resources_directory = f"{current_directory}/resources"

class MyTestCase(unittest.TestCase):
    def test_something(self):
        # DataRetrieval(aoi, opts, resources_directory, granule_1).retrieve_asf_data()
        strings_to_find = ['S1B', '20180402', '20191229']
        found_directories = []
        for directory_name in os.listdir(resources_directory):
            directory_path = os.path.join(resources_directory)
            if os.path.isdir(directory_path) and all(
                string in directory_name for string in strings_to_find): found_directories.append(directory_name)
        self.assertGreater(len(found_directories), 0)


if __name__ == '__main__':
    unittest.main()
