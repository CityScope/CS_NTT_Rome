from brix import Indicator
import math
import osmnx
import datetime



class Density_Indicator(Indicator):
    def setup(self, targets, grid):
        self.name='Density'
        self.viz_type='bar'
        self.targets = targets
                  
    def return_indicator(self, geogrid_data):
        grid = geogrid_data.as_df()
        side_length=geogrid_data.get_geogrid_props()['header']['cellSize']
        area = side_length*side_length
        volumes={t:0 for t in self.targets}
        tot_volume=0
        res = []
        for i,cell in grid.iterrows():
            name=cell['name'] 
            height=cell['height']
            
            if isinstance(height, list):
                height=height[-1]
                volumes[name] += area*height
                tot_volume += area*height
        for k,v in volumes.items():
            res.append({'name':k,'value':v/tot_volume})
            
        return res
    
    