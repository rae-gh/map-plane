#####################################################################
#RSA 17/03/23
#This helper function makes it easier to plot for demonstrations and examples, paritclarly on the colab page
#####################################################################

from map_plane.vxyz import spacetransform as space
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np


#####################################################################
PUBLICATION_CONFIG = {
    'toImageButtonOptions': {
        'format': 'png',
        'width': 2079,    # 8.8cm at 600dpi
        'height': 2079,
        'scale': 1
    }
}
#####################################################################
class MapPlotHelp(object):
    def __init__(self,filename):
        # PUBLIC INTERFACE
        self.filename = filename
        self.plots_2d = []
        self.plots_3d = []

    def add_plot_slice_2d(self,vals,tag):
        self.plots_2d.append((vals,tag))

    def add_plot_slice_3d(self,vals,tag):
        self.plots_3d.append((vals,tag))

    def make_plot_slice_3d(self,vals,min_percent=1, max_percent=1,
                            hue="GBR",title="Leucippus Plot 3d",levels=20,
                            transparency="medium"):

        #Takes a mat3d object and plots it in plotly

        #Input
        #---------
        #vals : mat3d
        #min_percent : 1
        #max_percent : 1
        #hue : GBR/GRB/BW/WB/RB/BR/GI/IG/MASK
        #title : "Leucippud Plot 3d
        #levels : 20
        #https://plotly.com/python/3d-isosurface-plots/
        #turn data into scatter for iso_surface

        xs = []
        ys = []
        zs = []
        values = []

        #fig = make_subplots(rows=1, cols=1,subplot_titles=[title],horizontal_spacing=0.05,vertical_spacing=0.05)

        minv = 1000
        maxv = -1000

        a,b,c = vals.shape()
        for i in range(a):
            for j in range(b):
                for k in range(a):
                    val = 0
                    if k < c:
                        val = vals.get(i,j,k=k)
                        minv = min(minv,val)
                        maxv = max(maxv,val)
                    xs.append(i)
                    ys.append(j)
                    zs.append(k)
                    values.append(val)


        #if hue == "RINGS":
        #    minv,maxv =  -0.5,1.5
        #    min_percent,max_percent = 1,1

        #if hue != "MASK":
        absmin,absmax,d0,d1,d2 = self.__get_levels__(values,min_percent,max_percent)
        #else:
        #absmin,absmax,d0,d1,d2 = minv,maxv,1,1,1



        colorscale=self.__get_colors__(hue,d0,d1,d2,transparency=transparency)

        fig= go.Figure(data=go.Isosurface(
        x=xs,
        y=ys,
        z=zs,
        value=values,
        colorscale=colorscale,
        showscale=True,
        showlegend=False,
        opacity=0.6,
        surface_count=levels,
        caps=dict(x_show=False, y_show=False,z_show=False),
        isomin=absmin,
        isomax=absmax,
        ),)

        fig.update_xaxes(showticklabels=False,visible=False,scaleanchor="x",scaleratio=1) # hide all the xticks
        fig.update_yaxes(showticklabels=False,visible=False,scaleanchor="x",scaleratio=1) # hide all the yticks

        fig.update_layout(title=dict(text=title),
                            scene = dict(
                            xaxis = dict(visible=False),
                            yaxis = dict(visible=False),
                            zaxis =dict(visible=False)
                        )
    )


        #print(values)
        if self.filename == "SHOW":
            fig.show(config=PUBLICATION_CONFIG)
        elif self.filename == "FIG":
            return fig
        elif ".html" in self.filename:
            fig.write_html(self.filename,config=PUBLICATION_CONFIG)
        else:
            fig.write_image(self.filename,width=2079,height=2079)

    def make_plot_slice_2d(self,vals2d,
                           plot_type="contour",
                           points=[],
                           naybs=[],
                           min_percent=0,
                           max_percent=100,
                           hue="GBR",
                           levels=20,
                           title="Map-Plane Plot 2d",
                           samples=-1,width=-1,
                           transparency="no",
                           plotwidth=2079):
        #https://plotly.com/python/3d-isosurface-plots/
        vals = vals2d.tolist()
        fig = make_subplots(
            rows=1, cols=1,
            horizontal_spacing=0.05,
            vertical_spacing=0.05)

        mind,maxd = 1000,-1000
        for i in range(len(vals)):
            for j in range(len(vals[0])):
                mind = min(vals[i][j],mind)
                maxd = max(vals[i][j],maxd)

        # quartiles

        # Flatten to 1D and find percentile
        absmin,absmax,d0,d1,d2 = self.__get_levels__(vals,min_percent,max_percent)
        contours = abs((absmax-absmin)/levels)
        #print("absmin:", absmin)
        #print("absmax:", absmax)
        #print("d0:", d0)
        #print("d1:", d1)
        #print("d2:", d2)
        #print(f"Contours: {contours}")

        colorscale=self.__get_colors__(hue,d0,d1,d2,transparency=transparency,)

        if len(naybs) > 0:
            if plot_type == "contour":
                data_vals = go.Contour(z=vals,showscale=False,
                                colorscale=colorscale,
                                contours=dict(start=absmin,end=absmax,size=contours),
                                text=naybs,
                                hovertemplate='<br>%{z:.4f}<br>%{text}',
                                line=dict(width=0.2,color="gray"),
                                zmin=absmin,zmax=absmax,name='')
            elif plot_type == "heatmap":
                data_vals = go.Heatmap(z=vals,showscale=False,
                                colorscale=colorscale,
                                text=naybs,
                                hovertemplate='<br>%{z:.4f}<br>%{text}',
                                zmin=absmin,zmax=absmax,name='')
        else:
            if plot_type == "contour":
                #print("Plotting contour with absmin:", absmin, "absmax:", absmax, "contours:", contours)
                data_vals = go.Contour(z=vals,showscale=False,
                                colorscale=colorscale,
                                contours=dict(start=absmin,end=absmax,size=contours),
                                hovertemplate='<br>%{z:.4f}<br>%{text}',
                                line=dict(width=0.2,color="gray"),
                                zmin=absmin,zmax=absmax,name='')
            elif plot_type == "heatmap":
                #print("Plotting heatmap with absmin:", absmin, "absmax:", absmax)
                data_vals = go.Heatmap(z=vals,showscale=False,
                                colorscale=colorscale,
                                hovertemplate='<br>%{z:.4f}<br>%{text}',
                                zmin=absmin,zmax=absmax,name='')


        fig.add_trace(data_vals,row=1,col=1)
        if len(points) == 3:
            data_scatter = self.add_points(points,samples,width, plotwidth)
            fig.add_trace(data_scatter,row=1,col=1)
        fig.update_xaxes(showticklabels=False,visible=False) # hide all the xticks
        fig.update_yaxes(showticklabels=False,visible=False) # hide all the xticks
        fig.update_yaxes(scaleanchor="x",scaleratio=1)
        fig.update_xaxes(scaleanchor="y",scaleratio=1)

        header_padding = 0.98
        top = 100
        if title == "":
            header_padding = 0.2
            top = 10

        fig.update_layout(
            margin=dict(l=1, r=1, t=top, b=10),  # t=30 gives title room
            title=dict(
                xanchor='center',
                text=title,
                x=0.5,
                y=header_padding,
                yanchor='top',
                font=dict(size=60, color='black')
            ),
            # Remove margins and background
            paper_bgcolor='white',
            plot_bgcolor='white',
            # Remove colour bar
            coloraxis_showscale=False,
            # Make the figure exactly the heatmap with no padding
            width=plotwidth,
            height=plotwidth,
            yaxis=dict(autorange='reversed')
        )


        #print(values)
        PUBLICATION_CONFIG['toImageButtonOptions']['filename'] = title.replace(" ","_")
        if self.filename == "SHOW":
            fig.show(config=PUBLICATION_CONFIG)
        elif self.filename == "FIG":
            return fig
        elif ".html" in self.filename:
            fig.write_html(self.filename,config=PUBLICATION_CONFIG)
        else:
            fig.write_image(self.filename,width=plotwidth, height=plotwidth)

    def add_points(self, points,samples,width,plotwidth):
        # First create the dots for the potitions as a scatter plot
        spc = space.SpaceTransform(points[0], points[1], points[2])
        posC = spc.reverse_transformation(points[0])
        posL = spc.reverse_transformation(points[1])
        posP = spc.reverse_transformation(points[2])
        posCp = posC.get_point_pos(samples,width)
        posLp = posL.get_point_pos(samples,width)
        posPp = posP.get_point_pos(samples,width)
                        
        scatterX = []
        scatterY = []
        # The C value will be zero as it is on the plane - that is because these are the points we made the plane with
        # The xy heatmap has been arranged so the x value is above so linear is upwards, so the y axis (ok a bit confusing.... should I change it)?
        if posCp.A > 0 and posCp.A < samples and posCp.B > 0 and posCp.B < samples:
            scatterX.append(posCp.B)
            scatterY.append(posCp.A)
        if posLp.A > 0 and posLp.A < samples and posLp.B > 0 and posLp.B < samples:
            scatterX.append(posLp.B)
            scatterY.append(posLp.A)
        if posPp.A > 0 and posPp.A < samples and posPp.B > 0 and posPp.B < samples:
            scatterX.append(posPp.B)
            scatterY.append(posPp.A)
  ###############################################################################

        data_scatter = go.Scatter(x=scatterX,y=scatterY,mode="markers",marker=dict(color="yellow",size=5),showlegend=False,hoverinfo='skip',hovertemplate='',name='')

        return data_scatter

    def __get_levels__(self,values,min_percent=0, max_percent=100):

        per_min = np.percentile(values, min_percent)    # 5th percentile   else:
        per_max = np.percentile(values, max_percent)  # 95th percentile

        actual_min = float(np.min(values))
        actual_max = float(np.max(values))

        #print(f"Actual min: {actual_min}, Actual max: {actual_max}")
        #print(f"Requested percentiles: {min_percent}th percentile = {per_min}, {max_percent}th percentile = {per_max}")

        if per_max <= per_min:
            d0, d1, d2 = 0,0.5, 1
            print(f"Warning: per_max is less than or equal to per_min, check the min_percent and max_percent values, {per_min} and {per_max}")
        elif actual_max <= actual_min:
            d0, d1, d2 = 0,0.5, 1
            print(f"Warning: actual_max is less than or equal to actual_min, check the data values, {actual_min} and {actual_max}")
        else:
            # scale the percentiles to 0-1 for the colorscale
            def scaled(x, min_val, max_val):
                x = x - min_val
                x = x / (max_val - min_val)
                return x
            d0 = scaled(per_min, actual_min, actual_max)
            d1 = scaled((per_min + per_max)/2, actual_min, actual_max)
            d2 = scaled(per_max, actual_min, actual_max)

        return per_min,per_max,d0,d1,d2
        #return float(absmin),float(absmax),float(d0),float(d1),float(d2)

    def __get_colors__(self,hue,d0,d1,d2,transparency):
        if d0 < 0 or d0 > 1 or d1 < 0 or d1 > 1 or d2 < 0 or d2 > 1:
            print("Warning: levels are out of bounds for colorscale, check the min_percent and max_percent values")

        t0,t1,t2,t3,t4,tx,tl,tm,tu = 1,1,1,1,1,1,1,1,1
        if transparency == "low":
            t0,t1,t2,t3,t4 = 0.5,0.5,0.5,0.5,0.5
            tx = 0.5
            tl,tm,tu = 0,0.5,1
        elif transparency == "medium":
            t0,t1,t2,t3,t4 = 0.4,0.1,0.4,0.5,0.4
            tx = 0.5
            tl,tm,tu = 0.1,0.5,0.4
        elif transparency == "high":
            t0,t1,t2,t3,t4 = 0,0.7,0.5,0.2,0
            tx = 0.5
            tl,tm,tu = 0.1,0.5,0.1
        if hue == 'GRB':
            t0,t1,t2,t3,t4 = t0,t1,t4,t3,t2
        elif hue == "RB" or hue == 'GI':
            tl,tm,tu = tu,tm,tl

        grey = f"rgba(119,136,153,{t0})"
        snow = f"rgba(240,248,255,{t1})"
        cornflower = f"rgba(100,149,237,{t2})"
        crimson = f"rgba(220,20,60,{t3})"
        darkred = f"rgba(100,0,0,{t4})"
        navy = f"rgba(0,0,128,{t4})"

        black = f"rgba(0,0,0,{tx})"
        ghost = f"rgba(248,248,255,{tx})"
        coral = f"rgba(255, 182, 193,{tx})"
        sky = f"rgba(176, 196, 222,{tx})"


        midnight = f"rgba(25,25,112,{tl})"
        maroon = f"rgba(128,0,0,{tu})"

        indigo = f"rgba(75,0,130,{tl})"
        sea = f"rgba(32,178,170,{tu})"

        slate = f"rgba(40,79,79,{0.7})"
        fire = f"rgba(178,34,34,{0.7})"
        alice = f"rgba(240,248,255,{0.7})"
        rose = f"rgba(255,228,225,{0.7})"

        if hue == "GBR":
            return [(0, grey), (d0, snow), (d1, cornflower),(d2, crimson),(1.0, darkred)]
        elif hue == "GRB":
            return [(0, grey), (d0, snow), (d1, crimson),(d2, cornflower),(1.0, navy)]
        elif hue == "BW":
            return [(0, black),(1.0, ghost)]
        elif hue == "WB":
            return [(0, ghost),(1.0, black)]
        elif hue == "RB":
            if d0 <= 0:
                return [(0,maroon),(0.5,ghost),(1.0,midnight)]
            else:
                return [(0,maroon),(d0,ghost),(1.0,midnight)]
        elif hue == "BR":
            if d0 <= 0:
                return [(0,midnight),(0.5,ghost),(1.0,maroon)]
            else:
                return [(0,midnight),(d0,ghost),(1.0,maroon)]
        elif hue == "CP":
            return [(0,maroon),(0.45,coral),(0.48,black),(0.52,black),(0.55,sky),(1.0,midnight)]
        elif hue == "R":
            if d0 <= 0:
                return [(0,maroon),(0.5,ghost),(1.0,midnight)]
            else:
                return [(0,maroon),(d0,ghost),(1.0,midnight)]
        elif hue == "IG":
            if d0 <= 0:
                return [(0,indigo),(0.5,ghost),(1.0,sea)]
            else:
                return [(0,indigo),(d0,ghost),(1.0,sea)]
        elif hue == "GI":
            if d0 <= 0:
                return [(0,sea),(0.5,ghost),(1.0,indigo)]
            else:
                return [(0,sea),(d0,ghost),(1.0,indigo)]
        elif hue == "MASK":
            return [(0,alice),(0.1,alice),(0.2,slate),(0.8,fire),(0.9,rose),(1.0,rose)]
















