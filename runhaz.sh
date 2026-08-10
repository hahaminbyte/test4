#!/bin/bash

base_dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
server_dir="$base_dir/server"

# check python is installed
if command -v python3 > /dev/null 2>&1; then
    python_cmd=$(command -v python3)
    base_py_cmd="$python_cmd $server_dir/manage.py "
elif command -v python > /dev/null 2>&1; then
    python_cmd=$(command -v python)
    base_py_cmd="$python_cmd $server_dir/manage.py "
else
  echo "Python3 not found"
  exit 1
fi

# check python version is at least 3.8
ver=$($python_cmd -V 2>&1 | sed 's/.* \([0-9]\).\([0-9]\).*/\1\2/')
if [ "$ver" -eq "31" ]; then
    :
elif [ "$ver" -lt "38" ]; then
    echo "Python version 3.8 or greater is expected, received $ver"
    exit 1
fi


print_usage() {
   # Display help
   echo "Command line utility to help develop Haztrak"
   echo
   echo "Syntax: $(basename "$0") <option>"
   echo "options:"
   echo "-d, --db            Prepare the local development database (migrate, no Docker required)"
   echo "-l, --load          load initial database data from fixture files"
   echo "-p, --pre-commit    installs hooks, if necessary, and runs pre-commit run --all-files"
   echo "-o, --openapi		   Generate the Open API Schema to /docs/API/"
   echo "-e, --erd           Graph the django models to an entity relationship diagram (ERD), requires graphviz"
   echo "-c, --coverage      Generate a coverage report for the python server"
   echo "-h, --help          Print this help message"
   echo
}

# prints colored text
print_style() {
    if [ "$2" == "info" ] ; then
        COLOR="96m";
    elif [ "$2" == "success" ] ; then
        COLOR="92m";
    elif [ "$2" == "warning" ] ; then
        COLOR="93m";
    elif [ "$2" == "danger" ] ; then
        COLOR="91m";
    else #default color
        COLOR="0m";
    fi
    START_COLOR="\e[$COLOR";
    END_COLOR="\e[0m";
    printf "$START_COLOR%b$END_COLOR" "$1";
}

load_local_django_env() {
    # Load a local (non-Docker) env file if it exists.
    # This script does not automatically read `.env` for Django.
    local env_file=""
    if [ -f "$base_dir/configs/.env.local" ]; then
        env_file="$base_dir/configs/.env.local"
    elif [ -f "$base_dir/configs/.env.dev" ]; then
        env_file="$base_dir/configs/.env.dev"
    fi

    if [ -n "$env_file" ]; then
        # Export all variables defined in env_file for `manage.py`.
        set -a
        # shellcheck disable=SC1090
        source "$env_file"
        set +a
    fi
}

start_db(){
    echo "Preparing local database..."
    load_local_django_env

    # If Docker is available, we can also spin up the dependent services.
    # Otherwise we assume Postgres/Redis are already running locally.
    if command -v docker >/dev/null 2>&1 && [ -f "$base_dir/compose.yaml" ]; then
        print_style "Docker detected: starting db/redis via compose.yaml (optional)" "info"
        docker_exec=$(command -v docker)
        eval "$docker_exec compose -f $base_dir/compose.yaml --env-file $base_dir/configs/.env.dev up -d db redis"
    else
        print_style "Docker not used. Ensure Postgres is running on localhost:5432." "warning"
    fi

    # Apply migrations so the database is usable.
    eval "$base_py_cmd migrate"
    exit 0
}

load_django_fixtures() {
    # load initial data, good if you need to drop the dev database
    load_local_django_env
    fixtures_dir="$server_dir/fixtures"
    exec_cmd="$base_py_cmd loaddata $fixtures_dir/dev_data.yaml"
    eval "$exec_cmd"
    exit
}

generate_api_schema() {
    print_style "Generating Open API schema...\n" "success";
    exec_cmd="$base_py_cmd spectacular --settings haztrak.settings --file $base_dir/docs/api/postman/schemas/openapi-schema.yaml"
    eval "$exec_cmd"
    exit
}


graph_models() {
    print_style "Generating Entity Relationship Diagram...\n" "success";
    exec_cmd="$base_py_cmd graph_models rcrasite handler core org wasteline manifest site profile\
    -g \
    --settings haztrak.settings \
    --rankdir=RL \
    --arrow-shape=normal \
    --exclude-models=*BaseModel \
    --disable-abstract-fields \
    -o $base_dir/docs/guide/src/assets/images/erd.png"
    eval "$exec_cmd"
    exit
}

run_pre_commit() {
    # This will install the pre-commit script, and run whatever pre-commit
    # hooks we have configured. Great to run before committing as a pre-commit hook
    # failure will abort the commit
    if command -V pre-commit > /dev/null 2>&1 ; then
        eval "pre-commit install"
        eval "pre-commit run --all-files"
        exit
    else
        echo "pre-commit not found, did you forget to activate your virtualenv?"
        exit 1
    fi
}

run_coverage() {
    # Run the test suite with coverage
    (cd "$base_dir"/server || exit; eval "coverage run")
    (cd "$base_dir"/server || exit; eval "coverage report")
    exit
  }

# Parse CLI argument
while [[ $# -gt 0 ]]; do
  case $1 in
    -d|--db)
        start_db
        ;;
    -l|--load)
        load_django_fixtures
        ;;
    -p|--pre-commit)
        run_pre_commit
        ;;
    -o|--openapi)
		generate_api_schema
		;;
    -e|--erd)
	  graph_models
		;;
    -c|--coverage)
    run_coverage
		;;
    -h|--help)
	  print_usage
    exit 0
		;;
    *)
      echo "Unknown option $1"
	  print_usage
      exit 1
      ;;
  esac
done
