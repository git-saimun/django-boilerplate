"""
NOTE:
    the below code is to be maintained Python 2.x-compatible
    as the whole devxhub_python Django project initialization
    can potentially be run in Python 2.x environment
    (at least so we presume in `pre_gen_project.py`).

TODO: restrict devxhub_python Django project initialization to
      Python 3.x environments only
"""
from __future__ import print_function

import json
import os
import random
import shutil
import string

try:
    # Inspired by
    # https://github.com/django/django/blob/master/django/utils/crypto.py
    random = random.SystemRandom()
    using_sysrandom = True
except NotImplementedError:
    using_sysrandom = False

TERMINATOR = "\x1b[0m"
WARNING = "\x1b[1;33m [WARNING]: "
INFO = "\x1b[1;33m [INFO]: "
HINT = "\x1b[3;33m"
SUCCESS = "\x1b[1;32m [SUCCESS]: "

DEBUG_VALUE = "debug"


def remove_open_source_files():
    file_names = ["CONTRIBUTORS.txt", "LICENSE"]
    for file_name in file_names:
        os.remove(file_name)


def remove_gplv3_files():
    file_names = ["COPYING"]
    for file_name in file_names:
        os.remove(file_name)


def remove_custom_user_manager_files():
    os.remove(
        os.path.join(
            "{{devxhub_python.project_slug}}",
            "users",
            "managers.py",
        )
    )
    os.remove(
        os.path.join(
            "{{devxhub_python.project_slug}}",
            "users",
            "tests",
            "test_managers.py",
        )
    )


def remove_pycharm_files():
    idea_dir_path = ".idea"
    if os.path.exists(idea_dir_path):
        shutil.rmtree(idea_dir_path)

    docs_dir_path = os.path.join("docs", "pycharm")
    if os.path.exists(docs_dir_path):
        shutil.rmtree(docs_dir_path)


def remove_docker_files():
    shutil.rmtree("compose")

    file_names = ["local.yml", "production.yml", ".dockerignore"]
    for file_name in file_names:
        os.remove(file_name)
    if "{{ devxhub_python.editor }}".lower() == "pycharm":
        file_names = ["docker_compose_up_django.xml", "docker_compose_up_docs.xml"]
        for file_name in file_names:
            os.remove(os.path.join(".idea", "runConfigurations", file_name))


def remove_utility_files():
    shutil.rmtree("utility")



def remove_postgres_env_files():
    local_postgres_envs_path = os.path.join(".envs", ".local", ".postgres")
    production_postgres_envs_path = os.path.join(".envs", ".production", ".postgres")

    os.remove(local_postgres_envs_path)
    os.remove(production_postgres_envs_path)


def remove_mysql_env_files():
    local_mysql_envs_path = os.path.join(".envs", ".local", ".mysql")
    production_mysql_envs_path = os.path.join(".envs", ".production", ".mysql")

    os.remove(local_mysql_envs_path)
    os.remove(production_mysql_envs_path)


def remove_postgres_docker_folder():
    postgres_compose_path = os.path.join("compose", "production", "postgres")
    shutil.rmtree(postgres_compose_path)


def remove_mysql_docker_folder():
    mysql_compose_path = os.path.join("compose", "production", "mysql")
    shutil.rmtree(mysql_compose_path)


def remove_heroku_files():
    file_names = ["Procfile", "runtime.txt", "requirements.txt"]
    for file_name in file_names:
        if file_name == "requirements.txt" and "{{ devxhub_python.ci_tool }}".lower() == "travis":
            # don't remove the file if we are using travisci but not using heroku
            continue
        os.remove(file_name)
    remove_heroku_build_hooks()


def remove_heroku_build_hooks():
    shutil.rmtree("bin")


def remove_sass_files():
    shutil.rmtree(os.path.join("{{devxhub_python.project_slug}}", "static", "sass"))


def remove_gulp_files():
    file_names = ["gulpfile.js"]
    for file_name in file_names:
        os.remove(file_name)


def remove_webpack_files():
    shutil.rmtree("webpack")
    remove_vendors_js()


