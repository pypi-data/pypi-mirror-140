from abc import abstractmethod
from ..utils import decode_distribution
import numpy as np
import copy
from .utils import logging


class AMBase(object):
    def __init__(self, class_dict=[]):
        """ class_dict could be get from the data manager object """
        assert isinstance(class_dict, (list, tuple))
        self._class_dict = sorted(class_dict, key=lambda x: x['class_id'])
        self._class2label_all = {x['class_name']:x['class_id'] for x in class_dict}
        self._label2class_all = {x['class_id']:x['class_name'] for x in class_dict}

        self._all_classes = [x['class_name'] for x in self._class_dict]
        self._leaf_classes = self._get_leaf_classes(class_dict)

        self.set_class()

    @property
    def classnames(self):
        # set in self.set_class()
        return self._distribution_classes

    def clone(self):
        return copy.deepcopy(self)
    
    #
    # class manipulateion Methods
    #
    def _get_leaf_classes(self, class_dict):
        # 1) collect all parent classnames
        nonleaf_classes = set([x['parent'] for x in class_dict if x['parent'] is not None])
        leaf_classes = list()
        for x in self._class_dict:
            if x['class_name'] not in nonleaf_classes:
                leaf_classes.append(x['class_name'])
        return leaf_classes

    def _check_classes_conflict(self, classname_list):
        """ because we have parent classes, this function checks if there are parent class
            and its child class in the classname_list.
        """
        # loop over classname_list to check if one's parent is also in classname_list
        for classname in classname_list:
            parent = 'WHAT THE FUCK'
            child  = classname
            while parent is not None:
                classid_global = self._class2label_all[child]
                parent = self._class_dict[classid_global]['parent']
                if parent in classname_list:
                    raise RuntimeError("(WARNING) conflict class pair found: ({}, {})".format(child, parent))
                child = parent

    def _extend_distribution(self, distribution_global, exclude_classes=[]):
        """ extend the global distribution: fill parents with their maximal child """
        for child_id, child_score in enumerate(distribution_global):
            # trace back to root class
            parent = self._class_dict[child_id]['parent']
            while parent is not None:
                parent_id = self._class2label_all[parent]
                parent_score = distribution_global[parent_id]
                if parent not in exclude_classes:
                    distribution_global[parent_id] = max(child_score, parent_score)  # update parent score
                parent = self._class_dict[parent_id]['parent']   # update parent
                child_score = max(child_score, parent_score)     # update child_score
        return distribution_global

    @staticmethod
    def _add_ok_class(class_dict):
        """ Add OK class to class dict """
        __OK__ = 'OK'
        new_class_dict = copy.deepcopy(class_dict)
        for class_unit in new_class_dict:
            class_unit['class_id'] += 1
            assert class_unit['class_id'] != 0
            assert class_unit['class_name'] != __OK__
        OK_class_unit = {
            'class_id': 0,
            'class_name': __OK__,
            'parent': None
        }
        return [OK_class_unit] + new_class_dict



    @abstractmethod
    def set_class(self, arg):
        raise NotImplementedError()

    @abstractmethod
    def get_score(self, arg):
        raise NotImplementedError()

    #@logging
    def get_classid(self, arg):
        if None: pass
        elif isinstance(arg, dict):
            if 'instances' in arg:  # a record
                return [self.get_classid(inst) for inst in arg['instances']]
            else:                   # a instance
                inst = arg
                if 'class_id' in inst:
                    return inst['class_id']
                elif 'class_name' in inst:
                    classname = inst['class_name']
                    assert classname in self._class2label, "{} not in class dict: {}".format(classname, self._class2label)
                    return self._class2label[classname]
                elif 'distribution' in inst:
                    dist_all = decode_distribution(inst['distribution'])
                    dist_oin = [dist_all[ix] for ix in self._classid_of_interested]
                    return int(np.argmax(dist_oin))
                else:
                    raise RuntimeError()
        elif isinstance(arg, str):
            classname = arg
            assert classname in self._class2label, "{} not in class dict: {}".format(classname, self._class2label)
            return self._class2label[classname]
        elif isinstance(arg, list):
            return [self.get_classid(x) for x in arg]
        elif isinstance(arg, int):
            class_id = arg
            assert class_id in self._label2class
            return class_id
        else:
            raise TypeError("Argument Type Not Supported: {}".format(type(arg)))

    #@logging
    def get_classname(self, arg):
        res = self.get_classid(arg)
        if isinstance(res, list):
            return [self.get_classname(class_id) for class_id in res]
        else:
            class_id = res
            assert class_id in self._label2class
            return self._label2class[class_id]
