import os


class Config:
    SECRET_KEY = "your-secret-key"
    DATABASE = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'instance',
        'flask.sqlite'
    )
