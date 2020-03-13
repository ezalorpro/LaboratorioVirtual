import numpy as np
import scipy as sp


def nichols_grid(cl_mags=None,
                 cl_phases=None,
                 line_style='dotted',
                 figure=None,
                 ax=None,
                 delay=False,
                 offsetP=0):
    """Nichols chart grid

    Plots a Nichols chart grid on the current axis, or creates a new chart
    if no plot already exists.

    Parameters
    ----------
    cl_mags : array-like (dB), optional
        Array of closed-loop magnitudes defining the iso-gain lines on a
        custom Nichols chart.
    cl_phases : array-like (degrees), optional
        Array of closed-loop phases defining the iso-phase lines on a custom
        Nichols chart. Must be in the range -360 < cl_phases < 0
    line_style : string, optional
        .. seealso:: https://matplotlib.org/gallery/lines_bars_and_markers/linestyles.html

    Returns
    -------
    None
    """
    # Default chart size
    ol_phase_min = -359.99
    ol_phase_max = 0.0
    ol_mag_min = -40.0
    ol_mag_max = default_ol_mag_max = 50.0

    # Find bounds of the current dataset, if there is one.
    if ax.has_data():
        ol_phase_min, ol_phase_max, ol_mag_min, ol_mag_max = ax.axis()
        if delay:
            ol_phase_min = -360
            ol_phase_max = 180

    # M-circle magnitudes.
    if cl_mags is None:
        # Default chart magnitudes
        # The key set of magnitudes are always generated, since this
        # guarantees a recognizable Nichols chart grid.
        key_cl_mags = np.array([
            -40.0,
            -20.0,
            -12.0,
            -6.0,
            -3.0,
            -1.0,
            -0.5,
            0.0,
            0.25,
            0.5,
            1.0,
            3.0,
            6.0,
            12.0
        ])
        # Extend the range of magnitudes if necessary. The extended arange
        # will end up empty if no extension is required. Assumes that closed-loop
        # magnitudes are approximately aligned with open-loop magnitudes beyond
        # the value of np.min(key_cl_mags)
        cl_mag_step = -20.0  # dB
        extended_cl_mags = np.arange(np.min(key_cl_mags),
                                     ol_mag_min + cl_mag_step,
                                     cl_mag_step)
        cl_mags = np.concatenate((extended_cl_mags, key_cl_mags))

    # N-circle phases (should be in the range -360 to 0)
    if cl_phases is None:
        # Choose a reasonable set of default phases (denser if the open-loop
        # data is restricted to a relatively small range of phases).
        key_cl_phases = np.array([-0.25, -45.0, -90.0, -180.0, -270.0, -325.0, -359.75])
        if np.abs(ol_phase_max - ol_phase_min) < 90.0:
            other_cl_phases = np.arange(-10.0, -360.0, -10.0)
        else:
            other_cl_phases = np.arange(-10.0, -360.0, -20.0)
        cl_phases = np.concatenate((key_cl_phases, other_cl_phases))
    else:
        assert ((-360.0 < np.min(cl_phases)) and (np.max(cl_phases) < 0.0))

    # Find the M-contours
    m = m_circles(cl_mags, phase_min=np.min(cl_phases), phase_max=np.max(cl_phases))
    m_mag = 20 * sp.log10(np.abs(m))
    m_phase = sp.mod(sp.degrees(sp.angle(m)), -360.0)  # Unwrap

    # Find the N-contours
    n = n_circles(cl_phases, mag_min=np.min(cl_mags), mag_max=np.max(cl_mags))
    n_mag = 20 * sp.log10(np.abs(n))
    n_phase = sp.mod(sp.degrees(sp.angle(n)), -360.0)  # Unwrap

    # Plot the contours behind other plot elements.
    # The "phase offset" is used to produce copies of the chart that cover
    # the entire range of the plotted data, starting from a base chart computed
    # over the range -360 < phase < 0. Given the range
    # the base chart is computed over, the phase offset should be 0
    # for -360 < ol_phase_min < 0.
    phase_offset_min = 360.0 * np.ceil(ol_phase_min / 360.0)
    phase_offset_max = 360.0 * np.ceil(ol_phase_max / 360.0) + offsetP
    if phase_offset_min == phase_offset_max:
        phase_offset_max += 360
    phase_offsets = np.arange(phase_offset_min, phase_offset_max, 360.0)

    for phase_offset in phase_offsets:
        # Draw M and N contours
        ax.plot(m_phase + phase_offset,
                m_mag,
                color='lightgray',
                linestyle=line_style,
                zorder=0)
        ax.plot(n_phase + phase_offset,
                n_mag,
                color='lightgray',
                linestyle=line_style,
                zorder=0)

        # Add magnitude labels
        for x, y, m in zip(m_phase[:][-1] + phase_offset, m_mag[:][-1], cl_mags):
            align = 'right' if m < 0.0 else 'left'
            ax.text(x, y, str(m) + ' dB', size='small', ha=align, color='gray')

    # Fit axes to generated chart
    ax.axis([
        phase_offset_min - 360.0,
        phase_offset_max - 360.0,
        np.min(cl_mags),
        np.max([ol_mag_max, default_ol_mag_max])
    ])


