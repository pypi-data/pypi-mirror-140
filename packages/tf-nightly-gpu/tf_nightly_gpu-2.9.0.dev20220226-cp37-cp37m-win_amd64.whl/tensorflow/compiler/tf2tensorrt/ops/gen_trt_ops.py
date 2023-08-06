"""Python wrappers around TensorFlow ops.

This file is MACHINE GENERATED! Do not edit.
"""

import collections

from tensorflow.python import pywrap_tfe as pywrap_tfe
from tensorflow.python.eager import context as _context
from tensorflow.python.eager import core as _core
from tensorflow.python.eager import execute as _execute
from tensorflow.python.framework import dtypes as _dtypes

from tensorflow.python.framework import op_def_registry as _op_def_registry
from tensorflow.python.framework import ops as _ops
from tensorflow.python.framework import op_def_library as _op_def_library
from tensorflow.python.util.deprecation import deprecated_endpoints
from tensorflow.python.util import dispatch as _dispatch
from tensorflow.python.util.tf_export import tf_export

from typing import TypeVar

@_dispatch.add_fallback_dispatch_list
@_dispatch.add_type_based_api_dispatcher
@tf_export('case')
def case(branch_index, input, Tout, branches, output_shapes=[], name=None):
  r"""TODO: add doc.

  Args:
    branch_index: A `Tensor` of type `int32`.
    input: A list of `Tensor` objects.
    Tout: A list of `tf.DTypes`.
    branches: A list of functions decorated with @Defun that has length `>= 1`.
    output_shapes: An optional list of shapes (each a `tf.TensorShape` or list of `ints`). Defaults to `[]`.
    name: A name for the operation (optional).

  Returns:
    A list of `Tensor` objects of type `Tout`.
  """
  _ctx = _context._context or _context.context()
  tld = _ctx._thread_local_data
  if tld.is_eager:
    try:
      _result = pywrap_tfe.TFE_Py_FastPathExecute(
        _ctx, "Case", name, branch_index, input, "Tout", Tout, "branches",
        branches, "output_shapes", output_shapes)
      return _result
    except _core._NotOkStatusException as e:
      _ops.raise_from_not_ok_status(e, name)
    except _core._FallbackException:
      pass
    try:
      _result = _dispatcher_for_case(
          (branch_index, input, Tout, branches, output_shapes, name,), None)
      if _result is not NotImplemented:
        return _result
      return case_eager_fallback(
          branch_index, input, Tout=Tout, branches=branches,
          output_shapes=output_shapes, name=name, ctx=_ctx)
    except _core._SymbolicException:
      pass  # Add nodes to the TensorFlow graph.
    except (TypeError, ValueError):
      _result = _dispatch.dispatch(
            case, (), dict(branch_index=branch_index, input=input, Tout=Tout,
                           branches=branches, output_shapes=output_shapes,
                           name=name)
          )
      if _result is not _dispatch.OpDispatcher.NOT_SUPPORTED:
        return _result
      raise
  else:
    _result = _dispatcher_for_case(
        (branch_index, input, Tout, branches, output_shapes, name,), None)
    if _result is not NotImplemented:
      return _result
  # Add nodes to the TensorFlow graph.
  if not isinstance(Tout, (list, tuple)):
    raise TypeError(
        "Expected list for 'Tout' argument to "
        "'case' Op, not %r." % Tout)
  Tout = [_execute.make_type(_t, "Tout") for _t in Tout]
  if not isinstance(branches, (list, tuple)):
    raise TypeError(
        "Expected list for 'branches' argument to "
        "'case' Op, not %r." % branches)
  if output_shapes is None:
    output_shapes = []
  if not isinstance(output_shapes, (list, tuple)):
    raise TypeError(
        "Expected list for 'output_shapes' argument to "
        "'case' Op, not %r." % output_shapes)
  output_shapes = [_execute.make_shape(_s, "output_shapes") for _s in output_shapes]
  try:
    _, _, _op, _outputs = _op_def_library._apply_op_helper(
        "Case", branch_index=branch_index, input=input, Tout=Tout,
                branches=branches, output_shapes=output_shapes, name=name)
  except (TypeError, ValueError):
    _result = _dispatch.dispatch(
          case, (), dict(branch_index=branch_index, input=input, Tout=Tout,
                         branches=branches, output_shapes=output_shapes,
                         name=name)
        )
    if _result is not _dispatch.OpDispatcher.NOT_SUPPORTED:
      return _result
    raise
  _result = _outputs[:]
  if not _result:
    return _op
  if _execute.must_record_gradient():
    _attrs = ("Tin", _op.get_attr("Tin"), "Tout", _op.get_attr("Tout"),
              "branches", _op.get_attr("branches"), "output_shapes",
              _op.get_attr("output_shapes"))
    _inputs_flat = _op.inputs
    _execute.record_gradient(
        "Case", _inputs_flat, _attrs, _result)
  return _result

Case = tf_export("raw_ops.Case")(_ops.to_raw_op(case))
_dispatcher_for_case = case._tf_type_based_dispatcher.Dispatch


def case_eager_fallback(branch_index, input, Tout, branches, output_shapes, name, ctx):
  if not isinstance(Tout, (list, tuple)):
    raise TypeError(
        "Expected list for 'Tout' argument to "
        "'case' Op, not %r." % Tout)
  Tout = [_execute.make_type(_t, "Tout") for _t in Tout]
  if not isinstance(branches, (list, tuple)):
    raise TypeError(
        "Expected list for 'branches' argument to "
        "'case' Op, not %r." % branches)
  if output_shapes is None:
    output_shapes = []
  if not isinstance(output_shapes, (list, tuple)):
    raise TypeError(
        "Expected list for 'output_shapes' argument to "
        "'case' Op, not %r." % output_shapes)
  output_shapes = [_execute.make_shape(_s, "output_shapes") for _s in output_shapes]
  _attr_Tin, input = _execute.convert_to_mixed_eager_tensors(input, ctx)
  branch_index = _ops.convert_to_tensor(branch_index, _dtypes.int32)
  _inputs_flat = [branch_index] + list(input)
  _attrs = ("Tin", _attr_Tin, "Tout", Tout, "branches", branches,
  "output_shapes", output_shapes)
  _result = _execute.execute(b"Case", len(Tout), inputs=_inputs_flat,
                             attrs=_attrs, ctx=ctx, name=name)
  if _execute.must_record_gradient():
    _execute.record_gradient(
        "Case", _inputs_flat, _attrs, _result)
  return _result


