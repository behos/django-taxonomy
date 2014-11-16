from bright_vc import check_tag
from fabric.context_managers import lcd
from fabric.operations import local
import taxonomy

repo = "git@bitbucket.org:behos/taxonomy.git"


def pylint():
    local('flake8 **/*.py --max-line-length=120')
    local('flake8 *.py --max-line-length=120')


def compilemessages():
    command = '../manage compilemessages'
    with lcd("taxonomy"):
        local(command)


def makemessages():
    command = '../manage makemessages --all -e html,txt -e xml'
    with lcd("taxonomy"):
        local(command)


def create_tag():
    tag = "v" + taxonomy.__version__
    check_tag(tag)
    test_and_pylint()
    local('git tag %s' % tag)
    local('git push --tags')


def test_and_pylint():
    local("./manage test")
    pylint()


def publish():
    create_tag()
    local('python setup.py register -r pypi')
    local('python setup.py sdist upload -r pypi')
