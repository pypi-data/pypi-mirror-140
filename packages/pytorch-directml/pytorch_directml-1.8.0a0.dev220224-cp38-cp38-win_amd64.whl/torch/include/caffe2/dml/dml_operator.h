/* Copyright (c) Microsoft Corporation.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/

#pragma once

#include <cstdint>
#include <functional>

#include "dml_common.h"
#include "dml_buffer_region.h"
#include "dml_kernel_key.h"
#include "dml_operator_traits.h"
#include "dml_util.h"

namespace dml {

// Forward declarations
struct DmlBackend;
struct IDmlTensor;

struct DmlOperatorBase
{
  DmlOperatorBase(DmlBackend* backend, const DML_OPERATOR_DESC& op_desc, size_t num_inputs, size_t num_outputs);
  DmlOperatorBase(DmlBackend* backend, IDMLCompiledOperator* compiled_op, size_t num_inputs, size_t num_outputs);

  void AssignInput(size_t index, D3D12BufferRegion buffer);
  void AssignOutput(size_t index, D3D12BufferRegion buffer);
  const DML_BUFFER_BINDING* GetPersistentResourceBinding() const;
  void Compute();
  void ClearBindings();
  void Initialize();

 private:
  bool IsGraphOp();

 protected:
  DmlBackend* backend_;
  const DML_OPERATOR_DESC op_desc_;

  std::vector<D3D12BufferRegion> inputs_;
  std::vector<D3D12BufferRegion> outputs_;

  Microsoft::WRL::ComPtr<IDMLCompiledOperator> compiled_op_;
  Microsoft::WRL::ComPtr<IDmlTensor> persistent_resource_tensor_;
  DML_BUFFER_BINDING persistent_resource_binding_;
  bool is_initialized_ = false;
};

template <DML_OPERATOR_TYPE TType>
struct HashableOperator {
  static constexpr bool IsHashable() { return DmlKernelKey<TType>::implemented; }
  static uint64_t CreateKey(const DML_OP_DESC<TType>& op_desc) {
    return DmlKernelKey<TType>(&op_desc).Hash();
  }
};

// DmlOperator
template <DML_OPERATOR_TYPE TType> struct DmlOperator {};

// Output-Only Operators
template <DML_OPERATOR_TYPE TType>
struct DmlOutputOperator : public DmlOperatorBase
{
  DmlOutputOperator(DmlBackend* backend, const DML_OP_DESC<TType>& op_desc) :
    DmlOperatorBase(backend, DML_OPERATOR_DESC {TType, &op_desc}, 0, 1)
  {}

  auto OutputTensor(D3D12BufferRegion buffer) {
    DmlOperatorBase::AssignOutput(0, buffer);
  }
};

template <> struct DmlOperator<DML_OPERATOR_FILL_VALUE_SEQUENCE> :
  DmlOutputOperator<DML_OPERATOR_FILL_VALUE_SEQUENCE>,
  public HashableOperator<DML_OPERATOR_FILL_VALUE_SEQUENCE>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_FILL_VALUE_SEQUENCE>& op_desc) :
     DmlOutputOperator<DML_OPERATOR_FILL_VALUE_SEQUENCE>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_FILL_VALUE_CONSTANT> :
  DmlOutputOperator<DML_OPERATOR_FILL_VALUE_CONSTANT>,
  public HashableOperator<DML_OPERATOR_FILL_VALUE_CONSTANT>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_FILL_VALUE_CONSTANT>& op_desc) :
     DmlOutputOperator<DML_OPERATOR_FILL_VALUE_CONSTANT>(backend, op_desc) {}
};

// Binary Operators
template <DML_OPERATOR_TYPE TType>
struct DmlBinaryOperator : public DmlOperatorBase
{
  DmlBinaryOperator(DmlBackend* backend, const DML_OP_DESC<TType>& op_desc) :
    DmlOperatorBase(backend, DML_OPERATOR_DESC {TType, &op_desc}, 2, 1)
  {}

  auto ATensor(D3D12BufferRegion buffer) {
    DmlOperatorBase::AssignInput(0, buffer);
  }
  auto BTensor(D3D12BufferRegion buffer) {
    DmlOperatorBase::AssignInput(1, buffer);
  }
  auto OutputTensor(D3D12BufferRegion buffer) {
    DmlOperatorBase::AssignOutput(0, buffer);
  }
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_DIVIDE> :
  DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_DIVIDE>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_DIVIDE>
{
  DmlOperator(DmlBackend* backend, const DML_ELEMENT_WISE_DIVIDE_OPERATOR_DESC& op_desc) :
     DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_DIVIDE>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_MULTIPLY> :
  DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_MULTIPLY>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_MULTIPLY>
{
  DmlOperator(DmlBackend* backend, const DML_ELEMENT_WISE_MULTIPLY_OPERATOR_DESC& op_desc) :
     DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_MULTIPLY>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_ADD> :
  DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_ADD>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_ADD>
{
  DmlOperator(DmlBackend* backend, const DML_ELEMENT_WISE_ADD_OPERATOR_DESC& op_desc) :
     DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_ADD>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_SUBTRACT> :
  DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_SUBTRACT>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_SUBTRACT>
{
  DmlOperator(DmlBackend* backend, const DML_ELEMENT_WISE_SUBTRACT_OPERATOR_DESC& op_desc) :
     DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_SUBTRACT>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_MAX> :
  DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_MAX>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_MAX>
{
  DmlOperator(DmlBackend* backend, const DML_ELEMENT_WISE_MAX_OPERATOR_DESC& op_desc) :
     DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_MAX>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_MIN> :
  DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_MIN>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_MIN>
{
  DmlOperator(DmlBackend* backend, const DML_ELEMENT_WISE_MIN_OPERATOR_DESC& op_desc) :
     DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_MIN>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_ADD1> :
  DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_ADD1>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_ADD1>
{
  DmlOperator(DmlBackend* backend, const DML_ELEMENT_WISE_ADD1_OPERATOR_DESC& op_desc) :
     DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_ADD1>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_MODULUS_TRUNCATE> :
  DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_MODULUS_TRUNCATE>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_MODULUS_TRUNCATE>
{
  DmlOperator(DmlBackend* backend, const DML_ELEMENT_WISE_MODULUS_TRUNCATE_OPERATOR_DESC& op_desc) :
     DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_MODULUS_TRUNCATE>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_GREATER_THAN_OR_EQUAL> :
  DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_GREATER_THAN_OR_EQUAL>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_GREATER_THAN_OR_EQUAL>
{
  DmlOperator(DmlBackend* backend, const DML_ELEMENT_WISE_LOGICAL_GREATER_THAN_OR_EQUAL_OPERATOR_DESC& op_desc) :
     DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_GREATER_THAN_OR_EQUAL>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_LESS_THAN_OR_EQUAL> :
  DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_LESS_THAN_OR_EQUAL>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_LESS_THAN_OR_EQUAL>
{
  DmlOperator(DmlBackend* backend, const DML_ELEMENT_WISE_LOGICAL_LESS_THAN_OR_EQUAL_OPERATOR_DESC& op_desc) :
     DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_LESS_THAN_OR_EQUAL>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_GREATER_THAN> :
  DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_GREATER_THAN>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_GREATER_THAN>
{
  DmlOperator(DmlBackend* backend, const DML_ELEMENT_WISE_LOGICAL_GREATER_THAN_OPERATOR_DESC& op_desc) :
     DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_GREATER_THAN>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_LESS_THAN> :
  DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_LESS_THAN>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_LESS_THAN>
{
  DmlOperator(DmlBackend* backend, const DML_ELEMENT_WISE_LOGICAL_LESS_THAN_OPERATOR_DESC& op_desc) :
     DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_LESS_THAN>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_EQUALS> :
  DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_EQUALS>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_EQUALS>
{
  DmlOperator(DmlBackend* backend, const DML_ELEMENT_WISE_LOGICAL_EQUALS_OPERATOR_DESC& op_desc) :
     DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_EQUALS>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_AND> :
  DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_AND>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_AND>
{
  DmlOperator(DmlBackend* backend, const DML_ELEMENT_WISE_LOGICAL_AND_OPERATOR_DESC& op_desc) :
     DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_AND>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_OR> :
  DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_OR>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_OR>
{
  DmlOperator(DmlBackend* backend, const DML_ELEMENT_WISE_LOGICAL_OR_OPERATOR_DESC& op_desc) :
     DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_OR>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_XOR> :
  DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_XOR>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_XOR>
{
  DmlOperator(DmlBackend* backend, const DML_ELEMENT_WISE_LOGICAL_XOR_OPERATOR_DESC& op_desc) :
     DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_XOR>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_BIT_AND> :
  DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_BIT_AND>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_BIT_AND>
{
  DmlOperator(DmlBackend* backend, const DML_ELEMENT_WISE_BIT_AND_OPERATOR_DESC& op_desc) :
     DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_BIT_AND>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_POW> :
  DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_POW>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_POW>
{
  DmlOperator(DmlBackend* backend, const DML_ELEMENT_WISE_POW_OPERATOR_DESC& op_desc) :
     DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_POW>(backend, op_desc) {}

  auto InputTensor(D3D12BufferRegion buffer) {
    ATensor(buffer);
  }

  auto ExponentTensor(D3D12BufferRegion buffer) {
    BTensor(buffer);
  }

  auto OutputTensor(D3D12BufferRegion buffer) {
    DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_POW>::OutputTensor(buffer);
  }

  auto Compute() {
    DmlBinaryOperator<DML_OPERATOR_ELEMENT_WISE_POW>::Compute();
  }
};

template <> struct DmlOperator<DML_OPERATOR_REVERSE_SUBSEQUENCES> :
  DmlBinaryOperator<DML_OPERATOR_REVERSE_SUBSEQUENCES>,
  public HashableOperator<DML_OPERATOR_REVERSE_SUBSEQUENCES>
{
  DmlOperator(DmlBackend* backend, const DML_REVERSE_SUBSEQUENCES_OPERATOR_DESC& op_desc) :
     DmlBinaryOperator<DML_OPERATOR_REVERSE_SUBSEQUENCES>(backend, op_desc) {}

  auto InputTensor(D3D12BufferRegion buffer) {
    ATensor(buffer);
  }

  auto SequenceLengthsTensor(D3D12BufferRegion buffer) {
    BTensor(buffer);
  }

  auto OutputTensor(D3D12BufferRegion buffer) {
    DmlBinaryOperator<DML_OPERATOR_REVERSE_SUBSEQUENCES>::OutputTensor(buffer);
  }

  auto Compute() {
    DmlBinaryOperator<DML_OPERATOR_REVERSE_SUBSEQUENCES>::Compute();
  }
};

// Unary Ops
template <DML_OPERATOR_TYPE TType>
struct DmlUnaryOperator : public DmlOperatorBase
{
  DmlUnaryOperator(DmlBackend* backend, const DML_OP_DESC<TType>& op_desc) :
    DmlOperatorBase(backend, DML_OPERATOR_DESC {TType, &op_desc}, 1, 1)
  {}

  auto InputTensor(D3D12BufferRegion buffer) {
    DmlOperatorBase::AssignInput(0, buffer);
  }

  auto OutputTensor(D3D12BufferRegion buffer) {
    DmlOperatorBase::AssignOutput(0, buffer);
  }
};

template <> struct DmlOperator<DML_OPERATOR_CAST> :
  DmlUnaryOperator<DML_OPERATOR_CAST>,
  public HashableOperator<DML_OPERATOR_CAST>
{
  DmlOperator(DmlBackend* backend, const DML_CAST_OPERATOR_DESC& op_desc) :
     DmlUnaryOperator<DML_OPERATOR_CAST>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_TILE> :
  DmlUnaryOperator<DML_OPERATOR_TILE>,
  public HashableOperator<DML_OPERATOR_TILE>
{
  DmlOperator(DmlBackend* backend, const DML_TILE_OPERATOR_DESC& op_desc) :
     DmlUnaryOperator<DML_OPERATOR_TILE>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_AVERAGE_POOLING> :
  DmlUnaryOperator<DML_OPERATOR_AVERAGE_POOLING>,
  public HashableOperator<DML_OPERATOR_AVERAGE_POOLING>
{
  DmlOperator(DmlBackend* backend, const DML_AVERAGE_POOLING_OPERATOR_DESC& op_desc) :
     DmlUnaryOperator<DML_OPERATOR_AVERAGE_POOLING>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ACTIVATION_RELU> :
  DmlUnaryOperator<DML_OPERATOR_ACTIVATION_RELU>,
  public HashableOperator<DML_OPERATOR_ACTIVATION_RELU>
{
  DmlOperator(DmlBackend* backend, const DML_ACTIVATION_RELU_OPERATOR_DESC& op_desc) :
     DmlUnaryOperator<DML_OPERATOR_ACTIVATION_RELU>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ACTIVATION_LOG_SOFTMAX> :
  DmlUnaryOperator<DML_OPERATOR_ACTIVATION_LOG_SOFTMAX>,
  public HashableOperator<DML_OPERATOR_ACTIVATION_LOG_SOFTMAX>
{
  DmlOperator(DmlBackend* backend, const DML_ACTIVATION_LOG_SOFTMAX_OPERATOR_DESC& op_desc) :
     DmlUnaryOperator<DML_OPERATOR_ACTIVATION_LOG_SOFTMAX>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_ASIN> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_ASIN>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_ASIN>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_ASIN>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_ASIN>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_ATAN> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_ATAN>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_ATAN>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_ATAN>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_ATAN>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_CEIL> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_CEIL>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_CEIL>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_CEIL>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_CEIL>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_EXP> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_EXP>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_EXP>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_EXP>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_EXP>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_ROUND> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_ROUND>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_ROUND>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_ROUND>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_ROUND>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_SIGN> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_SIGN>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_SIGN>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_SIGN>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_SIGN>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_FLOOR> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_FLOOR>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_FLOOR>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_FLOOR>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_FLOOR>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_LOG> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_LOG>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_LOG>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_LOG>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_LOG>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_COS> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_COS>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_COS>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_COS>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_COS>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_TAN> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_TAN>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_TAN>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_TAN>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_TAN>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_CONSTANT_POW> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_CONSTANT_POW>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_CONSTANT_POW>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_CONSTANT_POW>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_CONSTANT_POW>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_RECIP> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_RECIP>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_RECIP>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_RECIP>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_RECIP>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_SIN> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_SIN>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_SIN>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_SIN>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_SIN>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_SQRT> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_SQRT>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_SQRT>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_SQRT>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_SQRT>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_ERF> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_ERF>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_ERF>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_ERF>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_ERF>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_SINH> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_SINH>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_SINH>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_SINH>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_SINH>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_COSH> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_COSH>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_COSH>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_COSH>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_COSH>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_TANH> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_TANH>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_TANH>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_TANH>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_TANH>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_ASINH> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_ASINH>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_ASINH>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_ASINH>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_ASINH>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_NOT> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_NOT>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_NOT>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_LOGICAL_NOT>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_LOGICAL_NOT>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_ACOSH> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_ACOSH>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_ACOSH>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_ACOSH>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_ACOSH>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_ATANH> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_ATANH>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_ATANH>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_ATANH>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_ATANH>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_IDENTITY> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_IDENTITY>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_IDENTITY>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_IDENTITY>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_IDENTITY>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_ABS> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_ABS>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_ABS>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_ABS>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_ABS>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_ACOS> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_ACOS>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_ACOS>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_ACOS>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_ACOS>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_REDUCE> :
  DmlUnaryOperator<DML_OPERATOR_REDUCE>,
  public HashableOperator<DML_OPERATOR_REDUCE>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_REDUCE>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_REDUCE>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ACTIVATION_SIGMOID> :
  DmlUnaryOperator<DML_OPERATOR_ACTIVATION_SIGMOID>,
  public HashableOperator<DML_OPERATOR_ACTIVATION_SIGMOID>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ACTIVATION_SIGMOID>& op_desc) :
    DmlUnaryOperator<DML_OPERATOR_ACTIVATION_SIGMOID>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ACTIVATION_LEAKY_RELU> :
  DmlUnaryOperator<DML_OPERATOR_ACTIVATION_LEAKY_RELU>,
  public HashableOperator<DML_OPERATOR_ACTIVATION_LEAKY_RELU>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ACTIVATION_LEAKY_RELU>& op_desc) :
     DmlUnaryOperator<DML_OPERATOR_ACTIVATION_LEAKY_RELU>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_CLIP> :
  DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_CLIP>,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_CLIP>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_CLIP>& op_desc) :
     DmlUnaryOperator<DML_OPERATOR_ELEMENT_WISE_CLIP>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_RESAMPLE> :
  DmlUnaryOperator<DML_OPERATOR_RESAMPLE>,
  public HashableOperator<DML_OPERATOR_RESAMPLE>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_RESAMPLE>& op_desc) :
     DmlUnaryOperator<DML_OPERATOR_RESAMPLE>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_RESAMPLE_GRAD> :
  DmlUnaryOperator<DML_OPERATOR_RESAMPLE_GRAD>,
  public HashableOperator<DML_OPERATOR_RESAMPLE_GRAD>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_RESAMPLE_GRAD>& op_desc) :
     DmlUnaryOperator<DML_OPERATOR_RESAMPLE_GRAD>(backend, op_desc) {}
};

template <> struct DmlOperator<DML_OPERATOR_ELEMENT_WISE_IF> :
  public DmlOperatorBase,
  public HashableOperator<DML_OPERATOR_ELEMENT_WISE_IF>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ELEMENT_WISE_IF>& op_desc) :
    DmlOperatorBase(backend, DML_OPERATOR_DESC {DML_OPERATOR_ELEMENT_WISE_IF, &op_desc}, 3, 1)
  {}

  auto ConditionTensor(D3D12BufferRegion buffer) {
    AssignInput(0, buffer);
  }
  auto ATensor(D3D12BufferRegion buffer) {
    AssignInput(1, buffer);
  }
  auto BTensor(D3D12BufferRegion buffer) {
    AssignInput(2, buffer);
  }
  auto OutputTensor(D3D12BufferRegion buffer) {
    AssignOutput(0, buffer);
  }
};

template<> struct DmlOperator<DML_OPERATOR_MAX_POOLING1> :
  public DmlOperatorBase,
  public HashableOperator<DML_OPERATOR_MAX_POOLING1>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_MAX_POOLING1>& op_desc) :
    DmlOperatorBase(backend, DML_OPERATOR_DESC {DML_OPERATOR_MAX_POOLING1, &op_desc}, 1, 2)
  {}

  auto InputTensor(D3D12BufferRegion buffer) {
    AssignInput(0, buffer);
  }
  auto OutputTensor(D3D12BufferRegion buffer) {
    AssignOutput(0, buffer);
  }
  auto OutputIndicesTensor(D3D12BufferRegion buffer) {
    AssignOutput(1, buffer);
  }
};

template <> struct DmlOperator<DML_OPERATOR_GEMM> :
  public DmlOperatorBase,
  public HashableOperator<DML_OPERATOR_GEMM>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_GEMM>& op_desc) :
    DmlOperatorBase(backend, DML_OPERATOR_DESC {DML_OPERATOR_GEMM, &op_desc}, 3, 1)
  {}

  auto ATensor(D3D12BufferRegion buffer) {
    AssignInput(0, buffer);
  }

  auto BTensor(D3D12BufferRegion buffer) {
    AssignInput(1, buffer);
  }

  auto CTensor(D3D12BufferRegion buffer) {
    AssignInput(2, buffer);
  }

  auto OutputTensor(D3D12BufferRegion buffer) {
    AssignOutput(0, buffer);
  }
};

template <> struct DmlOperator<DML_OPERATOR_CONVOLUTION> :
  public DmlOperatorBase,
  public HashableOperator<DML_OPERATOR_CONVOLUTION>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_CONVOLUTION>& op_desc) :
    DmlOperatorBase(backend, DML_OPERATOR_DESC {DML_OPERATOR_CONVOLUTION, &op_desc}, 3, 1)
  {}

  auto InputTensor(D3D12BufferRegion buffer) {
    AssignInput(0, buffer);
  }

  auto FilterTensor(D3D12BufferRegion buffer) {
    AssignInput(1, buffer);
  }

  auto BiasTensor(D3D12BufferRegion buffer) {
    AssignInput(2, buffer);
  }

  auto OutputTensor(D3D12BufferRegion buffer) {
    AssignOutput(0, buffer);
  }
};

template <> struct DmlOperator<DML_OPERATOR_ACTIVATION_THRESHOLDED_RELU> :
  public DmlOperatorBase,
  public HashableOperator<DML_OPERATOR_ACTIVATION_THRESHOLDED_RELU>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_ACTIVATION_THRESHOLDED_RELU>& op_desc) :
    DmlOperatorBase(backend, DML_OPERATOR_DESC{DML_OPERATOR_ACTIVATION_THRESHOLDED_RELU,&op_desc}, 1,1)
  {}

  auto InputTensor(D3D12BufferRegion buffer) {
    AssignInput(0, buffer);
  }

  auto OutputTensor(D3D12BufferRegion buffer) {
    AssignOutput(0, buffer);
  }
};

template <> struct DmlOperator<DML_OPERATOR_JOIN> :
  public DmlOperatorBase,
  public HashableOperator<DML_OPERATOR_JOIN>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_JOIN>& op_desc) :
    DmlOperatorBase(backend, DML_OPERATOR_DESC{DML_OPERATOR_JOIN,&op_desc}, op_desc.InputCount, 1)
  {}

  auto InputTensorAtIndex(size_t index, D3D12BufferRegion buffer) {
    AssignInput(index, buffer);
  }

  auto OutputTensor(D3D12BufferRegion buffer) {
    AssignOutput(0, buffer);
  }
};

template <> struct DmlOperator<DML_OPERATOR_MAX_POOLING_GRAD> :
  public DmlOperatorBase,
  public HashableOperator<DML_OPERATOR_MAX_POOLING_GRAD>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_MAX_POOLING_GRAD>& op_desc) :
    DmlOperatorBase(backend, DML_OPERATOR_DESC{DML_OPERATOR_MAX_POOLING_GRAD,&op_desc}, 2, 1)
  {}

  auto InputTensor(D3D12BufferRegion buffer) {
    AssignInput(0, buffer);
  }

  auto InputGradientTensor(D3D12BufferRegion buffer) {
    AssignInput(1, buffer);
  }

  auto OutputGradientTensor(D3D12BufferRegion buffer) {
    AssignOutput(0, buffer);
  }
};

template <> struct DmlOperator<DML_OPERATOR_AVERAGE_POOLING_GRAD> :
  public DmlOperatorBase,
  public HashableOperator<DML_OPERATOR_AVERAGE_POOLING_GRAD>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_AVERAGE_POOLING_GRAD>& op_desc) :
    DmlOperatorBase(backend, DML_OPERATOR_DESC{DML_OPERATOR_AVERAGE_POOLING_GRAD,&op_desc}, 1, 1)
  {}

  auto InputGradientTensor(D3D12BufferRegion buffer) {
    AssignInput(0, buffer);
  }

  auto OutputGradientTensor(D3D12BufferRegion buffer) {
    AssignOutput(0, buffer);
  }
};

template <> struct DmlOperator<DML_OPERATOR_NONZERO_COORDINATES> :
  public DmlOperatorBase,
  public HashableOperator<DML_OPERATOR_NONZERO_COORDINATES>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_NONZERO_COORDINATES>& op_desc) :
    DmlOperatorBase(backend, DML_OPERATOR_DESC{DML_OPERATOR_NONZERO_COORDINATES,&op_desc}, 1, 2)
  {}

  auto InputTensor(D3D12BufferRegion buffer) {
    AssignInput(0, buffer);
  }

  auto OutputCountTensor(D3D12BufferRegion buffer) {
    AssignOutput(0, buffer);
  }

  auto OutputCoordinatesTensor(D3D12BufferRegion buffer) {
    AssignOutput(1, buffer);
  }
};

template <> struct DmlOperator<DML_OPERATOR_TOP_K1> :
  public DmlOperatorBase,
  public HashableOperator<DML_OPERATOR_TOP_K1>
{
  DmlOperator(DmlBackend* backend, const DML_OP_DESC<DML_OPERATOR_TOP_K1>& op_desc) :
    DmlOperatorBase(backend, DML_OPERATOR_DESC{DML_OPERATOR_TOP_K1,&op_desc}, 1, 2)
  {}

  auto InputTensor(D3D12BufferRegion buffer) {
    AssignInput(0, buffer);
  }

  auto OutputValueTensor(D3D12BufferRegion buffer) {
    AssignOutput(0, buffer);
  }

  auto OutputIndexTensor(D3D12BufferRegion buffer) {
    AssignOutput(1, buffer);
  }
};
}  // namespace dml