@_dispatch.add_fallback_dispatch_list
@_dispatch.add_type_based_api_dispatcher
@tf_export('device_index')
def device_index(device_names, name=None):
  r"""TODO: add doc.

  Args:
    device_names: A list of `strings`.
    name: A name for the operation (optional).

  Returns:
    A `Tensor` of type `int32`.
  """
  _ctx = _context._context or _context.context()
  tld = _ctx._thread_local_data
  if tld.is_eager:
    try:
      _result = pywrap_tfe.TFE_Py_FastPathExecute(
        _ctx, "DeviceIndex", name, "device_names", device_names)
      return _result
    except _core._NotOkStatusException as e:
      _ops.raise_from_not_ok_status(e, name)
    except _core._FallbackException:
      pass
    try:
      _result = _dispatcher_for_device_index(
          (device_names, name,), None)
      if _result is not NotImplemented:
        return _result
      return device_index_eager_fallback(
          device_names=device_names, name=name, ctx=_ctx)
    except _core._SymbolicException:
      pass  # Add nodes to the TensorFlow graph.
    except (TypeError, ValueError):
      _result = _dispatch.dispatch(
            device_index, (), dict(device_names=device_names, name=name)
          )
      if _result is not _dispatch.OpDispatcher.NOT_SUPPORTED:
        return _result
      raise
  else:
    _result = _dispatcher_for_device_index(
        (device_names, name,), None)
    if _result is not NotImplemented:
      return _result
  # Add nodes to the TensorFlow graph.
  if not isinstance(device_names, (list, tuple)):
    raise TypeError(
        "Expected list for 'device_names' argument to "
        "'device_index' Op, not %r." % device_names)
  device_names = [_execute.make_str(_s, "device_names") for _s in device_names]
  try:
    _, _, _op, _outputs = _op_def_library._apply_op_helper(
        "DeviceIndex", device_names=device_names, name=name)
  except (TypeError, ValueError):
    _result = _dispatch.dispatch(
          device_index, (), dict(device_names=device_names, name=name)
        )
    if _result is not _dispatch.OpDispatcher.NOT_SUPPORTED:
      return _result
    raise
  _result = _outputs[:]
  if _execute.must_record_gradient():
    _attrs = ("device_names", _op.get_attr("device_names"))
    _inputs_flat = _op.inputs
    _execute.record_gradient(
        "DeviceIndex", _inputs_flat, _attrs, _result)
  _result, = _result
  return _result

DeviceIndex = tf_export("raw_ops.DeviceIndex")(_ops.to_raw_op(device_index))
_dispatcher_for_device_index = device_index._tf_type_based_dispatcher.Dispatch


def device_index_eager_fallback(device_names, name, ctx):
  if not isinstance(device_names, (list, tuple)):
    raise TypeError(
        "Expected list for 'device_names' argument to "
        "'device_index' Op, not %r." % device_names)
  device_names = [_execute.make_str(_s, "device_names") for _s in device_names]
  _inputs_flat = []
  _attrs = ("device_names", device_names)
  _result = _execute.execute(b"DeviceIndex", 1, inputs=_inputs_flat,
                             attrs=_attrs, ctx=ctx, name=name)
  if _execute.must_record_gradient():
    _execute.record_gradient(
        "DeviceIndex", _inputs_flat, _attrs, _result)
  _result, = _result
  return _result


@_dispatch.add_fallback_dispatch_list
@_dispatch.add_type_based_api_dispatcher
@tf_export('fake_param')
def fake_param(dtype, shape, name=None):
  r"""TODO: add doc.

  Args:
    dtype: A `tf.DType`.
    shape: A `tf.TensorShape` or list of `ints`.
    name: A name for the operation (optional).

  Returns:
    A `Tensor` of type `dtype`.
  """
  _ctx = _context._context or _context.context()
  tld = _ctx._thread_local_data
  if tld.is_eager:
    try:
      _result = pywrap_tfe.TFE_Py_FastPathExecute(
        _ctx, "FakeParam", name, "dtype", dtype, "shape", shape)
      return _result
    except _core._NotOkStatusException as e:
      _ops.raise_from_not_ok_status(e, name)
    except _core._FallbackException:
      pass
    try:
      _result = _dispatcher_for_fake_param(
          (dtype, shape, name,), None)
      if _result is not NotImplemented:
        return _result
      return fake_param_eager_fallback(
          dtype=dtype, shape=shape, name=name, ctx=_ctx)
    except _core._SymbolicException:
      pass  # Add nodes to the TensorFlow graph.
    except (TypeError, ValueError):
      _result = _dispatch.dispatch(
            fake_param, (), dict(dtype=dtype, shape=shape, name=name)
          )
      if _result is not _dispatch.OpDispatcher.NOT_SUPPORTED:
        return _result
      raise
  else:
    _result = _dispatcher_for_fake_param(
        (dtype, shape, name,), None)
    if _result is not NotImplemented:
      return _result
  # Add nodes to the TensorFlow graph.
  dtype = _execute.make_type(dtype, "dtype")
  shape = _execute.make_shape(shape, "shape")
  try:
    _, _, _op, _outputs = _op_def_library._apply_op_helper(
        "FakeParam", dtype=dtype, shape=shape, name=name)
  except (TypeError, ValueError):
    _result = _dispatch.dispatch(
          fake_param, (), dict(dtype=dtype, shape=shape, name=name)
        )
    if _result is not _dispatch.OpDispatcher.NOT_SUPPORTED:
      return _result
    raise
  _result = _outputs[:]
  if _execute.must_record_gradient():
    _attrs = ("dtype", _op._get_attr_type("dtype"), "shape",
              _op.get_attr("shape"))
    _inputs_flat = _op.inputs
    _execute.record_gradient(
        "FakeParam", _inputs_flat, _attrs, _result)
  _result, = _result
  return _result

FakeParam = tf_export("raw_ops.FakeParam")(_ops.to_raw_op(fake_param))
_dispatcher_for_fake_param = fake_param._tf_type_based_dispatcher.Dispatch


def fake_param_eager_fallback(dtype, shape, name, ctx):
  dtype = _execute.make_type(dtype, "dtype")
  shape = _execute.make_shape(shape, "shape")
  _inputs_flat = []
  _attrs = ("dtype", dtype, "shape", shape)
  _result = _execute.execute(b"FakeParam", 1, inputs=_inputs_flat,
                             attrs=_attrs, ctx=ctx, name=name)
  if _execute.must_record_gradient():
    _execute.record_gradient(
        "FakeParam", _inputs_flat, _attrs, _result)
  _result, = _result
  return _result


