#   Copyright (c) 2021 PaddlePaddle Authors. All Rights Reserved.
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
from op_test import OpTest


class TestFlattenOp(OpTest):
    def setUp(self):
        self.python_api = paddle.flatten
        self.python_out_sig = ["Out"]
        self.op_type = "flatten_contiguous_range"
        self.start_axis = 0
        self.stop_axis = -1
        self.init_test_case()
        self.inputs = {"X": np.random.random(self.in_shape).astype("float64")}
        self.init_attrs()
        self.outputs = {
            "Out": self.inputs["X"].reshape(self.new_shape),
            "XShape": np.random.random(self.in_shape).astype("float32"),
        }

    def test_check_output(self):
        self.check_output(no_check_set=["XShape"], check_eager=True)

    def test_check_grad(self):
        self.check_grad(["X"], "Out", check_eager=True)

    def init_test_case(self):
        self.in_shape = (3, 2, 5, 4)
        self.start_axis = 0
        self.stop_axis = -1
        self.new_shape = 120

    def init_attrs(self):
        self.attrs = {
            "start_axis": self.start_axis,
            "stop_axis": self.stop_axis,
        }


class TestFlattenOp_1(TestFlattenOp):
    def init_test_case(self):
        self.in_shape = (3, 2, 5, 4)
        self.start_axis = 1
        self.stop_axis = 2
        self.new_shape = (3, 10, 4)

    def init_attrs(self):
        self.attrs = {
            "start_axis": self.start_axis,
            "stop_axis": self.stop_axis,
        }


class TestFlattenOp_2(TestFlattenOp):
    def init_test_case(self):
        self.in_shape = (3, 2, 5, 4)
        self.start_axis = 0
        self.stop_axis = 1
        self.new_shape = (6, 5, 4)

    def init_attrs(self):
        self.attrs = {
            "start_axis": self.start_axis,
            "stop_axis": self.stop_axis,
        }


class TestFlattenOp_3(TestFlattenOp):
    def init_test_case(self):
        self.in_shape = (3, 2, 5, 4)
        self.start_axis = 0
        self.stop_axis = 2
        self.new_shape = (30, 4)

    def init_attrs(self):
        self.attrs = {
            "start_axis": self.start_axis,
            "stop_axis": self.stop_axis,
        }


class TestFlattenOp_4(TestFlattenOp):
    def init_test_case(self):
        self.in_shape = (3, 2, 5, 4)
        self.start_axis = -2
        self.stop_axis = -1
        self.new_shape = (3, 2, 20)

    def init_attrs(self):
        self.attrs = {
            "start_axis": self.start_axis,
            "stop_axis": self.stop_axis,
        }


class TestFlattenOp_5(TestFlattenOp):
    def init_test_case(self):
        self.in_shape = (3, 2, 5, 4)
        self.start_axis = 2
        self.stop_axis = 2
        self.new_shape = (3, 2, 5, 4)

    def init_attrs(self):
        self.attrs = {
            "start_axis": self.start_axis,
            "stop_axis": self.stop_axis,
        }


class TestFlattenOpSixDims(TestFlattenOp):
    def init_test_case(self):
        self.in_shape = (3, 2, 3, 2, 4, 4)
        self.start_axis = 3
        self.stop_axis = 5
        self.new_shape = (3, 2, 3, 32)

    def init_attrs(self):
        self.attrs = {
            "start_axis": self.start_axis,
            "stop_axis": self.stop_axis,
        }


