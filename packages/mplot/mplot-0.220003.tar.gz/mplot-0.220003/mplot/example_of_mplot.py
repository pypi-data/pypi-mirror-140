import new_plot as plot
from mplot.color import *

x = list(range(2010,2020))
y = [1,1.1,1.24,1.18,1.5,1.46,1.99,2.0,2.34,2.55]
mat = [1000,1024,1032,1054,1045,1046,1056,1035,1076,1053]
def translate(alist,mult,add):
    newlist = []
    for elem in alist:
        val = elem*mult+add
        newlist.append(val)
    return newlist

yhigh = translate(y,1.23,0.1)
ylow = translate(y,0.89,-0.1)
pave = plot.line(x,y,legend = 'Average',color = BLUE)
pbet = plot.areabetween(x,yhigh,ylow,legend = 'Range',color = BLUE,alpha = 0.2)
pmat = plot.line(x,mat,legend = 'Matches',color = RED)
plot.displaysubplots([[[pave],[pbet]],[[pmat],[pmat]]],'examplegraph',title = 'Example savings',
             ylabel = 'Savings $',ylabels = ['hap\npy','bear'])