@_dispatch.add_fallback_dispatch_list
@_dispatch.add_type_based_api_dispatcher
@tf_export('partitioned_call')
def partitioned_call(args, Tout, f, config="", config_proto="", executor_type="", name=None):
  r"""TODO: add doc.

  Args:
    args: A list of `Tensor` objects.
    Tout: A list of `tf.DTypes`.
    f: A function decorated with @Defun.
    config: An optional `string`. Defaults to `""`.
    config_proto: An optional `string`. Defaults to `""`.
    executor_type: An optional `string`. Defaults to `""`.
    name: A name for the operation (optional).

  Returns:
    A list of `Tensor` objects of type `Tout`.
  """
  _ctx = _context._context or _context.context()
  tld = _ctx._thread_local_data
  if tld.is_eager:
    try:
      _result = pywrap_tfe.TFE_Py_FastPathExecute(
        _ctx, "PartitionedCall", name, args, "Tout", Tout, "f", f, "config",
        config, "config_proto", config_proto, "executor_type", executor_type)
      return _result
    except _core._NotOkStatusException as e:
      _ops.raise_from_not_ok_status(e, name)
    except _core._FallbackException:
      pass
    try:
      _result = _dispatcher_for_partitioned_call(
          (args, Tout, f, config, config_proto, executor_type, name,), None)
      if _result is not NotImplemented:
        return _result
      return partitioned_call_eager_fallback(
          args, Tout=Tout, f=f, config=config, config_proto=config_proto,
          executor_type=executor_type, name=name, ctx=_ctx)
    except _core._SymbolicException:
      pass  # Add nodes to the TensorFlow graph.
    except (TypeError, ValueError):
      _result = _dispatch.dispatch(
            partitioned_call, (), dict(args=args, Tout=Tout, f=f,
                                       config=config,
                                       config_proto=config_proto,
                                       executor_type=executor_type, name=name)
          )
      if _result is not _dispatch.OpDispatcher.NOT_SUPPORTED:
        return _result
      raise
  else:
    _result = _dispatcher_for_partitioned_call(
        (args, Tout, f, config, config_proto, executor_type, name,), None)
    if _result is not NotImplemented:
      return _result
  # Add nodes to the TensorFlow graph.
  if not isinstance(Tout, (list, tuple)):
    raise TypeError(
        "Expected list for 'Tout' argument to "
        "'partitioned_call' Op, not %r." % Tout)
  Tout = [_execute.make_type(_t, "Tout") for _t in Tout]
  if config is None:
    config = ""
  config = _execute.make_str(config, "config")
  if config_proto is None:
    config_proto = ""
  config_proto = _execute.make_str(config_proto, "config_proto")
  if executor_type is None:
    executor_type = ""
  executor_type = _execute.make_str(executor_type, "executor_type")
  try:
    _, _, _op, _outputs = _op_def_library._apply_op_helper(
        "PartitionedCall", args=args, Tout=Tout, f=f, config=config,
                           config_proto=config_proto,
                           executor_type=executor_type, name=name)
  except (TypeError, ValueError):
    _result = _dispatch.dispatch(
          partitioned_call, (), dict(args=args, Tout=Tout, f=f, config=config,
                                     config_proto=config_proto,
                                     executor_type=executor_type, name=name)
        )
    if _result is not _dispatch.OpDispatcher.NOT_SUPPORTED:
      return _result
    raise
  _result = _outputs[:]
  if _execute.must_record_gradient():
    _attrs = ("Tin", _op.get_attr("Tin"), "Tout", _op.get_attr("Tout"), "f",
              _op.get_attr("f"), "config", _op.get_attr("config"),
              "config_proto", _op.get_attr("config_proto"), "executor_type",
              _op.get_attr("executor_type"))
    _inputs_flat = _op.inputs
    _execute.record_gradient(
        "PartitionedCall", _inputs_flat, _attrs, _result)
  return _result

PartitionedCall = tf_export("raw_ops.PartitionedCall")(_ops.to_raw_op(partitioned_call))
_dispatcher_for_partitioned_call = partitioned_call._tf_type_based_dispatcher.Dispatch


def partitioned_call_eager_fallback(args, Tout, f, config, config_proto, executor_type, name, ctx):
  if not isinstance(Tout, (list, tuple)):
    raise TypeError(
        "Expected list for 'Tout' argument to "
        "'partitioned_call' Op, not %r." % Tout)
  Tout = [_execute.make_type(_t, "Tout") for _t in Tout]
  if config is None:
    config = ""
  config = _execute.make_str(config, "config")
  if config_proto is None:
    config_proto = ""
  config_proto = _execute.make_str(config_proto, "config_proto")
  if executor_type is None:
    executor_type = ""
  executor_type = _execute.make_str(executor_type, "executor_type")
  _attr_Tin, args = _execute.convert_to_mixed_eager_tensors(args, ctx)
  _inputs_flat = list(args)
  _attrs = ("Tin", _attr_Tin, "Tout", Tout, "f", f, "config", config,
  "config_proto", config_proto, "executor_type", executor_type)
  _result = _execute.execute(b"PartitionedCall", len(Tout),
                             inputs=_inputs_flat, attrs=_attrs, ctx=ctx,
                             name=name)
  if _execute.must_record_gradient():
    _execute.record_gradient(
        "PartitionedCall", _inputs_flat, _attrs, _result)
  return _result


