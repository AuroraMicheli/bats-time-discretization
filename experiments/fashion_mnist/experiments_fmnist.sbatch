#!/bin/sh

#SBATCH --partition=prb,insy,general
#SBATCH --qos=short
#SBATCH --time=3:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8192
#SBATCH --mail-type=END
#SBATCH --gres=gpu

source ~/.bashrc

module use /opt/insy/modulefiles
module load cuda/10.0 cudnn/10.0-7.4.2.24
module load devtoolset/7

dt="$1"

srun python experiments_fmnist.py --dt "$dt"