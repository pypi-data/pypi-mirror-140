import unittest 
import numpy as np
import pandas as pd

from proj import projxvals
from proj import projdata

def vectorized_2d(x):
    """
    Params: 
        x: x is a 2x1 vector

    Returns:
        The output of x'Ax - 2b'x
    """

    # Transpose the x vector so it is 2xn where n is 2 * number of data points 
    x = x.T 
    A = np.array([[3,2], [2,7]])
    b = np.array((1,10)).T
    
    y = np.diag(x.T.dot(A).dot(x)) - 2 * b.dot(x)
        
    return y

def nonvectorized_2d(x):
    """
    Params: 
        x: x is a 2x1 vector

    Returns:
        The output of x'Ax - 2b'x
    """
    A = np.array([[3,2], [2,7]])
    b = np.array((1,10)).T
    
    y = x.T.dot(A).dot(x.T) - 2 * b.dot(x) 
    
    return y 

def quadratic_1d(x):
    """
    Params:
        x: x is a 1x1 vector
    
    Returns:
        The output, y from the calculation of x^2 + 10x
    """
    y = x**2 + 10*x
    return y 

class TestProjData(unittest.TestCase):
    def test_2dvec_quadratic(self):
        # Optimal value from the quadratic formula
        theta = np.array([-0.76470588,  1.64705882])

        # Upper and lower bounds
        theta_lims = np.array([[-3., 1], [0, 4]])
        
        # Parameter names
        theta_names = ["x1", "x2"]

        # Number of evaluation points per coordinate
        n_pts = 10

        x_vals = projxvals(theta, theta_lims, n_pts)
        plot_data = projdata(vectorized_2d, x_vals, theta_names, is_vectorized=True)

        # Setup the correct dataframe
        correct_x = np.array([-3.        , -2.55555556, -2.11111111, -1.66666667, -1.22222222,
       -0.77777778, -0.33333333,  0.11111111,  0.55555556,  1.        ,
        0.        ,  0.44444444,  0.88888889,  1.33333333,  1.77777778,
        2.22222222,  2.66666667,  3.11111111,  3.55555556,  4.        ])
        correct_y = np.array([ -0.71626298,  -6.0844547 , -10.26746123, -13.26528258,
       -15.07791875, -15.70536973, -15.14763552, -13.40471613,
       -10.47661156,  -6.3633218 ,   3.28373702,  -5.58191294,
       -11.6821308 , -15.01691657, -15.58627024, -13.39019181,
        -8.42868128,  -0.70173865,   9.79063608,  23.04844291])
        correct_df = pd.DataFrame([correct_y, correct_x, np.repeat(theta_names, n_pts)]).T
        correct_df.columns = ['y', 'x', 'theta']
        correct_df["x"] = pd.to_numeric(correct_df["x"])
        correct_df["y"] = pd.to_numeric(correct_df["y"])

        pd.testing.assert_frame_equal(plot_data, correct_df)

    def test_2dnonvec_quadratic(self):
        # Optimal value from the quadratic formula
        theta = np.array([-0.76470588,  1.64705882])

        # Upper and lower bounds
        theta_lims = np.array([[-3., 1], [0, 4]])
        
        # Parameter names
        theta_names = ["x1", "x2"]

        # Number of evaluation points per coordinate
        n_pts = 10

        x_vals = projxvals(theta, theta_lims, n_pts)
        plot_data = projdata(nonvectorized_2d, x_vals, theta_names, is_vectorized=False)

        # Setup the correct dataframe
        correct_x = np.array([-3.        , -2.55555556, -2.11111111, -1.66666667, -1.22222222,
       -0.77777778, -0.33333333,  0.11111111,  0.55555556,  1.        ,
        0.        ,  0.44444444,  0.88888889,  1.33333333,  1.77777778,
        2.22222222,  2.66666667,  3.11111111,  3.55555556,  4.        ])
        correct_y = np.array([ -0.71626298,  -6.0844547 , -10.26746123, -13.26528258,
       -15.07791875, -15.70536973, -15.14763552, -13.40471613,
       -10.47661156,  -6.3633218 ,   3.28373702,  -5.58191294,
       -11.6821308 , -15.01691657, -15.58627024, -13.39019181,
        -8.42868128,  -0.70173865,   9.79063608,  23.04844291])
        correct_df = pd.DataFrame([correct_y, correct_x, np.repeat(theta_names, n_pts)]).T
        correct_df.columns = ['y', 'x', 'theta']
        correct_df["x"] = pd.to_numeric(correct_df["x"])
        correct_df["y"] = pd.to_numeric(correct_df["y"])

        pd.testing.assert_frame_equal(plot_data, correct_df)

    def test_1d_quadratic(self):
                # Optimal value from the quadratic formula
        theta = np.array([-5])

        # Upper and lower bounds
        theta_lims = np.array([[-10., 0]])
        
        # Parameter names
        theta_names = ["x1"]

        # Number of evaluation points per coordinate
        n_pts = 10

        x_vals = projxvals(theta, theta_lims, n_pts)
        plot_data = projdata(quadratic_1d, x_vals, theta_names, is_vectorized=False)

        # Setup the correct dataframe
        correct_x = np.array([-10.        ,  -8.88888889,  -7.77777778,  -6.66666667,
        -5.55555556,  -4.44444444,  -3.33333333,  -2.22222222,
        -1.11111111,   0.        ])
        correct_y = np.array([  0.        ,  -9.87654321, -17.28395062, -22.22222222,
       -24.69135802, -24.69135802, -22.22222222, -17.28395062,
        -9.87654321,   0.        ])
        correct_df = pd.DataFrame([correct_y, correct_x, np.repeat(theta_names, n_pts)]).T
        correct_df.columns = ['y', 'x', 'theta']
        correct_df["x"] = pd.to_numeric(correct_df["x"])
        correct_df["y"] = pd.to_numeric(correct_df["y"])

        pd.testing.assert_frame_equal(plot_data, correct_df)

if __name__ == '__main__':
    unittest.main()