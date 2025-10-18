from hyp3_sdk import HyP3
import getpass
import asf_search as asf

class DataRetrieval:
    def __init__(self, aoi:str, opts, output_path, granule_1:str):
        self.aoi = aoi
        self.opts = opts
        self.output_path = output_path
        self.granule_1 = granule_1

    def retrieve_asf_data(self):
        username = input('Username:')
        password = getpass.getpass('Password:')
        results = asf.geo_search(intersectsWith=self.aoi, **self.opts)
        granules = self._get_granules(results)
        granules = self._remove_duplicates(granules)

        granules_slc = self._get_slc_granules(granules)
        self._retrieve_data(granules_slc, username, password)
        return granules_slc


    def _retrieve_data(self, granules_slc:list, username:str, password:str):
        for granule in range(len(granules_slc)):
            granule_2 = granules_slc[granule]
            job = HyP3(username=username, password=password).submit_insar_job(granule1=self.granule_1, granule2=granule_2,
                                                                              include_displacement_maps=True,
                                                                              looks='10x2', apply_water_mask=True)
            job = HyP3(username=username, password=password).watch(job)
            job.download_files(self.output_path)
            print(f'Downloaded for {granule_2}')

    @staticmethod
    def _get_slc_granules(granules:list) -> list:
        granules_slc = [x for x in granules if "SLC" in x]
        return [x for x in granules_slc if "OPERA" not in x]

    @staticmethod
    def _remove_duplicates(granules:list) -> list:
        return list(dict.fromkeys(granules))

    @staticmethod
    def _get_granules(results) -> list:
        granules = []
        for result in range(len(results)):
            granules.append(results[result].properties['sceneName'])
        granules.reverse()
        return granules

