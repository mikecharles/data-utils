

"""
Contains methods for writing station data to a file.
"""


def terciles_to_txt(below, near, above, stn_ids, output_file):
    # Open output file
    f = open(output_file, 'w')
    # Loop over all stations
    f.write('id      below    near   above\n'.format())
    for i in range(len(stn_ids)):
        f.write('{:5s}   {:4.3f}   {:4.3f}   {:4.3f}\n'.format(
            stn_ids[i],
            below[i],
            near[i],
            above[i]
            )
        )
    # Close output file
    f.close()
