import os
import time
import argparse
import torch


def get_options(args=None):
    parser = argparse.ArgumentParser(
        description="Attention based model for solving the Travelling Salesman Problem with Reinforcement Learning")

    # Data
    parser.add_argument('--problem', default='tsp', help="The problem to solve, default 'tsp'") # Default is tsp, for CVRP set it to cvrp
    parser.add_argument('--graph_size', type=int, default=20, help="set to -1 when training for graph size variation expt. Set to 40 when training for GM distribution and Scaling expt. In case of run_single.py it is set to the graph size such as 40./0/120 etc.")
    parser.add_argument('--batch_size', type=int, default=256, help='Number of instances per batch during training')
    parser.add_argument('--epoch_size', type=int, default=None, help='depends upon batch size and fine tuning steps')
    parser.add_argument('--epoch_size_multi_single', type=int, default=256, help='same as batch size, check baseline defined in train_multi, train.py')

    parser.add_argument('--k_tune_steps', type=int, default=50, help='Number of inner fine tuning steps during training. Set to 50( parameter applicable only to meta-training run.py) ')

    parser.add_argument('--num_modes', type=int, default=None, help='num modes in gmm')


    parser.add_argument('--graph_size_continuous', action='store_true', help='continuous graph size')
    parser.add_argument('--train_tasks', type=str, default=None, help='train_tasks for cvrp') #cvrp

    parser.add_argument('--vrp_capacity', type=float, default=None, help='vrp_capacity')
    parser.add_argument('--alpha_decay', type=float, default=0.999, help='decaying reptile alpha')
    parser.add_argument('--alpha', type=float, default=0.99, help='alpha')

    parser.add_argument('--test_num_step_epochs', type=int, default=30, help='Fine_tuning steps test')
    parser.add_argument('--longer_fine_tune', type=int, default=0, help='long fine tune')# 0 no, 1 yes

    parser.add_argument('--write_test_file_tVSq', type=str, default=None, help='write_test_file_tVSquality for plot')  # 0 no, 1 yes

    parser.add_argument('--task_normalization', type=int, default=1, help="0 or 1. Whether to use task weights or not. Only applicable when using run.py( meta training) ")# 0 no, 1 yes

    parser.add_argument('--batch_size_query', type=int, default=512, help='Number of instances per batch during training')

    parser.add_argument('--epoch_size_query', type=int, default=512, help='Number of instances per epoch during training')
    parser.add_argument('--variation_type', type=str, default="size", help='graph_size or distribution or scale')
    parser.add_argument('--test_at_epoch_id', type=int, default=-1, help='Test on epoch id')

    parser.add_argument('--val_size', type=int, default=10000,
                        help='Number of instances used for reporting validation performance')


    parser.add_argument('--test_size', type=int, default=5000,
                        help='Number of instances used for reporting validation performance')

    parser.add_argument('--val_dataset', type=str, default="data/", help='Set to location where datasets are stored (set to  data/ )')


    parser.add_argument('--val_result_pickle_file', type=str, default=None, help='Name of pickle file which stores best validation epoch ')
    parser.add_argument('--test_result_pickle_file', type=str, default=None, help=' Stores the result of the model on test set')

    parser.add_argument('--tsp_file_ft', type=str, default=None,
                        help=' Stores the result of the model on test set')
    parser.add_argument('--tsp_file_test', type=str, default=None,
                        help=' Stores the result of the model on test set')

    parser.add_argument('--test_file_original_full_path_cvrplib', type=str, default=None,
                        help=' Stores the result of the model on test set')


    parser.add_argument('--scale', type=float, default=None, help='Scale')


    parser.add_argument('--opts_long_tune_for', type=str, default=None, help='Scale')


    parser.add_argument('--baseline_every_Xepochs_for_META', type=int, default=40, help='Controls frequency of baseline update. Set to 7 for meta-training. ( need to set  only for  meta-training run.py, for multi and scratch it is set to default value in options.py)')


    # Model
    parser.add_argument('--model', default='attention', help="Model, 'attention' (default) or 'pointer'")
    parser.add_argument('--embedding_dim', type=int, default=128, help='Dimension of input embedding')
    parser.add_argument('--hidden_dim', type=int, default=128, help='Dimension of hidden layers in Enc/Dec')
    parser.add_argument('--n_encode_layers', type=int, default=3,
                        help='Number of layers in the encoder/critic network')
    parser.add_argument('--tanh_clipping', type=float, default=10.,
                        help='Clip the parameters to within +- this value using tanh. '
                             'Set to 0 to not perform any clipping.')
    parser.add_argument('--normalization', default='batch', help="Normalization type, 'batch' (default) or 'instance'")

    # Training
    parser.add_argument('--lr_model', type=float, default=1e-4, help="Set the learning rate for the actor network")
    parser.add_argument('--lr_critic', type=float, default=1e-4, help="Set the learning rate for the critic network")
    parser.add_argument('--lr_decay', type=float, default=1.0, help='Learning rate decay per epoch')
    parser.add_argument('--eval_only', action='store_true', help='Set this value to only evaluate model')
    parser.add_argument('--n_epochs', type=int, default=1500000, help='The number of epochs to train')
    parser.add_argument('--seed', type=int, default=1234, help='Random seed to use')
    parser.add_argument('--max_grad_norm', type=float, default=1.0,
                        help='Maximum L2 norm for gradient clipping, default 1.0 (0 to disable clipping)')
    parser.add_argument('--no_cuda', action='store_true', help='Disable CUDA')
    parser.add_argument('--exp_beta', type=float, default=0.8,
                        help='Exponential moving average baseline decay (default 0.8)')
    parser.add_argument('--baseline', default='rollout',
                        help="Baseline to use: 'rollout', 'critic' or 'exponential'. Defaults to no baseline.")
    parser.add_argument('--bl_alpha', type=float, default=0.05,
                        help='Significance in the t-test for updating rollout baseline')
    parser.add_argument('--bl_warmup_epochs', type=int, default=None,
                        help='Number of epochs to warmup the baseline, default None means 1 for rollout (exponential '
                             'used for warmup phase), 0 otherwise. Can only be used with rollout baseline.')
    parser.add_argument('--eval_batch_size', type=int, default=1024,
                        help="Batch size to use during (baseline) evaluation")
    parser.add_argument('--checkpoint_encoder', action='store_true',
                        help='Set to decrease memory usage by checkpointing encoder')
    parser.add_argument('--shrink_size', type=int, default=None,
                        help='Shrink the batch size if at least this many instances in the batch are finished'
                             ' to save memory (default None means no shrinking)')
    parser.add_argument('--data_distribution', type=str, default=None,
                        help='Data distribution to use during training, defaults and options depend on problem.')

    # Misc
    parser.add_argument('--log_step', type=int, default=50, help='Log info every log_step steps')
    parser.add_argument('--log_dir', default='logs', help='Directory to write TensorBoard information to')
    parser.add_argument('--run_name', default='run', help='Name to identify the run')
    parser.add_argument('--output_dir', default='outputs', help='Directory to write output models to')
    parser.add_argument('--epoch_start', type=int, default=0,
                        help='Start at epoch # (relevant for learning rate decay)')
    parser.add_argument('--checkpoint_epochs', type=int, default=1,
                        help='Save checkpoint every n epochs (default 1), 0 to save no checkpoints')
    parser.add_argument('--load_path', help='Path to load model parameters and optimizer state from')
    parser.add_argument('--resume', help='Resume from previous checkpoint file')
    parser.add_argument('--no_tensorboard', action='store_true', help='Disable logging TensorBoard files')
    parser.add_argument('--no_progress_bar', action='store_true', help='Disable progress bar')



    parser.add_argument('--rescale_for_testing', type=int, default=None, help='for testing purpose for scale 3, for different scales')

    opts = parser.parse_args(args)

    opts.use_cuda = torch.cuda.is_available() and not opts.no_cuda
    opts.run_name = "{}".format(opts.run_name)
    root_folder_name = ''
    if(opts.variation_type=='graph_size'):
        root_folder_name='SIZE'
    if (opts.variation_type == 'distribution'):
        root_folder_name = 'MODE'
    if (opts.variation_type == 'scale'):
        root_folder_name = 'SCALE'

    if (opts.variation_type == 'cap_vrp'):
        root_folder_name = 'CAP_VRP'

    if (opts.variation_type == 'mix_distribution_size'):
        root_folder_name = 'MIX_VRP'

    opts.save_dir = os.path.join(
        opts.output_dir,opts.problem,root_folder_name,
        opts.run_name
    )

    print(" opts.save_dir ", opts.save_dir)
    if opts.bl_warmup_epochs is None:
        opts.bl_warmup_epochs = 1 if opts.baseline == 'rollout' else 0
    assert (opts.bl_warmup_epochs == 0) or (opts.baseline == 'rollout')
    # assert opts.epoch_size % opts.batch_size == 0, "Epoch size must be integer multiple of batch size!"
    return opts
