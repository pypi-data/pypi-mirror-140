import unittest 
import numpy as np

from proj import projxvals

class TestXVals(unittest.TestCase):

    def test_onetheta(self):
        """
        Test the case with:
        * One theta parameter
        * Equal spacing between upper and lower limit and optimal value 
        * n_pts = 3 
        """

        theta = np.array([1])
        theta_lims = np.array([[0,2]])
        n_theta = theta_lims.shape[0]
        n_pts = 3

        result = projxvals(theta, theta_lims, n_pts)
        correct = np.array([[0.], [1.], [2.]])

        np.testing.assert_array_equal(np.around(result, 8), np.around(correct, 8))

    def test_twotheta(self):
        """
        Test the case with:
        * Two theta parameters
        * Equal spacing between upper and lower limit and optimal value 
        * n_pts = 3 
        """

        theta = np.array([1, 15])
        theta_lims = np.array([[0,2], [10, 20]])
        n_theta = theta_lims.shape[0]
        n_pts = 3 

        result = projxvals(theta, theta_lims, n_pts)
        correct = np.array([[ 0., 15.], [ 1., 15.], [ 2., 15.],
                            [ 1., 10.], [ 1., 15.], [ 1., 20.]])

        np.testing.assert_array_equal(np.around(result, 8), np.around(correct, 8))

    def test_threetheta(self):
        """
        Test the case with:
        * Three theta parameters
        * Equal spacing between upper and lower limit and optimal value 
        * n_pts = 3 
        """

        theta = np.array([1, 5, 10])
        theta_lims = np.array([[0,2], [4, 6], [9,11]])
        n_theta = theta_lims.shape[0]
        n_pts = 3 

        result = projxvals(theta, theta_lims, n_pts)
        correct = np.array([[ 0.,  5., 10.],
                            [ 1.,  5., 10.],
                            [ 2.,  5., 10.],
                            [ 1.,  4., 10.],
                            [ 1.,  5., 10.],
                            [ 1.,  6., 10.],
                            [ 1.,  5.,  9.],
                            [ 1.,  5., 10.],
                            [ 1.,  5., 11.]])
        
        np.testing.assert_array_equal(np.around(result, 8), np.around(correct, 8))

    def test_higher_lower(self):
        """
        Test the case with:
        * Two theta parameters
        * Larger lower bound than upper bound from optimal value
        * n_pts = 4
        """
        theta = np.array([1, 15])
        theta_lims = np.array([[-2,2], [5, 20]])
        n_theta = theta_lims.shape[0]
        n_pts = 4 
        
        result = projxvals(theta, theta_lims, n_pts)
        correct = np.array([[-2.        , 15.        ],
                            [-0.66666667, 15.        ],
                            [ 0.66666667, 15.        ],
                            [ 2.        , 15.        ],
                            [ 1.        ,  5.        ],
                            [ 1.        , 10.        ],
                            [ 1.        , 15.        ],
                            [ 1.        , 20.        ]])

        np.testing.assert_array_equal(np.around(result, 8), np.around(correct, 8))

    def test_higher_upper(self):
        """
        Test the case with:
        * Two theta parameters
        * Larger upper bound than lower bound from optimal value
        * n_pts = 4
        """

        theta = np.array([1, 15])
        theta_lims = np.array([[0, 5], [10, 30]])
        n_theta = theta_lims.shape[0]
        n_pts = 4 

        result = projxvals(theta, theta_lims, n_pts)
        correct = np.array([[ 0.        , 15.        ],
                            [ 1.66666667, 15.        ],
                            [ 3.33333333, 15.        ],
                            [ 5.        , 15.        ],
                            [ 1.        , 10.        ],
                            [ 1.        , 16.66666667],
                            [ 1.        , 23.33333333],
                            [ 1.        , 30.        ]])

        np.testing.assert_array_equal(np.around(result, 8), np.around(correct, 8))

    def test_med_npts(self):
        """
        Test the case with:
        * Two theta parameters
        * Equal spacing between upper and lower limit and optimal value 
        * n_pts = 5
        """

        theta = np.array([1, 15])
        theta_lims = np.array([[0,2], [10, 20]])
        n_theta = theta_lims.shape[0]
        n_pts = 10

        result = projxvals(theta, theta_lims, n_pts)
        correct = np.array([[ 0.        , 15.        ],
                            [ 0.22222222, 15.        ],
                            [ 0.44444444, 15.        ],
                            [ 0.66666667, 15.        ],
                            [ 0.88888889, 15.        ],
                            [ 1.11111111, 15.        ],
                            [ 1.33333333, 15.        ],
                            [ 1.55555556, 15.        ],
                            [ 1.77777778, 15.        ],
                            [ 2.        , 15.        ],
                            [ 1.        , 10.        ],
                            [ 1.        , 11.11111111],
                            [ 1.        , 12.22222222],
                            [ 1.        , 13.33333333],
                            [ 1.        , 14.44444444],
                            [ 1.        , 15.55555556],
                            [ 1.        , 16.66666667],
                            [ 1.        , 17.77777778],
                            [ 1.        , 18.88888889],
                            [ 1.        , 20.        ]])

        np.testing.assert_array_equal(np.around(result, 8), np.around(correct, 8))

    def test_large_npts(self):
        """
        Test the case with:
        * Two theta parameters
        * Equal spacing between upper and lower limit and optimal value 
        * n_pts = 50
        """

        theta = np.array([1, 15])
        theta_lims = np.array([[0,2], [10, 20]])
        n_theta = theta_lims.shape[0]
        n_pts = 50

        result = projxvals(theta, theta_lims, n_pts)
        correct = np.array([[ 0.        , 15.        ],
                            [ 0.04081633, 15.        ],
                            [ 0.08163265, 15.        ],
                            [ 0.12244898, 15.        ],
                            [ 0.16326531, 15.        ],
                            [ 0.20408163, 15.        ],
                            [ 0.24489796, 15.        ],
                            [ 0.28571429, 15.        ],
                            [ 0.32653061, 15.        ],
                            [ 0.36734694, 15.        ],
                            [ 0.40816327, 15.        ],
                            [ 0.44897959, 15.        ],
                            [ 0.48979592, 15.        ],
                            [ 0.53061224, 15.        ],
                            [ 0.57142857, 15.        ],
                            [ 0.6122449 , 15.        ],
                            [ 0.65306122, 15.        ],
                            [ 0.69387755, 15.        ],
                            [ 0.73469388, 15.        ],
                            [ 0.7755102 , 15.        ],
                            [ 0.81632653, 15.        ],
                            [ 0.85714286, 15.        ],
                            [ 0.89795918, 15.        ],
                            [ 0.93877551, 15.        ],
                            [ 0.97959184, 15.        ],
                            [ 1.02040816, 15.        ],
                            [ 1.06122449, 15.        ],
                            [ 1.10204082, 15.        ],
                            [ 1.14285714, 15.        ],
                            [ 1.18367347, 15.        ],
                            [ 1.2244898 , 15.        ],
                            [ 1.26530612, 15.        ],
                            [ 1.30612245, 15.        ],
                            [ 1.34693878, 15.        ],
                            [ 1.3877551 , 15.        ],
                            [ 1.42857143, 15.        ],
                            [ 1.46938776, 15.        ],
                            [ 1.51020408, 15.        ],
                            [ 1.55102041, 15.        ],
                            [ 1.59183673, 15.        ],
                            [ 1.63265306, 15.        ],
                            [ 1.67346939, 15.        ],
                            [ 1.71428571, 15.        ],
                            [ 1.75510204, 15.        ],
                            [ 1.79591837, 15.        ],
                            [ 1.83673469, 15.        ],
                            [ 1.87755102, 15.        ],
                            [ 1.91836735, 15.        ],
                            [ 1.95918367, 15.        ],
                            [ 2.        , 15.        ],
                            [ 1.        , 10.        ],
                            [ 1.        , 10.20408163],
                            [ 1.        , 10.40816327],
                            [ 1.        , 10.6122449 ],
                            [ 1.        , 10.81632653],
                            [ 1.        , 11.02040816],
                            [ 1.        , 11.2244898 ],
                            [ 1.        , 11.42857143],
                            [ 1.        , 11.63265306],
                            [ 1.        , 11.83673469],
                            [ 1.        , 12.04081633],
                            [ 1.        , 12.24489796],
                            [ 1.        , 12.44897959],
                            [ 1.        , 12.65306122],
                            [ 1.        , 12.85714286],
                            [ 1.        , 13.06122449],
                            [ 1.        , 13.26530612],
                            [ 1.        , 13.46938776],
                            [ 1.        , 13.67346939],
                            [ 1.        , 13.87755102],
                            [ 1.        , 14.08163265],
                            [ 1.        , 14.28571429],
                            [ 1.        , 14.48979592],
                            [ 1.        , 14.69387755],
                            [ 1.        , 14.89795918],
                            [ 1.        , 15.10204082],
                            [ 1.        , 15.30612245],
                            [ 1.        , 15.51020408],
                            [ 1.        , 15.71428571],
                            [ 1.        , 15.91836735],
                            [ 1.        , 16.12244898],
                            [ 1.        , 16.32653061],
                            [ 1.        , 16.53061224],
                            [ 1.        , 16.73469388],
                            [ 1.        , 16.93877551],
                            [ 1.        , 17.14285714],
                            [ 1.        , 17.34693878],
                            [ 1.        , 17.55102041],
                            [ 1.        , 17.75510204],
                            [ 1.        , 17.95918367],
                            [ 1.        , 18.16326531],
                            [ 1.        , 18.36734694],
                            [ 1.        , 18.57142857],
                            [ 1.        , 18.7755102 ],
                            [ 1.        , 18.97959184],
                            [ 1.        , 19.18367347],
                            [ 1.        , 19.3877551 ],
                            [ 1.        , 19.59183673],
                            [ 1.        , 19.79591837],
                            [ 1.        , 20.        ]])

        np.testing.assert_array_equal(np.around(result, 8), np.around(correct, 8))
    
if __name__ == '__main__':
    unittest.main()

    
                            


