import h3 
import pandas as pd
from pandas.api.types import is_string_dtype, is_numeric_dtype
import folium
import branca.colormap as cm
import gc


#------------------------ can still be worked on -------------------------------
#gets data file (to obtain the number of columns and names)
ventoData = pd.read_csv("H3grid_intersect_Colombia.csv")

#get amount of colums, and columns names
NumberOfColumns=ventoData.shape[1]
column_names = ventoData.columns

#purges the table from memory 
del ventoData
gc.collect()
#-------------------- defines variables and layers to be used --------------------
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

print("drawing data")

#creates a map located on the center of colombia
DataMap = folium.Map(location=(5.892063, -73.228054), zoom_start=9)
folium.TileLayer("Cartodb dark_matter",overlay=False).add_to(DataMap)

#list of columns to be skipped 
skip_columns = ['center', 'Boundaries', 'GRID_ID','Shape_Leng',
                'Shape_Length','Shape_Area','Shape_Leng','Shape_area','shape_Leng']


#creates the map layers to graph the data and skips the ignored columns 
for x in column_names:
    #does not create the layer if the column is to be ignored 
    if x in skip_columns:  
        continue
    
    featureGroup = folium.FeatureGroup(name=x,show=False).add_to(DataMap)

#function to get the h3 coordinates on a table and return an array of it
def grid_location(table):
        Hexagon=h3.cell_to_latlng(table['GRID_ID'])
        Boundaries=h3.cell_to_boundary(table['GRID_ID'])
        return pd.Series([Hexagon,Boundaries])

#-------------------------reloads the data in chunks---------------------------------

#reloads the data in chunks to be processed
for chunk in pd.read_csv('H3grid_intersect_Colombia_full_map.csv', chunksize=1000):
    
    ventoData=chunk
    #use function to add the coordinates on the table in order to use it to graph
    ventoData[['center','Boundaries']]=ventoData.apply(grid_location,axis=1)

    #reads the chunk of data, and uses an index to assign the name of the column to be read
    index=0
    print("drawing data")
    while index < NumberOfColumns:
        print(index)
        column_name = ventoData.columns[index]
        # Skips columns that do not need to be graphed, does not increase the index
        if column_name in skip_columns:  
            continue
        
        #determines if the column is filed with numerical or categorical data
        if is_string_dtype(ventoData.iloc[:, index]):
            #in case the data is categorical, gets the unique categories of the column
            #and assigns a color to it
            unique_categories = ventoData.iloc[:, index].unique()
            n_categories = len(unique_categories)
             #assigns the color
            color_map = {}
            for i, category in enumerate(unique_categories):
                color_map[category] = categorical_colors[i % len(categorical_colors)]
            
            #confirms the data name is the same
            if column_name == column_names[index]:
                #sets the information details
                for _, row in ventoData.iterrows():
                    boundaries = [row['Boundaries']]
                    category_value = row.iloc[index]
                    color = color_map[category_value]
                    #draws the polygon with colors and adds to the map
                    folium.Polygon(
                        locations=boundaries,
                        color=color,
                        weight=1,
                        fill=True,
                        fill_opacity=0.7,
                        popup=f"{column_name}: {category_value}"
                    ).add_to(column_name)
            else:
                print("column name does not match on index:")
                print(i)
                print(column_name)
                print(column_names[index])


        if is_numeric_dtype(ventoData.iloc[:, index]):
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
                ).add_to(column_name)
        index += 1
            
#-------------------------- creates the map------------------------------------------
folium.LayerControl().add_to(DataMap)
DataMap.save("map.html")

print (NumberOfColumns)
print (column_names)