@_dispatch.add_fallback_dispatch_list
@_dispatch.add_type_based_api_dispatcher
@tf_export('remote_call')
def remote_call(target, args, Tout, f, name=None):
  r"""TODO: add doc.

  Args:
    target: A `Tensor` of type `string`.
    args: A list of `Tensor` objects.
    Tout: A list of `tf.DTypes` that has length `>= 1`.
    f: A function decorated with @Defun.
    name: A name for the operation (optional).

  Returns:
    A list of `Tensor` objects of type `Tout`.
  """
  _ctx = _context._context or _context.context()
  tld = _ctx._thread_local_data
  if tld.is_eager:
    try:
      _result = pywrap_tfe.TFE_Py_FastPathExecute(
        _ctx, "RemoteCall", name, target, args, "Tout", Tout, "f", f)
      return _result
    except _core._NotOkStatusException as e:
      _ops.raise_from_not_ok_status(e, name)
    except _core._FallbackException:
      pass
    try:
      _result = _dispatcher_for_remote_call(
          (target, args, Tout, f, name,), None)
      if _result is not NotImplemented:
        return _result
      return remote_call_eager_fallback(
          target, args, Tout=Tout, f=f, name=name, ctx=_ctx)
    except _core._SymbolicException:
      pass  # Add nodes to the TensorFlow graph.
    except (TypeError, ValueError):
      _result = _dispatch.dispatch(
            remote_call, (), dict(target=target, args=args, Tout=Tout, f=f,
                                  name=name)
          )
      if _result is not _dispatch.OpDispatcher.NOT_SUPPORTED:
        return _result
      raise
  else:
    _result = _dispatcher_for_remote_call(
        (target, args, Tout, f, name,), None)
    if _result is not NotImplemented:
      return _result
  # Add nodes to the TensorFlow graph.
  if not isinstance(Tout, (list, tuple)):
    raise TypeError(
        "Expected list for 'Tout' argument to "
        "'remote_call' Op, not %r." % Tout)
  Tout = [_execute.make_type(_t, "Tout") for _t in Tout]
  try:
    _, _, _op, _outputs = _op_def_library._apply_op_helper(
        "RemoteCall", target=target, args=args, Tout=Tout, f=f, name=name)
  except (TypeError, ValueError):
    _result = _dispatch.dispatch(
          remote_call, (), dict(target=target, args=args, Tout=Tout, f=f,
                                name=name)
        )
    if _result is not _dispatch.OpDispatcher.NOT_SUPPORTED:
      return _result
    raise
  _result = _outputs[:]
  if not _result:
    return _op
  if _execute.must_record_gradient():
    _attrs = ("Tin", _op.get_attr("Tin"), "Tout", _op.get_attr("Tout"), "f",
              _op.get_attr("f"))
    _inputs_flat = _op.inputs
    _execute.record_gradient(
        "RemoteCall", _inputs_flat, _attrs, _result)
  return _result

RemoteCall = tf_export("raw_ops.RemoteCall")(_ops.to_raw_op(remote_call))
_dispatcher_for_remote_call = remote_call._tf_type_based_dispatcher.Dispatch


def remote_call_eager_fallback(target, args, Tout, f, name, ctx):
  if not isinstance(Tout, (list, tuple)):
    raise TypeError(
        "Expected list for 'Tout' argument to "
        "'remote_call' Op, not %r." % Tout)
  Tout = [_execute.make_type(_t, "Tout") for _t in Tout]
  _attr_Tin, args = _execute.convert_to_mixed_eager_tensors(args, ctx)
  target = _ops.convert_to_tensor(target, _dtypes.string)
  _inputs_flat = [target] + list(args)
  _attrs = ("Tin", _attr_Tin, "Tout", Tout, "f", f)
  _result = _execute.execute(b"RemoteCall", len(Tout), inputs=_inputs_flat,
                             attrs=_attrs, ctx=ctx, name=name)
  if _execute.must_record_gradient():
    _execute.record_gradient(
        "RemoteCall", _inputs_flat, _attrs, _result)
  return _result


@_dispatch.add_fallback_dispatch_list
@_dispatch.add_type_based_api_dispatcher
@tf_export('stateful_partitioned_call')
def stateful_partitioned_call(args, Tout, f, config="", config_proto="", executor_type="", name=None):
  r"""TODO: add doc.

  Args:
    args: A list of `Tensor` objects.
    Tout: A list of `tf.DTypes`.
    f: A function decorated with @Defun.
    config: An optional `string`. Defaults to `""`.
    config_proto: An optional `string`. Defaults to `""`.
    executor_type: An optional `string`. Defaults to `""`.
    name: A name for the operation (optional).

  Returns:
    A list of `Tensor` objects of type `Tout`.
  """
  _ctx = _context._context or _context.context()
  tld = _ctx._thread_local_data
  if tld.is_eager:
    try:
      _result = pywrap_tfe.TFE_Py_FastPathExecute(
        _ctx, "StatefulPartitionedCall", name, args, "Tout", Tout, "f", f,
        "config", config, "config_proto", config_proto, "executor_type",
        executor_type)
      return _result
    except _core._NotOkStatusException as e:
      _ops.raise_from_not_ok_status(e, name)
    except _core._FallbackException:
      pass
    try:
      _result = _dispatcher_for_stateful_partitioned_call(
          (args, Tout, f, config, config_proto, executor_type, name,), None)
      if _result is not NotImplemented:
        return _result
      return stateful_partitioned_call_eager_fallback(
          args, Tout=Tout, f=f, config=config, config_proto=config_proto,
          executor_type=executor_type, name=name, ctx=_ctx)
    except _core._SymbolicException:
      pass  # Add nodes to the TensorFlow graph.
    except (TypeError, ValueError):
      _result = _dispatch.dispatch(
            stateful_partitioned_call, (), dict(args=args, Tout=Tout, f=f,
                                                config=config,
                                                config_proto=config_proto,
                                                executor_type=executor_type,
                                                name=name)
          )
      if _result is not _dispatch.OpDispatcher.NOT_SUPPORTED:
        return _result
      raise
  else:
    _result = _dispatcher_for_stateful_partitioned_call(
        (args, Tout, f, config, config_proto, executor_type, name,), None)
    if _result is not NotImplemented:
      return _result
  # Add nodes to the TensorFlow graph.
  if not isinstance(Tout, (list, tuple)):
    raise TypeError(
        "Expected list for 'Tout' argument to "
        "'stateful_partitioned_call' Op, not %r." % Tout)
  Tout = [_execute.make_type(_t, "Tout") for _t in Tout]
  if config is None:
    config = ""
  config = _execute.make_str(config, "config")
  if config_proto is None:
    config_proto = ""
  config_proto = _execute.make_str(config_proto, "config_proto")
  if executor_type is None:
    executor_type = ""
  executor_type = _execute.make_str(executor_type, "executor_type")
  try:
    _, _, _op, _outputs = _op_def_library._apply_op_helper(
        "StatefulPartitionedCall", args=args, Tout=Tout, f=f, config=config,
                                   config_proto=config_proto,
                                   executor_type=executor_type, name=name)
  except (TypeError, ValueError):
    _result = _dispatch.dispatch(
          stateful_partitioned_call, (), dict(args=args, Tout=Tout, f=f,
                                              config=config,
                                              config_proto=config_proto,
                                              executor_type=executor_type,
                                              name=name)
        )
    if _result is not _dispatch.OpDispatcher.NOT_SUPPORTED:
      return _result
    raise
  _result = _outputs[:]
  if not _result:
    return _op
  if _execute.must_record_gradient():
    _attrs = ("Tin", _op.get_attr("Tin"), "Tout", _op.get_attr("Tout"), "f",
              _op.get_attr("f"), "config", _op.get_attr("config"),
              "config_proto", _op.get_attr("config_proto"), "executor_type",
              _op.get_attr("executor_type"))
    _inputs_flat = _op.inputs
    _execute.record_gradient(
        "StatefulPartitionedCall", _inputs_flat, _attrs, _result)
  return _result

