import matplotlib.pyplot as plt
import numpy as np


class BeamTrace:
    """Class BeamTrace
    For very simple beam waist and gouy phase calculations in python.
    No fancy optimization like alamode, no nice GUI like jammt.
    Just mirrors, lenses, and lengths added in sequence.

    ### Better options:
    MATLAB alamode: https://github.com/nicolassmith/alm
    JAMMT: http://www.sr.bham.ac.uk/dokuwiki/doku.php?id=geosim:jammt
    Finesse + pykat: https://git.ligo.org/finesse/pykat


    ### Process:
    User adds in mirrors, lenses, and spaces *in sequential order*.
    User computes the cavity ABCD matrix from the components added using calculate_cavity_ABCD().
    If cavity is stable, find the fundamental eigenmode for the beam (q-parameter)
    Set this q-parameter as q_input beam.
    Scan the cavity beam parmater using scan_cavity().

    ### Examples:
    # Simple resonator
    import numpy as np
    from beamtrace import BeamTrace

    my_cav = BeamTrace()        # initializes ABCD class
    my_cav.add_mirror(1.0) # adds mirror with 1.0 meter radius of curvature at z=0.0 meters
    my_cav.add_space(0.5)  # adds 0.5 meters of space to cavity
    my_cav.add_mirror(1.0) # adds mirror with 1.0 meter radius of curvature at z=0.5 meters
    my_cav.calculate_cavity_ABCD() # Finds the cavity round-trip ABCD matrix, tells you if it's stable.  If it is stable, populates the my_cav.q_input parameter
    zz, ww, gouy, qq = my_cav.scan_cavity(round_trip=True) # Returns propagation distance, beam radius, accumulated gouy phase, and beam q-parameter for the entire cavity, plus the round-trip

    import matplotlib.pyplot as plt
    fig = my_cav.plot_cavity_scan(round_trip=True, label='Simple Cavity')
    plt.show()

    # LIGO arm cavity
    import numpy as np
    from beamtrace import BeamTrace
    R1 = 1934. # m
    R2 = 2245. # m
    L = 3994.469 # m
    arm_cav = BeamTrace()

    arm_cav.add_mirror(R1, name='ITMY')
    arm_cav.add_space(L)
    arm_cav.add_mirror(R2, name='ETMY')

    import matplotlib.pyplot as plt
    fig = arm_cav.plot_cavity_scan(round_trip=True)
    plt.show()
    """

    def __init__(self, isCavity=True, verbose=True, wavelength=1064e-9):
        self.isCavity = isCavity
        self.verbose = verbose
        self.wavelength = wavelength

        self.isStable = False  # cavity is never stable straightaway
        self.isUnity = True

        self.q_input = None  # for a cavity, the input q-parameter for a stable cav
        self.w_input = None  # for a cavity, the input beam radius
        self.RoC_input = None  # for a cavity, the input radius of curvature

        self.input_mirror_name = None  # for a cavity, the input mirror name
        self.end_mirror_name = None  # for a cavity, the end mirror name

        self.components = np.array([])  # holds component names in order
        self.comp_dict = {}

        self.ABCD = np.array([[1, 0], [0, 1]])
        self.q = 0.0 + 1.0j  # q parameter

        self.total_length = 0.0

        self.number_of_spaces = 0
        self.number_of_mirrors = 0
        self.number_of_lenses = 0
        self.number_of_refractions = 0

    ##### set functions #####
    def set_isCavity(self, isCavity):
        """Sets the isCavity parameter to True or False.  Default is True"""
        self.isCavity = isCavity
        return

    def set_seed_beam(self, q):
        """Sets the q-parameter of the input beam, default is q = 1.0j"""
        self.q_input = q
        return

    ##### get functions #####
    def get_q(self):
        """Calculate q-parameter from ABCD matrix
        From Koji Arai T1300189:
        q = [(A - D) +- sqrt((A + D)^2 - 4) ]/(2C)
        """
        A = self.ABCD[0, 0]
        B = self.ABCD[0, 1]
        C = self.ABCD[1, 0]
        D = self.ABCD[1, 1]
        q = ((A - D) + np.sqrt((A + D) ** 2 - 4 + 0j)) / (
            2 * C
        )  # Added the plus 0j to get complex numbers back
        if np.imag(q) < 0:
            q = np.conjugate(q)  # make imaginary part positve out of convention
        return q

    def get_total_cavity_gouy_phase(self, deg=True):
        """Calculate cavity round-trip accumulated gouy phase from the cav ABCD matrix
        From Koji Arai T1300189:
        gouy = sign(B) * arccos((A + D)/2)"""
        A = self.ABCD[0, 0]
        B = self.ABCD[0, 1]
        C = self.ABCD[1, 0]
        D = self.ABCD[1, 1]
        if deg == True:
            multiplier = 180 / np.pi
        else:
            multiplier = 1.0
        # total_gouy = np.sign(B) * np.arccos(0.5 * (A + D))
        total_gouy = 2 * np.arccos(np.sign(B) * np.sqrt((A + D + 2) / 4))
        return multiplier * total_gouy

    def get_beam_radius(self, q):
        """Calculate beam radius w from the q-parameter
        From Kogelnik and Li DCC P660001:
        1/q = 1/R - j lambda/(pi * w^2)
        """
        invq = 1.0 / q
        im_invq = -1 * np.imag(invq) * np.pi / self.wavelength  # = 1/w^2
        return np.sqrt(1.0 / im_invq)

    def get_beam_RoC(self, q):
        """Calculate beam radius of curvature from the q-parameter
        From Kogelnik and Li DCC P660001:
        1/q = 1/R - j lambda/(pi * w^2)
        """
        invq = 1.0 / q
        re_invq = np.real(invq)
        return 1.0 / re_invq

    def get_beam_gouy(self, q):
        """Gets beam gouy phase from beam radius and beam radius of curvature"""
        gouy = np.arctan2(np.real(q), np.imag(q))
        return gouy

    ##### Add component functions #####
    def add_space(self, length, index_of_refraction=1, name=None):
        """Adds a space to the beam path"""
        if name == None:
            name = "space_{}".format(self.number_of_spaces)

        start_location = self.total_length
        end_location = self.total_length + length
        self.total_length += length

        self.components = np.append(self.components, name)
        self.comp_dict[name] = {}
        self.comp_dict[name]["type"] = "space"
        self.comp_dict[name]["length"] = length
        self.comp_dict[name]["number"] = self.number_of_spaces
        self.comp_dict[name]["index_of_refraction"] = index_of_refraction
        self.comp_dict[name]["start_location"] = start_location
        self.comp_dict[name]["end_location"] = end_location

        self.comp_dict[name]["ABCD"] = self.space(length, index_of_refraction)
        self.number_of_spaces += 1
        return

    def add_lens(self, focal_length, name=None):
        """Adds a lens to the beam path"""
        if name == None:
            name = "lens_{}".format(self.number_of_spaces)

        location = self.total_length

        self.components = np.append(self.components, name)
        self.comp_dict[name] = {}
        self.comp_dict[name]["type"] = "lens"
        self.comp_dict[name]["number"] = self.number_of_lenses
        self.comp_dict[name]["focal_length"] = focal_length
        self.comp_dict[name]["location"] = location

        self.comp_dict[name]["ABCD"] = self.lens(focal_length)
        self.number_of_lenses += 1
        return

    def add_mirror(self, radius_of_curvature, index_of_refraction=1, name=None):
        """Adds a mirror to the beam path"""
        if name == None:
            name = "mirror_{}".format(self.number_of_spaces)

        location = self.total_length

        self.components = np.append(self.components, name)
        self.comp_dict[name] = {}
        self.comp_dict[name]["type"] = "mirror"
        self.comp_dict[name]["number"] = self.number_of_mirrors
        self.comp_dict[name]["radius_of_curvature"] = radius_of_curvature
        self.comp_dict[name]["location"] = location
        self.comp_dict[name]["index_of_refraction"] = index_of_refraction

        self.comp_dict[name]["ABCD"] = self.mirror(
            radius_of_curvature, index_of_refraction=index_of_refraction
        )
        self.number_of_mirrors += 1
        return

    def add_refraction(
        self, radius_of_curvature, index_of_refraction1, index_of_refraction2, name=None
    ):
        """Adds a refraction to the beam path.
        index_of_refraction1 is the refractive index of the starting medium,
        index_of_refraction2 is the index of the medium being entered
        """
        if name == None:
            name = "lens_{}".format(self.number_of_spaces)

        location = self.total_length

        self.components = np.append(self.components, name)
        self.comp_dict[name] = {}
        self.comp_dict[name]["type"] = "refraction"
        self.comp_dict[name]["number"] = self.number_of_refractions
        self.comp_dict[name]["radius_of_curvature"] = radius_of_curvature
        self.comp_dict[name]["location"] = location
        self.comp_dict[name]["index_of_refraction1"] = index_of_refraction1
        self.comp_dict[name]["index_of_refraction2"] = index_of_refraction2

        self.comp_dict[name]["ABCD"] = self.refraction(
            radius_of_curvature, index_of_refraction1, index_of_refraction2
        )
        self.number_of_lenses += 1
        return

    # ABCD matrices
    def space(self, length, index_of_refraction=1):
        """Returns ABCD numpy matrix of a space propagation. Optional index_of_refraction arg, default is 1."""
        return np.array([[1, length / index_of_refraction], [0, 1]])

    def lens(self, focal_length):
        """Returns ABCD numpy matrix of a lens"""
        if focal_length == np.inf:
            ABCD = np.array([[1, 0], [0, 1]])
        else:
            ABCD = np.array([[1, 0], [-1 / focal_length, 1]])
        return ABCD

    def mirror(self, radius_of_curvature, index_of_refraction=1):
        """Returns ABCD numpy matrix of a lens"""
        if radius_of_curvature == np.inf:
            ABCD = np.array([[1, 0], [0, 1]])
        else:
            ABCD = np.array(
                [[1, 0], [-2 * index_of_refraction / radius_of_curvature, 1]]
            )
        return ABCD

    def refraction(
        self, radius_of_curvature, index_of_refraction1, index_of_refraction2
    ):
        """Returns ABCD numpy matrix of a refracted beam at a curved surface. n1 is the refractive index of the starting medium, n2 is the index of the medium being entered"""
        if radius_of_curvature == np.inf:
            ABCD = np.array([[1, 0], [0, n1 / n2]])
        elif n1 == n2:
            ABCD = np.array([[1, 0], [0, 1]])
        else:
            ABCD = np.array([[1, 0], [(n1 - n2) / (n2 * radius_of_curvature), n1 / n2]])
        return ABCD

    def get_component_locations(self):
        """Returns two arrays, one of mirror and lens names, the other their z-location.
        Lists are sorted by z-location.
        """
        names = np.array([])
        locations = np.array([])
        for key in self.comp_dict.keys():
            if (
                self.comp_dict[key]["type"] == "mirror"
                or self.comp_dict[key]["type"] == "lens"
            ):
                names = np.append(names, key)
                locations = np.append(locations, self.comp_dict[key]["location"])
        # ensure locations are sorted in order
        idx = np.argsort(locations)
        names = names[idx]
        locations = locations[idx]
        return names, locations

    def get_space(self, z):
        """Given some position on the propagation axis z, returns the name of the space we're currently in"""
        for key in self.comp_dict.keys():
            if self.comp_dict[key]["type"] == "space":
                if (
                    self.comp_dict[key]["start_location"] - z <= 0
                    and self.comp_dict[key]["end_location"] - z >= 0
                ):
                    return key
        print('No space encompassing z={} m defined, returning "None"'.format(z))
        return None

    def print(self):
        """Prints the cavity components added so far"""
        print()
        print(
            "{name:<20}\t{number:>20}\t{RoC:>20}\t{z:>20}\t{index:>20}".format(
                name="Mirror",
                number="Order Number",
                RoC="Curve Radius",
                z="z-Location",
                index="Refraction Index",
            )
        )
        print("------------------------------------------------------------")
        for key in self.comp_dict.keys():
            if self.comp_dict[key]["type"] == "mirror":
                cd = self.comp_dict[key]
                print(
                    "{name:<20}\t{number:>20}\t{RoC:>20}\t{z:>20}\t{index:>20}".format(
                        name=key,
                        number=cd["number"],
                        RoC=cd["radius_of_curvature"],
                        z=cd["location"],
                        index=cd["index_of_refraction"],
                    )
                )
        print()
        print(
            "{name:<20}\t{number:>20}\t{f:>20}\t{z:>20}".format(
                name="Lenses",
                number="Order Number",
                f="Focal Length",
                z="z-Location",
            )
        )
        print("------------------------------------------------------------")
        for key in self.comp_dict.keys():
            if self.comp_dict[key]["type"] == "lens":
                cd = self.comp_dict[key]
                print(
                    "{name:<20}\t{number:>20}\t{f:>20}\t{z:>20}".format(
                        name=key,
                        number=cd["number"],
                        f=cd["focal_length"],
                        z=cd["location"],
                    )
                )
        print()
        print(
            "{name:<20}\t{number:>20}\t{RoC:>20}\t{z:>20}\t{index1:>20}\t{index2:>20}".format(
                name="Refractions",
                number="Order Number",
                RoC="Curve Radius",
                z="z-Location",
                index1="Refraction Index 1",
                index2="Refraction Index 2",
            )
        )
        print("------------------------------------------------------------")
        for key in self.comp_dict.keys():
            if self.comp_dict[key]["type"] == "refraction":
                cd = self.comp_dict[key]
                print(
                    "{name:<20}\t{number:>20}\t{RoC:>20}\t{z:>20}\t{index1:>20}\t{index2:>20}".format(
                        name=key,
                        number=cd["number"],
                        RoC=cd["radius_of_curvature"],
                        z=cd["location"],
                        index1=cd["index_of_refraction1"],
                        index2=cd["index_of_refraction2"],
                    )
                )
        print()
        print(
            "{name:<20}\t{number:>20}\t{length:>20}\t{z:>20}\t{zend:>20}\t{index:>20}".format(
                name="Space",
                number="Order Number",
                length="Length",
                z="z-Location",
                zend="z-Loc End",
                index="Refraction Index",
            )
        )
        print(
            "----------------------------------------------------------------------------"
        )
        for key in self.comp_dict.keys():
            if self.comp_dict[key]["type"] == "space":
                cd = self.comp_dict[key]
                print(
                    "{name:<20}\t{number:>20}\t{length:>20}\t{z:>20}\t{zend:>20}\t{index:>20}".format(
                        name=key,
                        number=cd["number"],
                        length=cd["length"],
                        z=cd["start_location"],
                        zend=cd["end_location"],
                        index=cd["index_of_refraction"],
                    )
                )
        print()
        return

    def check_stability(self, verbose=False):
        """Tells you if cavity is stable or not"""
        A = self.ABCD[0, 0]
        B = self.ABCD[0, 1]
        C = self.ABCD[1, 0]
        D = self.ABCD[1, 1]
        stability_criterion = 0.5 * (A + D)
        if verbose:
            print("(A + D)/2 = {:.3f}".format(stability_criterion))
        if -1 < stability_criterion and stability_criterion < 1:
            if verbose:
                print("Cavity is STABLE")
            self.isStable = True
        else:
            print("Cavity is NOT STABLE")
            self.isStable = False
        return self.isStable

    def check_unity(self, verbose=False):
        """Checks if ABCD matrix is unity, A*D - B*C = 1"""
        A = self.ABCD[0, 0]
        B = self.ABCD[0, 1]
        C = self.ABCD[1, 0]
        D = self.ABCD[1, 1]
        unity = A * D - B * C
        if np.abs(unity - 1.0) < 1e-6:
            if verbose:
                print("Cavity ABCD is unity")
            self.isUnity = True
        else:
            if verbose:
                print("Cavity ABCD is NOT unity")
            self.isUnity = False
        return self.isUnity

    def calculate_cavity_ABCD(self):
        """Calculates the total ABCD matrix for the cavity as constructed.
        Assumes the first and last two mirrors added form a cavity.
        Starts propagating from the first mirror into the first space (z=0) toward the second mirror.
        Tells you if the cavity is stable or not.
        If the cavity is stable, stores the input q-parameter expected for the stable cavity in self.q_input.
        """
        if self.number_of_mirrors < 2:
            print(
                'Number of mirrors in "cavity" is only {}'.format(
                    self.number_of_mirrors
                )
            )
            print("Add more mirrors!")
            return
        for ii, name in enumerate(self.components):
            if (
                self.comp_dict[name]["type"] == "mirror"
                and self.comp_dict[name]["number"] == 0
            ):
                self.input_mirror_name = name
                input_mirror_index = ii
            if (
                self.comp_dict[name]["type"] == "mirror"
                and self.comp_dict[name]["number"] == self.number_of_mirrors - 1
            ):
                self.end_mirror_name = name
                end_mirror_index = ii

        for name in self.components[input_mirror_index + 1 : end_mirror_index + 1]:
            tempABCD = self.comp_dict[name]["ABCD"]
            self.ABCD = np.dot(tempABCD, self.ABCD)

        for name in reversed(self.components[input_mirror_index:end_mirror_index]):
            tempABCD = self.comp_dict[name]["ABCD"]
            self.ABCD = np.dot(tempABCD, self.ABCD)

        self.check_unity()
        self.check_stability()
        if self.isStable and self.q_input == None:
            self.q = self.get_q()
            self.q_input = self.q
            self.w_input = self.get_beam_radius(self.q)
            self.RoC_input = self.get_beam_RoC(self.q)

        return

    def calc_q_from_ABCD(self, q_in, ABCD):
        """Takes input q and ABCD matrix and returns output q"""
        A = ABCD[0, 0]
        B = ABCD[0, 1]
        C = ABCD[1, 0]
        D = ABCD[1, 1]
        q_out = (A * q_in + B) / (C * q_in + D)
        return q_out

    def calc_beam_waists(self):
        """Calculates the minimum beam waist for each space in the cavity.
        Must be done after scan_cavity() has been run.
        """
        self.beam_waist_locations = np.array([])
        self.beam_waists = np.array([])

        for key in self.comp_dict.keys():
            if self.comp_dict[key]["type"] == "space":
                # print(f'key = {key}')
                z_start = self.comp_dict[key]["start_location"]
                z_end = self.comp_dict[key]["end_location"]

                z_start_index = np.argwhere(self.zz >= z_start)[0, 0]
                z_end_index = np.argwhere(self.zz <= z_end)[-1, 0]

                try:
                    temp_beam_waist_index = np.argmin(
                        self.ww[z_start_index : z_end_index + 1]
                    )
                except ValueError:
                    # z_start_index == z_end_index, meaning the steps are too large for this space
                    continue
                beam_waist_index = z_start_index + temp_beam_waist_index

                temp_beam_waist_location = self.zz[beam_waist_index]
                temp_beam_waist = self.ww[beam_waist_index]

                # check if radius around waist is smaller, then it is no waist
                if beam_waist_index == 0 or beam_waist_index + 1 >= len(self.ww):
                    continue
                if (
                    self.ww[beam_waist_index - 1] < temp_beam_waist
                    or self.ww[beam_waist_index + 1] < temp_beam_waist
                ):
                    continue

                self.beam_waist_locations = np.append(
                    self.beam_waist_locations, temp_beam_waist_location
                )
                self.beam_waists = np.append(self.beam_waists, temp_beam_waist)
        return

    def scan_beam(self, steps=500):
        """Scans the beam.  Needs only an q_input via set_seed_beam() and a space via add_space.
        Works with plot_beam()

        Example:
        from beamtrace.tracer import BeamTrace
        beam = BeamTrace()
        beam.set_seed_beam(1 + 1j)
        beam.add_space(5.0)
        beam.scan_beam()
        beam.plot_beam()
        """
        if not self.q_input:
            print("ERROR: seed beam q_input not set.")
            print(
                "Please run BeamTrace.set_seed_beam(q_input) to seed the starting beam"
            )
            print("Running with default seed beam q = {}".format(self.q))
            self.q_input = self.q

        if not self.total_length:
            print("ERROR: no spaces added.")
            print(
                "Please run BeamTrace.add_space(length) to define the length of the beam scan"
            )
            print("Returning...")
            return

        z_start = 0
        z_end = self.total_length
        zz = np.linspace(z_start, z_end, steps)
        dz = zz[1] - zz[0]

        # gets names and locations of all components that aren't spaces
        names, locations = self.get_component_locations()
        next_index = 0

        last_location = 0.0

        space_name = self.get_space(0.0)
        space_ABCD = self.comp_dict[space_name]["ABCD"]
        space_index_of_refraction = self.comp_dict[space_name]["index_of_refraction"]

        permanent_ABCD = np.array(
            [[1, 0], [0, 1]]
        )  # make an ABCD matrix to scan over z

        ww = np.array([])
        gouy = np.array([])
        qq = np.array([])
        gouy_ref = self.get_beam_gouy(self.q_input)

        for z_temp in zz:
            # Get the current space
            current_space_name = self.get_space(z_temp)

            # if we've reached the next space, separated by a component
            if current_space_name != space_name:

                # First, multiply in the old space into the ABCD permanently
                permanent_ABCD = np.dot(space_ABCD, permanent_ABCD)

                # Store the current space
                space_name = self.get_space(z_temp)
                space_ABCD = self.comp_dict[space_name]["ABCD"]
                space_index_of_refraction = self.comp_dict[space_name][
                    "index_of_refraction"
                ]

                # Get current component name, location, ABCD
                last_name = names[next_index]
                last_location = locations[next_index]
                comp_ABCD = self.comp_dict[last_name]["ABCD"]
                permanent_ABCD = np.dot(comp_ABCD, permanent_ABCD)

                # Reset the gouy phase reference
                try:
                    last_gouy = gouy[-1]
                except IndexError:
                    last_gouy = 0.0
                # get q_perm from q_in and the "permanent" ABCD
                q_perm = self.calc_q_from_ABCD(self.q_input, permanent_ABCD)
                # reset the accumulated gouy phase reference
                gouy_ref = self.get_beam_gouy(q_perm) - last_gouy

                next_index += 1  # increment the component counter

            # usual calcs
            temp_length = z_temp - last_location
            temp_space_ABCD = self.space(
                temp_length, index_of_refraction=space_index_of_refraction
            )
            # get the scan's temp ABCD matrix at z_temp
            temp_ABCD = np.dot(temp_space_ABCD, permanent_ABCD)  

            # get q_out from q_in and the temp ABCD
            q_out = self.calc_q_from_ABCD(self.q_input, temp_ABCD)  

            w_out = self.get_beam_radius(q_out)
            
            # gets "pure" gouy phase from beam q-parameter
            gouy_out = self.get_beam_gouy(q_out)
            # subtracts away the reference gouy phase to get relative phase added
            gouy_accumulated = gouy_out - gouy_ref  

            ww = np.append(ww, w_out)
            qq = np.append(qq, q_out)
            gouy = np.append(gouy, gouy_accumulated)

        # store as attributes
        self.zz = zz
        self.ww = ww
        self.gouy = gouy
        self.qq = qq

        # calculate the beam waists
        self.calc_beam_waists()

        return zz, ww, gouy, qq

    def scan_cavity(self, steps=500, round_trip=False):
        """Scans the cavity along the axis of propagation (aka z-axis) from input to end mirror.
        Inputs:
        steps = number of points on the z-axis to scan at.  z goes from 0 to the cavity length, unless round_trip is True.
        round_trip = scans from front mirror to end mirror and back again.  z goes from 0 to 2*cavity length.

        Returns arrays of the distance z, beam radius w, accumulated gouy phase, and q-parameters along the z-axis:
        z, w, gouy, q = scan_cavity()
        """

        if self.q_input == None:
            print("self.isCavity = {}".format(self.isCavity))
            if self.isCavity:
                print(
                    "Running calculate_cavity_ABCD() to find the fundamental eigenmode to use as the seed beam q-parameter"
                )
                self.calculate_cavity_ABCD()
            else:
                print("Running with default seed beam q = {}".format(self.q))
                self.q_input = self.q

        z_start = 0
        z_end = self.total_length
        if round_trip:
            length_scaler = 2
        else:
            length_scaler = 1
        zz = np.linspace(z_start, length_scaler * z_end, steps)
        dz = zz[1] - zz[0]

        # gets names and locations of all components that aren't spaces
        names, locations = self.get_component_locations()

        last_name = names[0]
        last_location = locations[0]
        next_index = 1
        next_name = names[next_index]
        next_location = locations[next_index]
        past_last_component = False

        space_name = self.get_space(0.0)
        space_ABCD = self.comp_dict[space_name]["ABCD"]
        space_index_of_refraction = self.comp_dict[space_name]["index_of_refraction"]

        permanent_ABCD = np.array(
            [[1, 0], [0, 1]]
        )  # make an ABCD matrix to scan over z

        ww = np.array([])
        gouy = np.array([])
        qq = np.array([])
        gouy_ref = self.get_beam_gouy(self.q_input)
        back_tracking = False

        for z_temp in zz:
            if z_temp < z_end:  # traveling to the end of the plotted cavity axis
                if (
                    z_temp >= next_location and not past_last_component
                ):  # if we've reached the next component that's not a space, and it's not the last component

                    # First, multiply in the old space into the ABCD permanently
                    permanent_ABCD = np.dot(space_ABCD, permanent_ABCD)

                    # Get the new component name and location
                    last_name = names[next_index]
                    last_location = locations[next_index]

                    # Get the new space
                    space_name = self.get_space(z_temp)
                    space_ABCD = self.comp_dict[space_name]["ABCD"]
                    space_index_of_refraction = self.comp_dict[space_name][
                        "index_of_refraction"
                    ]

                    # Get current component ABCD
                    comp_ABCD = self.comp_dict[last_name]["ABCD"]
                    permanent_ABCD = np.dot(comp_ABCD, permanent_ABCD)

                    # Reset the gouy phase reference
                    try:
                        last_gouy = gouy[-1]
                    except IndexError:
                        last_gouy = 0.0
                    q_perm = self.calc_q_from_ABCD(
                        self.q_input, permanent_ABCD
                    )  # get q_perm from q_in and the "permanent" ABCD
                    gouy_ref = (
                        self.get_beam_gouy(q_perm) - last_gouy
                    )  # reset the accumulated gouy phase reference

                    next_index += 1  # increment the component counter

                    if next_index == len(names):
                        past_last_component = True
                    else:
                        next_name = names[next_index]
                        next_location = locations[next_index]

            elif z_temp > z_end and not back_tracking:  # we've hit the end mirror

                back_tracking = True

                # First, multiply in the old space into the ABCD permanently
                permanent_ABCD = np.dot(space_ABCD, permanent_ABCD)

                # Get the new component name and location
                last_name = names[next_index]
                last_location = locations[next_index]

                # Get the new space going backwards
                space_name = self.get_space(2 * z_end - z_temp)
                space_ABCD = self.comp_dict[space_name]["ABCD"]
                space_index_of_refraction = self.comp_dict[space_name][
                    "index_of_refraction"
                ]

                # Get current component ABCD
                comp_ABCD = self.comp_dict[last_name]["ABCD"]
                permanent_ABCD = np.dot(comp_ABCD, permanent_ABCD)

                # Reset the gouy phase reference
                q_perm = self.calc_q_from_ABCD(
                    self.q_input, permanent_ABCD
                )  # get q_perm from q_in and the "permanent" ABCD
                gouy_ref = (
                    self.get_beam_gouy(q_perm) - gouy[-1]
                )  # reset the accumulated gouy phase reference

                next_index -= 1  # increment the component counter

            elif back_tracking:  # we've hit the end mirror and are returning
                if (
                    z_temp >= 2 * z_end - locations[next_index]
                ):  # if we've reached the next component that's not a space
                    # First, multiply in the old space into the ABCD permanently
                    permanent_ABCD = np.dot(space_ABCD, permanent_ABCD)

                    # Get the new component name and location
                    last_name = names[next_index]
                    last_location = locations[next_index]

                    # Get the new space going backwards
                    space_name = self.get_space(2 * z_end - z_temp)
                    space_ABCD = self.comp_dict[space_name]["ABCD"]
                    space_index_of_refraction = self.comp_dict[space_name][
                        "index_of_refraction"
                    ]

                    # Get current component ABCD
                    comp_ABCD = self.comp_dict[last_name]["ABCD"]
                    permanent_ABCD = np.dot(comp_ABCD, permanent_ABCD)

                    # Reset the gouy phase reference
                    q_perm = self.calc_q_from_ABCD(
                        self.q_input, permanent_ABCD
                    )  # get q_perm from q_in and the "permanent" ABCD
                    gouy_ref = (
                        self.get_beam_gouy(q_perm) - gouy[-1]
                    )  # reset the accumulated gouy phase reference

                    # Update the "last_location" for going backwards
                    last_location = 2 * z_end - last_location

                    next_index -= 1  # increment the component counter

            temp_length = z_temp - last_location
            temp_space_ABCD = self.space(
                temp_length, index_of_refraction=space_index_of_refraction
            )

            temp_ABCD = np.dot(
                temp_space_ABCD, permanent_ABCD
            )  # get the scan's temp ABCD matrix at z_temp

            q_out = self.calc_q_from_ABCD(
                self.q_input, temp_ABCD
            )  # get q_out from q_in and the temp ABCD

            w_out = self.get_beam_radius(q_out)
            gouy_out = self.get_beam_gouy(
                q_out
            )  # gets "pure" gouy phase from beam q-parameter
            gouy_accumulated = (
                gouy_out - gouy_ref
            )  # subtracts away the reference gouy phase to get relative phase added

            ww = np.append(ww, w_out)
            qq = np.append(qq, q_out)
            gouy = np.append(gouy, gouy_accumulated)

        # store as attributes
        self.zz = zz
        self.ww = ww
        self.gouy = gouy
        self.qq = qq

        # calculate the beam waists
        self.calc_beam_waists()

        return zz, ww, gouy, qq

    def plot_beam_scan(
        self, steps=500, plot_beam_waists=True, color="C3", ls="-", label=None, fig=None
    ):
        """Plot the beam scan profile for beam waist and accumulated gouy phase."""
        self.plot_beam_waists = plot_beam_waists

        zz, ww, gouy, qq = self.scan_beam(steps=steps)
        names, locations = self.get_component_locations()

        # switch to class-based attributes
        zz = self.zz
        ww = self.ww
        gouy = self.gouy
        qq = self.qq

        newFig = True
        if fig == None:
            fig, (s1, s2) = plt.subplots(2, figsize=(20, 9))
        else:
            newFig = False
            s1, s2 = fig.get_axes()

        if label == None:
            label = "Beam Scan"

        s1.plot(zz, ww * 1e3, ls=ls, color=color, label=label)
        s1.plot(zz, -ww * 1e3, ls=ls, color=color)

        s2.plot(zz, gouy * 180 / np.pi, ls=ls, color=color, label=label)

        if self.plot_beam_waists:
            beam_waists = 0
            max_plot_ww = np.max(ww * 1e3)
            arrow_height = max_plot_ww * 0.75
            for z_waist, w_waist in zip(self.beam_waist_locations, self.beam_waists):
                beam_waists += 1
                plot_w_waist = w_waist * 1e3

                # check if the arrow height is high enough
                if arrow_height < plot_w_waist:
                    text_height = 0
                    plot_arrow_height = max_plot_ww
                    verticalalignment = "center"
                else:
                    text_height = arrow_height
                    plot_arrow_height = arrow_height
                    verticalalignment = "bottom"

                s1.annotate(
                    f"Beam waist {beam_waists}\nLoc = {z_waist:.2f} m\nWaist = {plot_w_waist:.2f} mm",
                    xy=(z_waist, plot_w_waist),
                    xycoords="data",
                    xytext=(z_waist, text_height),
                    textcoords="data",
                    fontsize=12,
                    horizontalalignment="center",
                    verticalalignment=verticalalignment,
                )
                s1.annotate(
                    "",
                    xy=(z_waist, plot_w_waist),
                    xycoords="data",
                    xytext=(z_waist, plot_arrow_height),
                    textcoords="data",
                    fontsize=10,
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3"),
                )
                s1.annotate(
                    "",
                    xy=(z_waist, -plot_w_waist),
                    xycoords="data",
                    xytext=(z_waist, -plot_arrow_height),
                    textcoords="data",
                    fontsize=10,
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3"),
                )

        if newFig:
            for ii, name, location in zip(np.arange(len(names)), names, locations):
                s1.axvline(x=location, ls="--", color="C{}".format(ii), label=name)
                s2.axvline(x=location, ls="--", color="C{}".format(ii), label=name)

            s2.set_xlabel("Cavity Axis z [m]")
            s1.set_ylabel("Beam Radius [mm]")
            s2.set_ylabel("Gouy Phase [deg]")
            # s2.set_yticks(30*np.arange(0,2))

            s1.grid()
            s2.grid()
        s1.legend()
        s2.legend()

        return fig

    def plot_cavity_scan(
        self,
        steps=500,
        round_trip=False,
        plot_beam_waists=True,
        color="C3",
        ls="-",
        label=None,
        fig=None,
    ):
        """Plot the cavity scan beam profile for beam waist and accumulated gouy phase."""
        self.plot_beam_waists = plot_beam_waists

        zz, ww, gouy, qq = self.scan_cavity(steps=steps, round_trip=round_trip)
        names, locations = self.get_component_locations()

        # switch to class-based attributes
        zz = self.zz
        ww = self.ww
        gouy = self.gouy
        qq = self.qq

        newFig = True
        if fig == None:
            fig, (s1, s2) = plt.subplots(2, figsize=(20, 9))
        else:
            newFig = False
            s1, s2 = fig.get_axes()

        if label == None:
            label = "Beam Trace"

        s1.plot(zz, ww * 1e3, ls=ls, color=color, label=label)
        s1.plot(zz, -ww * 1e3, ls=ls, color=color)

        s2.plot(zz, gouy * 180 / np.pi, ls=ls, color=color, label=label)

        if self.plot_beam_waists:
            beam_waists = 0
            max_plot_ww = np.max(ww * 1e3)
            arrow_height = max_plot_ww * 0.75
            for z_waist, w_waist in zip(self.beam_waist_locations, self.beam_waists):
                beam_waists += 1
                plot_w_waist = w_waist * 1e3

                # check if the arrow height is high enough
                if arrow_height < plot_w_waist:
                    text_height = 0
                    plot_arrow_height = max_plot_ww
                    verticalalignment = "center"
                else:
                    text_height = arrow_height
                    plot_arrow_height = arrow_height
                    verticalalignment = "bottom"

                s1.annotate(
                    f"Beam waist {beam_waists}\nLoc = {z_waist:.2f} m\nWaist = {plot_w_waist:.2f} mm",
                    xy=(z_waist, plot_w_waist),
                    xycoords="data",
                    xytext=(z_waist, text_height),
                    textcoords="data",
                    fontsize=12,
                    horizontalalignment="center",
                    verticalalignment=verticalalignment,
                )
                s1.annotate(
                    "",
                    xy=(z_waist, plot_w_waist),
                    xycoords="data",
                    xytext=(z_waist, plot_arrow_height),
                    textcoords="data",
                    fontsize=10,
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3"),
                )
                s1.annotate(
                    "",
                    xy=(z_waist, -plot_w_waist),
                    xycoords="data",
                    xytext=(z_waist, -plot_arrow_height),
                    textcoords="data",
                    fontsize=10,
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3"),
                )

        if newFig:
            for ii, name, location in zip(np.arange(len(names)), names, locations):
                s1.axvline(x=location, ls="--", color="C{}".format(ii), label=name)
                s2.axvline(x=location, ls="--", color="C{}".format(ii), label=name)

            s2.set_xlabel("Cavity Axis z [m]")
            s1.set_ylabel("Beam Radius [mm]")
            s2.set_ylabel("Gouy Phase [deg]")
            # s2.set_yticks(30*np.arange(0,2))

            s1.grid()
            s2.grid()
        s1.legend()
        s2.legend()

        return fig
