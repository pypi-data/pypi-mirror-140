
# modules
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import warnings

from statsmodels.nonparametric.smoothers_lowess import lowess
from matplotlib import collections as matcoll

warnings.filterwarnings('ignore')

# Building package

class Mplot:
    """
    Class for plotting different OLS model iagnostic checks. 
    Reproduces the diagnostic plots in mplot package in R
    
    Attributses:
        mdl (object) representing statsmodels OLS model results
        n (int) representing the diagnostic check to plot
            1 = Residuals vs Fitted
            2 = Normal Q-Q
            3 = Scale-Location
            4 = Cook's Distance
            5 = Residuals vs Leverage
            6 = Cook's dist vs Leverage
            7 = 95% confidence intervals

    """
 
    def __init__(self, mdl, n):
        
        self.mdl = mdl
        self.n = n
        
        # fitted values
        self.fitted_values = pd.Series(self.mdl.fittedvalues)
        self.res_df = pd.DataFrame(self.fitted_values, index = self.mdl.fittedvalues.index, columns = ['fitted_values'])
        
        # residuals
        self.res_df['residuals'] = self.mdl.resid
        
        # Standardized (studentized) residuals
        self.res_df['student_residuals'] = self.mdl.get_influence().resid_studentized_internal
        
        # square rootof studentized residuals 
        self.res_df['sqrt_student_residuals'] = np.sqrt(np.abs(self.res_df['student_residuals']))
        
        # leverage
        self.res_df['leverage'] = self.mdl.get_influence().hat_matrix_diag

        # cooks distance
        self.res_df['cooks_distance'] = self.mdl.get_influence().cooks_distance[0]
        
        # parameter details
        self.df_params = pd.DataFrame(self.mdl.params.reset_index())
        self.df_params.columns = ['var', 'coef']
        self.df_params['errors'] = self.df_params['coef'] - self.mdl.conf_int().iloc[:,0].values
        self.df_params['pvalues'] = self.mdl.pvalues.values
        self.df_params['Significant'] = self.df_params['pvalues'] < 0.05
        #self.df_params.sort_values(by='coef', ascending = True, inplace = True)
        
    def plot(self):
        """
        Function to generate plot for chosen diagnostic check
        
        Args:
            None
        
        Returns
            Matplotlib plot: Plot of chosen diagnostic check
        """
        
        plt.style.use('ggplot')
        
        if self.n == 1:
            fig, ax = plt.subplots(figsize = (10,8))
            
            # rows with top residuals 
            top3 = abs(self.res_df['residuals']).sort_values(ascending = False)[:3]
            
            # x - cordinates
            X = self.res_df['fitted_values']
            # y - cordinates
            Y = self.res_df['residuals']
            # smoothened values for the regplot
            smoothed = lowess(self.res_df['residuals'],self.res_df['fitted_values'])
            
            #plotting
            
            ax.scatter(X, Y, linewidth = 3, alpha = 0.85, s = 6)
            ax.plot(smoothed[:,0], smoothed[:,1], color = 'k')
            ax.set_ylabel('Residuals', fontsize = 12, fontweight = 'bold')
            ax.set_xlabel('Fitted Values', fontsize = 12, fontweight = 'bold')
            ax.set_title('Residuals vs. Fitted', fontsize = 14, fontweight = 'bold')
            ax.plot([min(X),max(X)],[0,0],color = 'k',linestyle = ':', alpha = .8)
            for i in top3.index:
                ax.annotate(i,
                            xy=(X[i], Y[i]),
                            fontsize = 10, color = 'k', fontweight = 'bold'
                           )
            return plt.show()  
        
        if self.n == 2:
            fig, ax = plt.subplots(figsize = (10,8))
            Y = self.res_df['residuals']
           
            # qq plot from statsmodels.api = sm
            QQplot = sm.qqplot(Y, fit = True, line = "q",ax = ax)
            # qqplot title
            QQplot.axes[0].set_title('Normal Q-Q', fontsize = 14, fontweight = 'bold')
            # x_axis title
            QQplot.axes[0].set_xlabel('Theoretical Quantiles', fontsize = 12, fontweight = 'bold')
            # y_axis title
            QQplot.axes[0].set_ylabel('Standardized Residuals', fontsize = 12, fontweight = 'bold')
            
            # Annotation
            # top residuals from the plot
            locator = np.arange(3)-3
            # get plot x and y values
            axes = plt.gca()
            line = axes.lines[0]
            x_values = line.get_xdata()
            y_values = line.get_ydata()
            for i, j in enumerate(locator):
                indx = np.argsort(np.abs(Y)).values[j]
                QQplot.axes[0].annotate(indx,
                                        xy = (x_values[j], y_values[j]),
                                        fontsize = 10, color = 'k', fontweight = 'bold'
                                       )  
            return plt.show() 
        
        if self.n == 3:
            fig, ax = plt.subplots(figsize = (10,8))
            X = self.res_df['fitted_values']
            Y = self.res_df['sqrt_student_residuals']
            smoothed = lowess(Y,X)

            # rows with top residuals 
            top3 = abs(self.res_df['residuals']).sort_values(ascending = False)[:3]
            
            ax.scatter(X, Y, alpha = 0.85, linewidths = 3,color = 'r', s = 6)
            ax.plot(smoothed[:,0],smoothed[:,1],color = 'k');
            ax.set_ylabel('$\sqrt{Studentized \ Residuals}$', fontsize = 12, fontweight = 'bold')
            ax.set_xlabel('Fitted Values', fontsize = 12, fontweight = 'bold')
            ax.set_title('Scale-Location', fontsize = 14, fontweight = 'bold')
            ax.set_ylim(0,max(Y)+0.1)
            for i in top3.index:
                ax.annotate(i,
                            xy = (X[i],Y[i]),
                            fontsize = 10, color = 'k', fontweight = 'bold'
                           )
            return plt.show()  
        
        if self.n == 4:  
            
            # cordinates
            df_res = self.res_df.reset_index().drop('index', axis=1)
            X = df_res.index
            Y = df_res['cooks_distance']
            
            # rows with the highest cook distance
            top3 = abs(df_res['cooks_distance']).sort_values(ascending = False)[:3]

            # creates cordinates for vertical lines
            lines = []
            for i in range(len(X)):
                pair = [(X[i],0), (X[i], Y[i])]
                lines.append(pair)
            linecoll = matcoll.LineCollection(lines)
            
            # plot
            fig, ax = plt.subplots(figsize = (10,8))
            ax.add_collection(linecoll)
            plt.scatter(X,Y, alpha = 0.85, linewidths = 3,color = 'r', s = 6)
            ax.set_ylabel("Cook's distance", fontsize = 12, fontweight = 'bold')
            ax.set_xlabel('Observation number', fontsize = 12, fontweight = 'bold')
            # annotation
            for i in top3.index:
                ax.annotate(i,
                            xy = (X[i],Y[i]),
                            fontsize = 10, color = 'k', fontweight = 'bold'
                           )
            return plt.show()

        if self.n == 5: 
            
            # studentized residuals
            student_residuals = pd.Series(self.mdl.get_influence().resid_studentized_internal)
            student_residuals.index = self.mdl.resid.index
            df = pd.DataFrame(student_residuals)
            df.columns = ['student_residuals']
            # leverage
            df['leverage'] = self.mdl.get_influence().hat_matrix_diag
            
            # top 3
            sorted_student_residuals = abs(df['student_residuals']).sort_values(ascending = False)
            top3 = sorted_student_residuals[:3]

            # cordinates
            x = df['leverage']
            y = df['student_residuals']
            smoothed = lowess(y, x)
            
            # plot
            fig, ax = plt.subplots(figsize = (8,6))
            ax.scatter(x, y, linewidths = 3,color = 'r', s = 6)
            ax.plot(smoothed[:,0],smoothed[:,1],color = 'k')
            ax.set_ylabel('Studentized Residuals', fontsize = 12, fontweight = 'bold')
            ax.set_xlabel('Leverage', fontsize = 12, fontweight = 'bold')
            ax.set_title('Residuals vs. Leverage', fontsize = 14, fontweight = 'bold')
            ax.set_ylim(min(y)-abs(min(y))*0.25,max(y)+max(y)*0.15)
            ax.set_xlim(-0.01,max(x)+max(x)*0.05)
            plt.tight_layout()
            for val in top3.index:
                ax.annotate(val,
                            xy = (x.loc[val],y.loc[val]),
                            fontsize = 10, color = 'k', fontweight = 'bold'
                           )

            xpos = max(x)+max(x)*0.01  
            cooksx = np.linspace(min(x), xpos, 50)
            p = len(self.mdl.params)
            poscooks1y = np.sqrt((p*(1-cooksx))/cooksx)
            poscooks05y = np.sqrt(0.5*(p*(1-cooksx))/cooksx)
            negcooks1y = -np.sqrt((p*(1-cooksx))/cooksx)
            negcooks05y = -np.sqrt(0.5*(p*(1-cooksx))/cooksx)
            ax.plot(cooksx,poscooks1y,label = "Cook's Distance", ls = ':', color = 'r')
            ax.plot(cooksx,poscooks05y, ls = ':', color = 'r')
            ax.plot(cooksx,negcooks1y, ls = ':', color = 'r')
            ax.plot(cooksx,negcooks05y, ls = ':', color = 'r')
            ax.plot([0,0],ax.get_ylim(), ls=":", alpha = .3, color = 'k')
            ax.plot(ax.get_xlim(), [0,0], ls=":", alpha = .3, color = 'k')
            ax.annotate('1.0', xy = (xpos, poscooks1y[-1]), color = 'r')
            ax.annotate('0.5', xy = (xpos, poscooks05y[-1]), color = 'r')
            ax.annotate('1.0', xy = (xpos, negcooks1y[-1]), color = 'r')
            ax.annotate('0.5', xy = (xpos, negcooks05y[-1]), color = 'r')
            ax.legend()
            
            return plt.show()


        if self.n == 6: 
            fig, ax = plt.subplots(figsize = (10,8))
            # cordinates
            X = self.res_df['leverage']
            Y = self.res_df['cooks_distance']
            smoothed = lowess(Y,X)
            
            # rows with highest cooks distance
            top3 = abs(Y).sort_values(ascending = False)[:3]

            # plot
            ax.scatter(X, Y, alpha = 0.85, linewidths = 3,color = 'r', s = 6)
            ax.plot(smoothed[:,0],smoothed[:,1],color = 'k')
            ax.set_ylabel("Cook's distance", fontsize = 12, fontweight = 'bold')
            ax.set_xlabel('Leverage', fontsize = 12, fontweight = 'bold')
            ax.set_title("Cook's dist vs. Leverage", fontsize = 14, fontweight = 'bold')
            # annotation
            for i in top3.index:
                ax.annotate(i,
                            xy = (X.loc[i],Y.loc[i]),
                            fontsize = 10, color = 'k', fontweight = 'bold'
                           )
            return plt.show()
        
        if self.n == 7: 
            fig, ax = plt.subplots(figsize = (10,8))

            self.df_params.plot(x = 'var', y = 'coef',
                           kind = 'barh',
                           ax = ax, color = 'none', fontsize = 22, 
                           ecolor = self.df_params.Significant.map({True: '#20B2AA', False: '#F08080'}),
                           capsize = 0,
                           xerr = 'errors', 
                           legend = False
                          )
            # locate the coefficients on the confidence interval
            ax.scatter(y = pd.np.arange(self.df_params.shape[0]), 
                       marker = 'o',
                       s = 160, 
                       x = self.df_params['coef'], 
                       color = self.df_params.Significant.map({True: '#20B2AA', False: '#F08080'}),
                      )

            # the zero axis line
            ax.axvline(x = 0, linestyle = '--', color = '#F08080', linewidth = 1)

            # plot title
            plt.title('95% confidence intervals', fontsize = 16, fontweight = 'bold')

            # font sizes for the axis
            ax.tick_params(axis = 'both', which = 'major', labelsize = 10)

            # font size for the coefficients
            ax.set_ylabel('Coefficients',fontsize = 12, fontweight = 'bold')

            # font size for the variables
            ax.set_xlabel('estimates',fontsize = 12, fontweight = 'bold')

            return plt.show()
        