StatefulPartitionedCall = tf_export("raw_ops.StatefulPartitionedCall")(_ops.to_raw_op(stateful_partitioned_call))
_dispatcher_for_stateful_partitioned_call = stateful_partitioned_call._tf_type_based_dispatcher.Dispatch


def stateful_partitioned_call_eager_fallback(args, Tout, f, config, config_proto, executor_type, name, ctx):
  if not isinstance(Tout, (list, tuple)):
    raise TypeError(
        "Expected list for 'Tout' argument to "
        "'stateful_partitioned_call' Op, not %r." % Tout)
  Tout = [_execute.make_type(_t, "Tout") for _t in Tout]
  if config is None:
    config = ""
  config = _execute.make_str(config, "config")
  if config_proto is None:
    config_proto = ""
  config_proto = _execute.make_str(config_proto, "config_proto")
  if executor_type is None:
    executor_type = ""
  executor_type = _execute.make_str(executor_type, "executor_type")
  _attr_Tin, args = _execute.convert_to_mixed_eager_tensors(args, ctx)
  _inputs_flat = list(args)
  _attrs = ("Tin", _attr_Tin, "Tout", Tout, "f", f, "config", config,
  "config_proto", config_proto, "executor_type", executor_type)
  _result = _execute.execute(b"StatefulPartitionedCall", len(Tout),
                             inputs=_inputs_flat, attrs=_attrs, ctx=ctx,
                             name=name)
  if _execute.must_record_gradient():
    _execute.record_gradient(
        "StatefulPartitionedCall", _inputs_flat, _attrs, _result)
  return _result


@_dispatch.add_fallback_dispatch_list
@_dispatch.add_type_based_api_dispatcher
@tf_export('stateless_case')
def stateless_case(branch_index, input, Tout, branches, output_shapes=[], name=None):
  r"""TODO: add doc.

  Args:
    branch_index: A `Tensor` of type `int32`.
    input: A list of `Tensor` objects.
    Tout: A list of `tf.DTypes`.
    branches: A list of functions decorated with @Defun that has length `>= 1`.
    output_shapes: An optional list of shapes (each a `tf.TensorShape` or list of `ints`). Defaults to `[]`.
    name: A name for the operation (optional).

  Returns:
    A list of `Tensor` objects of type `Tout`.
  """
  _ctx = _context._context or _context.context()
  tld = _ctx._thread_local_data
  if tld.is_eager:
    try:
      _result = pywrap_tfe.TFE_Py_FastPathExecute(
        _ctx, "StatelessCase", name, branch_index, input, "Tout", Tout,
        "branches", branches, "output_shapes", output_shapes)
      return _result
    except _core._NotOkStatusException as e:
      _ops.raise_from_not_ok_status(e, name)
    except _core._FallbackException:
      pass
    try:
      _result = _dispatcher_for_stateless_case(
          (branch_index, input, Tout, branches, output_shapes, name,), None)
      if _result is not NotImplemented:
        return _result
      return stateless_case_eager_fallback(
          branch_index, input, Tout=Tout, branches=branches,
          output_shapes=output_shapes, name=name, ctx=_ctx)
    except _core._SymbolicException:
      pass  # Add nodes to the TensorFlow graph.
    except (TypeError, ValueError):
      _result = _dispatch.dispatch(
            stateless_case, (), dict(branch_index=branch_index, input=input,
                                     Tout=Tout, branches=branches,
                                     output_shapes=output_shapes, name=name)
          )
      if _result is not _dispatch.OpDispatcher.NOT_SUPPORTED:
        return _result
      raise
  else:
    _result = _dispatcher_for_stateless_case(
        (branch_index, input, Tout, branches, output_shapes, name,), None)
    if _result is not NotImplemented:
      return _result
  # Add nodes to the TensorFlow graph.
  if not isinstance(Tout, (list, tuple)):
    raise TypeError(
        "Expected list for 'Tout' argument to "
        "'stateless_case' Op, not %r." % Tout)
  Tout = [_execute.make_type(_t, "Tout") for _t in Tout]
  if not isinstance(branches, (list, tuple)):
    raise TypeError(
        "Expected list for 'branches' argument to "
        "'stateless_case' Op, not %r." % branches)
  if output_shapes is None:
    output_shapes = []
  if not isinstance(output_shapes, (list, tuple)):
    raise TypeError(
        "Expected list for 'output_shapes' argument to "
        "'stateless_case' Op, not %r." % output_shapes)
  output_shapes = [_execute.make_shape(_s, "output_shapes") for _s in output_shapes]
  try:
    _, _, _op, _outputs = _op_def_library._apply_op_helper(
        "StatelessCase", branch_index=branch_index, input=input, Tout=Tout,
                         branches=branches, output_shapes=output_shapes,
                         name=name)
  except (TypeError, ValueError):
    _result = _dispatch.dispatch(
          stateless_case, (), dict(branch_index=branch_index, input=input,
                                   Tout=Tout, branches=branches,
                                   output_shapes=output_shapes, name=name)
        )
    if _result is not _dispatch.OpDispatcher.NOT_SUPPORTED:
      return _result
    raise
  _result = _outputs[:]
  if _execute.must_record_gradient():
    _attrs = ("Tin", _op.get_attr("Tin"), "Tout", _op.get_attr("Tout"),
              "branches", _op.get_attr("branches"), "output_shapes",
              _op.get_attr("output_shapes"))
    _inputs_flat = _op.inputs
    _execute.record_gradient(
        "StatelessCase", _inputs_flat, _attrs, _result)
  return _result

StatelessCase = tf_export("raw_ops.StatelessCase")(_ops.to_raw_op(stateless_case))
_dispatcher_for_stateless_case = stateless_case._tf_type_based_dispatcher.Dispatch


