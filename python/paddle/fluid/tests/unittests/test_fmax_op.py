# Copyright (c) 2021 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import numpy as np
import paddle
import paddle.fluid.core as core
from op_test import OpTest


class ApiFMaxTest(unittest.TestCase):
    """ApiFMaxTest"""

    def setUp(self):
        """setUp"""
        if core.is_compiled_with_cuda():
            self.place = core.CUDAPlace(0)
        else:
            self.place = core.CPUPlace()

        self.input_x = np.random.rand(10, 15).astype("float32")
        self.input_y = np.random.rand(10, 15).astype("float32")
        self.input_z = np.random.rand(15).astype("float32")
        self.input_a = np.array([0, np.nan, np.nan]).astype('int64')
        self.input_b = np.array([2, np.inf, -np.inf]).astype('int64')
        self.input_c = np.array([4, 1, 3]).astype('int64')

        self.np_expected1 = np.fmax(self.input_x, self.input_y)
        self.np_expected2 = np.fmax(self.input_x, self.input_z)
        self.np_expected3 = np.fmax(self.input_a, self.input_c)
        self.np_expected4 = np.fmax(self.input_b, self.input_c)

    def test_static_api(self):
        """test_static_api"""
        paddle.enable_static()
        with paddle.static.program_guard(
            paddle.static.Program(), paddle.static.Program()
        ):
            data_x = paddle.static.data("x", shape=[10, 15], dtype="float32")
            data_y = paddle.static.data("y", shape=[10, 15], dtype="float32")
            result_fmax = paddle.fmax(data_x, data_y)
            exe = paddle.static.Executor(self.place)
            (res,) = exe.run(
                feed={"x": self.input_x, "y": self.input_y},
                fetch_list=[result_fmax],
            )
        np.testing.assert_allclose(res, self.np_expected1, rtol=1e-05)

        with paddle.static.program_guard(
            paddle.static.Program(), paddle.static.Program()
        ):
            data_x = paddle.static.data("x", shape=[10, 15], dtype="float32")
            data_z = paddle.static.data("z", shape=[15], dtype="float32")
            result_fmax = paddle.fmax(data_x, data_z)
            exe = paddle.static.Executor(self.place)
            (res,) = exe.run(
                feed={"x": self.input_x, "z": self.input_z},
                fetch_list=[result_fmax],
            )
        np.testing.assert_allclose(res, self.np_expected2, rtol=1e-05)

        with paddle.static.program_guard(
            paddle.static.Program(), paddle.static.Program()
        ):
            data_a = paddle.static.data("a", shape=[3], dtype="int64")
            data_c = paddle.static.data("c", shape=[3], dtype="int64")
            result_fmax = paddle.fmax(data_a, data_c)
            exe = paddle.static.Executor(self.place)
            (res,) = exe.run(
                feed={"a": self.input_a, "c": self.input_c},
                fetch_list=[result_fmax],
            )
        np.testing.assert_allclose(res, self.np_expected3, rtol=1e-05)

        with paddle.static.program_guard(
            paddle.static.Program(), paddle.static.Program()
        ):
            data_b = paddle.static.data("b", shape=[3], dtype="int64")
            data_c = paddle.static.data("c", shape=[3], dtype="int64")
            result_fmax = paddle.fmax(data_b, data_c)
            exe = paddle.static.Executor(self.place)
            (res,) = exe.run(
                feed={"b": self.input_b, "c": self.input_c},
                fetch_list=[result_fmax],
            )
        np.testing.assert_allclose(res, self.np_expected4, rtol=1e-05)

    def test_dynamic_api(self):
        """test_dynamic_api"""
        paddle.disable_static()
        x = paddle.to_tensor(self.input_x)
        y = paddle.to_tensor(self.input_y)
        z = paddle.to_tensor(self.input_z)

        a = paddle.to_tensor(self.input_a)
        b = paddle.to_tensor(self.input_b)
        c = paddle.to_tensor(self.input_c)

        res = paddle.fmax(x, y)
        res = res.numpy()
        np.testing.assert_allclose(res, self.np_expected1, rtol=1e-05)

        # test broadcast
        res = paddle.fmax(x, z)
        res = res.numpy()
        np.testing.assert_allclose(res, self.np_expected2, rtol=1e-05)

        res = paddle.fmax(a, c)
        res = res.numpy()
        np.testing.assert_allclose(res, self.np_expected3, rtol=1e-05)

        res = paddle.fmax(b, c)
        res = res.numpy()
        np.testing.assert_allclose(res, self.np_expected4, rtol=1e-05)


