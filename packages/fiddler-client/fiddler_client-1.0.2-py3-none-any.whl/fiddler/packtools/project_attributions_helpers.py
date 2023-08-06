import re
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
from fiddler import gem


class IGTextAttributionsTF2Keras:
    """
    Helper class for project attribution method when computing IG for Text data with Keras TF2.
    """
    def __init__(self, input_df, output_cols):
        """
        :param input_df: pandas dataframe for a single observation
        :param output_cols: list of output column names
        """
        self.input_df = input_df
        self.output_cols = output_cols

    def text_to_tokens_keras(self, tokenizer, max_seq_length, feature_label):
        """
        Helper function to convert text to tokens with keras TF2.

        :param tokenizer: keras tokenizer used during training
        :param max_seq_length: max sequence length used during training
        :param feature_label: str. Name of the text feature input
        :return: word tokens
        """
        unpadded_tokens = [
            tokenizer.texts_to_sequences([x])[0]
            for x in self.input_df[feature_label].values
        ]

        padded_tokens = pad_sequences(
            unpadded_tokens, max_seq_length, padding='post', truncating='post'
        )

        word_tokens = tokenizer.sequences_to_texts([[x] for x in padded_tokens[0]])
        return word_tokens

    def text_attributions(self, tokenizer, word_tokens, word_attributions, feature_label):
        """
        Helper function to define segments works and attributions.

        :param tokenizer: keras tokenizer used during training
        :param word_tokens: word tokens. Could be the output of the text_to_tokens_keras method
        :param word_attributions: associated word attributions
        :param feature_label: str. Name of the text feature input
        :return: final segments and attributions
        """
        segments = re.split(
            r'([ ' + tokenizer.filters + '])',
            self.input_df.iloc[0][feature_label],
        )
        i = 0
        final_attributions = []
        final_segments = []
        for segment in segments:
            if segment != '':  # dump empty tokens
                final_segments.append(segment)
                seg_low = segment.lower()
                if len(word_tokens) > i and seg_low == word_tokens[i]:
                    final_attributions.append(word_attributions[i])
                    i += 1
                else:
                    final_attributions.append(0)
        return final_segments, final_attributions

    def get_attribution_for_output(self, explanations_by_output, output_field_index, att, word_tokens,
                                   tokenizer, embedding_name, feature_label):
        """
        Helper function to get attributions for a given output.

        :param explanations_by_output: dictionary
        :param output_field_index: index of the given output
        :param att: dictionary of attributions for the given output
        :param word_tokens: word tokens
        :param tokenizer: keras tokenizer used during training
        :param embedding_name: str. Name of the embedding layer in the model
        :param feature_label: str. Name of the text feature input
        :return:
        """
        # Note - summing over attributions in the embedding direction
        word_attributions = np.sum(att[embedding_name][-len(word_tokens):],
                                   axis=1)
        final_segments, final_attributions = self.text_attributions(tokenizer, word_tokens, word_attributions,
                                                                    feature_label)
        gem_text = gem.GEMText(feature_name=feature_label,
                               text_segments=final_segments,
                               text_attributions=final_attributions)
        gem_container = gem.GEMContainer(contents=[gem_text])
        explanations_by_output[self.output_cols[output_field_index]] = gem_container.render()
        return explanations_by_output

    def get_project_attribution(self, attributions, tokenizer, word_tokens, embedding_name, feature_label):
        """
        Helper method to get project attributions when model has a single text input feature.

        :param attributions: list of IG attributions. Each element of the list corresponds to an output.
        :param tokenizer: tokenizer used during training
        :param word_tokens: word tokens
        :param embedding_name: str. Name of the embedding layer in the model
        :param feature_label: str. Name of the text feature input
        :return:
        """
        explanations_by_output = {}

        if isinstance(feature_label, list):
            if len(feature_label) == 1:
                feature_label = feature_label[0]
            else:
                raise ValueError("Your model has multiple inputs. You cannot use this helper. "
                                 "Please implement project_attributions accordingly. "
                                 "If you need some help, contact Fiddler.")
        if isinstance(embedding_name, list):
            if len(embedding_name) == 1:
                embedding_name = embedding_name[0]
            else:
                raise ValueError("Your model has multiple embeddings. You cannot use this helper. "
                                 "Please implement project_attributions accordingly. "
                                 "If you need some help, contact Fiddler.")

        for output_field_index, att in enumerate(attributions):
            explanations_by_output = self.get_attribution_for_output(explanations_by_output, output_field_index,
                                                                     att, word_tokens, tokenizer, embedding_name,
                                                                     feature_label)

        return explanations_by_output


class IGTabularAttributions:
    """
    Helper class for project attribution method when computing IG for Tabular data.
    """

    def __init__(self, input_df, output_cols):
        """
        :param input_df: pandas dataframe for a single observation
        :param output_cols: list of output column names
        """
        self.input_df = input_df
        self.output_cols = output_cols

    def get_project_attribution(self, attributions, attr_input_names_mapping, embedding_names=None):
        """
        Helper method to get project attributions when input data is tabular.

        :param attributions: list of IG attributions. Each element of the list corresponds to an output.
        :param attr_input_names_mapping: dict that map attributable layer names to input feature names
        :param embedding_names: list. List of name of the embedding layers in the model.
               Default to None if no embedding layers.
        :return:
        """
        if embedding_names is not None and isinstance(embedding_names, str):
            embedding_names = [embedding_names]
        explanations_by_output = {}
        for output_field_index, att in enumerate(attributions):
            dense_features = []
            for key in att.keys():
                if key not in attr_input_names_mapping:
                    raise ValueError(f"The key {key} is missing in the attr_input_names_mapping dictionary.")
                for ind, col in enumerate(attr_input_names_mapping[key]):
                    if (embedding_names is not None) and (key in embedding_names):
                        attr_val = np.sum(att[key][ind])
                    else:
                        attr_val = att[key][ind]
                    dense_features.append(
                        gem.GEMSimple(
                            feature_name=col,
                            value=float(self.input_df.iloc[0][col]),
                            attribution=float(attr_val),
                        )
                    )
            gem_container = gem.GEMContainer(contents=dense_features)
            explanations_by_output[self.output_cols[output_field_index]] = gem_container.render()
        return explanations_by_output