def stateless_case_eager_fallback(branch_index, input, Tout, branches, output_shapes, name, ctx):
  if not isinstance(Tout, (list, tuple)):
    raise TypeError(
        "Expected list for 'Tout' argument to "
        "'stateless_case' Op, not %r." % Tout)
  Tout = [_execute.make_type(_t, "Tout") for _t in Tout]
  if not isinstance(branches, (list, tuple)):
    raise TypeError(
        "Expected list for 'branches' argument to "
        "'stateless_case' Op, not %r." % branches)
  if output_shapes is None:
    output_shapes = []
  if not isinstance(output_shapes, (list, tuple)):
    raise TypeError(
        "Expected list for 'output_shapes' argument to "
        "'stateless_case' Op, not %r." % output_shapes)
  output_shapes = [_execute.make_shape(_s, "output_shapes") for _s in output_shapes]
  _attr_Tin, input = _execute.convert_to_mixed_eager_tensors(input, ctx)
  branch_index = _ops.convert_to_tensor(branch_index, _dtypes.int32)
  _inputs_flat = [branch_index] + list(input)
  _attrs = ("Tin", _attr_Tin, "Tout", Tout, "branches", branches,
  "output_shapes", output_shapes)
  _result = _execute.execute(b"StatelessCase", len(Tout), inputs=_inputs_flat,
                             attrs=_attrs, ctx=ctx, name=name)
  if _execute.must_record_gradient():
    _execute.record_gradient(
        "StatelessCase", _inputs_flat, _attrs, _result)
  return _result


@_dispatch.add_fallback_dispatch_list
@_dispatch.add_type_based_api_dispatcher
@tf_export('stateless_if')
def stateless_if(cond, input, Tout, then_branch, else_branch, output_shapes=[], name=None):
  r"""TODO: add doc.

  Args:
    cond: A `Tensor`.
    input: A list of `Tensor` objects.
    Tout: A list of `tf.DTypes`.
    then_branch: A function decorated with @Defun.
    else_branch: A function decorated with @Defun.
    output_shapes: An optional list of shapes (each a `tf.TensorShape` or list of `ints`). Defaults to `[]`.
    name: A name for the operation (optional).

  Returns:
    A list of `Tensor` objects of type `Tout`.
  """
  _ctx = _context._context or _context.context()
  tld = _ctx._thread_local_data
  if tld.is_eager:
    try:
      _result = pywrap_tfe.TFE_Py_FastPathExecute(
        _ctx, "StatelessIf", name, cond, input, "Tout", Tout, "then_branch",
        then_branch, "else_branch", else_branch, "output_shapes",
        output_shapes)
      return _result
    except _core._NotOkStatusException as e:
      _ops.raise_from_not_ok_status(e, name)
    except _core._FallbackException:
      pass
    try:
      _result = _dispatcher_for_stateless_if(
          (cond, input, Tout, then_branch, else_branch, output_shapes, name,),
          None)
      if _result is not NotImplemented:
        return _result
      return stateless_if_eager_fallback(
          cond, input, Tout=Tout, then_branch=then_branch,
          else_branch=else_branch, output_shapes=output_shapes, name=name,
          ctx=_ctx)
    except _core._SymbolicException:
      pass  # Add nodes to the TensorFlow graph.
    except (TypeError, ValueError):
      _result = _dispatch.dispatch(
            stateless_if, (), dict(cond=cond, input=input, Tout=Tout,
                                   then_branch=then_branch,
                                   else_branch=else_branch,
                                   output_shapes=output_shapes, name=name)
          )
      if _result is not _dispatch.OpDispatcher.NOT_SUPPORTED:
        return _result
      raise
  else:
    _result = _dispatcher_for_stateless_if(
        (cond, input, Tout, then_branch, else_branch, output_shapes, name,),
        None)
    if _result is not NotImplemented:
      return _result
  # Add nodes to the TensorFlow graph.
  if not isinstance(Tout, (list, tuple)):
    raise TypeError(
        "Expected list for 'Tout' argument to "
        "'stateless_if' Op, not %r." % Tout)
  Tout = [_execute.make_type(_t, "Tout") for _t in Tout]
  if output_shapes is None:
    output_shapes = []
  if not isinstance(output_shapes, (list, tuple)):
    raise TypeError(
        "Expected list for 'output_shapes' argument to "
        "'stateless_if' Op, not %r." % output_shapes)
  output_shapes = [_execute.make_shape(_s, "output_shapes") for _s in output_shapes]
  try:
    _, _, _op, _outputs = _op_def_library._apply_op_helper(
        "StatelessIf", cond=cond, input=input, Tout=Tout,
                       then_branch=then_branch, else_branch=else_branch,
                       output_shapes=output_shapes, name=name)
  except (TypeError, ValueError):
    _result = _dispatch.dispatch(
          stateless_if, (), dict(cond=cond, input=input, Tout=Tout,
                                 then_branch=then_branch,
                                 else_branch=else_branch,
                                 output_shapes=output_shapes, name=name)
        )
    if _result is not _dispatch.OpDispatcher.NOT_SUPPORTED:
      return _result
    raise
  _result = _outputs[:]
  if _execute.must_record_gradient():
    _attrs = ("Tcond", _op._get_attr_type("Tcond"), "Tin",
              _op.get_attr("Tin"), "Tout", _op.get_attr("Tout"),
              "then_branch", _op.get_attr("then_branch"), "else_branch",
              _op.get_attr("else_branch"), "output_shapes",
              _op.get_attr("output_shapes"))
    _inputs_flat = _op.inputs
    _execute.record_gradient(
        "StatelessIf", _inputs_flat, _attrs, _result)
  return _result

StatelessIf = tf_export("raw_ops.StatelessIf")(_ops.to_raw_op(stateless_if))
_dispatcher_for_stateless_if = stateless_if._tf_type_based_dispatcher.Dispatch


