#pragma once

#include "DirectML.h"

//#define DEBUG_STRINGS

namespace dml {

inline constexpr const char * operator"" _debugonly (const char * str, std::size_t )
{
#ifdef DEBUG_STRINGS
    return str;
#else
    return nullptr;
#endif
}

template <DML_OPERATOR_TYPE TType> struct DmlOperatorTraits;

template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_IDENTITY> { using T = DML_ELEMENT_WISE_IDENTITY_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_IDENTITY"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_ABS> { using T = DML_ELEMENT_WISE_ABS_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_ABS"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_ACOS> { using T = DML_ELEMENT_WISE_ACOS_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_ACOS"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_ADD> { using T = DML_ELEMENT_WISE_ADD_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_ADD"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_ASIN> { using T = DML_ELEMENT_WISE_ASIN_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_ASIN"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_ATAN> { using T = DML_ELEMENT_WISE_ATAN_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_ATAN"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_CEIL> { using T = DML_ELEMENT_WISE_CEIL_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_CEIL"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_CLIP> { using T = DML_ELEMENT_WISE_CLIP_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_CLIP"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_COS> { using T = DML_ELEMENT_WISE_COS_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_COS"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_DIVIDE> { using T = DML_ELEMENT_WISE_DIVIDE_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_DIVIDE"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_EXP> { using T = DML_ELEMENT_WISE_EXP_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_EXP"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_FLOOR> { using T = DML_ELEMENT_WISE_FLOOR_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_FLOOR"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_LOG> { using T = DML_ELEMENT_WISE_LOG_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_LOG"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_LOGICAL_AND> { using T = DML_ELEMENT_WISE_LOGICAL_AND_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_LOGICAL_AND"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_LOGICAL_EQUALS> { using T = DML_ELEMENT_WISE_LOGICAL_EQUALS_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_LOGICAL_EQUALS"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_LOGICAL_GREATER_THAN> { using T = DML_ELEMENT_WISE_LOGICAL_GREATER_THAN_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_LOGICAL_GREATER_THAN"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_LOGICAL_LESS_THAN> { using T = DML_ELEMENT_WISE_LOGICAL_LESS_THAN_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_LOGICAL_LESS_THAN"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_LOGICAL_NOT> { using T = DML_ELEMENT_WISE_LOGICAL_NOT_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_LOGICAL_NOT"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_LOGICAL_OR> { using T = DML_ELEMENT_WISE_LOGICAL_OR_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_LOGICAL_OR"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_LOGICAL_XOR> { using T = DML_ELEMENT_WISE_LOGICAL_XOR_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_LOGICAL_XOR"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_MAX> { using T = DML_ELEMENT_WISE_MAX_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_MAX"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_MEAN> { using T = DML_ELEMENT_WISE_MEAN_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_MEAN"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_MIN> { using T = DML_ELEMENT_WISE_MIN_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_MIN"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_MULTIPLY> { using T = DML_ELEMENT_WISE_MULTIPLY_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_MULTIPLY"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_POW> { using T = DML_ELEMENT_WISE_POW_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_POW"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_CONSTANT_POW> { using T = DML_ELEMENT_WISE_CONSTANT_POW_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_CONSTANT_POW"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_RECIP> { using T = DML_ELEMENT_WISE_RECIP_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_RECIP"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_SIN> { using T = DML_ELEMENT_WISE_SIN_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_SIN"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_SQRT> { using T = DML_ELEMENT_WISE_SQRT_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_SQRT"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_SUBTRACT> { using T = DML_ELEMENT_WISE_SUBTRACT_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_SUBTRACT"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_TAN> { using T = DML_ELEMENT_WISE_TAN_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_TAN"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_THRESHOLD> { using T = DML_ELEMENT_WISE_THRESHOLD_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_THRESHOLD"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_QUANTIZE_LINEAR> { using T = DML_ELEMENT_WISE_QUANTIZE_LINEAR_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_QUANTIZE_LINEAR"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_DEQUANTIZE_LINEAR> { using T = DML_ELEMENT_WISE_DEQUANTIZE_LINEAR_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_DEQUANTIZE_LINEAR"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ACTIVATION_ELU> { using T = DML_ACTIVATION_ELU_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ACTIVATION_ELU"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ACTIVATION_HARDMAX> { using T = DML_ACTIVATION_HARDMAX_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ACTIVATION_HARDMAX"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ACTIVATION_HARD_SIGMOID> { using T = DML_ACTIVATION_HARD_SIGMOID_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ACTIVATION_HARD_SIGMOID"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ACTIVATION_IDENTITY> { using T = DML_ACTIVATION_IDENTITY_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ACTIVATION_IDENTITY"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ACTIVATION_LEAKY_RELU> { using T = DML_ACTIVATION_LEAKY_RELU_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ACTIVATION_LEAKY_RELU"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ACTIVATION_LINEAR> { using T = DML_ACTIVATION_LINEAR_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ACTIVATION_LINEAR"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ACTIVATION_LOG_SOFTMAX> { using T = DML_ACTIVATION_LOG_SOFTMAX_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ACTIVATION_LOG_SOFTMAX"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ACTIVATION_PARAMETERIZED_RELU> { using T = DML_ACTIVATION_PARAMETERIZED_RELU_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ACTIVATION_PARAMETERIZED_RELU"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ACTIVATION_PARAMETRIC_SOFTPLUS> { using T = DML_ACTIVATION_PARAMETRIC_SOFTPLUS_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ACTIVATION_PARAMETRIC_SOFTPLUS"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ACTIVATION_RELU> { using T = DML_ACTIVATION_RELU_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ACTIVATION_RELU"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ACTIVATION_SCALED_ELU> { using T = DML_ACTIVATION_SCALED_ELU_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ACTIVATION_SCALED_ELU"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ACTIVATION_SCALED_TANH> { using T = DML_ACTIVATION_SCALED_TANH_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ACTIVATION_SCALED_TANH"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ACTIVATION_SIGMOID> { using T = DML_ACTIVATION_SIGMOID_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ACTIVATION_SIGMOID"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ACTIVATION_SOFTMAX> { using T = DML_ACTIVATION_SOFTMAX_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ACTIVATION_SOFTMAX"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ACTIVATION_SOFTPLUS> { using T = DML_ACTIVATION_SOFTPLUS_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ACTIVATION_SOFTPLUS"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ACTIVATION_SOFTSIGN> { using T = DML_ACTIVATION_SOFTSIGN_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ACTIVATION_SOFTSIGN"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ACTIVATION_TANH> { using T = DML_ACTIVATION_TANH_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ACTIVATION_TANH"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ACTIVATION_THRESHOLDED_RELU> { using T = DML_ACTIVATION_THRESHOLDED_RELU_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ACTIVATION_THRESHOLDED_RELU"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_CONVOLUTION> { using T = DML_CONVOLUTION_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_CONVOLUTION"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_GEMM> { using T = DML_GEMM_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_GEMM"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_REDUCE> { using T = DML_REDUCE_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_REDUCE"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_AVERAGE_POOLING> { using T = DML_AVERAGE_POOLING_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_AVERAGE_POOLING"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_LP_POOLING> { using T = DML_LP_POOLING_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_LP_POOLING"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_MAX_POOLING> { using T = DML_MAX_POOLING_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_MAX_POOLING"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ROI_POOLING> { using T = DML_ROI_POOLING_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ROI_POOLING"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_SLICE> { using T = DML_SLICE_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_SLICE"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_CAST> { using T = DML_CAST_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_CAST"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_SPLIT> { using T = DML_SPLIT_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_SPLIT"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_JOIN> { using T = DML_JOIN_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_JOIN"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_PADDING> { using T = DML_PADDING_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_PADDING"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_VALUE_SCALE_2D> { using T = DML_VALUE_SCALE_2D_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_VALUE_SCALE_2D"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_UPSAMPLE_2D> { using T = DML_UPSAMPLE_2D_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_UPSAMPLE_2D"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_GATHER> { using T = DML_GATHER_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_GATHER"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_SPACE_TO_DEPTH> { using T = DML_SPACE_TO_DEPTH_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_SPACE_TO_DEPTH"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_DEPTH_TO_SPACE> { using T = DML_DEPTH_TO_SPACE_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_DEPTH_TO_SPACE"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_TILE> { using T = DML_TILE_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_TILE"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_TOP_K> { using T = DML_TOP_K_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_TOP_K"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_BATCH_NORMALIZATION> { using T = DML_BATCH_NORMALIZATION_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_BATCH_NORMALIZATION"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_MEAN_VARIANCE_NORMALIZATION> { using T = DML_MEAN_VARIANCE_NORMALIZATION_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_MEAN_VARIANCE_NORMALIZATION"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_LOCAL_RESPONSE_NORMALIZATION> { using T = DML_LOCAL_RESPONSE_NORMALIZATION_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_LOCAL_RESPONSE_NORMALIZATION"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_LP_NORMALIZATION> { using T = DML_LP_NORMALIZATION_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_LP_NORMALIZATION"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_RNN> { using T = DML_RNN_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_RNN"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_LSTM> { using T = DML_LSTM_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_LSTM"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_GRU> { using T = DML_GRU_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_GRU"_debugonly; };

#if DML_TARGET_VERSION >= 0x2000
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_SIGN> { using T = DML_ELEMENT_WISE_SIGN_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_SIGN"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_IS_NAN> { using T = DML_ELEMENT_WISE_IS_NAN_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_IS_NAN"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_ERF> { using T = DML_ELEMENT_WISE_ERF_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_ERF"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_SINH> { using T = DML_ELEMENT_WISE_SINH_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_SINH"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_COSH> { using T = DML_ELEMENT_WISE_COSH_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_COSH"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_TANH> { using T = DML_ELEMENT_WISE_TANH_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_TANH"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_ASINH> { using T = DML_ELEMENT_WISE_ASINH_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_ASINH"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_ACOSH> { using T = DML_ELEMENT_WISE_ACOSH_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_ACOSH"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_ATANH> { using T = DML_ELEMENT_WISE_ATANH_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_ATANH"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_IF> { using T = DML_ELEMENT_WISE_IF_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_IF"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_ADD1> { using T = DML_ELEMENT_WISE_ADD1_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_ADD1"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ACTIVATION_SHRINK> { using T = DML_ACTIVATION_SHRINK_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ACTIVATION_SHRINK"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_MAX_POOLING1> { using T = DML_MAX_POOLING1_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_MAX_POOLING1"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_MAX_UNPOOLING> { using T = DML_MAX_UNPOOLING_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_MAX_UNPOOLING"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_DIAGONAL_MATRIX> { using T = DML_DIAGONAL_MATRIX_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_DIAGONAL_MATRIX"_debugonly; };
//template <> struct DmlOperatorTraits<DML_OPERATOR_SCATTER_ELEMENTS> { using T = DML_SCATTER_ELEMENTS_OPERATOR_DESC; static constexpr const char * const Name = "DmlOperatorTraits"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_SCATTER> { using T = DML_SCATTER_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_SCATTER"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ONE_HOT> { using T = DML_ONE_HOT_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ONE_HOT"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_RESAMPLE> { using T = DML_RESAMPLE_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_RESAMPLE"_debugonly; };
#endif // DML_TARGET_VERSION >= 0x2000

#if DML_TARGET_VERSION >= 0x2100
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_BIT_SHIFT_LEFT> { using T = DML_ELEMENT_WISE_BIT_SHIFT_LEFT_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_BIT_SHIFT_LEFT"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_BIT_SHIFT_RIGHT> { using T = DML_ELEMENT_WISE_BIT_SHIFT_RIGHT_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_BIT_SHIFT_RIGHT"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_ROUND> { using T = DML_ELEMENT_WISE_ROUND_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_ROUND"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_IS_INFINITY> { using T = DML_ELEMENT_WISE_IS_INFINITY_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_IS_INFINITY"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_MODULUS_TRUNCATE> { using T = DML_ELEMENT_WISE_MODULUS_TRUNCATE_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_MODULUS_TRUNCATE"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_MODULUS_FLOOR> { using T = DML_ELEMENT_WISE_MODULUS_FLOOR_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_MODULUS_FLOOR"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_FILL_VALUE_CONSTANT> { using T = DML_FILL_VALUE_CONSTANT_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_FILL_VALUE_CONSTANT"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_FILL_VALUE_SEQUENCE> { using T = DML_FILL_VALUE_SEQUENCE_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_FILL_VALUE_SEQUENCE"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_CUMULATIVE_SUMMATION> { using T = DML_CUMULATIVE_SUMMATION_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_CUMULATIVE_SUMMATION"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_REVERSE_SUBSEQUENCES> { using T = DML_REVERSE_SUBSEQUENCES_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_REVERSE_SUBSEQUENCES"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_GATHER_ELEMENTS> { using T = DML_GATHER_ELEMENTS_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_GATHER_ELEMENTS"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_GATHER_ND> { using T = DML_GATHER_ND_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_GATHER_ND"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_SCATTER_ND> { using T = DML_SCATTER_ND_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_SCATTER_ND"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_MAX_POOLING2> { using T = DML_MAX_POOLING2_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_MAX_POOLING2"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_SLICE1> { using T = DML_SLICE1_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_SLICE1"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_TOP_K1> { using T = DML_TOP_K1_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_TOP_K1"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_DEPTH_TO_SPACE1> { using T = DML_DEPTH_TO_SPACE1_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_DEPTH_TO_SPACE1"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_SPACE_TO_DEPTH1> { using T = DML_SPACE_TO_DEPTH1_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_SPACE_TO_DEPTH1"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_MEAN_VARIANCE_NORMALIZATION1> { using T = DML_MEAN_VARIANCE_NORMALIZATION1_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_MEAN_VARIANCE_NORMALIZATION1"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_RESAMPLE1> { using T = DML_RESAMPLE1_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_RESAMPLE1"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_MATRIX_MULTIPLY_INTEGER> { using T = DML_MATRIX_MULTIPLY_INTEGER_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_MATRIX_MULTIPLY_INTEGER"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_QUANTIZED_LINEAR_MATRIX_MULTIPLY> { using T = DML_QUANTIZED_LINEAR_MATRIX_MULTIPLY_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_QUANTIZED_LINEAR_MATRIX_MULTIPLY"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_CONVOLUTION_INTEGER> { using T = DML_CONVOLUTION_INTEGER_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_CONVOLUTION_INTEGER"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_QUANTIZED_LINEAR_CONVOLUTION> { using T = DML_QUANTIZED_LINEAR_CONVOLUTION_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_QUANTIZED_LINEAR_CONVOLUTION"_debugonly; };
#endif // DML_TARGET_VERSION >= 0x2100

#if DML_TARGET_VERSION >= 0x3000
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_BIT_AND> { using T = DML_ELEMENT_WISE_BIT_AND_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_BIT_AND"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_BIT_OR> { using T = DML_ELEMENT_WISE_BIT_OR_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_BIT_OR"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_BIT_XOR> { using T = DML_ELEMENT_WISE_BIT_XOR_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_BIT_XOR"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_BIT_NOT> { using T = DML_ELEMENT_WISE_BIT_NOT_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_BIT_NOT"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_BIT_COUNT> { using T = DML_ELEMENT_WISE_BIT_COUNT_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_BIT_COUNT"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_LOGICAL_GREATER_THAN_OR_EQUAL> { using T = DML_ELEMENT_WISE_LOGICAL_GREATER_THAN_OR_EQUAL_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_LOGICAL_GREATER_THAN_OR_EQUAL"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_LOGICAL_LESS_THAN_OR_EQUAL> { using T = DML_ELEMENT_WISE_LOGICAL_LESS_THAN_OR_EQUAL_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_LOGICAL_LESS_THAN_OR_EQUAL"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ACTIVATION_CELU> { using T = DML_ACTIVATION_CELU_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ACTIVATION_CELU"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ACTIVATION_RELU_GRAD> { using T = DML_ACTIVATION_RELU_GRAD_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ACTIVATION_RELU_GRAD"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_AVERAGE_POOLING_GRAD> { using T = DML_AVERAGE_POOLING_GRAD_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_AVERAGE_POOLING_GRAD"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_MAX_POOLING_GRAD> { using T = DML_MAX_POOLING_GRAD_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_MAX_POOLING_GRAD"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_RANDOM_GENERATOR> { using T = DML_RANDOM_GENERATOR_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_RANDOM_GENERATOR"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_NONZERO_COORDINATES> { using T = DML_NONZERO_COORDINATES_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_NONZERO_COORDINATES"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_RESAMPLE_GRAD> { using T = DML_RESAMPLE_GRAD_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_RESAMPLE_GRAD"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_SLICE_GRAD> { using T = DML_SLICE_GRAD_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_SLICE_GRAD"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ADAM_OPTIMIZER> { using T = DML_ADAM_OPTIMIZER_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ADAM_OPTIMIZER"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ARGMIN> { using T = DML_ARGMIN_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ARGMIN"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ARGMAX> { using T = DML_ARGMAX_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ARGMAX"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ROI_ALIGN> { using T = DML_ROI_ALIGN_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ROI_ALIGN"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_GATHER_ND1> { using T = DML_GATHER_ND1_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_GATHER_ND1"_debugonly; };
#endif // DML_TARGET_VERSION >= 0x3000

#if DML_TARGET_VERSION >= 0x3100
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_ATAN_YX> { using T = DML_ELEMENT_WISE_ATAN_YX_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_ATAN_YX"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_CLIP_GRAD> { using T = DML_ELEMENT_WISE_CLIP_GRAD_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_CLIP_GRAD"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_DIFFERENCE_SQUARE> { using T = DML_ELEMENT_WISE_DIFFERENCE_SQUARE_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_DIFFERENCE_SQUARE"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_LOCAL_RESPONSE_NORMALIZATION_GRAD> { using T = DML_LOCAL_RESPONSE_NORMALIZATION_GRAD_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_LOCAL_RESPONSE_NORMALIZATION_GRAD"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_CUMULATIVE_PRODUCT> { using T = DML_CUMULATIVE_PRODUCT_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_CUMULATIVE_PRODUCT"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_BATCH_NORMALIZATION_GRAD> { using T = DML_BATCH_NORMALIZATION_GRAD_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_BATCH_NORMALIZATION_GRAD"_debugonly; };
#endif // DML_TARGET_VERSION >= 0x3100

#if DML_TARGET_VERSION >= 0x4000
template <> struct DmlOperatorTraits<DML_OPERATOR_ELEMENT_WISE_QUANTIZED_LINEAR_ADD> { using T = DML_ELEMENT_WISE_QUANTIZED_LINEAR_ADD_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ELEMENT_WISE_QUANTIZED_LINEAR_ADD"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_DYNAMIC_QUANTIZE_LINEAR> { using T = DML_DYNAMIC_QUANTIZE_LINEAR_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_DYNAMIC_QUANTIZE_LINEAR"_debugonly; };
template <> struct DmlOperatorTraits<DML_OPERATOR_ROI_ALIGN1> { using T = DML_ROI_ALIGN1_OPERATOR_DESC; static constexpr const char * const Name = "DML_OPERATOR_ROI_ALIGN1"_debugonly; };
#endif // DML_TARGET_VERSION >= 0x4000


template <DML_OPERATOR_TYPE TType>
using DML_OP_DESC = typename DmlOperatorTraits<TType>::T;

}