def remove_vendors_js():
    vendors_js_path = os.path.join(
        "{{ devxhub_python.project_slug }}",
        "static",
        "js",
        "vendors.js",
    )
    if os.path.exists(vendors_js_path):
        os.remove(vendors_js_path)


def remove_packagejson_file():
    file_names = ["package.json"]
    for file_name in file_names:
        os.remove(file_name)


def update_package_json(remove_dev_deps=None, remove_keys=None, scripts=None):
    remove_dev_deps = remove_dev_deps or []
    remove_keys = remove_keys or []
    scripts = scripts or {}
    with open("package.json", mode="r") as fd:
        content = json.load(fd)
    for package_name in remove_dev_deps:
        content["devDependencies"].pop(package_name)
    for key in remove_keys:
        content.pop(key)
    content["scripts"].update(scripts)
    with open("package.json", mode="w") as fd:
        json.dump(content, fd, ensure_ascii=False, indent=2)
        fd.write("\n")


def handle_js_runner(choice, use_docker, use_async):
    if choice == "Gulp":
        update_package_json(
            remove_dev_deps=[
                "@babel/core",
                "@babel/preset-env",
                "babel-loader",
                "concurrently",
                "css-loader",
                "mini-css-extract-plugin",
                "postcss-loader",
                "postcss-preset-env",
                "sass-loader",
                "webpack",
                "webpack-bundle-tracker",
                "webpack-cli",
                "webpack-dev-server",
                "webpack-merge",
            ],
            remove_keys=["babel"],
            scripts={
                "dev": "gulp",
                "build": "gulp generate-assets",
            },
        )
        remove_webpack_files()
    elif choice == "Webpack":
        scripts = {
            "dev": "webpack serve --config webpack/dev.config.js",
            "build": "webpack --config webpack/prod.config.js",
        }
        remove_dev_deps = [
            "browser-sync",
            "cssnano",
            "gulp",
            "gulp-imagemin",
            "gulp-plumber",
            "gulp-postcss",
            "gulp-rename",
            "gulp-sass",
            "gulp-uglify-es",
        ]
        if not use_docker:
            dev_django_cmd = "uvicorn config.asgi:application --reload" if use_async else "python manage.py runserver"
            scripts.update(
                {
                    "dev": "concurrently npm:dev:*",
                    "dev:webpack": "webpack serve --config webpack/dev.config.js",
                    "dev:django": dev_django_cmd,
                }
            )
        else:
            remove_dev_deps.append("concurrently")
        update_package_json(remove_dev_deps=remove_dev_deps, scripts=scripts)
        remove_gulp_files()


def remove_celery_files():
    file_names = [
        os.path.join("config", "celery_app.py"),
        os.path.join("{{ devxhub_python.project_slug }}", "users", "tasks.py"),
        os.path.join("{{ devxhub_python.project_slug }}", "users", "tests", "test_tasks.py"),
    ]
    for file_name in file_names:
        os.remove(file_name)


def remove_async_files():
    file_names = [
        os.path.join("config", "asgi.py"),
        os.path.join("config", "websocket.py"),
    ]
    for file_name in file_names:
        os.remove(file_name)


def remove_dottravisyml_file():
    os.remove(".travis.yml")


def remove_dotgitlabciyml_file():
    os.remove(".gitlab-ci.yml")


def remove_dotgithub_folder():
    shutil.rmtree(".github")


def generate_random_string(length, using_digits=False, using_ascii_letters=False, using_punctuation=False):
    """
    Example:
        opting out for 50 symbol-long, [a-z][A-Z][0-9] string
        would yield log_2((26+26+50)^50) ~= 334 bit strength.
    """
    if not using_sysrandom:
        return None

    symbols = []
    if using_digits:
        symbols += string.digits
    if using_ascii_letters:
        symbols += string.ascii_letters
    if using_punctuation:
        all_punctuation = set(string.punctuation)
        # These symbols can cause issues in environment variables
        unsuitable = {"'", '"', "\\", "$"}
        suitable = all_punctuation.difference(unsuitable)
        symbols += "".join(suitable)
    return "".join([random.choice(symbols) for _ in range(length)])