def stateless_if_eager_fallback(cond, input, Tout, then_branch, else_branch, output_shapes, name, ctx):
  if not isinstance(Tout, (list, tuple)):
    raise TypeError(
        "Expected list for 'Tout' argument to "
        "'stateless_if' Op, not %r." % Tout)
  Tout = [_execute.make_type(_t, "Tout") for _t in Tout]
  if output_shapes is None:
    output_shapes = []
  if not isinstance(output_shapes, (list, tuple)):
    raise TypeError(
        "Expected list for 'output_shapes' argument to "
        "'stateless_if' Op, not %r." % output_shapes)
  output_shapes = [_execute.make_shape(_s, "output_shapes") for _s in output_shapes]
  _attr_Tcond, (cond,) = _execute.args_to_matching_eager([cond], ctx, [])
  _attr_Tin, input = _execute.convert_to_mixed_eager_tensors(input, ctx)
  _inputs_flat = [cond] + list(input)
  _attrs = ("Tcond", _attr_Tcond, "Tin", _attr_Tin, "Tout", Tout,
  "then_branch", then_branch, "else_branch", else_branch, "output_shapes",
  output_shapes)
  _result = _execute.execute(b"StatelessIf", len(Tout), inputs=_inputs_flat,
                             attrs=_attrs, ctx=ctx, name=name)
  if _execute.must_record_gradient():
    _execute.record_gradient(
        "StatelessIf", _inputs_flat, _attrs, _result)
  return _result


@_dispatch.add_fallback_dispatch_list
@_dispatch.add_type_based_api_dispatcher
@tf_export('stateless_while')
def stateless_while(input, cond, body, output_shapes=[], parallel_iterations=10, name=None):
  r"""TODO: add doc.

  Args:
    input: A list of `Tensor` objects.
    cond: A function decorated with @Defun.
    body: A function decorated with @Defun.
    output_shapes: An optional list of shapes (each a `tf.TensorShape` or list of `ints`). Defaults to `[]`.
    parallel_iterations: An optional `int`. Defaults to `10`.
    name: A name for the operation (optional).

  Returns:
    A list of `Tensor` objects. Has the same type as `input`.
  """
  _ctx = _context._context or _context.context()
  tld = _ctx._thread_local_data
  if tld.is_eager:
    try:
      _result = pywrap_tfe.TFE_Py_FastPathExecute(
        _ctx, "StatelessWhile", name, input, "cond", cond, "body", body,
        "output_shapes", output_shapes, "parallel_iterations",
        parallel_iterations)
      return _result
    except _core._NotOkStatusException as e:
      _ops.raise_from_not_ok_status(e, name)
    except _core._FallbackException:
      pass
    try:
      _result = _dispatcher_for_stateless_while(
          (input, cond, body, output_shapes, parallel_iterations, name,), None)
      if _result is not NotImplemented:
        return _result
      return stateless_while_eager_fallback(
          input, cond=cond, body=body, output_shapes=output_shapes,
          parallel_iterations=parallel_iterations, name=name, ctx=_ctx)
    except _core._SymbolicException:
      pass  # Add nodes to the TensorFlow graph.
    except (TypeError, ValueError):
      _result = _dispatch.dispatch(
            stateless_while, (), dict(input=input, cond=cond, body=body,
                                      output_shapes=output_shapes,
                                      parallel_iterations=parallel_iterations,
                                      name=name)
          )
      if _result is not _dispatch.OpDispatcher.NOT_SUPPORTED:
        return _result
      raise
  else:
    _result = _dispatcher_for_stateless_while(
        (input, cond, body, output_shapes, parallel_iterations, name,), None)
    if _result is not NotImplemented:
      return _result
  # Add nodes to the TensorFlow graph.
  if output_shapes is None:
    output_shapes = []
  if not isinstance(output_shapes, (list, tuple)):
    raise TypeError(
        "Expected list for 'output_shapes' argument to "
        "'stateless_while' Op, not %r." % output_shapes)
  output_shapes = [_execute.make_shape(_s, "output_shapes") for _s in output_shapes]
  if parallel_iterations is None:
    parallel_iterations = 10
  parallel_iterations = _execute.make_int(parallel_iterations, "parallel_iterations")
  try:
    _, _, _op, _outputs = _op_def_library._apply_op_helper(
        "StatelessWhile", input=input, cond=cond, body=body,
                          output_shapes=output_shapes,
                          parallel_iterations=parallel_iterations, name=name)
  except (TypeError, ValueError):
    _result = _dispatch.dispatch(
          stateless_while, (), dict(input=input, cond=cond, body=body,
                                    output_shapes=output_shapes,
                                    parallel_iterations=parallel_iterations,
                                    name=name)
        )
    if _result is not _dispatch.OpDispatcher.NOT_SUPPORTED:
      return _result
    raise
  _result = _outputs[:]
  if _execute.must_record_gradient():
    _attrs = ("T", _op.get_attr("T"), "cond", _op.get_attr("cond"), "body",
              _op.get_attr("body"), "output_shapes",
              _op.get_attr("output_shapes"), "parallel_iterations",
              _op._get_attr_int("parallel_iterations"))
    _inputs_flat = _op.inputs
    _execute.record_gradient(
        "StatelessWhile", _inputs_flat, _attrs, _result)
  return _result

StatelessWhile = tf_export("raw_ops.StatelessWhile")(_ops.to_raw_op(stateless_while))
_dispatcher_for_stateless_while = stateless_while._tf_type_based_dispatcher.Dispatch


def stateless_while_eager_fallback(input, cond, body, output_shapes, parallel_iterations, name, ctx):
  if output_shapes is None:
    output_shapes = []
  if not isinstance(output_shapes, (list, tuple)):
    raise TypeError(
        "Expected list for 'output_shapes' argument to "
        "'stateless_while' Op, not %r." % output_shapes)
  output_shapes = [_execute.make_shape(_s, "output_shapes") for _s in output_shapes]
  if parallel_iterations is None:
    parallel_iterations = 10
  parallel_iterations = _execute.make_int(parallel_iterations, "parallel_iterations")
  _attr_T, input = _execute.convert_to_mixed_eager_tensors(input, ctx)
  _inputs_flat = list(input)
  _attrs = ("T", _attr_T, "cond", cond, "body", body, "output_shapes",
  output_shapes, "parallel_iterations", parallel_iterations)
  _result = _execute.execute(b"StatelessWhile", len(input),
                             inputs=_inputs_flat, attrs=_attrs, ctx=ctx,
                             name=name)
  if _execute.must_record_gradient():
    _execute.record_gradient(
        "StatelessWhile", _inputs_flat, _attrs, _result)
  return _result


