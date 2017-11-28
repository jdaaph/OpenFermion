#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import unittest
from numpy.random import rand, seed
from numpy.linalg import norm

from openfermion.utils._bch_expansion import *

def bch_expand_baseline(x, y, order):
    """Compute log[e^x e^y] using the Baker-Campbell-Hausdorff formula
    Args:
        x: An operator for which multiplication and addition are supported.
            For instance, a QubitOperator, FermionOperator or numpy array.
        y: The same type as x.
        order(int): The order to truncate the BCH expansions. Currently
            function goes up to only third order.

    Returns:
        z: The truncated BCH operator.

    Raises:
        ValueError: operator x is not same type as operator y.
        ValueError: invalid order parameter.
        ValueError: order exceeds maximum order supported.
    """
    # Initialize.
    max_order = 4
    if type(x) != type(y):
        raise ValueError('Operator x is not same type as operator y.')
    elif (not isinstance(order, int)) or order < 0:
        raise ValueError('Invalid order parameter.')

    # Zeroth order.
    z = x + y

    # First order.
    if order > 0:
        z += commutator(x, y) / 2.

    # Second order.
    if order > 1:
        z += commutator(x, commutator(x, y)) / 12.
        z += commutator(y, commutator(y, x)) / 12.

    # Third order.
    if order > 2:
        z -= commutator(y, commutator(x, commutator(x, y))) / 24.

    # Fourth order.
    if order > 3:
        z -= commutator(
            y, commutator(y, commutator(y, commutator(y, x)))) / 720.
        z -= commutator(
            x, commutator(x, commutator(x, commutator(x, y)))) / 720.
        z += commutator(
            x, commutator(y, commutator(y, commutator(y, x)))) / 360.
        z += commutator(
            y, commutator(x, commutator(x, commutator(x, y)))) / 360.
        z += commutator(
            y, commutator(x, commutator(y, commutator(x, y)))) / 120.
        z += commutator(
            x, commutator(y, commutator(x, commutator(y, x)))) / 120.

    # Return.
    if order > max_order:
        raise ValueError('Order exceeds maximum order supported.')
    else:
        return z

class BCHTest(unittest.TestCase):

    def setUp(self):
        """Initialize a few density matrices"""
        self.seed = [13579, 34628, 2888, 11111, 67917]
        self.dim = 6
        self.test_order = 4

    def test_bch(self):
        """Test efficient bch expansion against hard coded baseline coefficients"""
        for s in self.seed:
            seed(s)
            x = rand(self.dim, self.dim)
            y = rand(self.dim, self.dim)
            test = bch_expand(x, y, self.test_order)
            baseline = bch_expand_baseline(x, y, self.test_order)
            self.assertAlmostEquals(norm(test-baseline), 0.0)

    def test_verification(self):
        """Verify basic sanity checking on inputs"""
        with self.assertRaises(ValueError):
            order = 2
            _ = bch_expand(1, np.ones((2, 2)), order)

        with self.assertRaises(ValueError):
            order = 100
            _ = bch_expand(np.ones((2, 2)), np.ones((2, 2)), order)

        with self.assertRaises(ValueError):
            order = '38'
            _ = bch_expand(np.ones((2, 2)), np.ones((2, 2)), order)
