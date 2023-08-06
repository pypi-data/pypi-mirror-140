global_constraints = [
    *["{0} = ( float ( {0}_min ) + float ( {0}_max ) ) / 2".format(i) for i in ["x", "y", "z"]],
    *["{0}_span = float ( {0}_max ) - float ( {0}_min )".format(i) for i in ["x", "y", "z"]],
    *["{0}_min = float ( {0} ) - float ( {0}_span ) / 2 ".format(i) for i in ["x", "y", "z"]],
    *["{0}_max = float ( {0} ) + float ( {0}_span ) / 2 ".format(i) for i in ["x", "y", "z"]],
    # *["rotate_{0} = float ( rotate{1} )".format(i, i.upper()) for i in ["x", "y", "z"]],
    *["rotate{1} = 0 * float ( rotate_{0} )".format(i, i.upper()) for i in ["x", "y", "z"]],
    "frequency = 299792458 / 1000000 / wavelength",
    "wavelength = 299792458 / 1000000 / frequency",
    "start_frequency = 299792458 / 1000000 / stop_wavelength",
    "stop_wavelength = 299792458 / 1000000 / start_frequency",
    "start_wavelength = 299792458 / 1000000 / stop_frequency",
    "stop_frequency = 299792458 / 1000000 / start_wavelength",
    "h = float ( z_span )",
    "bent_radius = bend_radius",
    "bend_radius = bent_radius",
    # "extrude = {'h': float ( z_span )}",
    # "define_x_mesh = int ( solver_type != 0 )",
    # "number_of_points = int ( ( float ( stop ) - float ( start ) ) / float ( interval ) )",
    "interval = ( float ( stop ) - float ( start ) ) / ( int ( number_of_points ) - 1 )",
    "overrideMeshOrder = int ( bool ( meshOrder + 1 ) )"
    # NotImplemented
    # *["rotate_{0} == rotate{1}".format(i, i.upper()) for i in ['x', 'y', 'z'] ]
    # *["rotate_{0} <= rotate{1}".format(i, i.upper()) for i in ['x', 'y', 'z'] ]
]

local_constraints = {"geo": []}
