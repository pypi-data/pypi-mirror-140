import panphon.distance

import fed


panphon_dst = panphon.distance.Distance()


class WeightedFeatureEditDistance(object):

    def __init__(self):
        self.cached_word = {}

    def __call__(self, source, target):
        if source not in self.cached_word:
            source_vec = panphon_dst.fm.word_to_vector_list(
                source, numeric=True, xsampa=False)
            self.cached_word[source] = source_vec
        if target not in self.cached_word:
            target_vec = panphon_dst.fm.word_to_vector_list(
                target, numeric=True, xsampa=False)
            self.cached_word[target] = target_vec
        return fed.weighted_feature_edit_distance(
            self.cached_word[source],
            self.cached_word[target],
            panphon_dst.fm.weights)
