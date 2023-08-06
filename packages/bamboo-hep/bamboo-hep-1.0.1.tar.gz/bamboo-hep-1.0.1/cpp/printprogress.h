#pragma once

#include <chrono>
#include <ctime>
#include <iostream>

namespace rdfhelpers {
class PrintProgress {
public:
  using counter_t = unsigned long long;

  explicit PrintProgress(int nThreads) : m_nThreads{nThreads} {}

  void start() {
    m_start = std::chrono::system_clock::now();
    std::cout << "RDF event loop started to process entries" << std::endl;
  }

  void update(counter_t& count) const {
    const std::chrono::duration<double> elapsed = std::chrono::system_clock::now() - m_start;
    std::cout << "Processed " << count*m_nThreads << " entries. "
              << "Elapsed: " << elapsed.count() << "s, "
              << "average rate: " << .001*count*m_nThreads/elapsed.count() << " kHz" << std::endl;
  }

  template<typename RDF>
  static std::unique_ptr<PrintProgress> addToNode(RDF df, int printFreq, int nThreads=1) {
    auto cnt = df.Count();
    auto pp = std::make_unique<PrintProgress>(nThreads);
    auto pp_p = pp.get(); // just the pointer
    cnt.OnPartialResult(0, [pp_p] (counter_t&) { pp_p->start(); });
    // the callback will be called by the slowest thread, with its partial result.
    // Therefore it should be configured with printFreq/nThreads, and count will be multiplied by nTheads.
    const auto corrFreq = int(std::round(1.*printFreq/nThreads));
    cnt.OnPartialResult(corrFreq, [pp_p] (counter_t& c) { pp_p->update(c); });
    return std::move(pp);
  }
private:
  std::chrono::time_point<std::chrono::system_clock> m_start;
  int m_nThreads;
};
};
