# This module will transform data from AIS (https://marinecadastre.gov/ais/) into individual TSPI files according to the MMSI index provided in the data file. 

### The user must specify minimum and maximum latitude and longitude (in double format) for the creation of the TSPI files. 
### This module will also remove repetitive points when entities are not moving (speed = 0) to reduce the redundancy of the data that is stored within the TSPI files.

### The function convert_ais_data_to_tspi reads in the data path, a boolean determining whether to create TSPI files, the output path, minimum latitude, maximum latitude, minimum longitude, and maximum longitude.

###  The min/max latitude/longitude inputs allow the user to sort out a subset of the dataset entered. This function will only capture those points that lie within the specified range. If the data extends beyond the range specifed, those points will not be included. 