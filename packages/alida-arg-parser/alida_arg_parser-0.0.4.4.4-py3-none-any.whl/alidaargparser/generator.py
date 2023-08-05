from re import template
from jinja2 import Template, defaults
import jinja2
import json
from .translation_dictionary import translation
import os


templates = {"default": "template.py", "spark:3.2.0":"spark_3_2_0.py"}

# Load jinja template
def get_template(path):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), path)
    templateLoader = jinja2.FileSystemLoader(os.path.dirname(path))
    templateEnv = jinja2.Environment(loader=templateLoader)
    return templateEnv.get_template(name=os.path.basename(path))



def generate_meta_model(name, description, framework, area, mode, properties, input_datasets, output_datasets, input_models, output_models, docker_image, json=json):
    
    template = get_template(os.path.join("templates", templates[framework]))

    outputText = template.render(name=name, description=description, area = area, properties=properties, json=json, translation=translation, 
                                input_datasets=input_datasets, output_datasets=output_datasets,
                                input_models=input_models, output_models=output_models,
                                docker_image=docker_image,
                                mode=mode
                                )

    return outputText

