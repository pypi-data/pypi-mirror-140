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

import copy
import json
import logging
import re
import string
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
from keras import layers
from sklearn.metrics import classification_report
from tqdm import tqdm

from insynth.calculators import StrongNeuronActivationCoverageCalculator, \
    KMultiSectionNeuronCoverageCalculator, NeuronCoverageCalculator, NeuronBoundaryCoverageCalculator, \
    TopKNeuronCoverageCalculator, TopKNeuronPatternsCalculator
from insynth.perturbators.audio import AudioBackgroundWhiteNoisePerturbator, AudioPitchPerturbator, \
    AudioClippingPerturbator, AudioVolumePerturbator, AudioEchoPerturbator, \
    AudioShortNoisePerturbator, AudioBackgroundNoisePerturbator, AudioImpulseResponsePerturbator, \
    AudioCompressionPerturbator
from insynth.perturbators.image import ImageNoisePerturbator, ImageBrightnessPerturbator, ImageContrastPerturbator, \
    ImageSharpnessPerturbator, ImageFlipPerturbator, ImageOcclusionPerturbator, ImageCompressionPerturbator, \
    ImagePixelizePerturbator
from insynth.perturbators.text import TextTypoPerturbator, TextCasePerturbator, TextWordRemovalPerturbator, \
    TextStopWordRemovalPerturbator, TextWordSwitchPerturbator, TextCharacterSwitchPerturbator, \
    TextPunctuationErrorPerturbator


class AbstractRunner(ABC):
    @abstractmethod
    def run(self):
        """
        Returns a report by running the robustness test.
        :return:
        """
        raise NotImplementedError


class BasicRunner(AbstractRunner):

    def __init__(self, perturbators, coverage_calculators, dataset_x, dataset_y, model, pre_predict_lambda=None):
        self.perturbators = perturbators
        self.coverage_calculators = coverage_calculators
        self.dataset_x = dataset_x
        self.dataset_y = dataset_y
        self.model = model
        self.pre_predict_lambda = pre_predict_lambda or (lambda sample: np.array(sample))

    def run(self, save_incorrect_mutated_samples=False, output_path=None):
        results = {}

        y_pred = []
        for sample in tqdm(self.dataset_x(), desc='Processing Original Dataset...'):
            transformed_sample = self.pre_predict_lambda(sample)
            raw_prediction = self.model(transformed_sample, training=False).numpy()
            if raw_prediction.size == 1:
                prediction = 1 if raw_prediction.flatten()[0] > 0.5 else 0
            else:
                prediction = np.argmax(raw_prediction)
            y_pred.append(prediction)
            for coverage_calculator in self.coverage_calculators:
                coverage_calculator.update_coverage(transformed_sample)

        self.put_results_into_dict(results, 'Original', self.dataset_y, y_pred)
        self.put_coverage_into_dict(results, 'Original',
                                    self.coverage_calculators)

        all_coverage_calculators = [copy.copy(calculator) for calculator in self.coverage_calculators]
        logging.info('Processing mutated dataset...')
        for perturbator_index, perturbator in tqdm(enumerate(self.perturbators), desc='Applying Perturbators...'):
            perturbator_name = str(perturbator_index) + '_' + type(perturbator).__name__
            logging.info(f'Working on Perturbator: {perturbator_name}')
            mutated_coverage_calculators = [copy.copy(calculator) for calculator in self.coverage_calculators]

            predictions = []
            for index, sample in tqdm(enumerate(self.dataset_x()), desc='Running on Samples...'):
                mutated_sample = perturbator.apply(sample)
                correct_label = self.dataset_y[index]
                previous_prediction = y_pred[index]
                transformed_mutated_sample = self.pre_predict_lambda(mutated_sample)
                raw_prediction = self.model(transformed_mutated_sample, training=False).numpy()
                if raw_prediction.size == 1:
                    prediction = 1 if raw_prediction.flatten()[0] > 0.5 else 0
                else:
                    prediction = np.argmax(raw_prediction)
                predictions.append(prediction)
                # save if wrongly predicted but was correctly predicted previously
                if save_incorrect_mutated_samples and prediction != correct_label and previous_prediction == correct_label:
                    self._save(mutated_sample, f'{output_path}/{perturbator_name}_{correct_label}_{prediction}_{index}')

                for calculator in mutated_coverage_calculators:
                    calculator.update_coverage(transformed_mutated_sample)

            self.put_results_into_dict(results, perturbator_name, self.dataset_y, predictions, args=vars(perturbator))
            self.put_coverage_into_dict(results, perturbator_name,
                                        mutated_coverage_calculators)

            for original_calc, mutated_calc in zip(all_coverage_calculators, mutated_coverage_calculators):
                original_calc.merge(mutated_calc)
        results['All'] = {}
        self.put_coverage_into_dict(results, 'All',
                                    all_coverage_calculators)
        # logging.info('Result: ' + json.dumps(results))
        df = pd.DataFrame.from_dict(results, orient='index')
        df.loc['All', 0:7] = df.mean(numeric_only=True)
        return df, (1 - df.loc['Original', 'acc'] + df.loc['All', 'acc'])

    def put_coverage_into_dict(self, dct, perturbator_name, coverage_calculators):
        for coverage_result, calculator_name in zip(map(lambda x: x.get_coverage(), coverage_calculators),
                                                    map(lambda x: type(x).__name__, coverage_calculators)):
            dct[perturbator_name][calculator_name] = coverage_result

    def put_results_into_dict(self, dct, name, y_true, y_pred, args=None):
        results = classification_report(y_true,
                                        y_pred,
                                        output_dict=True, zero_division=0)
        logging.info(f'Results for {name}: ' + json.dumps(results))
        dct[name] = {
            'acc': results['accuracy'],
            'macro_f1': results['macro avg']['f1-score'],
            'macro_rec': results['macro avg']['recall'],
            'macro_prec': results['macro avg']['precision'],
            'micro_f1': results['weighted avg']['f1-score'],
            'micro_rec': results['weighted avg']['recall'],
            'micro_prec': results['weighted avg']['precision']}
        if args:
            dct[name]['args'] = args

    @abstractmethod
    def _save(self, sample, output_path):
        raise NotImplementedError()


