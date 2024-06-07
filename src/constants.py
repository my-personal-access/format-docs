"""Constants folder."""
from logging import getLogger
from src.files import convert_lots_to_json

version = "v1" # v1 non-regression for old lot files
encoding = 'utf-8'

# Set project var to compile this file
project = ''

def init(project_: str):
    """Init shared variable."""
    global project
    project = project_
    
    global review_log
    review_log = getLogger("review_log")


def mkdocs():
    """Build path with project value."""
    return project + '/' + 'mkdocs.yml'


def docs():
    """Build path with project value."""
    return project + '/' + "docs"


def custom():
    """Build custom.css path from project name."""
    return docs() + '/custom.css'


def lots():
    """Build path with project value."""
    return docs() + '/' + 'lots'


def fichiers(extension: str = None):
    """Build path with project value."""
    return docs() + '/fichiers' + (('/' + extension) if extension is not None else '')


def images(extension: str = None):
    """Build path with project value."""
    return docs() + '/images' + (('/' + extension) if extension is not None else '')


orphans = "orphans"

def all__():
    """Build path with project value."""
    return [
    {
        'path': mkdocs(),
        'is_file': True,
        'data': { 
                'project_name': project.replace("hwi6_", ""),
                'lots': convert_lots_to_json()
        }
    },
    {
        'path': custom(),
        'is_file': True,
        'data': None
    },
    {
        'path': docs(),
        'is_file': False
    },
    {
        'path': lots(),
        'is_file': False
    },
    {
        'path': fichiers(),
        'is_file': False
    },
    {
        'path': images(),
        'is_file': False
    },
    {
        'path': fichiers(orphans),
        'is_file': False
    },
    {
        'path': images(orphans),
        'is_file': False
    }
]


pictures_ext = [
    'png',
    'jpeg',
    'jpg',
    'gif'
]

markdown_ext = 'md'

merged_tag = "MERGED"

lot = 'lot'
livrables = 'livrables'
targets = 'targets'
tokens = 'tokens'
bases = 'bases'

keys = {
    livrables: [],
    tokens: [],
    bases: [],
    targets: {}
}