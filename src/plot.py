import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np

def plotData(data, velocities, eq_coords, gal_coords, lsr, time):
    # Create figure and title
    fig = plt.figure(figsize=(10,7))
    fig.suptitle(f"Observation at: {time}", fontsize=16)
    
    # Add grid for table and plot
    grid = fig.add_gridspec(5,1)
    table_ax = fig.add_subplot(grid[0,0])
    spectrum_ax = fig.add_subplot(grid[1:,0])

    # Plot table with details
    table_ax.axis("off")
    labels = [r"Galactic $l$/$b$", r"Equatorial $RA$/$Dec$", "LSR correction"]
    values = [[fr"{gal_coords[0]}$^\circ$ / {gal_coords[1]}$^\circ$", fr"{eq_coords[0]}$^\circ$ / {eq_coords[1]}$^\circ$", f"{-lsr}" + r"$\frac{km}{s}$"]]
    color = [colors.to_rgba("b", 0.5)]*len(labels)
    table = table_ax.table(cellText = values, colLabels = labels, colColours = color, cellLoc = "center", loc="center")
    table.auto_set_font_size(False)

    # Set font size of column labels and cell values
    for cell in table._cells:
        if cell[0] != 0:
            table._cells[cell].set_fontsize(12)
        else:
            table._cells[cell].set_fontsize(16)

    table.scale(1,3)
    
    # Plot spectrum
    spectrum_ax.plot(velocities, data, color = "b", linewidth = 0.75, label = "Observed data")
    spectrum_ax.set(xlim = (velocities[0], velocities[-1]))
    spectrum_ax.set(xlabel = r"Radial velocity [$\frac{km}{s}$]")

    # Plot 0 km/s reference line
    spectrum_ax.axvline(x = 0, color = colors.to_rgba('k', 0.5), linestyle = ':', linewidth = 1, label = 'Theoretical frequency')
    
    # Add legend, gridlines and padding
    spectrum_ax.legend(prop = {'size': 10}, loc = 1)
    plt.tight_layout(pad=1.5)
    plt.show()
