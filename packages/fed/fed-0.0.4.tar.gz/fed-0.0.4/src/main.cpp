#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <numeric>


double weighted_substitution_cost(std::vector<int> v1,
                                  std::vector<int> v2,
                                  std::vector<double> weights,
                                  double gl_wt=1.0) {
  double ret = 0.0;
  for (size_t i = 0; i < v1.size(); ++i) {
    ret += std::abs(v1[i] - v2[i]) / 2.0 * weights[i];
  }
  return ret * gl_wt;
}


double weighted_feature_edit_distance(const std::vector<std::vector<int>> source,
                             const std::vector<std::vector<int> > target,
                             const std::vector<double> weights) {
  // Get lengths of source and target
  const int n = source.size();
  const int m = target.size();
  const double deletion_cost = std::accumulate(weights.begin(), weights.end(), 0.0);
  const double insertion_cost = deletion_cost;

  // Create "matrix"
  std::vector< std::vector<double> > d(n + 1, std::vector<double>(m + 1));
  d[0][0] = 0.0;
  for (size_t i = 1; i < n + 1; ++i) {
    d[i][0] = d[i - 1][0] + deletion_cost;
  }
  for (size_t j = 1; j < m + 1; ++j) {
    d[0][j] = d[0][j - 1] + insertion_cost;
  }
  // Recurrence relation
  for (size_t i = 1; i < n + 1; ++i) {
    for (size_t j = 1; j < m + 1; ++j) {
      d[i][j] = std::min(std::min(
                                  d[i - 1][j] + deletion_cost,
                                  d[i - 1][j - 1] + weighted_substitution_cost(source[i - 1], target[j - 1], weights)),
                         d[i][j - 1] + insertion_cost);
    }
  }
  return d[n][m];
}


double edit_distance(const std::string str1,
                              const std::string str2,
                              const std::vector<double> weights) {
  const int size1 = str1.size();
  const int size2 = str2.size();
  std::vector< std::vector<double> > d(2, std::vector<double>(size2 + 1));
  d[0][0] = 0;
  d[1][0] = 1;
  for (int i = 0; i < size2 + 1; i++) d[0][i] = i;
  for (int i = 1; i < size1 + 1; i++) {
    for (int j = 1; j < size2 + 1; j++) {
      d[i&1][j] = std::min(std::min(d[(i-1)&1][j], d[i&1][j-1]) + 1,
                           d[(i-1)&1][j-1] + (str1[i-1] == str2[j-1] ? 0 : 1));
    }
  }
  return d[size1&1][size2];
}

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
    m.doc() = R"pbdoc(
        EditDistance Library
        --------------------

        .. currentmodule:: editdistance

        .. autosummary::
           :toctree: _generate

           edit_distance
           weighted_feature_edit_distance
    )pbdoc";


    m.def("edit_distance", &edit_distance, R"pbdoc(
        Calculate edit distance.
    )pbdoc");

    m.def("weighted_feature_edit_distance", &weighted_feature_edit_distance, R"pbdoc(
        Calculate edit distance for feature vector.
    )pbdoc");
}
