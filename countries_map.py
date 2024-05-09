countries with the number overlayed in geometry 
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize

class SoftLogNormalize(Normalize):
    """Custom normalization using a softer logarithmic scale."""
    def __init__(self, vmin=None, vmax=None):
        super().__init__(vmin, vmax)
        self.linthresh = 10  # Threshold below which the data is treated linearly (to avoid taking log(0))
        self.linscale = 1    # Scale factor for linear range

    def __call__(self, value, clip=None):
        return np.ma.masked_array(np.where(value <= self.linthresh,
                                           self.linscale * (value / self.linthresh),
                                           1 + np.log(value / self.linthresh)))

def standardize_country_names(data):
    # Dictionary to map your data country names to the GeoPandas format
    name_mapping = {
        'United States': 'United States of America',
        # Add other mappings here if needed
    }
    data['Name'] = data['Name'].replace(name_mapping)
    return data

def plot_app_usage_map(data_path):
    # Load app usage data
    data = pd.read_csv(data_path)

    # Standardize country names
    data = standardize_country_names(data)

    # Load world map
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    # remove Antartica 
    world = world[world['name'] != 'Antarctica']

    # Merge the app usage data with the world map
    world_data = world.merge(data, how="left", left_on="name", right_on="Name")

    # Fill NaNs and set color scale
    world_data['Users'] = world_data['Users'].fillna(0)
    vmin = world_data['Users'].min()
    vmax = 936  # Set the maximum scale to the highest user count

    # Using a soft logarithmic normalization
    norm = SoftLogNormalize(vmin=vmin, vmax=vmax)

    fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    world.boundary.plot(ax=ax, linewidth=0.8, color='black')
    world_data.plot(column='Users', ax=ax, legend=True, cmap='YlOrRd',
                    legend_kwds={'label': "Number of App Users by Country",
                                 'orientation': "horizontal"},
                    norm=norm)

    # Add text annotations for each country's user count
    for idx, row in world_data.iterrows():
        if row['Users'] > 0:  # Only label countries with users to avoid clutter
            x, y = row['geometry'].centroid.x, row['geometry'].centroid.y
            ax.text(x, y, int(row['Users']), fontsize=8, ha='center')

    ax.set_title('Microbiometer Usage Map')
    ax.set_axis_off()

    plt.show()

if __name__ == "__main__":
    data_path = 'countries.csv'  # Update this to the path of your CSV file
    plot_app_usage_map(data_path)
