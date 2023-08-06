from medusa.components import ExperimentData
import numpy as np


class MIData(ExperimentData):

    # TODO: Check everything

    """Class with the necessary attributes to define motor imagery (MI)
    experiments. It provides compatibility with high-level functions for this
    MI paradigms in BCI module.
    """
    def __init__(self, mode, onsets, w_trial_t, mi_result, control_state_result,
                 mi_labels=None, control_state_labels=None, w_rest_t=None,
                 **kwargs):
        """MIData constructor

        Parameters
        ----------
        mode : str {"train"|"test"}
            Mode of this run.
        onsets : list or numpy.ndarray [n_stim x 1]
            Timestamp of each stimulation
        w_trial_t: list [start, end]
            Temporal window of the motor imagery with respect to each onset in
            ms. For example, if  w_trial_t = [500, 4000] the subject was
            performing the motor imagery task from 500ms after to 4000ms after
            the onset.
        mi_result : list or numpy.ndarray [n_trials x 3]
            Spell result of this run. Each position contains the data of the
            selected target (matrix_idx, row, col)
        control_state_result : list or numpy.ndarray
            Control state result of this run. Each position contains the
            detected control state of the user (0 -> non-control, 1-> control)
        mi_labels : list or numpy.ndarray [n_stim x 1] {0|1}
            Only in train mode. Contains the erp labels of each stimulation
            (0 -> non-target, 1-> target)
        control_state_labels : list or numpy.ndarray [n_stim x 1] {0|1}
            Only in train mode. Contains the erp labels of each stimulation
            (0 -> non-control, 1-> control)
         w_trial_t: list [start, end]
            Temporal window of the rest with respect to each onset in ms. For
            example, if w_rest_t = [-1000, 0] the subject was resting from
            1000ms before to the onset.
        kwargs : kwargs
            Custom arguments that will also be saved in the class
            (e.g., timings, calibration gaps, etc.)
        """

        # Check errors
        if mode == 'train':
            if mi_labels is None or control_state_labels is None:
                raise ValueError('Attributes mi_labels, control_state_labels '
                                 'be provided in train mode')

        # Standard attributes
        self.mode = mode
        self.onsets = np.array(onsets)
        self.w_trial_t = np.array(w_trial_t)
        self.mi_result = np.array(mi_result)
        self.control_state_result = np.array(control_state_result)
        self.mi_labels = np.array(mi_labels) if mi_labels is not None else \
            mi_labels
        self.control_state_labels = np.array(control_state_labels) \
            if control_state_labels is not None else control_state_labels

        # Optional attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_serializable_obj(self):
        rec_dict = self.__dict__
        for key in rec_dict.keys():
            if type(rec_dict[key]) == np.ndarray:
                rec_dict[key] = rec_dict[key].tolist()
        return rec_dict

    @staticmethod
    def from_serializable_obj(dict_data):
        return MIData(**dict_data)

