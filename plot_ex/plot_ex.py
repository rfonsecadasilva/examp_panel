from plot import Hs_Mfv_fig
import xarray as xr
import numpy as np
import panel as pn
pn.extension()
path="data/"
ds=xr.merge([xr.open_dataset(path+i) for i in ["GRID.nc","HSIG.nc","MVEL.nc"]])
Nx=18
dep_levels=np.arange(9)/Nx
fig = lambda dx,dy,vel_clip_max,scale:Hs_Mfv_fig(ds,dx=dx,dy=dy,vel_clip_max=vel_clip_max,vel_clip_min=0.30,scale=scale,plot_dep_dev=False,dep_levels=dep_levels,Hs0=0.11)
a=pn.interact(fig,dx=np.arange(1,10),dy=np.arange(1,10),vel_clip_max=[0.5,0.6,0.7,0.8,0.9],scale=[0.5,1,2,4,8])
b=pn.Column(pn.Row(a[1]),pn.Row(a[0]))
b.servable()