@_dispatch.add_fallback_dispatch_list
@_dispatch.add_type_based_api_dispatcher
@tf_export('symbolic_gradient')
def symbolic_gradient(input, Tout, f, name=None):
  r"""TODO: add doc.

  Args:
    input: A list of `Tensor` objects.
    Tout: A list of `tf.DTypes` that has length `>= 1`.
    f: A function decorated with @Defun.
    name: A name for the operation (optional).

  Returns:
    A list of `Tensor` objects of type `Tout`.
  """
  _ctx = _context._context or _context.context()
  tld = _ctx._thread_local_data
  if tld.is_eager:
    try:
      _result = pywrap_tfe.TFE_Py_FastPathExecute(
        _ctx, "SymbolicGradient", name, input, "Tout", Tout, "f", f)
      return _result
    except _core._NotOkStatusException as e:
      _ops.raise_from_not_ok_status(e, name)
    except _core._FallbackException:
      pass
    try:
      _result = _dispatcher_for_symbolic_gradient(
          (input, Tout, f, name,), None)
      if _result is not NotImplemented:
        return _result
      return symbolic_gradient_eager_fallback(
          input, Tout=Tout, f=f, name=name, ctx=_ctx)
    except _core._SymbolicException:
      pass  # Add nodes to the TensorFlow graph.
    except (TypeError, ValueError):
      _result = _dispatch.dispatch(
            symbolic_gradient, (), dict(input=input, Tout=Tout, f=f,
                                        name=name)
          )
      if _result is not _dispatch.OpDispatcher.NOT_SUPPORTED:
        return _result
      raise
  else:
    _result = _dispatcher_for_symbolic_gradient(
        (input, Tout, f, name,), None)
    if _result is not NotImplemented:
      return _result
  # Add nodes to the TensorFlow graph.
  if not isinstance(Tout, (list, tuple)):
    raise TypeError(
        "Expected list for 'Tout' argument to "
        "'symbolic_gradient' Op, not %r." % Tout)
  Tout = [_execute.make_type(_t, "Tout") for _t in Tout]
  try:
    _, _, _op, _outputs = _op_def_library._apply_op_helper(
        "SymbolicGradient", input=input, Tout=Tout, f=f, name=name)
  except (TypeError, ValueError):
    _result = _dispatch.dispatch(
          symbolic_gradient, (), dict(input=input, Tout=Tout, f=f, name=name)
        )
    if _result is not _dispatch.OpDispatcher.NOT_SUPPORTED:
      return _result
    raise
  _result = _outputs[:]
  if _execute.must_record_gradient():
    _attrs = ("Tin", _op.get_attr("Tin"), "Tout", _op.get_attr("Tout"), "f",
              _op.get_attr("f"))
    _inputs_flat = _op.inputs
    _execute.record_gradient(
        "SymbolicGradient", _inputs_flat, _attrs, _result)
  return _result

SymbolicGradient = tf_export("raw_ops.SymbolicGradient")(_ops.to_raw_op(symbolic_gradient))
_dispatcher_for_symbolic_gradient = symbolic_gradient._tf_type_based_dispatcher.Dispatch


def symbolic_gradient_eager_fallback(input, Tout, f, name, ctx):
  if not isinstance(Tout, (list, tuple)):
    raise TypeError(
        "Expected list for 'Tout' argument to "
        "'symbolic_gradient' Op, not %r." % Tout)
  Tout = [_execute.make_type(_t, "Tout") for _t in Tout]
  _attr_Tin, input = _execute.convert_to_mixed_eager_tensors(input, ctx)
  _inputs_flat = list(input)
  _attrs = ("Tin", _attr_Tin, "Tout", Tout, "f", f)
  _result = _execute.execute(b"SymbolicGradient", len(Tout),
                             inputs=_inputs_flat, attrs=_attrs, ctx=ctx,
                             name=name)
  if _execute.must_record_gradient():
    _execute.record_gradient(
        "SymbolicGradient", _inputs_flat, _attrs, _result)
  return _result


@_dispatch.add_fallback_dispatch_list
@_dispatch.add_type_based_api_dispatcher
@tf_export('to_bool')
def to_bool(input, name=None):
  r"""TODO: add doc.

  Args:
    input: A `Tensor`.
    name: A name for the operation (optional).

  Returns:
    A `Tensor` of type `bool`.
  """
  _ctx = _context._context or _context.context()
  tld = _ctx._thread_local_data
  if tld.is_eager:
    try:
      _result = pywrap_tfe.TFE_Py_FastPathExecute(
        _ctx, "ToBool", name, input)
      return _result
    except _core._NotOkStatusException as e:
      _ops.raise_from_not_ok_status(e, name)
    except _core._FallbackException:
      pass
    try:
      _result = _dispatcher_for_to_bool(
          (input, name,), None)
      if _result is not NotImplemented:
        return _result
      return to_bool_eager_fallback(
          input, name=name, ctx=_ctx)
    except _core._SymbolicException:
      pass  # Add nodes to the TensorFlow graph.
    except (TypeError, ValueError):
      _result = _dispatch.dispatch(
            to_bool, (), dict(input=input, name=name)
          )
      if _result is not _dispatch.OpDispatcher.NOT_SUPPORTED:
        return _result
      raise
  else:
    _result = _dispatcher_for_to_bool(
        (input, name,), None)
    if _result is not NotImplemented:
      return _result
  # Add nodes to the TensorFlow graph.
  try:
    _, _, _op, _outputs = _op_def_library._apply_op_helper(
        "ToBool", input=input, name=name)
  except (TypeError, ValueError):
    _result = _dispatch.dispatch(
          to_bool, (), dict(input=input, name=name)
        )
    if _result is not _dispatch.OpDispatcher.NOT_SUPPORTED:
      return _result
    raise
  _result = _outputs[:]
  if _execute.must_record_gradient():
    _attrs = ("T", _op._get_attr_type("T"))
    _inputs_flat = _op.inputs
    _execute.record_gradient(
        "ToBool", _inputs_flat, _attrs, _result)
  _result, = _result
  return _result

ToBool = tf_export("raw_ops.ToBool")(_ops.to_raw_op(to_bool))
_dispatcher_for_to_bool = to_bool._tf_type_based_dispatcher.Dispatch


def to_bool_eager_fallback(input, name, ctx):
  _attr_T, (input,) = _execute.args_to_matching_eager([input], ctx, [])
  _inputs_flat = [input]
  _attrs = ("T", _attr_T)
  _result = _execute.execute(b"ToBool", 1, inputs=_inputs_flat, attrs=_attrs,
                             ctx=ctx, name=name)
  if _execute.must_record_gradient():
    _execute.record_gradient(
        "ToBool", _inputs_flat, _attrs, _result)
  _result, = _result
  return _result

