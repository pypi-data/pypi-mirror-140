from ..utils import decode_distribution, encode_distribution
from .base import AMBase
from .utils import logging
import numpy as np


class AMMC(AMBase):
    def __init__(self, *args, **kwargs):
        super(AMMC, self).__init__(*args, **kwargs)
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
    def get_classid(self, arg):
        if isinstance(arg, dict):
            rec = arg
            if 'info' in rec:
                info = rec['info']
                if 'distribution' in info:
                    dist_all = decode_distribution(info['distribution'])
                    dist_oin = [dist_all[ix] for ix in self._classid_of_interested]
                    return int(np.argmax(dist_oin))
                else:
                    return RuntimeError()
            else:
                raise RuntimeError()
        else:
            return super(AMMC, self).get_classid(arg)

    #@logging
    def get_score(self, arg):
        if None: pass
        elif isinstance(arg, dict):
            if 'info' in arg:
                rec = arg
                if 'distribution' in rec['info']:
                    dist_all = decode_distribution(rec['info']['distribution'])
                    dist_oin = [dist_all[ix] for ix in self._classid_of_interested]
                    return max(dist_oin)
                else:
                    raise RuntimeError('Input:', arg)
            else:
                raise RuntimeError()
        else:
            raise TypeError("Argument Type Not Supported: {}".format(type(arg)))

    #@logging
    def create_distribution(self, obj, score=1):
        """
        obj:
            - classname (str): classname + score in effect
            - distribution: distribution of classes of interested
        return:
            encoded scores (full distribution)
        """
        # create distribution
        if None: pass
        elif isinstance(obj, (tuple, list, np.ndarray)):
            distribution = list(obj)
            assert len(distribution) == len(self.classnames)
            distribution_all = [0]*len(self._all_classes)
            for class_id, sc in enumerate(distribution):
                class_name = self._label2class[class_id]
                class_id_global = self._class2label_all[class_name]
                distribution_all[class_id_global] = sc
                distribution_all = self._extend_distribution(distribution_all, exclude_classes=self.classnames)
        elif isinstance(obj, str):
            class_name = obj
            distribution_all = [0]*len(self._all_classes)
            class_id_global = self._class2label_all[class_name]
            distribution_all[class_id_global] = score
            distribution_all = self._extend_distribution(distribution_all, exclude_classes=[class_name])
        else:
            raise RuntimeError("Unknown type: {}".format(obj))

        return encode_distribution(distribution_all)