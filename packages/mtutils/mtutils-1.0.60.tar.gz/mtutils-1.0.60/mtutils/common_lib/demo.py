from lib.dm import DMDet
import numpy as np

data_det = DMDet.load('assets/toy.json')
data_det.set_class('leaf')  # set classes of interested


for rec in data_det:
    if len(rec['instances']):
        inst = rec['instances'][0]
    else:
        inst = rec

    # get class id
    data_det.get_classid(rec)      # return a list of integers
    data_det.get_classid(inst)     # return 1 integer
    data_det.get_classid('dirt')   # return 1 integer
    data_det.get_classid(['scratch', 'grindmark'])  # return a list of integers

    # get class name
    data_det.get_classname(rec)   # return a list of strings
    data_det.get_classname(inst)  # return 1 string
    data_det.get_classname(3)     # return 1 string
    data_det.get_classname([0, 3, 1])  # return a list of strings (of class 0, 3, 1, in order)

    # get score
    data_det.get_score(rec)  # return a list of score (same length with get_classid(rec))
    data_det.get_score(inst) # return the instance score

    # get shape
    data_det.get_shape(rec)  # return a list of shapes
    data_det.get_shape(inst) # return 1 shape


data_ml = data_det.to_ml()

for rec in data_ml:
    # get class id
    data_ml.get_classid('dent')            # return 1 integer
    data_ml.get_classid(['dent', 'dent'])  # return a list of integers

    # get class name
    data_ml.get_classname(3)          # return 1 string
    data_ml.get_classname([0, 3, 1])  # return a list of strings (of class 0, 3, 1, in order)

    # get score
    data_ml.get_score(rec)    # return scores of all classes





data_mc = data_det.to_mc()

for rec in data_mc:
    # get class id
    data_mc.get_classid(rec)        # return the class id with max score
    data_mc.get_classid('scratch')  # return 1 integer
    data_mc.get_classid(['dent', 'grindmark'])  # return a list of integers

    # get class name
    data_mc.get_classname(rec)   # return the class name with max score
    data_mc.get_classname(0)     # return 1 string
    data_mc.get_classname([0, 3, 1])  # return a list of strings (of class 0, 3, 1, in order)

    # get score
    data_mc.get_score(rec)  # return the max score


data_ml2mc = data_ml.to_mc()  # ml2mc, pick the class with highest score and suppress the other classes,
                              # then and add a OK class to make the distribution sum up to one (class dict chaIBes)


data_ml2mc.set_class(['OK', 'NG'])
data_ml2mc.get_score(rec)
data_ml2mc.get_classname(rec)


data_det.create_instance('scratch', score=.7, shape=[100,20,221,35])

data_ml.create_scores('scratch', score=.3)
data_ml.create_scores(np.random.rand(len(data_ml.am.classnames)))

data_mc.create_distribution('OK', score=.3)
data_mc.create_distribution(np.random.rand(len(data_mc.am.classnames)))

data_det.save('/tmp/det.json')
data_ml.save('/tmp/ml.json')
data_mc.save('/tmp/mc.json')
