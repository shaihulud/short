#!/bin/bash
set -e

PORT=${2:-8080}

case "$1" in
    start)
        alembic upgrade head
        uvicorn app.server:app --host 0.0.0.0 --port $PORT --reload
        ;;
    tests)
        isort -c --diff --settings-file .isort.cfg .
        black --config pyproject.toml --check .
        pylint --rcfile=.pylintrc --errors-only app
        mypy .
        alembic downgrade base
        alembic upgrade head
        pytest -s -vv tests/
        exit 0
        ;;
    pytest)
        alembic downgrade base
        alembic upgrade head
        pytest -s -vv -x tests/ --trace-config
        exit 0
        ;;
    *)
        exec "$@"
        ;;
esac
