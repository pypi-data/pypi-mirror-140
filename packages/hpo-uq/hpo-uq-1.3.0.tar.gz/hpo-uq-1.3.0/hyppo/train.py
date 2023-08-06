# System
import os
import sys
import logging
import importlib
import time
import types

# External
import yaml
import numpy
import pickle5 as pickle

# Local
from .datasets import get_loader
from .dnnmodels import training, run_uq
from .hyperparams import get_hyperprms
from .utils.extract import gather_trials, check_evaluation_outer_loss
from .obj_fct import calculate_outer_loss

def train_evaluation(x_sc, samples, trainer, model, dist, output='out', data={}, uq={}, **kwargs):
    """
    Execute training according to requested trainer mode. This function looks at the
    trainer mode requested in the configuration file and initiate the training
    accordingly.
    
    Parameters
    ----------
    x_sc : :class:`dict`
      Random hyperparameter set. Each key corresponds to the hyperparameter names
      and the corresponding value to the randomly selected sample value.
    samples : :class:`numpy.ndarray`
      Random hyperparameter integer values for single target evaluation.
    trainer : :class:`str`
      Trainer mode to be used.
    model : :class:`dict`
      Model setting extracted from the YAML configuration file.
    output : :class:`str`
      Directory name to save output training results.
    data : :class:`dict`
      Data setting extracted from the YAML configuration file (empty by default).
    uq : :class:`dict`
      Uncertainty quantification parameter setting extracted from the YAML configuration
      file (empty by default).

    Returns
    -------
    res : :class:`float`
      Output of objective function.
    """
    # Start timer for recording function evaluation time
    start_time = time.time()
    # Display hyperparameter set only once, before the first trial
    hyperprms = get_hyperprms(trainer, x_sc, **model)
    # Prepare list of trial indexes to be evaluated in rank
    trials = numpy.arange(model['trial'])
    if dist['split']=='trial':
        trials = trials[dist['rank']::dist['size']]
    loaders = get_loader(data, **hyperprms, **model, **dist) if trainer=='internal' else None
    # Loop through all selected trials
    for i in trials:
        out_path = '%s/%02i' % (output,i+1)
        if trainer=='internal':
            loss = training(itrial=i,data=loaders,hyperprms=hyperprms,output=out_path,**model,**dist)
        else:
            loss = external_training(i, x_sc, trainer, out_path, model, **dist)
    # Check if all losses over all trials are found
    res = None
    if dist['rank']==0:
        while len(gather_trials(samples,output,**model,**dist)) != model['trial']:
            continue
        losses = gather_trials(samples,output,**model,**dist)
        if 'uq_on' in uq.keys() and uq['uq_on']==True:
            valid_trials = numpy.argwhere(~numpy.isnan(losses)).squeeze()
            res = run_uq(trials=valid_trials,hyperprms=hyperprms,data=loaders,output=output,loss=losses,**model,**dist,**uq)
        else:
            if numpy.isnan(losses).all():
                outer_loss = float('nan')
                inner_loss = float('nan')
                std        = float('nan')
            else:
                outer_loss = numpy.nanmean(calculate_outer_loss(losses,**model))
                inner_loss = numpy.nanmean(losses)
                std        = numpy.nanstd(losses)
            logging.info('-'*40)
            logging.info('OUTER OBJECTIVE FUNCTION {:>8} TRIALS'.format(len(losses)))
            logging.info('-'*40)
            logging.info('\tOuter Loss : {:>11.5f}'.format(outer_loss))
            logging.info('\tInner Loss : {:>11.5f}'.format(inner_loss))
            logging.info('\tSTD        : {:>11.5f}'.format(std))
    else:
        logging.info('-'*40)
        logging.info('Waiting for other processes to finish...')
        while check_evaluation_outer_loss(samples,output,**dist)==False:
            continue
    logging.info('-'*40)
    logging.info("Execution Time : %.3f s" % (time.time() - start_time)) 
    return res

def external_training(itrial, x_sc, trainer, output_dir, model, log_dir, **kwargs):
    start_time = time.time()
    logging.info('-'*40)
    logging.info('{} {:>3} / {:<3} {:>24}'.format('TRIAL',itrial+1,model['trial'],'TRAINING'))
    logging.info('-'*40)
    model['output_dir'] = os.path.join(log_dir,'output',output_dir)
    if 'yaml_input' in model.keys():
        params = yaml_creation(x_sc,model['output_dir'],**model['yaml_input'])
    else:
        params = {**model,**x_sc}
    if type(trainer)==types.FunctionType:
        loss = trainer(**params)
    else:
        modlist = trainer.split('.')
        module = importlib.import_module('.' + modlist[-2], '.'.join(modlist[:-2]))
        loss = eval('module.'+modlist[-1])(**params)
    logging.info('-'*40)
    logging.info('{} {:>3} / {:<3} {:>24}'.format('TRIAL',itrial+1,model['trial'],'TESTING'))
    logging.info('-'*40)
    logging.info('\t Test Loss : {:>11.5f}'.format(loss))
    logging.info('\tTrain Time : {:>11.5f} s'.format(time.time()-start_time))

def yaml_creation(x_sc,output_dir,src,config=None,**kwargs):
    # Extract input configuration file
    with open(src) as f:
        params = yaml.load(f, Loader=yaml.FullLoader)
    # Update parameters
    if config==None:
        params = {**params,**x_sc}
    else:
        params[config] = {**params[config],**x_sc}
    # Save new input configuration file
    os.makedirs(output_dir,exist_ok=True)
    yaml_config = os.path.join(output_dir,'config.yaml')
    with open(yaml_config, 'w') as f:
        yaml.dump(params, f, default_flow_style=False)
    params = {'yaml_config':yaml_config,'config':config,**kwargs}
    return params
