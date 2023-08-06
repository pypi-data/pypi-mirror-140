import re

def get_params_names(pipeline, param_str='.*'):
    """Función para filtrar los nombres de los parámetros que interesan 
    del pipeline.

    Args:
        param_str (str, optional): Expresión regular a matchear. 
            Defaults to 'estimator__'.
    """
    return [x for x in pipeline.get_params().keys() if 
            re.compile(param_str).search(x)]