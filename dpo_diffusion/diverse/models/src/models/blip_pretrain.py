'''
 * Adapted from BLIP (https://github.com/salesforce/BLIP)
'''

from models.med import BertConfig, BertModel, BertLMHeadModel
from transformers import BertTokenizer
import transformers
transformers.logging.set_verbosity_error()

import torch
from torch import nn
import torch.nn.functional as F

from models.src.models.blip import create_vit, init_tokenizer, load_checkpoint
from config.options import *
from config.utils import *

class BLIP_Pretrain(nn.Module):
    def __init__(self,                 
                 med_config = config['med_config'],  
                 image_size = 224,
                 vit = 'base',
                 vit_grad_ckpt = False,
                 vit_ckpt_layer = 0,                    
                 embed_dim = 256,     
                 queue_size = 57600,
                 momentum = 0.995,
                 ):
        """
        Args:
            med_config (str): path for the mixture of encoder-decoder model's configuration file
            image_size (int): input image size
            vit (str): model size of vision transformer
        """               
        super().__init__()
        
        self.visual_encoder, vision_width = create_vit(vit, image_size, vit_grad_ckpt, vit_ckpt_layer, 0)
        
        self.tokenizer = init_tokenizer()   
        encoder_config = BertConfig.from_json_file(med_config)
        encoder_config.encoder_width = vision_width
        self.text_encoder = BertModel(config=encoder_config, add_pooling_layer=False)

        text_width = self.text_encoder.config.hidden_size
        
        self.vision_proj = nn.Linear(vision_width, embed_dim)
        self.text_proj = nn.Linear(text_width, embed_dim)


def blip_pretrain(pretrained='', **kwargs):
    model = BLIP_Pretrain(**kwargs)
    if pretrained and get_rank() == 0:
        model, msg = load_checkpoint(model,pretrained)
        print("missing keys:")
        print(msg.missing_keys)
    return model 

