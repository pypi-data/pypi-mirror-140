# AUTOGENERATED! DO NOT EDIT! File to edit: 06_dip.ipynb (unless otherwise specified).

__all__ = ['sparse_to_full', 'SMPL_ForwardKinematics_Sparse', 'iter_pkl_in']

# Cell
import os
import pickle
from pathlib import Path
import numpy as np
import torch
import llamass.core
import llamass.transforms
from einops import repeat, rearrange
from scipy.spatial.transform import Rotation as R

# Cell
def sparse_to_full(joint_angles_sparse, sparse_joints_idxs, tot_nr_joints, rep="rotmat"):
    """
    Pad the given sparse joint angles with identity elements to retrieve a full skeleton with `tot_nr_joints`
    many joints.
    Args:
        joint_angles_sparse: Tensor of shape (N, len(sparse_joints_idxs) * dof)
          or (N, len(sparse_joints_idxs), dof)
        sparse_joints_idxs: A list of joint indices pointing into the full skeleton given by range(0, tot_nr_joints)
        tot_nr_jonts: Total number of joints in the full skeleton.
        rep: Which representation is used, rotmat or quat
    Returns:
        The padded joint angles as an array of shape (N, tot_nr_joints*dof)
    """
    device = joint_angles_sparse.device
    joint_idxs = sparse_joints_idxs
    joint_idx_mapping = {j:i for i,j in enumerate(joint_idxs)}
    assert rep in ["rotmat", "quat", "aa"]
    dof = 9 if rep == "rotmat" else 4 if rep == "quat" else 3
    n_sparse_joints = len(sparse_joints_idxs)
    angles_sparse = joint_angles_sparse.view(-1, n_sparse_joints, dof)



    # fill in the missing indices with the identity element
    N = angles_sparse.size(0)
    #smpl_full = torch.zeros((N, tot_nr_joints, dof)).to(device)
    if rep == "quat":
        smpl_full = torch.tensor([1.0, 0., 0., 0.]).to(device)
        #smpl_full[..., 0] = 1.0
    elif rep == "rotmat":
        smpl_full = torch.eye(3).view(-1).to(device)
        #smpl_full[..., 0] = 1.0
        #smpl_full[..., 4] = 1.0
        #smpl_full[..., 8] = 1.0
    else:
        smpl_full = torch.zeros(3).to(device)

    # repeat these tensors along the N axis
    smpl_full = repeat(smpl_full, 'd -> N () d', N=N)

    # make a list of tensors for each joint
    joint_tensors = []
    for j in range(tot_nr_joints):
        if j in joint_idxs:
            k = joint_idx_mapping[j]
            joint_tensors.append(angles_sparse[:, [k]])
        else:
            joint_tensors.append(smpl_full)

    smpl_full =  torch.cat(joint_tensors, 1)
    smpl_full = smpl_full.view(-1, tot_nr_joints*dof)
    return smpl_full

# Cell
class SMPL_ForwardKinematics_Sparse(llamass.transforms.SMPL_ForwardKinematics):
    def from_rotmat(self, joint_angles):
        mj, nj = self.major_joints, self.n_joints
        return super().from_rotmat(sparse_to_full(joint_angles, mj, nj, rep="rotmat"))

    def from_aa(self, joint_angles):
        mj, nj = self.major_joints, self.n_joints
        return super().from_aa(sparse_to_full(joint_angles, mj, nj, rep="aa"))

# Cell
def iter_pkl_in(dip_dir):
    # open a random pickle file in the DIPS dataset
    example_file = None
    for dirpath, dirnames, filenames in os.walk(dips_path):
        dirpath = Path(dirpath)
        for filename in filenames:
            filename = Path(filename)
            if not filename.is_dir() and filename.suffix == ".pkl":
                yield dirpath/filename