#pragma once

#include <ROOT/RVec.hxx>

namespace rdfhelpers {

class ModifiedPtCollection {
public:
  using compv_t = ROOT::VecOps::RVec<float>;

  ModifiedPtCollection() = default;
  ModifiedPtCollection(std::size_t n, const compv_t& pt) : m_pt(n, pt) {}

  std::size_t size() const { return m_pt.size(); }
  const compv_t& pt(std::size_t i) const { return m_pt[i]; }

  void set(std::size_t i, const compv_t& pt) { m_pt[i] = pt; }
  void set(std::size_t i, compv_t&& pt) { m_pt[i] = std::move(pt); }
private:
  std::vector<compv_t> m_pt;
};

};
