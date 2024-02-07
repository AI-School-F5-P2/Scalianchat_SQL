import tempfile


def save_chart_code_to_temp_file(chart):
    '''
    Save the chart code to a temporary file
    '''
    with tempfile.NamedTemporaryFile(mode='w', suffix=".py", delete=False) as file:
        file.write(chart)
        return file.name