class TestElementwiseFmaxOp(OpTest):
    """TestElementwiseFmaxOp"""

    def setUp(self):
        """setUp"""
        self.op_type = "elementwise_fmax"
        self.python_api = paddle.fmax
        # If x and y have the same value, the max() is not differentiable.
        # So we generate test data by the following method
        # to avoid them being too close to each other.
        x = np.random.uniform(0.1, 1, [13, 17]).astype("float64")
        sgn = np.random.choice([-1, 1], [13, 17]).astype("float64")
        y = x + sgn * np.random.uniform(0.1, 1, [13, 17]).astype("float64")
        self.inputs = {'X': x, 'Y': y}
        self.outputs = {'Out': np.fmax(self.inputs['X'], self.inputs['Y'])}

    def test_check_output(self):
        """test_check_output"""
        self.check_output(check_eager=True)

    def test_check_grad_normal(self):
        """test_check_grad_normal"""
        self.check_grad(['X', 'Y'], 'Out', check_eager=True)

    def test_check_grad_ingore_x(self):
        """test_check_grad_ingore_x"""
        self.check_grad(
            ['Y'],
            'Out',
            max_relative_error=0.005,
            no_grad_set=set("X"),
            check_eager=True,
        )

    def test_check_grad_ingore_y(self):
        """test_check_grad_ingore_y"""
        self.check_grad(
            ['X'],
            'Out',
            max_relative_error=0.005,
            no_grad_set=set('Y'),
            check_eager=True,
        )


class TestElementwiseFmax2Op(OpTest):
    """TestElementwiseFmax2Op"""

    def setUp(self):
        """setUp"""
        self.op_type = "elementwise_fmax"
        self.python_api = paddle.fmax
        # If x and y have the same value, the max() is not differentiable.
        # So we generate test data by the following method
        # to avoid them being too close to each other.
        x = np.random.uniform(0.1, 1, [13, 17]).astype("float64")
        sgn = np.random.choice([-1, 1], [13, 17]).astype("float64")
        y = x + sgn * np.random.uniform(0.1, 1, [13, 17]).astype("float64")

        y[2, 10:] = np.nan
        self.inputs = {'X': x, 'Y': y}
        self.outputs = {'Out': np.fmax(self.inputs['X'], self.inputs['Y'])}

    def test_check_output(self):
        """test_check_output"""
        self.check_output(check_eager=True)

    def test_check_grad_normal(self):
        """test_check_grad_normal"""
        self.check_grad(['X', 'Y'], 'Out', check_eager=True)

    def test_check_grad_ingore_x(self):
        """test_check_grad_ingore_x"""
        self.check_grad(
            ['Y'],
            'Out',
            max_relative_error=0.005,
            no_grad_set=set("X"),
            check_eager=True,
        )

    def test_check_grad_ingore_y(self):
        """test_check_grad_ingore_y"""
        self.check_grad(
            ['X'],
            'Out',
            max_relative_error=0.005,
            no_grad_set=set('Y'),
            check_eager=True,
        )


class TestElementwiseFmax3Op(OpTest):
    """TestElementwiseFmax3Op"""

    def setUp(self):
        """setUp"""
        self.op_type = "elementwise_fmax"
        self.python_api = paddle.fmax
        # If x and y have the same value, the max() is not differentiable.
        # So we generate test data by the following method
        # to avoid them being too close to each other.
        x = np.random.uniform(0.1, 1, [13, 17]).astype("float16")
        sgn = np.random.choice([-1, 1], [13, 17]).astype("float16")
        y = x + sgn * np.random.uniform(0.1, 1, [13, 17]).astype("float16")

        self.inputs = {'X': x, 'Y': y}
        self.outputs = {'Out': np.fmax(self.inputs['X'], self.inputs['Y'])}

    def test_check_output(self):
        """test_check_output"""
        self.check_output(check_eager=True)

    def test_check_grad_normal(self):
        """test_check_grad_normal"""
        self.check_grad(['X', 'Y'], 'Out', check_eager=True)


if __name__ == "__main__":
    unittest.main()
