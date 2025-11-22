# Set the output terminal to Encapsulated PostScript (EPS)
# This is the standard vector format for LaTeX 2e
set terminal postscript eps color solid "Helvetica" 14
set output "debian_plot.eps"

# Set the chart title and axis labels
set title "Growth of Debian Packages (1995-2025)"
set xlabel "Year"
set ylabel "Number of Packages"

# Set axis ranges and tick marks
set xrange [1994:2026]
set yrange [0:78000]
set xtics 1995, 5, 2025  # Major tick every 5 years
set grid     # Enable grid lines

# Add text annotations to highlight specific releases
set label "Buzz" at 1996, 2000 center
set label "Woody" at 2002, 10000 left
set label "Wheezy" at 2013, 39000 left
set label "Bookworm" at 2023, 66000 right
set label "Trixie" at 2024, 70000 center

# Plot the data
# 'using 1:2' means use column 1 for X and column 2 for Y
# 'linespoints' draws both lines and points
# 'pt 7' is a solid circle, 'ps 1.0' is point size
plot "debian.dat" using 1:2 title "Packages in Main" with linespoints 2 7