def set_flag(file_path, flag, value=None, formatted=None, *args, **kwargs):
    if value is None:
        random_string = generate_random_string(*args, **kwargs)
        if random_string is None:
            print(
                "We couldn't find a secure pseudo-random number generator on your "
                "system. Please, make sure to manually {} later.".format(flag)
            )
            random_string = flag
        if formatted is not None:
            random_string = formatted.format(random_string)
        value = random_string

    with open(file_path, "r+") as f:
        file_contents = f.read().replace(flag, value)
        f.seek(0)
        f.write(file_contents)
        f.truncate()

    return value


def set_django_secret_key(file_path):
    django_secret_key = set_flag(
        file_path,
        "!!!SET DJANGO_SECRET_KEY!!!",
        length=64,
        using_digits=True,
        using_ascii_letters=True,
    )
    return django_secret_key


def set_django_admin_url(file_path):
    django_admin_url = set_flag(
        file_path,
        "!!!SET DJANGO_ADMIN_URL!!!",
        formatted="{}/",
        length=32,
        using_digits=True,
        using_ascii_letters=True,
    )
    return django_admin_url

def generate_random_user():
    return generate_random_string(length=32, using_ascii_letters=True)


def generate_database_user(debug=False):
    return DEBUG_VALUE if debug else generate_random_user()


def set_database_user(file_path: str, value: str, database_engine: str):
    database_user = set_flag(
        file_path, f"!!!SET {database_engine.upper()}_USER!!!", value=value
    )
    return database_user


def set_database_password(file_path: str, database_engine: str, value: str = None):
    database_password = set_flag(
        file_path,
        f"!!!SET {database_engine.upper()}_PASSWORD!!!",
        value=value,
        length=64,
        using_digits=True,
        using_ascii_letters=True,
    )
    return database_password


def set_mysql_root_password(file_path: str, database_engine: str, value: str = None):
    database_root_password = set_flag(
        file_path,
        f"!!!SET {database_engine.upper()}_ROOT_PASSWORD!!!",
        value=value,
        length=74,
        using_digits=True,
        using_ascii_letters=True,
    )
    return database_root_password


def get_database_env_path(env: str, database_engine: str):
    local_postgres_envs_path = os.path.join(".envs", ".local", ".postgres")
    production_postgres_envs_path = os.path.join(".envs", ".production", ".postgres")
    local_mysql_envs_path = os.path.join(".envs", ".local", ".mysql")
    production_mysql_envs_path = os.path.join(".envs", ".production", ".mysql")

    is_mysql = database_engine == "mysql"
    is_postgres = database_engine == "postgresql"

    if env == "local":
        if is_mysql:
            return local_mysql_envs_path
        if is_postgres:
            return local_postgres_envs_path
    if env == "prod":
        if is_mysql:
            return production_mysql_envs_path
        if is_postgres:
            return production_postgres_envs_path

    return None


def set_celery_flower_user(file_path, value):
    celery_flower_user = set_flag(file_path, "!!!SET CELERY_FLOWER_USER!!!", value=value)
    return celery_flower_user


def set_celery_flower_password(file_path, value=None):
    celery_flower_password = set_flag(
        file_path,
        "!!!SET CELERY_FLOWER_PASSWORD!!!",
        value=value,
        length=64,
        using_digits=True,
        using_ascii_letters=True,
    )
    return celery_flower_password


def append_to_gitignore_file(ignored_line):
    with open(".gitignore", "a") as gitignore_file:
        gitignore_file.write(ignored_line)
        gitignore_file.write("\n")


