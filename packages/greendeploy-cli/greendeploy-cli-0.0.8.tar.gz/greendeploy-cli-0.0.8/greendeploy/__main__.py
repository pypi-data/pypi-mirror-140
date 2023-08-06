"""Entry point when invoked with python -m greendeploy."""  # pragma: no cover

if __name__ == "__main__":  # pragma: no cover
    import sys

    from greendeploy.framework.cli import main

    if sys.argv[0].endswith("__main__.py"):
        sys.argv[0] = "python -m greendeploy"
    main()
