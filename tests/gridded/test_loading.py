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
    loading.load_obs(dates, file_template=file_template, data_type=data_type,
                     grid=test_grid)
