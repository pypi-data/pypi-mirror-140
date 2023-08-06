'''
Reinan Br <slimchatuba@gmail.com>
5 jan 2022 19:08
lib: noaawc
license: GPLv3
--------------------------------------------------

'''

import numpy as np
import pygrib
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from noawclg import get_noaa_data as gnd
import pandas as pd
import psutil as ps
import imageio
import time
import os

dn = gnd()

'''
the function base and more
important from it work
'''
def plot_global(path:str,indice:int,title='plot',text:str=False,pos_text:tuple=False,annotate:str=False,
               pos_annotate:tuple=False,text_color='white',text_size=9,fontweight_text='bold',
               facecolor_text:str='red',edgecolor_text:str='black',annotate_size:float=9, 
                annotate_color:str='white',loc_focus:tuple=(0,0),key_noaa='tmpmwl',subtr_data=273,
               text_cb='ºC',alpha=1):
    ax = plt.subplot(111)
    lat  = dn['lat'][:]
    lon  = dn['lon'][:]
    data = dn[key_noaa][indice]-subtr_data
    data1 = dn[key_noaa][1]-subtr_data
    print(len(data),len(lat))
    
    date=dn['time'][indice].to_numpy()

    #import pandas as pd 
    ts = pd.to_datetime(str(date)) 
    date_text = ts.strftime('%d %h %Y\n %H:%M UTC')
    #print(d)

#     m=Basemap(projection='mill',lat_0=-9.41,lon_0=40,lat_ts=10,llcrnrlon=lon.min(), \
#       urcrnrlon=lon.max(),llcrnrlat=lat.min(),urcrnrlat=lat.max(), \
#       resolution='l')
    
    m = Basemap(projection='ortho',lat_0=loc_focus[0],lon_0=loc_focus[1],resolution='c')
    # convert the lat/lon values to x/y projections.
    
    x, y = m(*np.meshgrid(lon,lat))
#     x[x>1e20]=np.nan
#     y[y>1e20]=np.nan
    # plot the field using the fast pcolormesh routine 
    # set the colormap to jet.

#     Z = data
#     import numpy.ma as ma

#     Zm = ma.masked_invalid(Z)
    #m.contour(x,y,data,50,cmap=plt.cm.jet)
    min_temp = data1.min()
    max_temp = data1.max()
    levels = np.linspace(min_temp,max_temp,25)
    
    m.fillcontinents(color='coral',lake_color='aqua')
    cm=m.contourf(x,y,data,100,alpha=alpha,levels=levels,cmap=plt.cm.inferno)
    #cm1=plt.contourf(x,y,data1,100,shading='nearest',cmap=plt.get_cmap('inferno'))
    #plt.cla()
    #plt.clf()
    cbar=plt.colorbar(cm,orientation='horizontal',extend='both',fraction=0.07,pad=0.05)
    cbar.set_label(text_cb,y=0,ha='right')
    cbar.ax.set_title('by: @gpftc_ifsertão',fontweight='bold')
    
    
    #temp_cbar=np.linspace(-40,36,8)
    #cbar.set_ticks([int(i) for i in temp_cbar])
    #cbar.ax.invert_yaxis()
    #cbar.ax.set_yticklabels(["{:2.2f}".format(i) for i in data_cm]) # add the labels

    # Add a coastline and axis values.
    #print(dir(m))
    m.drawcoastlines()
    #m.drawmapboundary(fill_color='aqua')
    #m.drawrivers(linewidth=0.1)
    m.drawcountries(linewidth=0.25)
    m.drawcountries(linewidth=0.25)
    
    #m.drawmapboundary(fill_color='aqua')

    m.drawmeridians(np.arange(0,360,30))
    m.drawparallels(np.arange(-90,90,30))
    #print(dir(m))
    m.drawmapboundary(fill_color='aqua')
    #print(dir(m))
    
    
    
   
