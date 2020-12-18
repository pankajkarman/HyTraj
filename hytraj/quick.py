from dipy.segment.metric import Metric, ResampleFeature
from dipy.segment.clustering import QuickBundles


class TrajDistance(Metric):
    def __init__(self):
        super(TrajDistance, self).__init__(feature=ResampleFeature(nb_points=400))

    def are_compatible(self, shape1, shape2):
        return len(shape1) == len(shape2)

    def dist(self, v1, v2):
        x = [
            geopy.distance.vincenty([p[0][0], p[0][1]], [p[1][0], p[1][1]]).km
            for p in list(zip(v1, v2))
        ]
        distance = np.mean(x)
        return distance


metric = TrajDistance()
qb = QuickBundles(threshold=1000, metric=metric)
clusters = qb.cluster(lst)
