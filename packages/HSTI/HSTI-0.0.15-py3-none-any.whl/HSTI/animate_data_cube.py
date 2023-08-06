from matplotlib.animation import FuncAnimation
from IPython import display
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable

def animation(data_cube, title_list, fps, DPI, fixed_color = True):
    fig = plt.figure(dpi=DPI)
    fig.set_figheight(8) #set height of the entire figure
    fig.set_figwidth(8) #set width of the entire figure
    gs = gridspec.GridSpec(1, 1) #set size ratio of the subfigures
    ax1 = fig.add_subplot(gs[0,0])
    a=np.zeros((data_cube.shape[0],data_cube.shape[1]))
    if not fixed_color:
        im=plt.imshow(a,interpolation='none', vmin = np.min(data_cube), vmax = np.max(data_cube))
    else:
        im=plt.imshow(a,interpolation='none', vmin = np.min(data_cube[:,:,0]), vmax = np.max(data_cube[:,:,0]))
    divider = make_axes_locatable(ax1)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    fig.colorbar(im, cax=cax, orientation='vertical')
    def animate(frame):
        #update plot
        ax1.set_title(title_list[frame])
        im.set_data(data_cube[:,:,frame])
        if not fixed_color:
            im.set_clim(vmin = np.min(data_cube[:,:,frame]), vmax = np.max(data_cube[:,:,frame]))

    I = 1000/fps
    anim = FuncAnimation(fig, animate, frames=data_cube.shape[2], interval=I)
    video = anim.to_html5_video()
    html = display.HTML(video)
    display.display(html)
    plt.close('all')
    return