def set_flags_in_envs(database_user, celery_flower_user, debug=False):
    local_django_envs_path = os.path.join(".envs", ".local", ".django")
    production_django_envs_path = os.path.join(".envs", ".production", ".django")

    selected_database = "{{ devxhub_python.database_engine }}"

    set_django_secret_key(production_django_envs_path)
    set_django_admin_url(production_django_envs_path)

    set_database_user(
        get_database_env_path(env="local", database_engine=selected_database),
        value=database_user,
        database_engine=selected_database,
    )
    set_database_password(
        get_database_env_path(env="local", database_engine=selected_database),
        database_engine=selected_database,
        value=DEBUG_VALUE if debug else None,
    )

    set_database_user(
        get_database_env_path(env="prod", database_engine=selected_database),
        value=database_user,
        database_engine=selected_database,
    )
    set_database_password(
        get_database_env_path(env="prod", database_engine=selected_database),
        database_engine=selected_database,
        value=DEBUG_VALUE if debug else None,
    )

    if selected_database == "mysql":
        set_mysql_root_password(
            get_database_env_path(env="local", database_engine=selected_database),
            database_engine=selected_database,
            value=DEBUG_VALUE if debug else None,
        )

        set_mysql_root_password(
            get_database_env_path(env="prod", database_engine=selected_database),
            database_engine=selected_database,
            value=DEBUG_VALUE if debug else None,
        )
        
    set_celery_flower_user(local_django_envs_path, value=celery_flower_user)
    set_celery_flower_password(local_django_envs_path, value=DEBUG_VALUE if debug else None)
    set_celery_flower_user(production_django_envs_path, value=celery_flower_user)
    set_celery_flower_password(production_django_envs_path, value=DEBUG_VALUE if debug else None)


def set_flags_in_settings_files():
    set_django_secret_key(os.path.join("config", "settings", "local.py"))
    set_django_secret_key(os.path.join("config", "settings", "test.py"))


def remove_envs_and_associated_files():
    shutil.rmtree(".envs")
    os.remove("merge_production_dotenvs_in_dotenv.py")
    shutil.rmtree("tests")


def remove_celery_compose_dirs():
    shutil.rmtree(os.path.join("compose", "local", "django", "celery"))
    shutil.rmtree(os.path.join("compose", "production", "django", "celery"))


def remove_node_dockerfile():
    shutil.rmtree(os.path.join("compose", "local", "node"))


def remove_aws_dockerfile():
    shutil.rmtree(os.path.join("compose", "production", "aws"))


def remove_drf_starter_files():
    os.remove(os.path.join("config", "api_router.py"))
    # shutil.rmtree(os.path.join("{{devxhub_python.project_slug}}", "users", "api"))
    os.remove(os.path.join("{{devxhub_python.project_slug}}", "users", "api", "serializers.py"))
    os.remove(os.path.join("{{devxhub_python.project_slug}}", "users", "api", "views.py"))
    os.remove(os.path.join("{{devxhub_python.project_slug}}", "users", "tests", "test_drf_urls.py"))
    os.remove(os.path.join("{{devxhub_python.project_slug}}", "users", "tests", "test_drf_views.py"))
    os.remove(os.path.join("{{devxhub_python.project_slug}}", "users", "tests", "test_swagger.py"))


def remove_graphene_starter_files():
    os.remove(os.path.join("config", "schema.py"))
    shutil.rmtree(os.path.join("api"))
    os.remove(os.path.join("{{devxhub_python.project_slug}}", "users", "api", "schema.py"))
    os.remove(os.path.join("{{devxhub_python.project_slug}}", "users", "api", "queries.py"))
    os.remove(os.path.join("{{devxhub_python.project_slug}}", "users", "api", "mutations.py"))
    os.remove(os.path.join("{{devxhub_python.project_slug}}", "users", "api", "filters.py"))
    os.remove(os.path.join("{{devxhub_python.project_slug}}", "users", "api", "inputs.py"))
    



def remove_tenant_files():
    shutil.rmtree(os.path.join("{{devxhub_python.project_slug}}", "client"))


def remove_storages_module():
    os.remove(os.path.join("{{devxhub_python.project_slug}}", "utils", "storages.py"))


