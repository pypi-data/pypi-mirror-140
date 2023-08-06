
import scipy.linalg as la
import numpy as np
import matplotlib.pyplot as plt
import scipy.special as sp

"""
Creating an entire pressure field based on the locations of various sources
"""
def pressure_field(positions,frequencies,
               time = 0.0,
               areas = [0.001],
               strengths = [0.01],
               phases = [0],
               x_range = [-1,1],
               y_range = [-1,1],
               point_density = 100,
               directivity_distance = 1000,
               method = "Free Space",
               directivity_only = False,
               directivity_plot_alone = False,
               show_plots = False,
               color_limits = [-50,50]):
    
    # Making all arrays that describe the sources be equal lengths
    num_sources = len(positions)
    
    if len(frequencies) == 1:
        frequencies = np.ones(num_sources) * frequencies
    
    if len(areas) == 1:
        areas = np.ones(num_sources) * areas
        
    if len(strengths) == 1:
        strengths = np.ones(num_sources) * strengths
        
    if len(phases) == 1:
        phases = np.ones(num_sources) * phases

    time = complex(time)
    
    numPoints_x = int(np.floor((x_range[1] - x_range[0]) * point_density))
    numPoints_y = int(np.floor((y_range[1] - y_range[0]) * point_density))
    x = np.linspace(x_range[0],x_range[1],numPoints_x)
    y = np.linspace(y_range[0],y_range[1],numPoints_y)

    grid = np.meshgrid(x,y)
    field_points = np.append(grid[0].reshape(-1,1),grid[1].reshape(-1,1),axis=1)
    X = grid[0]
    Y = grid[1]
    
    if method == "Rayleigh":
        
        if not directivity_only:
            pressure_field = rayleigh(positions,areas,strengths,phases,field_points,frequencies,time)
            pressure_field = pressure_field.reshape(-1,numPoints_x) # It's the number of points in the x-direction that you use here
        
        # Getting the directivity at a given distance. Default is 1000 meters away
        num_directivity_points = 1000
        directivity_points, theta = define_arc(directivity_distance,num_directivity_points)
        directivity = np.abs(rayleigh(positions,areas,strengths,phases,directivity_points,frequencies,time))
        directivity = directivity / np.max(directivity)
    
    elif method == "Free Space":
        
        if not directivity_only:
            pressure_field = monopole_field(positions,frequencies,strengths,phases,field_points,time)
            pressure_field = pressure_field.reshape(-1,numPoints_x)
        
        # Getting the directivity at a given distance. Default is 1000 meters away
        num_directivity_points = 10000
        directivity_points, theta = define_arc(directivity_distance,num_directivity_points)
        directivity = np.abs(monopole_field(positions,frequencies,strengths,phases,directivity_points,time))
        directivity = directivity / np.max(directivity)
    
    # Only show plots if you calculated the entirie pressure field
    if show_plots and not directivity_only:
        # Defining the figure
        fig, ax = plt.subplots(2,2)
        fig.set_size_inches(8,8)

        # Plotting the real part
        c = ax[0,0].pcolormesh(X,Y,np.real(pressure_field),shading = "gouraud",cmap = "RdBu",vmin = color_limits[0],vmax = color_limits[1])
        ax[0,0].set_aspect('equal')
        ax[0,0].set_title("Real Part")
        ax[0,0].set_xlabel("X (m)")
        ax[0,0].set_ylabel("Y (m)")
        fig.colorbar(c,ax = ax[0,0],fraction=0.046, pad=0.04)

        # Plotting the imaginary part
        c = ax[1,0].pcolormesh(X,Y,np.imag(pressure_field),shading = "gouraud",cmap = "RdBu",vmin = color_limits[0],vmax = color_limits[1])
        ax[1,0].set_aspect('equal')
        ax[1,0].set_title("Imaginary Part")
        ax[1,0].set_xlabel("X (m)")
        ax[1,0].set_ylabel("Y (m)")
        fig.colorbar(c,ax = ax[1,0],fraction=0.046, pad=0.04)

        # Plotting the magnitude
        c = ax[0,1].pcolormesh(X,Y,np.abs(pressure_field),shading = "gouraud",cmap = "jet",vmin = 0,vmax = color_limits[1])
        ax[0,1].set_aspect('equal')
        ax[0,1].set_title("Pressure Magnitude")
        ax[0,1].set_xlabel("X (m)")
        ax[0,1].set_ylabel("Y (m)")
        fig.colorbar(c,ax = ax[0,1],fraction=0.046, pad=0.04)

        # Plotting the directivity
        ax[1,1].axis("off")
        ax = fig.add_subplot(224,projection = 'polar')
        c = ax.plot(theta,directivity)
        ax.set_aspect('equal')
        ax.set_title(str("Directivity at {0} m".format(directivity_distance)))

        fig.show()

        
        if method == "Rayleigh":
            ax.set_thetamin(-90)
            ax.set_thetamax(90)
        
        fig.tight_layout(pad = 0.5)
        fig.show()
        
    if directivity_plot_alone:
        fig, ax = plt.subplots(1,2,subplot_kw={'projection': 'polar'})
        ax[0].plot(theta,directivity)
        ax[0].set_title("Normalized Directivity")
        
        ax[1].plot(theta,10*np.log10(directivity))
        ax[1].set_title("Normalized Directivity (dB)")
        ax[1].set_rmin(-20)
        ax[1].set_rticks([0,-5,-10,-15,-20])
        
        fig.tight_layout()
        fig.set_size_inches(8,8)
        fig.show()
        
        
    if directivity_only:
        return directivity, theta
    else:
        return pressure_field, directivity, theta

