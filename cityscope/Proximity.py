import osmnet
import pandana
import geopandas as gpd
import pandas as pd
import pandana as pdn
import numpy as np
from scipy.spatial import KDTree
import datetime
from brix import Indicator


class Proximity_Indicator(Indicator):
    def setup(self, grid,target_settings):
        self.target_settings = target_settings
        self.requires_geometry = True
        self.indicator_type = 'hybrid'
        
        nodes_df, edges_df = osmnet.load.network_from_bbox(
            bbox=tuple(grid.total_bounds), two_way=True)
        net = pdn.Network(
            nodes_df["x"], nodes_df["y"], edges_df["from"], edges_df["to"], edges_df[["distance"]])
        
        grid['centroid_x'] = grid.centroid.x
        grid['centroid_y'] = grid.centroid.y
        self.centroids = grid[['centroid_x','centroid_y']]
        grid['node'] = net.get_node_ids(grid.centroid.x, grid.centroid.y)
        self.nearest_nodes = grid['node']
        
        self.shortest_paths=pd.DataFrame(index=grid.index, columns=grid.index)
        for i,row in grid.iterrows():
            self.shortest_paths.iloc[i] = net.shortest_path_lengths([row["node"]] * len(grid), grid['node'])

    #'housing': {'column': 'residential','max': 1, 'from': 'office'},
    
    def return_indicator(self, geogrid_data):
        grid = geogrid_data.as_df()
        grid = pd.concat([grid,self.centroids],axis=1)
        threshold = 1000.0
        
        res = {'heatmap': {'type': 'FeatureCollection', 'properties': [], 'features': []}, 'numeric': []}
        
        for t in self.target_settings:
            res['heatmap']['properties'].append(t)
            m_from = grid['name']==self.target_settings[t]['from']
            m_to = grid['name']==self.target_settings[t]['column']
            grid[t]=0
            distances = self.shortest_paths.loc[m_from,m_to]#grid[m_to].index]
            if not distances.empty:
                prox = distances.min(axis=1)
                prox[prox>threshold]=threshold
                prox = 1 - prox/threshold
                grid.loc[m_from,t] = prox
                res['numeric'].append({'name': t, 'value': prox.mean(), 'viz_type': 'radar'})
            else:
                res['numeric'].append({'name': t, 'value': 0, 'viz_type': 'radar'})
                
        for i,cell in grid.iterrows():
            res['heatmap']['features'].append(
                {
                    'type': 'Feature',
                     'properties': [cell[t] for t in self.target_settings],
                     'geometry': {'type': 'Point', 'coordinates': [cell['centroid_x'],cell['centroid_y']]}
                }
             )
        #print (res)
        return res

