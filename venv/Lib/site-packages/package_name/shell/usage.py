from time import ctime

# change package_name to your package name.
from package_name import __version__


def run():
    cur_time = ctime()
    # change package_name to your package name.
    text = f"""
    # package_name
    
    version {__version__} ({cur_time} +0800)
    """
    print(text)
