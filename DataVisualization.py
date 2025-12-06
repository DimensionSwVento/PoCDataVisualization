import h3 
import pandas as pd
from pandas.api.types import is_string_dtype, is_numeric_dtype
import folium
import branca.colormap as cm



#gets data file 
ventoData = pd.read_csv("H3grid_intersect_Colombia.csv")

#function to get the h3 coordinates on a table and return an array of it
def grid_location(table):
        Hexagon=h3.cell_to_latlng(table['GRID_ID'])
        Boundaries=h3.cell_to_boundary(table['GRID_ID'])
        return pd.Series([Hexagon,Boundaries])


#use function to add the coordinates on the table in order to use it to graph
ventoData[['center','Boundaries']]=ventoData.apply(grid_location,axis=1)


#-----------------------------------------------------------

# Create a map using the location
locationCoordinates=(ventoData.iat[0,13])

DataMap = folium.Map(location=locationCoordinates, zoom_start=9)
folium.TileLayer("Cartodb dark_matter",overlay=False).add_to(DataMap)

#determine how many colormaps are going to be generated
numberOfmaps=(ventoData.shape[1])
# Columns to skip 
skip_columns = ['center', 'Boundaries', 'GRID_ID','Shape_Leng',
                'Shape_Length','Shape_Area','Shape_Leng','Shape_area','shape_Leng']

# Predefined color palette for categorical data
categorical_colors = [
    '#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231',
    '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe',
    '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000',
    '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080',
    '#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#6c5ce7',
    '#a29bfe', '#fd79a8', '#fdcb6e', '#00b894', '#00cec9',
    '#0984e3', '#74b9ff', '#a29bfe', '#fd79a8', '#fab1a0',
    '#ff7675', '#d63031', '#e17055', '#fdcb6e', '#ffeaa7',
    '#55efc4', '#81ecec', '#74b9ff', '#a29bfe', '#dfe6e9',
    '#b2bec3', '#636e72', '#2d3436', '#ff6348', '#ff4757',
    '#ffa502', '#ffd32a', '#05c46b', '#0fbcf9', '#3742fa',
    '#5f27cd', '#00d2d3', '#1dd1a1', '#10ac84', '#ee5a6f'
]

#use a index to go over the list of columns one by one and add them to a colormap
index=0
while index < numberOfmaps:
    column_name = ventoData.columns[index]
    
    # Skip non-numeric columns and coordinate columns
    if column_name in skip_columns:  
        index += 1
        continue
    # Check if column is not numeric and doesn't contain tuples/lists
    if is_string_dtype(ventoData.iloc[:, index]):
        # Creates a feature group for categorical data
        featureGroup = folium.FeatureGroup(name=column_name,show=False).add_to(DataMap)
        
        # Get unique categories
        unique_categories = ventoData.iloc[:, index].unique()
        n_categories = len(unique_categories)
        
        # Create color mapping for each category
        color_map = {}
        for i, category in enumerate(unique_categories):
            color_map[category] = categorical_colors[i % len(categorical_colors)]
        
        # Draw polygons with categorical colors
        for _, row in ventoData.iterrows():
            boundaries = [row['Boundaries']]
            category_value = row.iloc[index]
            color = color_map[category_value]
            
            folium.Polygon(
                locations=boundaries,
                color=color,
                weight=1,
                fill=True,
                fill_opacity=0.7,
                popup=f"{column_name}: {category_value}"
            ).add_to(featureGroup)
    # Check if column is numeric and doesn't contain tuples/lists
    if is_numeric_dtype(ventoData.iloc[:, index]):
        # Additional check to ensure no tuples/lists in the column
        sample_value = ventoData.iloc[0, index]
        if isinstance(sample_value, (tuple, list)):
            index += 1
            continue
        
        # Creates a feature group to add the graph onto the map as a layer
        featureGroup = folium.FeatureGroup(name=column_name,show=False).add_to(DataMap)
        
        # Creates the colormap using numeric data
        colormap = cm.LinearColormap(
            colors=["#002fff", '#ff0000'],
            vmin=ventoData.iloc[:, index].min(),
            vmax=ventoData.iloc[:, index].max()
        )
        
        for _, row in ventoData.iterrows():
            boundaries = [row['Boundaries']]
            count = row.iloc[index]
            color = colormap(count)
            folium.Polygon(
                locations=boundaries,
                color=color,
                weight=1,
                fill=True,
                fill_opacity=0.7,
                popup=f"{column_name}: {count}"
            ).add_to(featureGroup)
    
    index += 1

folium.LayerControl().add_to(DataMap)
DataMap.save("index.html")


