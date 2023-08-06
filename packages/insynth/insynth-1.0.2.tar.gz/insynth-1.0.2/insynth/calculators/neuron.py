#  Copyright (c) 2022, Chair of Software Technology
#  All rights reserved.
#  Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#
#  - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#
#  - Neither the name of the University Mannheim nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from copy import deepcopy

import numpy as np

from insynth.calculators.abstract_calculator import AbstractCoverageCalculator, num_neurons


def neurons_covered(coverage_dict):
    """
    Returns the number of neurons covered from the given coverage dictionary.
    :param coverage_dict:
    :return:
    """
    covered_neurons = sum(arr.sum() for arr in coverage_dict.values())
    total_neurons = sum(len(arr) for arr in coverage_dict.values())
    return covered_neurons, total_neurons, covered_neurons / float(total_neurons)


def merge_np_arrays(arr1, arr2):
    """
    Merges two numpy arrays containing boolean values using the logical OR operator.
    :param arr1:
    :param arr2:
    :return:
    """
    arr1[arr2] = True
    return arr1


def merge_dicts(dict_1, dict_2):
    """
    Merges two dictionaries of numpy arrays containing boolean values.
    :param dict_1:
    :param dict_2:
    :return:
    """
    for key in dict_1.keys():
        dict_1[key] = merge_np_arrays(dict_1[key], dict_2[key])
    return dict_1


class NeuronCoverageCalculator(AbstractCoverageCalculator):
    def __copy__(self):
        self_copy = NeuronCoverageCalculator(self.model, self.activation_threshold)
        self_copy.coverage_dict = deepcopy(self.coverage_dict)
        return self_copy

    def __init__(self, model, activation_threshold=0):
        super().__init__(model)

        self.activation_threshold = activation_threshold
        self.coverage_dict = self._init_plain_coverage_dict(False)

    def update_coverage(self, input_data):
        for layer_name, layer_activations in self.iterate_over_layer_activations(input_data):
            layer_coverage_arr = self.coverage_dict[layer_name]
            layer_activations = layer_activations.flatten()
            layer_coverage_arr[layer_activations > self.activation_threshold] = True

    def get_coverage(self) -> dict:
        covered_neurons, total_neurons, covered_percentage = neurons_covered(self.coverage_dict)
        return {
            'total_neurons': total_neurons,
            'covered_neurons': covered_neurons,
            'covered_neurons_percentage': covered_percentage
        }

    def merge(self, other_calculator):
        self.coverage_dict = merge_dicts(self.coverage_dict, other_calculator.coverage_dict)


class StrongNeuronActivationCoverageCalculator(AbstractCoverageCalculator):
    def __copy__(self):
        self_copy = StrongNeuronActivationCoverageCalculator(self.model)
        self_copy.coverage_dict = deepcopy(self.coverage_dict)
        self_copy.upper_neuron_bounds_dict = deepcopy(self.upper_neuron_bounds_dict)
        self_copy.lower_neuron_bounds_dict = deepcopy(self.lower_neuron_bounds_dict)
        return self_copy

    def __init__(self, model):
        super().__init__(model)
        self.coverage_dict = self._init_plain_coverage_dict(False)
        self.upper_neuron_bounds_dict = self._init_plain_coverage_dict(np.NAN)
        self.lower_neuron_bounds_dict = self._init_plain_coverage_dict(np.NAN)

    def update_neuron_bounds(self, input_batch):
        for layer_name, layer_activations in self.iterate_over_layer_activations(input_batch):
            upper_neuron_bounds_dict = self.upper_neuron_bounds_dict[layer_name]
            lower_neuron_bounds_dict = self.lower_neuron_bounds_dict[layer_name]
            layer_activations = layer_activations.flatten()

            activation_larger_or_not_set_condition = (layer_activations > upper_neuron_bounds_dict) | np.isnan(
                upper_neuron_bounds_dict)
            upper_neuron_bounds_dict[activation_larger_or_not_set_condition] = layer_activations[activation_larger_or_not_set_condition]

            activation_lower_or_not_set_condition = (layer_activations < lower_neuron_bounds_dict) | np.isnan(
                lower_neuron_bounds_dict)
            lower_neuron_bounds_dict[activation_lower_or_not_set_condition] = layer_activations[activation_lower_or_not_set_condition]

    def update_coverage(self, input_data):
        for layer_name, layer_activations in self.iterate_over_layer_activations(input_data):
            layer_coverage_dict = self.coverage_dict[layer_name]
            upper_neuron_bounds_dict = self.upper_neuron_bounds_dict[layer_name]
            layer_activations = layer_activations.flatten()
            layer_coverage_dict[layer_activations > upper_neuron_bounds_dict] = True

    def get_coverage(self) -> dict:
        covered_neurons, total_neurons, covered_percentage = neurons_covered(self.coverage_dict)
        return {
            'total_neurons': total_neurons,
            'covered_neurons': covered_neurons,
            'covered_neurons_percentage': covered_percentage
        }

    def merge(self, other_calculator):
        self.coverage_dict = merge_dicts(self.coverage_dict, other_calculator.coverage_dict)


