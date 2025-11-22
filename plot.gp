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
set yrange [0:75000]
set xtics 5  # Major tick every 5 years
set mxtics 5 # Minor ticks
set grid     # Enable grid lines

# Add text annotations to highlight specific releases
set label "Buzz" at 1996, 2000 center font "Helvetica,10"
set label "Woody" at 2002, 10000 left font "Helvetica,10"
set label "Wheezy" at 2013, 39000 left font "Helvetica,10"
set label "Bookworm" at 2023, 66000 right font "Helvetica,10"
set label "Trixie" at 2025, 72000 center font "Helvetica,10"

# Plot the data
# 'using 1:2' means use column 1 for X and column 2 for Y
# 'linespoints' draws both lines and points
# 'pt 7' is a solid circle, 'ps 1.0' is point size
plot "debian.dat" using 1:2 title "Packages in Main" with linespoints lw 2 pt 7 ps 1.0 lc 3