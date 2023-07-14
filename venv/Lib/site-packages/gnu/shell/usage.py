from time import ctime

from gnu import __version__


def run():
    cur_time = ctime()
    text = f"""
    # gnu
    
    version {__version__} ({cur_time} +0800)
    """
    print(text)
