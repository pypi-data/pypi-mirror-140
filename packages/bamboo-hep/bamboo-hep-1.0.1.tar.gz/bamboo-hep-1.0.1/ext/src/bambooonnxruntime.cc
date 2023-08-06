#include "bambooonnxruntime.h"

#include <iostream>
#include <cstring>
#include <numeric>

Ort::Env& bamboo::ONNXRuntimeEvaluator::env() {
  static Ort::Env env{ORT_LOGGING_LEVEL_WARNING, "bamboo"};
  return env;
}

namespace {
  Ort::SessionOptions getSessionOptions() {
    Ort::SessionOptions session_options;
    session_options.SetIntraOpNumThreads(1);
    session_options.SetGraphOptimizationLevel(GraphOptimizationLevel::ORT_ENABLE_EXTENDED); // -O2
    return session_options;
  }
}

bamboo::ONNXRuntimeEvaluator::ONNXRuntimeEvaluator(const std::string& modelFile, const std::vector<const char*> outNodeNames)
  : m_sessionOptions(getSessionOptions())
  , m_session{env(), modelFile.c_str(), m_sessionOptions}
  , m_allocator{}
  , m_memoryInfo{Ort::MemoryInfo::CreateCpu(OrtArenaAllocator, OrtMemTypeDefault)}
  , m_inputNames{}
  , m_outNames(outNodeNames)
{
  const auto num_input_nodes = m_session.GetInputCount();
  //std::cout << "Found " << num_input_nodes << " input nodes" << std::endl;
  for ( std::size_t i{0}; i != num_input_nodes; ++i ) {
    //std::cout << " - " << m_session.GetInputName(i, m_allocator) << std::endl;
    m_inputNames.push_back(m_session.GetInputName(i, m_allocator));
    Ort::TypeInfo type_info = m_session.GetInputTypeInfo(i);
    auto shape_info = type_info.GetTensorTypeAndShapeInfo();
    auto shape = shape_info.GetShape();
    if ( shape[0] == -1 ) {
      shape[0] = 1;
    }
    const auto totSize = std::accumulate(std::begin(shape), std::end(shape), 1L,
        [] ( long n, int64_t dim ) { return n*dim; });
    m_inputInfo.emplace_back(std::move(shape), totSize, shape_info.GetElementType());
  }
  //const auto num_output_nodes = m_session.GetOutputCount();
  //std::cout << "Found " << num_output_nodes << " output nodes" << std::endl;
  //for ( std::size_t i{0}; i != num_output_nodes; ++i ) {
  //  std::cout << " - " << m_session.GetOutputName(i, m_allocator) << std::endl;
  //}
}

bamboo::ONNXRuntimeEvaluator::output_t bamboo::ONNXRuntimeEvaluator::evaluate_tensors(InputTensors& inputValues) {
  auto output_tensors = m_session.Run(Ort::RunOptions{nullptr}, m_inputNames.data(), inputValues.data(), inputValues.size(), m_outNames.data(), m_outNames.size());
  output_t out_cat{};
  const auto totElements = std::accumulate(std::begin(output_tensors), std::end(output_tensors),
      std::size_t(0), [] (std::size_t n, const Ort::Value& tensor) { return n+tensor.GetTensorTypeAndShapeInfo().GetElementCount(); });
  out_cat.reserve(totElements);
  for ( auto& tensor : output_tensors ) {
    std::copy(tensor.GetTensorData<float>(), tensor.GetTensorData<float>()+tensor.GetTensorTypeAndShapeInfo().GetElementCount(), std::back_inserter(out_cat));
  }
  return out_cat;
}
