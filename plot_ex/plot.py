import warnings, math
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

def Hs_Mfv_fig(ds,xmin=None,xmax=None,dx=None,ymin=None,ymax=None,dy=None,scale=None,vel_clip_max=0.9,vel_clip_min=0.1,plot_dep_dev=False,dep_levels=None,hs_levels=None,hs_ticks=None,Hs0=None,cmap="jet"):
    """
    Create 2D fig with significant wave height and mass flux velocities.
    Args:
        ds (xr data structure): Single data structure with 'x', 'Botlev', 'Hs', 'Mfvx' and Mfvy'.
        xmin (float, optional): minimum x-position (m). If None, ds.x.min().
        xmax (float, optional): maximum x-position (m). If None, ds.x.max().
        ymin (float, optional): minimum y-position (m). If None, ds.y.min().
        ymax (float, optional): maximum y-position (m). If None, ds.y.max().
        scale (float, optional): quiver scale (larger values result in smaller arrows). Default to 1.
        vel_clip_max (float, optional): maximum x- and y-velocity clip (in % of x quantile). Default to 0.9.
        vel_clip_min (float, optional): minimum absolute velocity (in % of x quantile) to be plotted (otherwise nan). Default to 0.1
        plot_dep_dev (bool), optional: Condition plotting deviations from depth at the first cross-shore section. Default to False.        
        dep_levels(np array, optional): array with depth contour levels (in m) to be plotted. If None, no depth contours.
        hs_levels(np array, optional): array with significant wave height contour levels (in m) to be plotted.
        hs_ticks(np array, optional): array with significant wave height contour levels ticks (in m) to be plotted.
        Hs0 (float, optional): deep water significant wave height (in m). If provided, Hs is normalised.
        cmap (str): hs matplotlib colour map. Default to "jet".
    """
    warnings.filterwarnings('ignore')
    # Assign xmin, xmax, dx, ymin, ymax, dy, tmin, tmax, and dt if not defined
    xmin = xmin or ds.x.min().item()
    xmax = xmax or ds.x.max().item()
    dx = dx or (ds.x.isel(x=1)-ds.x.isel(x=0)).item()
    ymin = ymin or ds.y.min().item()
    ymax = ymax or ds.y.max().item()    
    dy = dy or (ds.y.isel(y=1)-ds.y.isel(y=0)).item()    
    if Hs0:
         ds["Hsig"]=ds["Hsig"]/Hs0
    temp=ds.sel(x=slice(xmin,xmax,math.ceil(dx/((ds.x.isel(x=1)-ds.x.isel(x=0)).values.item()))),
                y=slice(ymin,ymax,math.ceil(dy/((ds.y.isel(y=1)-ds.y.isel(y=0)).values.item()))))
    hs_levels = hs_levels or np.arange(0,temp["Hsig"].max().item(),temp["Hsig"].max().item()/100)
    hs_ticks = hs_ticks or np.around(np.arange(0,hs_levels.max(),hs_levels.max()/5),decimals=2)
    # velocity clipping
    vel_clip_max=xr.apply_ufunc(np.abs,temp["Mfvx"]).quantile(vel_clip_max).item()
    temp["Mfvx"]=temp["Mfvx"].clip(min=-vel_clip_max,max=vel_clip_max)
    temp["Mfvy"]=temp["Mfvy"].clip(min=-vel_clip_max,max=vel_clip_max)
    vel_clip_min=xr.apply_ufunc(np.abs,temp["Mfvx"]).quantile(vel_clip_min).item()
    temp=temp.where(lambda x:(x["Mfvx"]**2+x["Mfvy"]**2)**0.5>=vel_clip_min,drop=True)
    # figure
    fig,ax=plt.subplots(figsize=(9.2,5.2))
    ax=[ax]
    ax[0].axis('equal')
    # plot hs
    hs=ds["Hsig"].plot(ax=ax[0],cmap=cmap,levels=hs_levels,add_colorbar=False,clip_on=True)
    fig.colorbar(hs,ticks=hs_ticks,label=[r'$\mathrm{ H_S}$ [m]',r'$\mathrm{ H_S\,/\,H_{S,0}}$'][Hs0 is not None],orientation='horizontal',cax=ax[0].inset_axes([0.05,1.05,0.85,0.05],transform=ax[0].transAxes),ticklocation='top')
    # plot land surface
    ax[0].fill_betweenx(ds.y,ds.isel(y=0).where(lambda x:x.Botlev<=0,drop=True).isel(x=0).x.item(),xmax,color="peachpuff",clip_on=True)
    # plot reef contour
    if plot_dep_dev:
        (-(ds.where(ds.Botlev-ds.isel(y=0).Botlev!=0,drop=True).Botlev)).plot.contourf(ax=ax[0],colors="k",add_colorbar=False)
    # plot quiver with Mfv
    quiv=temp.plot.quiver(ax=ax[0],x="x",y="y",u="Mfvx",v="Mfvy",scale=scale,add_guide=False)
    ax[0].quiverkey(quiv,0.95,1.02,vel_clip_max*scale,f"{vel_clip_max:.2f} m/s")
    # plot depth contour
    if dep_levels is not None:
        x_dep_levels=[ds.isel(y=-1).where(lambda x:x["Botlev"]<=i,drop=True).isel(x=0).x.item() for i in dep_levels]
        depcont=(ds['Botlev']).plot.contour(levels=dep_levels,colors='grey',linewidth=3,linestyles="-",ax=ax[0])
        ax[0].clabel(depcont,fmt='-%.2f m',manual=[(i,ymin+(ymax-ymin)*0.9) for i in x_dep_levels],fontsize=14)
    # set axis properties
    ax[0].set_title("")
    [(i.set_xlabel('X [m]'),i.set_ylabel('Y [m]')) for i in ax]
    [(i.set_xlim([xmin,xmax]),i.set_ylim([ymin,ymax])) for i in ax]
    plt.close()
    return fig