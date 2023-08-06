import tensorflow as tf

from transformers.modeling_tf_utils import shape_list
from transformers import TFBertModel, AutoTokenizer
        
from transformers.modeling_tf_outputs import TFBaseModelOutputWithPooling
from transformers.file_utils import DUMMY_INPUTS, DUMMY_MASK

from polus.core import get_jit_compile
from polus.models import PolusModel

class TFBertSplited(PolusModel):
    
    def __init__(self, 
                 bert_layers, 
                 *args,
                 run_in_training_mode = True,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.layer = bert_layers
        self.run_in_training_mode = run_in_training_mode
    
    def _efficient_attention_mask(self, x):
        # This codes mimics the transformer BERT implementation: https://github.com/huggingface/transformers/blob/master/src/transformers/models/bert/modeling_tf_bert.py#L1057
        
        attention_mask_shape = shape_list(x)

        
        extended_attention_mask = tf.reshape(
                x, (attention_mask_shape[0], 1, 1, attention_mask_shape[1])
            )

        # Since attention_mask is 1.0 for positions we want to attend and 0.0 for
        # masked positions, this operation will create a tensor which is 0.0 for
        # positions we want to attend and -10000.0 for masked positions.
        # Since we are adding it to the raw scores before the softmax, this is
        # effectively the same as removing these entirely.
        extended_attention_mask = tf.cast(extended_attention_mask, dtype=tf.float32)
        one_cst = tf.constant(1.0, dtype=tf.float32)
        ten_thousand_cst = tf.constant(-10000.0, dtype=tf.float32)
        extended_attention_mask = tf.multiply(tf.subtract(one_cst, extended_attention_mask), ten_thousand_cst)
        
        return extended_attention_mask
    
    @tf.function(input_signature=[tf.TensorSpec([None, None, None], dtype=tf.float32),
                                  tf.TensorSpec([None, None], dtype=tf.int32),
                                  tf.TensorSpec([], dtype=tf.bool)],
                jit_compile=get_jit_compile())
    def call(self, hidden_states, attention_mask, training=False):
        
        attention_mask = self._efficient_attention_mask(attention_mask)
        
        for layer_module in self.layer:
            hidden_states = layer_module(hidden_states=hidden_states, 
                                         attention_mask=attention_mask,
                                         head_mask=None,
                                         output_attentions=None,
                                         encoder_hidden_states=None, 
                                         encoder_attention_mask=None, 
                                         past_key_value=None,
                                         training=(self.run_in_training_mode & training))[0]

        return TFBaseModelOutputWithPooling(last_hidden_state=hidden_states,
                                            pooler_output=hidden_states[:,0,:])

    
def split_bert_model_from_checkpoint(bert_model_checkpoint, 
                                     index_layer, 
                                     init_models=False,
                                     return_pre_bert_model=True,
                                     return_post_bert_model=True):
    
    bert_model = TFBertModel.from_pretrained(bert_model_checkpoint,
                                             output_attentions = False,
                                             output_hidden_states = False,
                                             return_dict=True,
                                             from_pt=True)
    
    output = split_bert_model(bert_model, 
                              index_layer, 
                              init_models=init_models,
                              return_pre_bert_model=return_pre_bert_model,
                              return_post_bert_model=return_post_bert_model)
    
    if not return_pre_bert_model:
        del bert_model
    
    return output
    
def split_bert_model(bert_model, 
                     index_layer, 
                     init_models=False,
                     return_pre_bert_model=True,
                     return_post_bert_model=True):
    """
    Utility function that splits a bert model in a pre established index, given by *index_layer*,
    which results into two models. The *pre_model* that corresponds to the *bert_model* but without
    a some layers that were cut off and a *post_model* that corresponds to a *PolusModel*, which runs
    the remain bert layers.
    """
    
    assert return_pre_bert_model or return_post_bert_model # at least one must be true
    
    assert  bert_model.config.num_hidden_layers > index_layer > -bert_model.config.num_hidden_layers and index_layer!=0
    
    # create a new keras model that uses the layers previous removed bert layers
    if return_post_bert_model:
        encoder_layers = bert_model.layers[0].encoder.layer[index_layer:]
        post_model = TFBertSplited(encoder_layers)
    
    if return_pre_bert_model:
        del bert_model.layers[0].encoder.layer[index_layer:]
        bert_model.config.num_hidden_layers = len(bert_model.layers[0].encoder.layer)
    else:
        del bert_model
    
    
    
    if init_models and return_pre_bert_model:
        # run a dummy example to build post_model and check for errors
        sample = "hello, this is a sample that i want to tokenize"
        
        tokenizer = AutoTokenizer.from_pretrained(bert_model.config._name_or_path)
        
        inputs = tokenizer.encode_plus(sample,
                                           padding = "max_length",
                                           truncation = True,
                                           max_length = 50,
                                           return_attention_mask = True,
                                           return_token_type_ids = True,
                                           return_tensors = "tf",
                                          )
        hidden_states = bert_model(**inputs)["last_hidden_state"]
            
        if return_post_bert_model:
            post_model(hidden_states=hidden_states, attention_mask=inputs["attention_mask"])
    
    if return_pre_bert_model and return_post_bert_model:
        return bert_model, post_model
    if return_pre_bert_model:
        return bert_model
    if return_post_bert_model:
        return post_model