class TestFlatten2OpError(unittest.TestCase):
    def test_errors(self):
        image_shape = (2, 3, 4, 4)
        x = (
            np.arange(
                image_shape[0]
                * image_shape[1]
                * image_shape[2]
                * image_shape[3]
            ).reshape(image_shape)
            / 100.0
        )
        x = x.astype('float32')

        def test_ValueError1():
            x_var = paddle.static.data(
                name="x", shape=image_shape, dtype='float32'
            )
            out = paddle.flatten(x_var, start_axis=2, stop_axis=1)

        self.assertRaises(ValueError, test_ValueError1)

        def test_ValueError2():
            x_var = paddle.static.data(
                name="x", shape=image_shape, dtype='float32'
            )
            paddle.flatten(x_var, start_axis=10, stop_axis=1)

        self.assertRaises(ValueError, test_ValueError2)

        def test_ValueError3():
            x_var = paddle.static.data(
                name="x", shape=image_shape, dtype='float32'
            )
            paddle.flatten(x_var, start_axis=2, stop_axis=10)

        self.assertRaises(ValueError, test_ValueError3)

        def test_type():
            # dtype must be float32, float64, int8, int32, int64, uint8.
            x2 = (
                np.arange(
                    image_shape[0]
                    * image_shape[1]
                    * image_shape[2]
                    * image_shape[3]
                ).reshape(image_shape)
                / 100.0
            )
            x2 = x2.astype('float16')
            x2_var = paddle.fluid.data(
                name='x2', shape=[3, 2, 4, 5], dtype='float16'
            )
            paddle.flatten(x2_var)

        self.assertRaises(TypeError, test_type)

        def test_InputError():
            out = paddle.flatten(x)

        self.assertRaises(ValueError, test_InputError)


class TestStaticFlattenPythonAPI(unittest.TestCase):
    def execute_api(self, x, start_axis=0, stop_axis=-1):
        return paddle.flatten(x, start_axis, stop_axis)

    def test_static_api(self):
        paddle.enable_static()
        np_x = np.random.rand(2, 3, 4, 4).astype('float32')

        main_prog = paddle.static.Program()
        with paddle.static.program_guard(main_prog, paddle.static.Program()):
            x = paddle.static.data(
                name="x", shape=[2, 3, 4, 4], dtype='float32'
            )
            out = self.execute_api(x, start_axis=-2, stop_axis=-1)

        exe = paddle.static.Executor(place=paddle.CPUPlace())
        fetch_out = exe.run(main_prog, feed={"x": np_x}, fetch_list=[out])
        self.assertTrue((2, 3, 16) == fetch_out[0].shape)


class TestStaticFlattenInferShapePythonAPI(unittest.TestCase):
    def execute_api(self, x, start_axis=0, stop_axis=-1):
        return paddle.flatten(x, start_axis, stop_axis)

    def test_static_api(self):
        paddle.enable_static()
        main_prog = paddle.static.Program()
        with paddle.static.program_guard(main_prog, paddle.static.Program()):
            x = paddle.static.data(
                name="x", shape=[-1, 3, -1, -1], dtype='float32'
            )
            out = self.execute_api(x, start_axis=2, stop_axis=3)
        self.assertTrue((-1, 3, -1) == out.shape)


class TestStaticInplaceFlattenPythonAPI(TestStaticFlattenPythonAPI):
    def execute_api(self, x, start_axis=0, stop_axis=-1):
        return x.flatten_(start_axis, stop_axis)


class TestFlattenPython(unittest.TestCase):
    def test_python_api(self):
        image_shape = (2, 3, 4, 4)
        x = (
            np.arange(
                image_shape[0]
                * image_shape[1]
                * image_shape[2]
                * image_shape[3]
            ).reshape(image_shape)
            / 100.0
        )
        x = x.astype('float32')

        def test_InputError():
            out = paddle.flatten(x)

        self.assertRaises(ValueError, test_InputError)

        def test_Negative():
            paddle.disable_static()
            img = paddle.to_tensor(x)
            out = paddle.flatten(img, start_axis=-2, stop_axis=-1)
            return out.numpy().shape

        res_shape = test_Negative()
        self.assertTrue((2, 3, 16) == res_shape)


class TestDygraphInplaceFlattenPython(unittest.TestCase):
    def test_python_api(self):
        image_shape = (2, 3, 4, 4)
        x = (
            np.arange(
                image_shape[0]
                * image_shape[1]
                * image_shape[2]
                * image_shape[3]
            ).reshape(image_shape)
            / 100.0
        )
        x = x.astype('float32')

        def test_Negative():
            paddle.disable_static()
            img = paddle.to_tensor(x)
            out = img.flatten_(start_axis=-2, stop_axis=-1)
            return out.numpy().shape

        res_shape = test_Negative()
        self.assertTrue((2, 3, 16) == res_shape)
        paddle.enable_static()


if __name__ == "__main__":
    unittest.main()
