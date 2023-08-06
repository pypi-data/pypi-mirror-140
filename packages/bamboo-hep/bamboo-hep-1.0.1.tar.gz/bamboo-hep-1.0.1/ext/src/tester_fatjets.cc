#include "JMESystematicsCalculators.h"

int main() {
  std::cout << "Constructing FatJet variations calculator" << std::endl;
  FatJetVariationsCalculator mycalc{};
  std::cout << "Done" << std::endl;
  reco::FormulaEvaluator genForm{"1.0062610283313527-1.061605139842829*((x*0.07999000770091785)^-1.2045376937033758)"};
  std::cout << "genFormula: " << genForm.numberOfVariables() << std::endl;
  std::cout << "genFormula2: " << reco::FormulaEvaluator{"x*0.07999000770091785"}.numberOfVariables() << std::endl;
  std::cout << "genFormula3: " << reco::FormulaEvaluator{"(x*0.07999000770091785)^-1.2045376937033758"}.numberOfVariables() << std::endl;
  return 0;
}
