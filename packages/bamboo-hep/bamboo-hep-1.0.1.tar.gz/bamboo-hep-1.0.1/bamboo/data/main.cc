#include <iostream>
#include <filesystem>
#include <fstream>

#include <boost/program_options/cmdline.hpp>
#include <boost/program_options/options_description.hpp>
#include <boost/program_options/parsers.hpp>
#include <boost/program_options/variables_map.hpp>

#include "TChain.h"
#include "ROOT/RDataFrame.hxx"
#include "ROOT/RDFHelpers.hxx"

// BAMBOO_INSERT includes

// BAMBOO_INSERT helpermethods

class Results {
public:
  using ToSaveResult = ROOT::RDF::RResultPtr<TObject>;
  using SnapshotResult = ROOT::RDF::RResultPtr<ROOT::RDF::RInterface<ROOT::Detail::RDF::RLoopManager,void>>;

  Results() = default;

  const std::vector<ToSaveResult>& toSave() const { return m_toSave; }
  const std::vector<SnapshotResult>& snapshots() const { return m_snapshots; }
  bool empty() const { return toSave().empty() && snapshots().empty(); }
  const std::vector<ROOT::RDF::RResultHandle> results() const {
    std::vector<ROOT::RDF::RResultHandle> out;
    std::copy(std::begin(m_toSave), std::end(m_toSave), std::back_inserter(out));
    std::copy(std::begin(m_snapshots), std::end(m_snapshots), std::back_inserter(out));
    return out;
  }

  void add(ToSaveResult prod) { m_toSave.push_back(prod); }
  void add(SnapshotResult prod) { m_snapshots.push_back(prod); }
private:
  std::vector<ToSaveResult> m_toSave;
  std::vector<SnapshotResult> m_snapshots;
};

Results defineHistograms(ROOT::RDataFrame& df) {
  Results results{};

  auto snapshotOptions = ROOT::RDF::RSnapshotOptions{};
  snapshotOptions.fLazy = true;

  // BAMBOO_INSERT initialisation

  // BAMBOO_INSERT resultdefinitions

  return results;
}

int main (int argc, char* argv[]) {
  namespace fs = std::filesystem;
  namespace po = boost::program_options;

  po::options_description opt_desc("Allowed options");
  opt_desc.add_options()
      ("help", "Print this help message")
      ("output", po::value<std::string>(), "Output filename")
      ("tree", po::value<std::string>(), "Tree name")
      ("input", po::value<std::vector<std::string>>(), "Input filenames")
      ("input-files", po::value<std::string>(), "Text file with input files")
      ("threads", po::value<unsigned int>(), "Number of threads");
  po::positional_options_description pos_desc;
  pos_desc.add("input", -1);
  po::variables_map vm;
  po::store(po::command_line_parser(argc, argv).
                options(opt_desc).positional(pos_desc).run(), vm);
  po::notify(vm);
  if (vm.count("help")) {
    std::cout << opt_desc << std::endl;
    return 1;
  }
  if (!vm.count("tree")) {
    std::cout << "ERROR: A tree name must be specified" << std::endl;
    return 2;
  }
  if (!(vm.count("input") || vm.count("input-files"))) {
    std::cout << "ERROR: No input files specified, so no output will be produced" << std::endl;
    return 1;
  }
  if (!vm.count("output")) {
    std::cout << "ERROR: An output file must be specified" << std::endl;
    return 2;
  }
  const auto outputFileName = vm["output"].as<std::string>();
  if ( fs::exists(fs::path(outputFileName)) ) {
    std::cout << "ERROR: Output file " << outputFileName << " already exists" << std::endl;
    return 4;
  }

  TChain inChain(vm["tree"].as<std::string>().c_str());
  std::vector<std::string> inFiles;
  if (vm.count("input")) {
    inFiles = vm["input"].as<std::vector<std::string>>();
  }
  if (vm.count("input-files")) {
    const auto fileList = vm["input-files"].as<std::string>();
    if ( ! fs::exists(fs::path(fileList)) ) {
      std::cout << "ERROR: Input file list " << fileList << " does not exist" << std::endl;
      return 3;
    }
    std::ifstream inFileList{fileList};
    std::string ln;
    while (std::getline(inFileList, ln)) {
      inFiles.push_back(ln);
    }
  }
  for ( const auto& inFile : inFiles ) {
    if ( ! fs::exists(fs::path(inFile)) ) {
      std::cout << "ERROR: Input file " << inFile << " does not exist" << std::endl;
      return 3;
    } else {
      const auto ret = inChain.Add(inFile.c_str());
      if ( ! ret ) {
        std::cout << "ERROR: Could not add input file " << inFile << " to " << inChain.GetName() << " chain " << std::endl;
        return 3;
      } else {
        std::cout << "INFO: Added input file " << inFile << std::endl;
      }
    }
  }
  if (vm.count("threads")) {
    const auto nThreads = vm["threads"].as<unsigned int>();
    if ( nThreads > 1 ) {
      std::cout << "INFO: Enabling implicit multi-threading with " << nThreads << " threads" << std::endl;
      ROOT::EnableImplicitMT(vm["threads"].as<unsigned int>());
    }
  }

  std::cout << "INFO: Defining RDataFrame graph" << std::endl;

  ROOT::RDataFrame inDF{inChain};
  Results results{};
  try {
    results = defineHistograms(inDF);
  } catch (const std::exception& e) {
    std::cout << "ERROR: exception during definition: " << e.what();
    return 5;
  }
  if ( results.empty() ) {
    std::cout << "INFO: No results defined, exiting" << std::endl;
    return 0;
  }

  TFile* outputFile = TFile::Open(outputFileName.c_str(), "CREATE");
  if ( ! outputFile ) {
    std::cout << "ERROR: Could not create ROOT file " << outputFileName << std::endl;
  }
  std::cout << "INFO: Triggering event loop and storing outputs" << std::endl;
  ROOT::RDF::RunGraphs(results.results());
  try {
    outputFile->cd();
    for ( auto res : results.toSave() ) {
      res->Write();
    }
  } catch (const std::exception& e) {
    std::cout << "ERROR: exception during evaluation: " << e.what();
    return 6;
  }
  outputFile->Close();
  std::cout << "INFO: Done. Outputs were saved in " << outputFileName << std::endl;

  return 0;
}
