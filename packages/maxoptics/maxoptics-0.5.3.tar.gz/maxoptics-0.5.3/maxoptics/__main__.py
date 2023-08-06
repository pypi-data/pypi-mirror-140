import sys


def help():

    print(
        """
            Set output dir:

                python3 -m maxoptics setdir

            Set url:

                python3 -m maxoptics seturl

              """
    )


if __name__ == "__main__":
    if len(sys.argv) == 1:
        help()
    elif len(sys.argv) == 2:
        if sys.argv[1] == "setdir":
            import maxoptics.configtools.set_save_dir
        elif sys.argv[1] == "seturl":
            import maxoptics.configtools.set_url
        elif sys.argv[1] == "update":
            from maxoptics.configtools.update import update

            update()
        else:
            help()
    elif len(sys.argv) >= 3 and sys.argv[1] == "update":
        from maxoptics.configtools.update import update_one

        for fp in sys.argv[2:]:
            update_one(fp)

    elif len(sys.argv) == 4 and sys.argv[1] == "set":
        from maxoptics.configtools.set import set_value as _set

        _set(str(sys.argv[2]), str(sys.argv[3]))
    else:
        help()
