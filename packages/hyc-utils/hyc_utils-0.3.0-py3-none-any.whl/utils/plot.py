import matplotlib.pyplot as plt

def subplots(rows, cols, plot_size=(6.4,4.8), keep_shape=False, **kwargs):
    fig, axes = plt.subplots(rows, cols, figsize=(plot_size[0]*cols, plot_size[1]*rows), **kwargs)
    if keep_shape:
        axes = axes.reshape((rows, cols))
    return fig, axes
