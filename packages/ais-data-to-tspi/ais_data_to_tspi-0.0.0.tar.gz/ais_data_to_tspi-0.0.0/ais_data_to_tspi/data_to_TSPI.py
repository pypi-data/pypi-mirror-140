import pandas as pd


def convert_ais_data_to_tspi(data_path, create_tspi_files, output_path, min_lat, max_lat, min_lon, max_lon):

    df = pd.read_csv(data_path)
    print('Initial number of IDs:', len(df['MMSI'].unique()))

    df = df[(min_lat < df['LAT']) & (df['LAT'] < max_lat)]
    df = df[(min_lon < df['LON']) & (df['LON'] < max_lon)]

    list_of_ids = df['MMSI'].unique()
    print('Reduction by latitude & longitude: ', len(list_of_ids))

    # extract and calculate time in seconds
    df[['Date', 'Time']] = df['BaseDateTime'].str.split('T', 1, expand=True)
    df[['Hours', 'Minutes', 'Seconds']] = df['Time'].str.split(':', 2, expand=True)
    df['Seconds_Total'] = df['Hours'].astype(int) * 3600 + df['Minutes'].astype(int) * 60 + df['Seconds'].astype(int)

    # create TSPI file for each individual ship
    ds = {}

    list_of_ids = df['MMSI'].unique()
    for id in list_of_ids:
        df1 = df[df['MMSI'] == id].sort_values(by=['Seconds_Total'], ascending=True)

        ds[id] = {}

        i = 0
        for index, row in df1.iterrows():
            i += 1
            ds[id][row['Seconds_Total']] = {'time': row['Seconds_Total'], 'latitude': row['LAT'],
                                            'longitude': row['LON'], 'altitude': 0, 'speed': row['SOG'],
                                            'heading': row['Heading'], 'pitch': 0, 'roll': 0}

    # begin outputting to file format
    if create_tspi_files:
        i = 1
        for id in ds:
            file_name = output_path + 'tspi_out-' + str(i) + '.tspi'
            f = open(file_name, 'w')

            # print if moving, otherwise print the first non-moving point and ignore subsequent non-moving points
            repetitive_point = False
            for t in ds[id]:
                if repetitive_point and ds[id][t]['speed'] == 0:
                    repetitive_point = True
                else:
                    str_out = str(ds[id][t]['time']) + ' ' + str(ds[id][t]['latitude']) + ' ' + \
                              str(ds[id][t]['longitude']) + ' ' + str(ds[id][t]['altitude']) + ' ' + \
                              str(ds[id][t]['speed']) + ' ' + str(ds[id][t]['heading']) + ' ' + \
                              str(ds[id][t]['pitch']) + ' ' + str(ds[id][t]['roll']) + '\n '
                    f.write(str_out)
                    repetitive_point = False
                    if ds[id][t]['speed'] == 0:
                        repetitive_point = True
            i += 1

    print('TSPI file generation complete.')
    return ds