class BasicImageRunner(BasicRunner):
    def __init__(self, perturbators, coverage_calculators, dataset_x, dataset_y, model, pre_predict_lambda=None):
        super().__init__(perturbators, coverage_calculators, dataset_x, dataset_y, model,
                         pre_predict_lambda or (lambda sample: np.expand_dims(np.array(sample), axis=0)))

    def _save(self, sample, output_path):
        sample.save(output_path + '.jpg', 'JPEG')


class BasicTextRunner(BasicRunner):
    def __init__(self, perturbators, coverage_calculators, dataset_x, dataset_y, model, pre_predict_lambda=None):
        super().__init__(perturbators, coverage_calculators, dataset_x, dataset_y, model,
                         pre_predict_lambda or self._pre_prediction)

    def _save(self, sample, output_path):
        with open(output_path + '.txt', 'w', encoding='utf-8') as txt_out:
            txt_out.write(sample)

    def custom_standardization(self, input_data):
        import tensorflow as tf
        lowercase = tf.strings.lower(input_data)
        stripped_html = tf.strings.regex_replace(lowercase, '<br />', ' ')
        return tf.strings.regex_replace(stripped_html,
                                        '[%s]' % re.escape(string.punctuation),
                                        '')

    def _pre_prediction(self, sample):
        vectorize_layer = layers.TextVectorization(
            standardize=self.custom_standardization,
            max_tokens=10000,
            output_mode='int',
            output_sequence_length=250)
        vectorize_layer.adapt(np.array([sample]))
        return vectorize_layer(np.array([sample])).numpy()