"""
Creating a field from a monopole
"""

def monopole_field(positions,frequencies,strengths,phases,field_points,time):
    
    # Convert everything to a numpy array
    positions = np.asarray(positions)
    strengths = np.asarray(strengths)
    phases = np.asarray(phases)
    field_points = np.asarray(field_points)
    
    # Initialize the responses
    responses = np.zeros([len(field_points),1], dtype = complex)
    
    # Define constants
    c = 343 # Phase speed in air
    rho_0 = 1.2 # Density of air
    
    for i in range(len(field_points)):
        
        # Define the current field point
        current_field_point = field_points[i,:]
        
        # Loop over all sources for a particular theta
        for j in range(len(strengths)):
            
            # Define the current source
            current_source_location = positions[j,:]
            current_source_strength = strengths[j]
            current_source_phase = phases[j]
            current_source_frequency = frequencies[j]
            #print(current_source_phase)
            
            # Define frequency-dependent quantities
            omega = 2 * np.pi * current_source_frequency # angular frequency
            k = omega / c # wavenumber
            
            # Get the distance between the field point and the source
            distance = get_distance(current_source_location,current_field_point)
            
            # get contribution to a theta location from an individual source
            A = 1j*rho_0*c*k/(4*np.pi) * current_source_strength
            current_source_impact = A * np.exp(-1j*k*distance)/distance * np.exp(1j * current_source_phase) * np.exp(1j*omega*time)
            
            responses[i] = responses[i] + current_source_impact
            
    return responses

"""
Perform Rayleigh Integration
"""

def rayleigh(positions,areas,strengths,phases,field_points,frequencies,time):
    
    # Convert everything to a numpy array
    positions = np.asarray(positions)
    areas = np.asarray(areas)
    strengths = np.asarray(strengths)
    phases = np.asarray(phases) 
    field_points = np.asarray(field_points)
    
    # Initialize the responses
    responses = np.zeros([len(field_points),1], dtype = complex)
    
    # Define constants
    c = 343 # Phase speed in air
    rho_0 = 1.2 # Density of air
    
    for i in range(len(field_points)):
        
        # Define the current field point
        current_field_point = field_points[i,:]
        
        # Loop over all sources for a particular theta
        for j in range(len(strengths)):
            
            # Define the current source
            current_source_location = positions[j,:]
            current_source_strength = strengths[j]
            current_source_phase = phases[j]
            current_source_area = areas[j]
            current_source_frequency = frequencies[j]
            
            # Defining the velocity
            # FIXME: Should I use the source area or source length in two dimensions?
            current_source_velocity = current_source_strength / current_source_area
            
            # Define frequency-dependent quantities
            omega = 2 * np.pi * current_source_frequency # angular frequency
            k = omega / c # wavenumber
            
            # Get the distance between the field point and the source
            distance = get_distance(current_source_location,current_field_point)
            
            # get contribution to a theta location from an individual source
            current_source_impact = (1j * omega * rho_0 / (2 * np.pi) * 
                                    current_source_velocity * 
                                    np.exp(-1j * k * distance)/distance * 
                                    np.exp(1j*current_source_phase) * np.exp(1j*omega*time) * 
                                    current_source_area)
            
            responses[i] = responses[i] + current_source_impact
            
    return responses

"""
Get the distance between two 2D points
"""
def get_distance(source_point,field_point):
    return la.norm(field_point - source_point)

"""
Define an arc for whatever reasons you may want to do so
"""
def define_arc(radius,numPoints,theta_lims = (0,360)):
    theta_min = theta_lims[0] * np.pi/180
    theta_max = theta_lims[1] * np.pi/180
    theta = np.linspace(theta_min,theta_max,numPoints)
    
    points = np.empty([0,2])
    
    for i in range(0,numPoints):
        points = np.append(points,radius * np.array([[np.cos(theta[i]), np.sin(theta[i])]]),axis = 0)
        
    return points, theta

"""
Define an array of loudspeakers
"""

def define_loudspeaker_array(num_speakers,cone_diameter,cone_separation,
                             cone_strengths = [1],
                             cone_phases = [0],
                             num_points = 100,
                             show_plots = False):

    if len(cone_strengths) == 1:
        cone_strengths = np.ones(num_speakers) * cone_strengths
        
    if len(cone_phases) == 1:
        cone_phases = np.ones(num_speakers) * cone_phases

    total_length = cone_diameter*num_speakers + cone_separation*num_speakers

    cone_positions = np.array([]);
    for i in range(num_speakers):
        cone_positions = np.append(cone_positions,i*cone_separation + cone_diameter/2)
        
    # Centering about the origin
    cone_positions = cone_positions - max(cone_positions)/2 - cone_diameter/4


    # Creating the array of mini-sources
    positions = np.linspace(min(cone_positions) - cone_diameter/2,max(cone_positions)+cone_diameter/2,num_points)
    strengths = np.zeros(len(positions))
    phases = np.zeros(len(positions))
    for i in range(0,len(positions)):

        for j in range(0,num_speakers):

            if np.abs(positions[i] - cone_positions[j]) <= cone_diameter:
                strengths[i] = cone_strengths[j]
                phases[i] = cone_phases[j]

    if show_plots:
        plt.figure()
        plt.plot(positions,strengths)
        plt.title("Speaker Cone Source Strengths")
        plt.xlabel("Position (m)")
        plt.ylabel("Cone Source Strength (m^3/s)")
        
        plt.figure()
        plt.plot(positions,phases)
        plt.title("Speaker Cone Source Phases")
        plt.xlabel("Position (m)")
        plt.ylabel("Cone Phase (rad/s)")
        
    return positions, strengths, phases, cone_positions