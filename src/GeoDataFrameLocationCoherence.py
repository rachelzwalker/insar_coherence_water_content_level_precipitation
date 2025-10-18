import os
from operator import itemgetter

import geopandas as gpd
import pandas as pd
import rasterio
from rasterio.features import shapes
from rasterio.transform import rowcol
from shapely.geometry import mapping
from rasterio.mask import mask
from shapely.geometry import Point


from src.ListOfFiles import GetListShapefiles, get_list_of_files
from src.DirectorySearchTiff import DirectorySearchTif


class GeoDataframeLocationCoherence:
    def __init__(self, path: str, location: str, reference_date: str = '20180402T175024',
                 sentinel_focus: None | str = None, path_to_points: None | str = None, input_data: str = 'polygon',
                 buffer=None, data_series_dates_to_remove=None):
        self.path = path
        self.location = location
        self.reference_date = reference_date
        self.sentinel_focus = sentinel_focus
        self.path_to_points = path_to_points
        self.input_data = input_data
        self.buffer = buffer
        self.data_to_remove = data_series_dates_to_remove

    '''
    sentinel_focus should equal none if want all, B is only BB and A if not BB
    '''

    def dataframe_coherence(self) -> pd.DataFrame:
        site_tifs = self._get_site_specific_tifs()
        focused_file_list = self._get_focused_file_lists(site_tifs)
        sorted_list_files = self._get_sorted_list_based_on_date(focused_file_list)

        if self.input_data == 'polygon':
            list_of_tiffs = DirectorySearchTif(root_directory=self.path, sentinel_focus=self.sentinel_focus).get_tifs()

            tif_file_example = list_of_tiffs[0]
            points = self._extract_pixel_centroids(tif_file_example)

            geodataframe = gpd.GeoDataFrame()


            tiff_name_list = []
            for file in list_of_tiffs:
                tiff_name = [file.split("/")[-1]]
                tiff_name_list.append(tiff_name)


                early_date = [x.split('_')[1] for x in tiff_name]
                late_date = [x.split('_')[2] for x in tiff_name]

                with rasterio.open(file) as src:
                    tiff_crs = src.crs

                results = []
                for index, point in points.iterrows():
                    # Get the closest raster value to the point
                    with rasterio.open(file) as src:
                        value = self._get_closest_raster_value(point.geometry, src)
                        points.drop(list(points.filter(regex='OSGB36|Site')), axis=1, inplace=True)

                        if early_date[0] < self.reference_date:
                            date_time = early_date[0]
                        else:
                            date_time = late_date[0]
                    date = date_time[:8]
                    temp_df = pd.DataFrame([[point.geometry, date, value]], columns=['geometry', 'Date', f'mean_{index}'])
                    results.append(temp_df)

                # Combine extracted values
                merged_df = pd.concat(results)

                # Merge with original geodataframe on Geometry and Date
                geodataframe = geodataframe.merge(merged_df, on=['geometry', 'Date'], how='left')

        elif self.input_data == 'point':
            list_of_shapefiles = GetListShapefiles(shape_file_path=self.path_to_points).get_list_of_shapefiles()

            site_shapefile = [x for x in list_of_shapefiles if self.location in x]

            site = site_shapefile[0]


            list_of_tiffs = DirectorySearchTif(root_directory=self.path, sentinel_focus=self.sentinel_focus).get_tifs()

            geodataframe = gpd.GeoDataFrame()

            tiff_name_list = []
            for file in list_of_tiffs:
                tiff_name = [file.split("/")[-1]]
                tiff_name_list.append(tiff_name)


                early_date = [x.split('_')[1] for x in tiff_name]
                late_date = [x.split('_')[2] for x in tiff_name]

                with rasterio.open(file) as src:
                    tiff_crs = src.crs

                points = gpd.read_file(f'{self.path_to_points}/{site}')
                points = points.to_crs(tiff_crs)

                if self.buffer is None:

                    # Iterate through each reprojected point
                    for index, point in points.iterrows():
                        # Get the closest raster value to the point
                        with rasterio.open(file) as src:
                            closest_value = self._get_closest_raster_value(point.geometry, src)
                            points['mean'] = closest_value
                            points.drop(list(points.filter(regex='OSGB36|Site')), axis=1, inplace=True)

                            if early_date[0] < self.reference_date:
                                date_time = early_date[0]
                            else:
                                date_time = late_date[0]
                        points['Date'] = date_time[:8]
                        geodataframe = pd.concat([geodataframe, points])


                else:
                    for index, point in points.iterrows():
                        point_geom = point.geometry
                        buffered_point = point_geom.buffer(self.buffer)  # Adjust the buffer size as needed
                        geo = mapping(buffered_point)

                        with rasterio.open(file) as src:
                            out_image, out_transform = mask(src, [geo], crop=True)

                            mean_value = out_image.mean() if out_image.size > 0 else None
                            points['mean'] = mean_value

                            points.drop(list(points.filter(regex='OSGB36|Site')), axis=1, inplace=True)

                            if early_date[0] < self.reference_date:
                                date_time = early_date[0]
                            else:
                                date_time = late_date[0]
                        points['Date'] = date_time[:8]
                        geodataframe = pd.concat([geodataframe, points])


            geodataframe['Date'] = pd.to_datetime(geodataframe['Date'])
            print(f'Maximum date is {geodataframe['Date'].max()}')

            if self.data_to_remove is not None:
                geodataframe = geodataframe[~geodataframe['Date'].isin(self.data_to_remove)]

            geodataframe = geodataframe.set_index(('Date'))
            return geodataframe

    # Function to get the closest raster value to a point
    @staticmethod
    def _get_closest_raster_value(point, src):
        row, col = rowcol(src.transform, point.x, point.y)
        value = src.read(1, window=((row, row + 1), (col, col + 1)))
        return value[0][0]

    def _get_complete_geo_dataframe(self, name, heading_name, sorted_list_files, geo_dataframe) -> pd.DataFrame:
        with rasterio.open(f'{self.path}/{name}') as src:
            raster_data = src.read(1)
            shapes_gen = (
                {'properties': {heading_name: value}, 'geometry': shape}
                for shape, value in shapes(raster_data, mask=None)
            )
            if name == sorted_list_files[0]:
                return gpd.GeoDataFrame.from_features(shapes_gen, crs=src.crs)
            else:
                interim_gdf = gpd.GeoDataFrame.from_features(shapes_gen, crs=src.crs)
                return pd.merge(geo_dataframe, interim_gdf, on='geometry')

    def _get_column_names_from_dates(self, sorted_list_files: list) -> list:
        column_headings = []
        list_of_early_dates = [x.split('_')[2] for x in sorted_list_files]
        list_of_late_dates = [x.split('_')[3] for x in sorted_list_files]
        for early_date, late_date in zip(list_of_early_dates, list_of_late_dates):
            if early_date < self.reference_date:
                column_headings.append(early_date)
            else:
                column_headings.append(late_date)
        return column_headings

    @staticmethod
    def _get_sorted_list_based_on_date(focused_files: list) -> list:  # need to check this works
        return sorted(focused_files, key=lambda x: itemgetter(3)(x.split('_')))

    @staticmethod
    def _get_focused_file_lists(site_tifs:list) -> list:
        focused_files_lists = []
        for filename in site_tifs:
            file = os.path.split(filename)[-1]
            if 'corr' in file and 'xml' not in file:
                focused_files_lists.append(file)
        return focused_files_lists

    def _get_site_specific_tifs(self) -> list:
        if self.input_data == 'polygon':
            all_files = get_list_of_files(self.path)
            site_tifs = all_files
        else:
            all_files = self.path
            site_tifs = [x for x in all_files if self.location in x]
        return site_tifs

    def _extract_pixel_centroids(self, tiff_path):
        # Load the polygon
        polygon_gdf = gpd.read_file(self.path_to_points)

        # Open the raster
        with rasterio.open(tiff_path) as src:
            raster_crs = src.crs
            if polygon_gdf.crs != raster_crs:
                polygon_gdf = polygon_gdf.to_crs(raster_crs)

            polygon = polygon_gdf.unary_union  # Merge all polygons if multiple exist

            out_image, out_transform = rasterio.mask.mask(src, [polygon], crop=True)
            out_image = out_image[0]  # Read the first band
            nodata = src.nodata
            rows, cols = out_image.shape  # Get new raster dimensions

            centroids = []
            sites = []

            # Iterate over pixels
            for row in range(rows):
                for col in range(cols):
                    # Get pixel centroid
                    x, y = out_transform * (col + 0.5, row + 0.5)  # Center of pixel
                    point = Point(x, y)

                    # Check if the point is inside the polygon
                    if polygon.contains(point):
                        centroids.append(point)
                        sites.append(row)

        gdf = gpd.GeoDataFrame({"Site": sites}, geometry=centroids, crs=src.crs)
        gdf.index = gdf['Site']
        return gdf