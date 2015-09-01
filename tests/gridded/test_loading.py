from data_utils.gridded import loading, grid
import uuid


def test_load_obs():
    """
    Test load_obs function
    """
    # Shouldn't fail due to a missing file
    dates = ['20120101', '20120102']
    file_template = str(uuid.uuid4())
    data_type = 'bin'
    test_grid = grid.Grid('1deg-global')
    loading.load_obs(dates, file_template, data_type, test_grid)

    # Should run for a single day
    dates = ['20120101', '20120101']
    file_template = str(uuid.uuid4())
    data_type = 'bin'
    test_grid = grid.Grid('1deg-global')
    loading.load_obs(dates, file_template, data_type, test_grid)


def test_load_ens_fcsts():
    """
    Test load_fcsts function

    dates, file_template, data_type, grid, variable=None,
               level=None, record_num=None, fhr_range=None,
               fhr_int=6, fhr_stat='mean',
               num_members=None
    """
    # Shouldn't fail due to a missing file
    dates = ['20120101', '20120102']
    file_template = str(uuid.uuid4())
    data_type = 'bin'
    test_grid = grid.Grid('1deg-global')
    num_members = 11
    fhr_range = (150, 264)
    loading.load_ens_fcsts(dates, file_template, data_type, test_grid,
                           num_members, fhr_range)

    # Should run for a single day
    dates = ['20120101', '20120101']
    file_template = str(uuid.uuid4())
    data_type = 'bin'
    test_grid = grid.Grid('1deg-global')
    num_members = 11
    fhr_range = (150, 264)
    loading.load_ens_fcsts(dates, file_template, data_type, test_grid,
                           num_members, fhr_range)

    # Should run for a single fhr
    dates = ['20120101', '20120102']
    file_template = str(uuid.uuid4())
    data_type = 'bin'
    test_grid = grid.Grid('1deg-global')
    num_members = 11
    fhr_range = (150, 150)
    loading.load_ens_fcsts(dates, file_template, data_type, test_grid,
                           num_members, fhr_range)