class BasicAudioRunner(BasicRunner):
    def __init__(self, perturbators, coverage_calculators, dataset_x, dataset_y, model, pre_predict_lambda=None):
        super().__init__(perturbators, coverage_calculators, dataset_x, dataset_y, model,
                         pre_predict_lambda or self._pre_prediction)

    def _save(self, sample, output_path):
        from scipy.io.wavfile import write
        signal, sample_rate = sample
        write(output_path + '.wav', sample_rate, signal)

    def _pre_prediction(self, sample):
        import tensorflow as tf

        signal = np.expand_dims(sample[0], axis=1)
        sample_rate = sample[1]
        audio = signal
        fft = tf.signal.fft(
            tf.cast(tf.complex(real=audio, imag=tf.zeros_like(audio)), tf.complex64)
        )
        fft = tf.expand_dims(fft, axis=0)
        return tf.math.abs(fft[:, : (sample_rate // 2), :]).numpy()


class ExtensiveImageRunner(BasicImageRunner):
    def __init__(self, dataset_x, dataset_y, model, snac_data, pre_predict_lambda=None):
        super().__init__(None, None, dataset_x, dataset_y,
                         model, pre_predict_lambda)
        self.snac_data = snac_data
        self.perturbators = self._get_all_perturbators()
        self.coverage_calculators = self._get_all_coverage_calculators(self.model)

    def _get_all_perturbators(self):
        return [ImageNoisePerturbator(p=1.0),
                ImageBrightnessPerturbator(p=1.0),
                ImageContrastPerturbator(p=1.0),
                ImageSharpnessPerturbator(p=1.0),
                ImageFlipPerturbator(p=1.0),
                ImageOcclusionPerturbator(p=1.0),
                ImageCompressionPerturbator(p=1.0),
                ImagePixelizePerturbator(p=1.0)
                ]

    def _get_all_coverage_calculators(self, model):
        calcs = [
            NeuronCoverageCalculator(model),
            StrongNeuronActivationCoverageCalculator(model),
            KMultiSectionNeuronCoverageCalculator(model),
            NeuronBoundaryCoverageCalculator(model),
            TopKNeuronCoverageCalculator(model),
            TopKNeuronPatternsCalculator(model)
        ]
        for calc in calcs:
            update_neuron_bounds_op = getattr(calc, "update_neuron_bounds", None)
            if callable(update_neuron_bounds_op):
                for sample in tqdm(self.snac_data(), desc='Processing SNAC...'):
                    calc.update_neuron_bounds(self.pre_predict_lambda(sample))
        return calcs


class ExtensiveAudioRunner(BasicAudioRunner):
    def __init__(self, dataset_x, dataset_y, model, snac_data, pre_predict_lambda=None):
        super().__init__(None, None, dataset_x, dataset_y,
                         model, pre_predict_lambda)
        self.snac_data = snac_data
        self.perturbators = self._get_all_perturbators()
        self.coverage_calculators = self._get_all_coverage_calculators(self.model)

    def _get_all_perturbators(self):
        return [AudioBackgroundWhiteNoisePerturbator(p=1.0),
                AudioCompressionPerturbator(p=1.0),
                AudioPitchPerturbator(p=1.0),
                AudioClippingPerturbator(p=1.0),
                AudioVolumePerturbator(p=1.0),
                AudioEchoPerturbator(p=1.0),
                AudioShortNoisePerturbator(p=1.0),
                AudioBackgroundNoisePerturbator(p=1.0),
                AudioImpulseResponsePerturbator(p=1.0)
                ]

    def _get_all_coverage_calculators(self, model):
        calcs = [
            NeuronCoverageCalculator(model),
            StrongNeuronActivationCoverageCalculator(model),
            KMultiSectionNeuronCoverageCalculator(model),
            NeuronBoundaryCoverageCalculator(model),
            TopKNeuronCoverageCalculator(model),
            TopKNeuronPatternsCalculator(model)
        ]
        for calc in calcs:
            update_neuron_bounds_op = getattr(calc, "update_neuron_bounds", None)
            if callable(update_neuron_bounds_op):
                for sample in tqdm(self.snac_data(), desc='Processing SNAC...'):
                    calc.update_neuron_bounds(self.pre_predict_lambda(sample))
        return calcs


class ExtensiveTextRunner(BasicTextRunner):
    def __init__(self, dataset_x, dataset_y, model, snac_data, pre_predict_lambda=None):
        super().__init__(None, None, dataset_x, dataset_y,
                         model, pre_predict_lambda)
        self.snac_data = snac_data
        self.perturbators = self._get_all_perturbators()
        self.coverage_calculators = self._get_all_coverage_calculators(self.model)

    def _get_all_perturbators(self):
        return [TextTypoPerturbator(p=1.0),
                TextCasePerturbator(p=1.0),
                TextWordRemovalPerturbator(p=1.0),
                TextStopWordRemovalPerturbator(p=1.0),
                TextWordSwitchPerturbator(p=1.0),
                TextCharacterSwitchPerturbator(p=1.0),
                TextPunctuationErrorPerturbator(p=1.0),
                ]

    def _get_all_coverage_calculators(self, model):
        calcs = [
            NeuronCoverageCalculator(model),
            StrongNeuronActivationCoverageCalculator(model),
            KMultiSectionNeuronCoverageCalculator(model),
            NeuronBoundaryCoverageCalculator(model),
            TopKNeuronCoverageCalculator(model),
            TopKNeuronPatternsCalculator(model)]
        for calc in calcs:
            update_neuron_bounds_op = getattr(calc, "update_neuron_bounds", None)
            if callable(update_neuron_bounds_op):
                for sample in tqdm(self.snac_data(), desc='Processing SNAC...'):
                    calc.update_neuron_bounds(self.pre_predict_lambda(sample))
        return calcs
