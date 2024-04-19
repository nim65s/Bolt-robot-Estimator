import numpy as np
import matplotlib.pyplot as plt


    
# a class for plotting the computed trajectories and comparing them
class Graphics:
    def __init__(self, logger=None):
        self.currentColor = 0
        self.colors = ['#73d2de', '#8f2d56', '#ffbc42', '#218380', '#d81159', '#fe7f2d', '#3772ff', '#70161E', '#F46036']
        self.counter = 1
        if logger is not None :
            self.logger = logger
            self.logger.LogTheLog("started Graphics")

    def start(self, titre):
        # initialize a pretty plot
        self.currentColor = 0
        plt.figure(self.counter, dpi=200)
        plt.grid('lightgrey')
        if titre != '':
            plt.title(titre)
        self.counter += 1
    
    def SetLegend(self, legend, ndim=0):
        if ndim != 0: self.ndim=ndim
        self.legend = []
        for l in legend:
            for dir in [" - x", " - y", " - z"][:self.ndim]:
                self.legend = self.legend + [l+dir]
        
        
    def plot2DTraj(self, trajs, titre=''):
        # plot a x, y traj in its plane
        # data : [ [x] [y] ]
        self.start(titre)
        for traj in trajs :
            plt.plot(traj[0], traj[1], self.colors[self.currentColor])
            self.currentColor = (self.currentColor+1)%len(self.colors)
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.show()
    
    def CompareNDdatas(self, dataset, datatype="speed", title='', StyleAdapter=False, width=1, selectmarker=[]):
        # plot a X or X,Y or X,Y,Z dataset evolving over time
        # enable StyleAdapter when datas are not very different from one another
        # data : [ [data1: [x][y][z]   ] [data2: [x][y][z]   ] ]
        self.start(title)
        self.ndim = len(dataset[0])
        marker = len(selectmarker) >0
        # adjust size of things following approximate number of curves to plot
        legsize = max(3, round(9 - len(dataset) * len(dataset[0])/ 4  ))
        width = max(0.8, round(9 - len(dataset) * len(dataset[0]))/3)
        #print(width)
        

        if StyleAdapter:
            # adjust linestyle
            style = ['solid', 'dotted', 'solid', 'solid', 'dashed', 'dotted']
        else :
            style = ['-']

        if "Noisy" in self.legend[0] or "noisy" in self.legend[0] or "true" in self.legend[0]:
            # adjust width 
            Width = [width/2] + [width]
        else:
            Width = [width]
        k,j=0,0
        for data in dataset :
            for line in data :
                if marker : # select marker
                    plt.plot(line, self.colors[self.currentColor], linewidth=Width[j], marker='D', markevery=selectmarker)
                else :
                    plt.plot(line, self.colors[self.currentColor], linestyle=style[k], linewidth=Width[j])
                self.currentColor = (self.currentColor+1)%len(self.colors)
            k = (k+1)%len(style)
            j = min(len(Width)-1, j+1)
        

        plt.legend(self.legend, fontsize=legsize)
        
        plt.xlabel('sample (N)')
        plt.ylabel(datatype + 's')
        #plt.show()
    
    def end(self):
        # so that all grapph appear at once
        plt.show()
    



