# Copyright 2022 Google LLC.
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

# pytype: skip-file
"""Tests for rax.examples.web30k."""

import io
from unittest import mock

from absl.testing import absltest
from jax import test_util as jtu

from examples import web30k
import tensorflow_datasets as tfds

EXPECTED_OUTPUT = """epoch=1
  loss=46.48952
  metric/mrr=0.00000
  metric/ndcg=0.80958
  metric/ndcg@10=0.62020
epoch=2
  loss=46.47362
  metric/mrr=0.00000
  metric/ndcg=0.81584
  metric/ndcg@10=0.63113
epoch=3
  loss=46.46141
  metric/mrr=0.00000
  metric/ndcg=0.82966
  metric/ndcg@10=0.65239
"""


class Web30kTest(jtu.JaxTestCase):

  def test_end_to_end(self):
    mock_stdout = io.StringIO()
    with mock.patch("sys.stdout", mock_stdout):
      with tfds.testing.mock_data(
          num_examples=256, policy=tfds.testing.MockPolicy.USE_CODE):
        argv = ()
        web30k.main(argv)

    output = mock_stdout.getvalue()
    self.assertEqual(EXPECTED_OUTPUT, output)


if __name__ == "__main__":
  absltest.main(testLoader=jtu.JaxTestLoader())