def main():
    debug = "{{ devxhub_python.debug }}".lower() == "y"

    set_flags_in_envs(
        DEBUG_VALUE if debug else generate_random_user(),
        DEBUG_VALUE if debug else generate_random_user(),
        debug=debug,
    )
    set_flags_in_settings_files()

    if "{{ devxhub_python.open_source_license }}" == "Not open source":
        remove_open_source_files()
    if "{{ devxhub_python.open_source_license}}" != "GPLv3":
        remove_gplv3_files()

    if "{{ devxhub_python.username_type }}" == "username":
        remove_custom_user_manager_files()

    if "{{ devxhub_python.editor }}".lower() != "pycharm":
        remove_pycharm_files()

    if "{{ devxhub_python.use_docker }}".lower() == "y":
        if "{{ devxhub_python.database_engine }}".lower() == "postgresql":
            remove_mysql_docker_folder()
        elif "{{ devxhub_python.database_engine }}".lower() == "mysql":
            remove_postgres_docker_folder()
        
        remove_utility_files()
    else:
        remove_docker_files()

    if "{{ devxhub_python.database_engine }}".lower() == "postgresql":
        remove_mysql_env_files()
    elif "{{ devxhub_python.database_engine }}".lower() == "mysql":
        remove_postgres_env_files()


    if "{{ devxhub_python.use_docker }}".lower() == "y" and "{{ devxhub_python.cloud_provider}}" != "AWS":
        remove_aws_dockerfile()

    if "{{ devxhub_python.use_heroku }}".lower() == "n":
        remove_heroku_files()
    elif "{{ devxhub_python.frontend_pipeline }}" != "Django Compressor":
        remove_heroku_build_hooks()

    if "{{ devxhub_python.use_docker }}".lower() == "n" and "{{ devxhub_python.use_heroku }}".lower() == "n":
        if "{{ devxhub_python.keep_local_envs_in_vcs }}".lower() == "y":
            print(
                INFO + ".env(s) are only utilized when Docker Compose and/or "
                "Heroku support is enabled so keeping them does not "
                "make sense given your current setup." + TERMINATOR
            )
        remove_envs_and_associated_files()
    else:
        append_to_gitignore_file(".env")
        append_to_gitignore_file(".envs/*")
        if "{{ devxhub_python.keep_local_envs_in_vcs }}".lower() == "y":
            append_to_gitignore_file("!.envs/.local/")

    if "{{ devxhub_python.frontend_pipeline }}" in ["None", "Django Compressor"]:
        remove_gulp_files()
        remove_webpack_files()
        remove_sass_files()
        remove_packagejson_file()
        if "{{ devxhub_python.use_docker }}".lower() == "y":
            remove_node_dockerfile()
    else:
        handle_js_runner(
            "{{ devxhub_python.frontend_pipeline }}",
            use_docker=("{{ devxhub_python.use_docker }}".lower() == "y"),
            use_async=("{{ devxhub_python.use_async }}".lower() == "y"),
        )

    if "{{ devxhub_python.cloud_provider }}" == "None" and "{{ devxhub_python.use_docker }}".lower() == "n":
        print(
            WARNING + "You chose to not use any cloud providers nor Docker, "
            "media files won't be served in production." + TERMINATOR
        )
        remove_storages_module()

    if "{{ devxhub_python.use_celery }}".lower() == "n":
        remove_celery_files()
        if "{{ devxhub_python.use_docker }}".lower() == "y":
            remove_celery_compose_dirs()

    if "{{ devxhub_python.ci_tool }}" != "Travis":
        remove_dottravisyml_file()

    if "{{ devxhub_python.ci_tool }}" != "Gitlab":
        remove_dotgitlabciyml_file()

    if "{{ devxhub_python.ci_tool }}" != "Github":
        remove_dotgithub_folder()

    if "{{ devxhub_python.use_drf }}".lower() == "n":
        remove_drf_starter_files()

    if "{{ devxhub_python.use_graphene }}".lower() == "n":
        remove_graphene_starter_files()

    if "{{ devxhub_python.use_async }}".lower() == "n":
        remove_async_files()
        
    if "{{ devxhub_python.use_tenants }}".lower() == "n":
        remove_tenant_files()

    print(SUCCESS + "Project initialized, keep up the good work!" + TERMINATOR)


if __name__ == "__main__":
    main()
