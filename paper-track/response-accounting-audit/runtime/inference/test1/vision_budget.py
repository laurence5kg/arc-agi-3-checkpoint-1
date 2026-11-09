"""Pinned Qwen processor geometry, including resize bounds and merged patches.

Geometry follows Transformers 5.12.1 Qwen2VL smart_resize (Apache-2.0):
https://github.com/huggingface/transformers/blob/v5.12.1/src/transformers/models/qwen2_vl/image_processing_qwen2_vl.py
The pinned target uses patch_size=16, merge_size=2, min_pixels=65536,
max_pixels=16777216. Chat-template overhead remains part of text calibration.
"""
import math

FACTOR=32
MIN_PIXELS=65536
MAX_PIXELS=16777216


def image_tokens(width,height):
    if type(width) is not int or type(height) is not int or min(width,height)<=0:
        raise ValueError('Invalid image dimensions')
    if max(width,height)>200*min(width,height): raise ValueError('Image aspect ratio exceeds pinned processor support')
    w=round(width/FACTOR)*FACTOR;h=round(height/FACTOR)*FACTOR
    area=w*h
    if area<MIN_PIXELS:
        scale=math.sqrt(MIN_PIXELS/(width*height))
        w=math.ceil(width*scale/FACTOR)*FACTOR;h=math.ceil(height*scale/FACTOR)*FACTOR
    elif area>MAX_PIXELS:
        scale=math.sqrt((width*height)/MAX_PIXELS)
        w=max(FACTOR,math.floor(width/scale/FACTOR)*FACTOR)
        h=max(FACTOR,math.floor(height/scale/FACTOR)*FACTOR)
    return (w//FACTOR)*(h//FACTOR)+2


def validate_processor(config):
    actual=config.get('image_processor',config)
    expected={'patch_size':16,'merge_size':2,'do_resize':True,
        'size':{'shortest_edge':MIN_PIXELS,'longest_edge':MAX_PIXELS}}
    for key,value in expected.items():
        if actual.get(key)!=value: raise ValueError('Pinned image processor contract changed: '+key)
    return expected
