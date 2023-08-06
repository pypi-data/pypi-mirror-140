import numpy as np 
import pandas as pd
import seaborn as sns

def projxvals(theta, theta_lims, n_pts):
    """
    Args:
        theta (NumPy array): An array of parameter values
        theta_lims (NumPy array): An array of limits or a 2 x theta.shape[0] matrix of lower and upper limits for each parameter
        n_pts (int): The number of points to plot

    Returns:
        x_vals (NumPy array): An array of all possible combinations of the x-values based on the limits (theta_lims) and optimal values (theta)

    Example: 
        projxvals([1, 15], [[0, 2], [10, 20]], 3) => [[0, 15],
                                                     [1, 15],
                                                     [2, 15],
                                                     [1, 10],
                                                     [1, 15],
                                                     [1, 20]]
    """
    
    x_theta = np.linspace(theta_lims[:,0], theta_lims[:,1], n_pts).T
    n_theta = theta_lims.shape[0]
    x_vals = np.empty((n_pts * n_theta, n_theta))

    for i in range(n_theta):
        theta_tmp = np.copy(theta)
        theta_tmp = np.delete(theta_tmp, i, axis=0) 

        tmp_grid = x_vals[i*n_pts:(i+1)*n_pts]
        # Initializes theta values that are changing in the tmp_grid
        tmp_grid[:, i] = x_theta[i]

        # Update the other two columns to be constant values in tmp_grid
        b = np.ones((n_theta), dtype=bool)
        b[i] = False

        tmp_grid[:, b] = np.ones((n_pts, n_theta-1)) * theta_tmp

        x_vals[i*n_pts:(i+1)*n_pts] = tmp_grid
    
    return x_vals

def generate_plot(plot_data): 
    """
    Args:
        plot_data (DataFrame): A DataFrame that contains columns for the calculated y-value, varying x value and the respective theta name associated with the varying x
    
    Produces a plot for each unique theta using the x and y values in plot_data
    """
    sns.relplot(
    data=plot_data, kind="line",
    x="x", y="y", col="theta",
    facet_kws=dict(sharex=False, sharey=False))

def projdata(fun, x_vals, theta_names, is_vectorized = False):
    """
    Args:
        fun (Python function): The objective function that is being optimized
        x_vals (NumPy array): A matrix of the x_vals, this should be outputted from projxvals()
        theta_names (List): A list of the theta names respective to varying x-values for plotting
        is_vectorized (Bool): TRUE if the objective function is vectorized, else FALSE

    Returns:
        plot_df (DataFrame): The y-value in each projection plot appended to the x-values in a DataFrame format that's amenable to plotting
        It will also plot the projection plots which results in a plot for each varying theta. 
    
    """
    n_x = x_vals.shape[0]
    n_param = x_vals.shape[1]
    n_pts = int(n_x/n_param)
    
    # Initialize empty y vector
    y_vals = np.zeros(n_x)

    # Function is not vectorized 
    if is_vectorized == False:
        for i in range(n_x):
            y_vals[i] = fun(x_vals[i])
    
    # Function is vectorized
    else: 
        y_vals = fun(x_vals)

    # Get the x-values that vary for each parameter 
    varying_x = np.concatenate([x_vals[i*n_pts:(i+1)*n_pts, i] for i in range(n_param)])
    
    # Append the y_values to the dataframe
    plot_df = pd.DataFrame(varying_x, y_vals)
    plot_df.reset_index(inplace=True)
    plot_df.columns = ['y', 'x']
    plot_df['theta'] = np.repeat(theta_names, n_pts)
    
    # Generate plots
    generate_plot(plot_df)
    
    return plot_df