#     lats = [-40.5,-40.6,-40.5,-40.6]
#     lons = [-9.41,-9.51,-9.41,-9.51]
#     draw_screen_poly(lats,lons,m)

    #xn2,yn2=m(-9.52,-40.61)
    t = plt.text(-0.3,0.99,date_text, transform=ax.transAxes,
                color='white', fontweight='bold',fontsize=14)
    t = plt.text(1.1,0.03,'data: GFS 0.25', transform=ax.transAxes,
                color='white', fontweight='bold',fontsize=8)
    t = plt.text(1.12,-0.01,'NOAA/NASA', transform=ax.transAxes,
                color='grey', fontweight='bold',fontsize=8)
    #t.set_bbox(dict(facecolor='red', alpha=0.81, edgecolor='black'))
    
    if pos_text and text:
        t = plt.text(pos_text[0],pos_text[1], text, transform=ax.transAxes,
                     color=text_color, fontweight='bold',fontsize=text_size)
        t.set_bbox(dict(facecolor='red', alpha=0.81, edgecolor='black'))
    
    if annotate and pos_annotate:
        xn,yn=m(pos_annotate[1],pos_annotate[0])
        plt.annotate(annotate,color=annotate_color,xy=(xn,yn),xytext=(xn,yn),xycoords='data',textcoords='data')
    
    
    plt.title(title,fontweight='bold',fontsize=16)
    plt.savefig(path)
    #plt.show()



'''
the second function more
important from it project
'''
## plotting gif only a city (juazeiro)
#data_j = dn.get_data_from_point(point=(-9.41,-40.5))['tmpsig995']-273
size = 60

def create_plot_gif(path_gif='img.gif',size:int=60,path_data='data/img_',title='',key_noaa='vgrdpbl',
                   loc_focus=(0,0),point_init=False,point_end=False,text_cb='',lon_stop=False,alpha=1,
                   subtr_data=0):
    assert size < 128, print('size of data is max 128!!')
    images = []
    #size = frames
    time_0 = time.time()
    ping_list = np.array([0])
    
    locs_focus = []
    if loc_focus:
        for _ in range(size):
            locs_focus.append(loc_focus)
        
    if point_init and point_end:
        lat_space = (point_init[0],point_end[0])
        lon_space = (point_init[1],point_end[1])
        print(lon_space)
        
        
        lat_list = np.linspace(lat_space[0],lat_space[1],size)
        
        lon_list = np.linspace(lon_space[0],lon_space[1],size)
        #print('after',lon_list)
        
        if lon_stop:
            lon_list[abs(lon_list)<abs(lon_stop)] = lon_stop 
            #print('before',lon_list)
        locs_focus = list(zip(lat_list,lon_list))
        
    for i in range(size):
        path_img = f'{path_data}_{i}.png'

        time0 = time.time()

        #temp_j = float(data_j[i])
        print(locs_focus)
        plot_global(path=path_img,title=title,key_noaa=key_noaa,alpha=alpha,
                indice=i,loc_focus=locs_focus[i],subtr_data=subtr_data,text_cb=text_cb)
        ping = time.time()-time0
        ping_list = np.append(ping_list,[ping])
        ping_m = sum(ping_list)/len(ping_list)
        i_=i+1
        eta = (size-i_)*ping_m
        min_eta = eta//60
        seg_eta = eta%60
        per = (i_/size)*100
        perr = time.time()-time_0
        min_perr = perr//60
        seg_perr = perr%60
        os.system(f'echo "[{i_}/{size} {per:.2f}% | PER :{int(min_perr)}min :{int(seg_perr)}seg / ETA: {int(min_eta)}min :{int(seg_eta)}seg]   [CPU:{ps.cpu_percent()}% | RAM:{ps.virtual_memory().percent}% swap:{ps.swap_memory().percent}%]"')

        images.append(imageio.imread(path_img))

    print('criando gif...')
    imageio.mimsave(path_gif,images)