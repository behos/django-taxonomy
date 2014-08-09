import os
from bright_vc import check_tag
from fabric.context_managers import lcd, cd
from fabric.operations import local, run
from fabric.state import env

env.roledefs = {
    "live": [
        ".ohmypixelhosting.com"
    ]
}

app_dir = "~/apps"
project_name = "[project name]"
project_dir = os.path.join(app_dir, project_name)
repo = "git@bitbucket.org:behos/%s.git" % project_name

env.forward_agent = True


def pylint():
    local('flake8 **/*.py --max-line-length=120')
    local('flake8 *.py --max-line-length=120')


def compilemessages():
    command = '../manage compilemessages'
    with lcd("removals"):
        local(command)

    with lcd("removal_manager"):
        local(command)


def makemessages():
    command = '../manage makemessages --all -e html,txt -e xml'
    with lcd("removals"):
        local(command)

    with lcd("removal_manager"):
        local(command)


def tag_and_rollout(tag):
    create_tag(tag)
    rollout(tag)


def create_tag(tag):
    check_tag(tag)
    test_and_pylint()
    local('git tag %s' % tag)
    local('git push --tags')


def test_and_pylint():
    local("./manage test")
    pylint()


def rollout(tag):
    check_tag(tag)
    with cd(project_dir):
        run('git fetch -t')
        run('git checkout %s' % tag)
    update_environment()
    run_management_commands()
    increment_runner()


def initialise(db_name, db_user, db_pass):
    run("rm -Rf %s" % project_dir)
    git_clone()
    update_environment()
    create_db_settings(db_name, db_user, db_pass)
    run_management_commands()
    create_media_folder()
    create_static_symlinks()
    deploy()


def run_management_commands():
    with cd(project_dir):
        run(". activate; ./manage syncdb --migrate")
        run(". activate; echo 'yes' | ./manage collectstatic")
        run(". activate; echo 'yes' | ./manage compress")
        run(". activate; ./manage sync_translation_fields")
        run(". activate; ./manage update_translation_fields")


def deploy():
    with cd(project_dir):
        run("cp deploy/.htaccess ~/public_html/.htaccess")
        run("cp deploy/runner__0__.fcgi ~/public_html/runner__0__.fcgi")
        run("chmod go-w ~/public_html/.htaccess")
        run("chmod go-w ~/public_html/runner__0__.fcgi")


def increment_runner():
    with cd("~/public_html"):
        current_number_grabber = "ls -l | grep -o -P 'runner__\d+__' | grep -o -P '\d+'"
        output = run(current_number_grabber)
        current_number = int(output.split("\n")[-1])
        next_number = current_number + 1
        current_runner = "runner__%s__.fcgi" % current_number
        next_runner = "runner__%s__.fcgi" % next_number
        run("cp %s %s" % (current_runner, next_runner))
        run("sed -i.bak s/%s/%s/g .htaccess" % (current_runner, next_runner))
        run("rm %s" % current_runner)
        run("chmod go-w %s" % next_runner)


def git_clone():
    run("if [[ ! -d %s ]]; then mkdir %s; fi" % (app_dir, app_dir))
    with cd(app_dir):
        run("git clone %s" % repo)


def update_environment(clean=False):
    with cd(project_dir):
        run(". activate -u " + (" --clean" if clean else ""))


def create_db_settings(db_name, db_user, db_pass):
    file_path = os.path.join(project_dir, project_name, "local_db.py")
    run("touch %s" % file_path)
    run("echo \"DB_NAME='%s'\" > %s" % (db_name, file_path))
    run("echo \"DB_USER='%s'\" >> %s" % (db_user, file_path))
    run("echo \"DB_PASS='%s'\" >> %s" % (db_pass, file_path))


def create_media_folder():
    with cd(project_dir):
        run("if [[ ! -d media ]]; then mkdir media; fi;")
        run("if [[ ! -d media/uploads ]]; then mkdir media/uploads; fi;")
        run("chmod 755 media")
        run("chmod 755 media/uploads")


def tail_logs():
    with cd(project_dir):
        run('tail -f log/error.log')


def create_static_symlinks():
    with cd("~/public_html"):
        run("if [[ -e static ]]; then rm static; fi;  ln -s %s/static static" % project_dir)
        run("if [[ -e media ]]; then rm media; fi; ln -s %s/media media" % project_dir)