class KMultiSectionNeuronCoverageCalculator(StrongNeuronActivationCoverageCalculator):
    def __copy__(self):
        self_copy = KMultiSectionNeuronCoverageCalculator(self.model, self.k)
        self_copy.coverage_dict = deepcopy(self.coverage_dict)
        self_copy.upper_neuron_bounds_dict = deepcopy(self.upper_neuron_bounds_dict)
        self_copy.lower_neuron_bounds_dict = deepcopy(self.lower_neuron_bounds_dict)
        return self_copy

    def __init__(self, model, k=3):
        super().__init__(model)
        self.k = k
        self.upper_neuron_bounds_dict = self._init_plain_coverage_dict(np.NAN)
        self.lower_neuron_bounds_dict = self._init_plain_coverage_dict(np.NAN)
        self.coverage_dict = self._init_dict(model)

    def update_coverage(self, input_data):
        for layer_name, layer_activations in self.iterate_over_layer_activations(input_data):
            layer_coverage_dict = self.coverage_dict[layer_name]
            upper_neuron_bounds_arr = self.upper_neuron_bounds_dict[layer_name]
            lower_neuron_bounds_arr = self.lower_neuron_bounds_dict[layer_name]
            layer_activations = layer_activations.flatten()

            step_sizes = (upper_neuron_bounds_arr - lower_neuron_bounds_arr) / self.k
            activated_sections = ((layer_activations - lower_neuron_bounds_arr) / step_sizes).astype(int)

            layer_coverage_dict[(0 <= activated_sections) & (activated_sections < self.k), activated_sections[
                (0 <= activated_sections) & (activated_sections < self.k)]] = True

    def _init_dict(self, model):
        coverage_dict = {}
        for layer in self.layers_with_neurons:
            layer_name = layer.name
            coverage_dict[layer_name] = np.full((num_neurons(layer), self.k), False)
        return coverage_dict

    def neurons_covered(self):
        covered_neurons = sum((arr.sum(axis=1) == self.k).sum() for arr in self.coverage_dict.values())
        total_neurons = sum(len(arr) for arr in self.coverage_dict.values())
        return covered_neurons, total_neurons, covered_neurons / float(total_neurons)

    def sections_covered(self):
        covered_sections = sum(arr.sum() for arr in self.coverage_dict.values())
        total_sections = sum(len(arr) for arr in self.coverage_dict.values()) * self.k
        return covered_sections, total_sections, covered_sections / float(total_sections)

    def get_coverage(self) -> dict:
        covered_neurons, total_neurons, covered_percentage = self.neurons_covered()
        covered_sections, total_sections, sections_covered_percentage = self.sections_covered()
        return {
            'total_neurons': total_neurons,
            'covered_neurons': covered_neurons,
            'covered_neurons_percentage': covered_percentage,
            'total_sections': total_sections,
            'covered_sections': covered_sections,
            'sections_covered_percentage': sections_covered_percentage,
        }

    def merge(self, other_calculator):
        self.coverage_dict = merge_dicts(self.coverage_dict, other_calculator.coverage_dict)


class NeuronBoundaryCoverageCalculator(StrongNeuronActivationCoverageCalculator):
    def __copy__(self):
        self_copy = NeuronBoundaryCoverageCalculator(self.model)
        self_copy.coverage_dict = deepcopy(self.coverage_dict)
        self_copy.upper_neuron_bounds_dict = deepcopy(self.upper_neuron_bounds_dict)
        self_copy.lower_neuron_bounds_dict = deepcopy(self.lower_neuron_bounds_dict)
        return self_copy

    def __init__(self, model):
        super().__init__(model)
        self.coverage_dict = self._init_dict(model)
        self.upper_neuron_bounds_dict = self._init_plain_coverage_dict(np.NAN)
        self.lower_neuron_bounds_dict = self._init_plain_coverage_dict(np.NAN)

    def update_coverage(self, input_data):
        for layer_name, layer_activations in self.iterate_over_layer_activations(
                input_data):
            layer_coverage_dict = self.coverage_dict[layer_name]
            upper_neuron_bounds_arr = self.upper_neuron_bounds_dict[layer_name]
            lower_neuron_bounds_arr = self.lower_neuron_bounds_dict[layer_name]
            layer_activations = layer_activations.flatten()

            layer_coverage_dict[layer_activations > upper_neuron_bounds_arr, 1] = True
            layer_coverage_dict[layer_activations < lower_neuron_bounds_arr, 0] = True

    def neurons_covered(self):
        covered_neurons = sum((arr.sum(axis=1) == 2).sum() for arr in self.coverage_dict.values())
        total_neurons = sum(len(arr) for arr in self.coverage_dict.values())
        return covered_neurons, total_neurons, covered_neurons / float(total_neurons)

    def corners_covered(self):
        covered_corners = sum(arr.sum() for arr in self.coverage_dict.values())
        total_corners = sum(len(arr) for arr in self.coverage_dict.values()) * 2
        return covered_corners, total_corners, covered_corners / float(total_corners)

    def get_coverage(self) -> dict:
        covered_neurons, total_neurons, covered_percentage = self.neurons_covered()
        covered_corners, total_corners, corners_covered_percentage = self.corners_covered()
        return {
            'total_neurons': total_neurons,
            'covered_neurons': covered_neurons,
            'covered_neurons_percentage': covered_percentage,
            'total_corners': total_corners,
            'covered_corners': covered_corners,
            'corners_covered_percentage': corners_covered_percentage,
        }

    def _init_dict(self, model):
        coverage_dict = {}
        for layer in self.layers_with_neurons:
            layer_name = layer.name
            coverage_dict[layer_name] = np.full((num_neurons(layer), 2), False)
        return coverage_dict

    def merge(self, other_calculator):
        self.coverage_dict = merge_dicts(self.coverage_dict, other_calculator.coverage_dict)


