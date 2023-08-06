from ais_data_to_tspi import data_to_TSPI


def test_data_to_tspi():
    data_to_TSPI.convert_ais_data_to_tspi('../AIS_2021_01_01.csv', create_tspi_files=True,
                                          output_path='C:/Users/U220739/OneDrive - L3Harris Technologies '
                                                      'Inc/Documents/Lit Cap/data/', min_lat=37, max_lat=38,
                                          min_lon=-77, max_lon=-75)