#
# Utility functions
#
# This section of the code contains some utility functions for
# generating Nichols plots
#


def closed_loop_contours(Gcl_mags, Gcl_phases):
    """Contours of the function Gcl = Gol/(1+Gol), where
    Gol is an open-loop transfer function, and Gcl is a corresponding
    closed-loop transfer function.

    Parameters
    ----------
    Gcl_mags : array-like
        Array of magnitudes of the contours
    Gcl_phases : array-like
        Array of phases in radians of the contours

    Returns
    -------
    contours : complex array
        Array of complex numbers corresponding to the contours.
    """
    # Compute the contours in Gcl-space. Since we're given closed-loop
    # magnitudes and phases, this is just a case of converting them into
    # a complex number.
    Gcl = Gcl_mags * sp.exp(1.j * Gcl_phases)

    # Invert Gcl = Gol/(1+Gol) to map the contours into the open-loop space
    return Gcl / (1.0-Gcl)


def m_circles(mags, phase_min=-359.75, phase_max=-0.25):
    """Constant-magnitude contours of the function Gcl = Gol/(1+Gol), where
    Gol is an open-loop transfer function, and Gcl is a corresponding
    closed-loop transfer function.

    Parameters
    ----------
    mags : array-like
        Array of magnitudes in dB of the M-circles
    phase_min : degrees
        Minimum phase in degrees of the N-circles
    phase_max : degrees
        Maximum phase in degrees of the N-circles

    Returns
    -------
    contours : complex array
        Array of complex numbers corresponding to the contours.
    """
    # Convert magnitudes and phase range into a grid suitable for
    # building contours
    phases = sp.radians(sp.linspace(phase_min, phase_max, 2000))
    Gcl_mags, Gcl_phases = sp.meshgrid(10.0**(mags / 20.0), phases)
    return closed_loop_contours(Gcl_mags, Gcl_phases)


def n_circles(phases, mag_min=-40.0, mag_max=12.0):
    """Constant-phase contours of the function Gcl = Gol/(1+Gol), where
    Gol is an open-loop transfer function, and Gcl is a corresponding
    closed-loop transfer function.

    Parameters
    ----------
    phases : array-like
        Array of phases in degrees of the N-circles
    mag_min : dB
        Minimum magnitude in dB of the N-circles
    mag_max : dB
        Maximum magnitude in dB of the N-circles

    Returns
    -------
    contours : complex array
        Array of complex numbers corresponding to the contours.
    """
    # Convert phases and magnitude range into a grid suitable for
    # building contours
    mags = sp.linspace(10**(mag_min / 20.0), 10**(mag_max / 20.0), 2000)
    Gcl_phases, Gcl_mags = sp.meshgrid(sp.radians(phases), mags)
    return closed_loop_contours(Gcl_mags, Gcl_phases)
