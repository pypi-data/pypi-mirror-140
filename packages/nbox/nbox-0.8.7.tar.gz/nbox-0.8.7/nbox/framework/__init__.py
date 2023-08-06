r"""This submodule concerns itself with conversion of different framworks to other frameworks.
It achieves this by providing a fix set of functions for each framework. There are a couple of
caveats that the developer must know about.

1. We use joblib to serialize the model, see `reason <https://stackoverflow.com/questions/12615525/what-are-the-different-use-cases-of-joblib-versus-pickle>`_ \
so when you will try to unpickle the model ``pickle`` will not work correctly and will throw the error
``_pickle.UnpicklingError: invalid load key, '\x00'``. So ensure that you use ``joblib``.

2. Serializing torch models directly is a bit tricky and weird, you can read more about it
`here <https://github.com/pytorch/pytorch/blob/master/torch/csrc/jit/docs/serialization.md>`_,
so technically pytorch torch.save() automatically pickles the object along with the required
datapoint (model hierarchy, constants, data, etc.)

Lazy Loading
------------

All the dependencies are checked at runtime only, meaning all the modules coded can be referenced
removing blockers and custom duct taping.

Documentation
-------------
"""

from .on_ml import NBXModel, TorchModel, SklearnModel, ONNXRtModel, IllegalFormatError
from .on_operators import AirflowMixin

# this function is for getting the meta data and is framework agnostic, so adding this in the
# __init__ of framework submodule
def get_meta(input_names, input_shapes, args, output_names, output_shapes, outputs):
  """Generic method to convert the inputs to get ``nbox_meta['metadata']`` dictionary"""
  # get the meta object
  def __get_struct(names_, shapes_, tensors_):
    return {
      name: {
        "dtype": str(tensor.dtype),
        "tensorShape": {"dim": [{"name": "", "size": x} for x in shapes], "unknownRank": False},
        "name": name,
      }
      for name, shapes, tensor in zip(names_, shapes_, tensors_)
    }

  meta = {"inputs": __get_struct(input_names, input_shapes, args), "outputs": __get_struct(output_names, output_shapes, outputs)}

  return meta

def get_model_mixin(i0, i1):
  all_e = []
  for m in (
    NBXModel, TorchModel, SklearnModel, ONNXRtModel
  ):
    try:
      # if this is the correct method 
      return m(i0, i1)
    except IllegalFormatError as e:
      all_e.append(f"--> ERROR: {type(m)}: {e}")

  raise IllegalFormatError(
    f"Unkown inputs: {type(i0)} {type(i1)}!" + \
    "\n".join(all_e)
  )
