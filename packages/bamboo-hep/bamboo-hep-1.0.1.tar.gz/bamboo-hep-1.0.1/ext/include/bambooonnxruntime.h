#pragma once

#include <string>
#include <vector>

#include "onnxruntime_cxx_api.h"

namespace bamboo {
class ONNXRuntimeEvaluator {
public:
  using output_t = std::vector<float>;

  static Ort::Env& env();

  explicit ONNXRuntimeEvaluator(const std::string& modelFile, const std::vector<const char*> outNodeNames);

  template<class... Types>
  output_t evaluate(Types&&... inputsPerNode) {
    InputTensors inputValues;
    inputValues.reserve(m_inputInfo.size());
    inputValues.load(m_memoryInfo, m_inputInfo, std::forward<Types>(inputsPerNode)...);
    if ( inputValues.size() != m_inputInfo.size() ) {
      throw std::runtime_error("Not enough inputs, model has "+std::to_string(m_inputInfo.size())+" but passed only "+std::to_string(inputValues.size()));
    }
    return evaluate_tensors(inputValues);
  }
private:
  Ort::SessionOptions m_sessionOptions;
  Ort::Session m_session;
  Ort::AllocatorWithDefaultOptions m_allocator;
  const OrtMemoryInfo* m_memoryInfo;

  struct InputTensorInfo {
    std::vector<int64_t> shape;
    std::size_t size;
    ONNXTensorElementDataType dataType;
    InputTensorInfo(std::vector<int64_t>&& shape_, std::size_t size_, ONNXTensorElementDataType dataType_)
      : shape(std::move(shape_)), size(size_), dataType(dataType_) {}
  };
  std::vector<InputTensorInfo> m_inputInfo;
  std::vector<const char*> m_inputNames, m_outNames;


  class InputTensors {
  public:
    void reserve(std::size_t n) { m_tensors.reserve(n); }
    Ort::Value const* data() const { return m_tensors.data(); }
    std::size_t size() const { return m_tensors.size(); }
  private:
    std::vector<Ort::Value> m_tensors;
  public:
    template<typename NodeInputs, typename ...NextInputs>
    void load(const OrtMemoryInfo* memoryInfo, const std::vector<InputTensorInfo>& inputInfo, NodeInputs&& nodeInputs, NextInputs&&... nextInputs) {
      load(memoryInfo, inputInfo, std::forward<NodeInputs>(nodeInputs));
      load(memoryInfo, inputInfo, std::forward<NextInputs>(nextInputs)...);
    }
    template<typename NodeInputs>
    void load(const OrtMemoryInfo* memoryInfo, const std::vector<InputTensorInfo>& inputsInfo, NodeInputs&& nodeInputs) {
      if ( m_tensors.size() == inputsInfo.size() ) {
        throw std::runtime_error("Too many inputs, model has only "+std::to_string(inputsInfo.size()));
      }
      const auto& inputInfo = inputsInfo[m_tensors.size()];
      if ( inputInfo.size != nodeInputs.size() ) {
        throw std::runtime_error("Incorrect number of inputs for node "+
            std::to_string(m_tensors.size())+
            " : expected "+std::to_string(inputInfo.size)+
            " values, but received "+std::to_string(nodeInputs.size()));
      }
      using element_type = typename std::remove_reference<decltype(nodeInputs)>::type::value_type;
      bool type_ok = false;
      switch(inputInfo.dataType) {
        case ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT:
          type_ok = std::is_same<element_type,float>::value;
          break;
        case ONNX_TENSOR_ELEMENT_DATA_TYPE_UINT8:
          type_ok = std::is_same<element_type,std::uint8_t>::value;
          break;
        case ONNX_TENSOR_ELEMENT_DATA_TYPE_INT8:
          type_ok = std::is_same<element_type,std::int8_t>::value;
          break;
        case ONNX_TENSOR_ELEMENT_DATA_TYPE_UINT16:
          type_ok = std::is_same<element_type,std::uint16_t>::value;
          break;
        case ONNX_TENSOR_ELEMENT_DATA_TYPE_INT16:
          type_ok = std::is_same<element_type,std::int16_t>::value;
          break;
        case ONNX_TENSOR_ELEMENT_DATA_TYPE_INT32:
          type_ok = std::is_same<element_type,std::int32_t>::value;
          break;
        case ONNX_TENSOR_ELEMENT_DATA_TYPE_INT64:
          type_ok = std::is_same<element_type,std::int64_t>::value;
          break;
        case ONNX_TENSOR_ELEMENT_DATA_TYPE_STRING:
          type_ok = std::is_same<element_type,std::string>::value;
          break;
        case ONNX_TENSOR_ELEMENT_DATA_TYPE_BOOL:
          type_ok = std::is_same<element_type,bool>::value;
          break;
        // no float16
        case ONNX_TENSOR_ELEMENT_DATA_TYPE_DOUBLE:
          type_ok = std::is_same<element_type,double>::value;
          break;
        case ONNX_TENSOR_ELEMENT_DATA_TYPE_UINT32:
          type_ok = std::is_same<element_type,std::uint32_t>::value;
          break;
        case ONNX_TENSOR_ELEMENT_DATA_TYPE_UINT64:
          type_ok = std::is_same<element_type,std::uint64_t>::value;
          break;
        // skipped complex and bfloat16
        default:
          break;
      }
      if ( ! type_ok ) {
        std::runtime_error{"Unsupported type or type mismatch for input "+std::to_string(m_tensors.size())};
      }
      m_tensors.push_back(Ort::Value::CreateTensor(memoryInfo,
          const_cast<element_type*>(nodeInputs.data()), nodeInputs.size()*sizeof(element_type),
          inputInfo.shape.data(), inputInfo.shape.size(), inputInfo.dataType));
    }
  };

  output_t evaluate_tensors(InputTensors& inputValues);
};
}
