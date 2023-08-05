from ..utils import decode_distribution, decode_labelme_shape
from ..utils import encode_labelme_shape
from ..utils import create_uuid
import numpy as np
from .base import AMBase
from .utils import logging


class AMDet(AMBase):
    def __init__(self, *args, **kwargs):
        super(AMDet, self).__init__(*args, **kwargs)
        self.set_class()


    def set_class(self, arg='leaf'):
        """
        Set classes of interested (default 'all')
        """
        if None: pass
        elif arg == 'leaf':
            classname_list = self._leaf_classes
        elif isinstance(arg, (list, tuple)):
            classname_list = arg
        else:
            raise RuntimeError("Unknown args")

        self._check_classes_conflict(classname_list)

        self._class2label = {name:label for label, name in enumerate(classname_list)}
        self._label2class = {label:name for label, name in enumerate(classname_list)}

        # global class ids of interested classes
        self._classid_of_interested = [self._class2label_all[classname] for classname in classname_list]
        self._distribution_classes = classname_list


    #@logging
    def get_score(self, arg):
        if None: pass
        elif isinstance(arg, dict):
            if 'instances' in arg:  # a record
                return [self.get_score(inst) for inst in arg['instances']]
            else:                   # a instance
                inst = arg
                if 'class_id' in inst or 'class_name' in inst:
                    assert 'score' in inst
                    return inst['score']
                elif 'distribution' in inst:
                    dist_all = decode_distribution(inst['distribution'])
                    dist_oin = [dist_all[ix] for ix in self._classid_of_interested]
                    return float(np.max(dist_oin))
                else:
                    raise RuntimeError("inst: ", inst)
        else:
            raise TypeError("Argument Type Not Supported: {}".format(type(arg)))

    #@logging
    def get_shape(self, arg):
        if None: pass
        elif isinstance(arg, dict):
            if 'instances' in arg:  # a record
                return [self.get_shape(inst) for inst in arg['instances']]
            else:                   # a instance
                inst = arg
                assert 'points' in inst
                return decode_labelme_shape(inst['points'])
        else:
            raise TypeError("Argument Type Not Supported: {}".format(type(arg)))

    #@logging
    def get_shape(self, arg):
        if None: pass
        elif isinstance(arg, dict):
            if 'instances' in arg:  # a record
                return [self.get_shape(inst) for inst in arg['instances']]
            else:                   # a instance
                inst = arg
                assert 'points' in inst
                return decode_labelme_shape(inst['points'])
        else:
            raise TypeError("Argument Type Not Supported: {}".format(type(arg)))

    #@logging
    def get_xyxy(self, arg):
        points = self.get_shape(arg)
        def _points2xyxy(points):
            points = np.reshape(points, [-1,2])
            x1,y1,x2,y2 = points[:,0].min(), points[:,1].min(), points[:,0].max(), points[:,1].max()
            return [x1,y1,x2,y2]
        if len(points) == 0:
            return []
        elif isinstance(points[0], (list, tuple)):
            return [_points2xyxy(pts) for pts in points]
        else:
            return _points2xyxy(points)

    
    #@logging
    def get_xywh(self, arg):
        points = self.get_shape(arg)
        def _points2xywh(points):
            points = np.reshape(points, [-1,2])
            x1,y1,x2,y2 = points[:,0].min(), points[:,1].min(), points[:,0].max(), points[:,1].max()
            return [x1,y1,x2-x1,y2-y1]
        if len(points) == 0:
            return []
        elif isinstance(points[0], (list, tuple)):
            return [_points2xywh(pts) for pts in points]
        else:
            return _points2xywh(points)


    #@logging
    def create_instance(self, classname, score=1, shape=[]):
        """
        return a bbox or a list of bboxes
        """
        # create class id
        assert classname in self.classnames


        # create shape
        shape_type = 'polygon'
        assert isinstance(shape, (list, tuple, np.ndarray))
        if None: pass
        elif len(shape) == 0:
            shape_type = None
            points = []
        elif len(shape) == 2:
            assert isinstance(shape[0], (list, tuple, np.ndarray))
            (x1,y1),(x2,y2) = shape[0], shape[1]
            points = [[x1,y1],[x1,y2],[x2,y2],[x2,y1],[x1,y2]]
        elif len(shape) == 4:
            mark_list = [not hasattr(item, '__iter__') for item in shape]
            if all(mark_list):
                x1, y1, x2, y2 = shape
                points = [[x1, y1], [x1, y2], [x2, y2], [x2, y1], [x1, y2]]
            elif not any(mark_list):
                points = [[x, y] for x, y in shape]
            else:
                raise RuntimeError("Invalid shape: {}".format(shape))
        elif len(shape) >= 3:
            points = [[x, y] for x, y in shape]
        else:
            raise RuntimeError("Invalid shape: {}".format(shape))

        instance = {
            'uuid': create_uuid(),
            'class_name': classname,
            'score': score,
            'shape_type': shape_type,
            'points': encode_labelme_shape(points)
        } 

        return instance