# Project Overview

## Title

Impact-Weighted Optimization for Expert-in-the-Loop Brain Tumor Segmentation

## Core Research Question

Given a fixed, pretrained brain tumor segmentation model and a limited expert correction budget, how should expert effort be optimally allocated across 2D slices to maximize final 3D segmentation quality?

## Problem Framing

This project treats expert interaction as a **decision-making problem**, not a learning or interface problem.

- The segmentation model is frozen.
- The expert cannot review the entire volume.
- Only a limited number of axial slices can be corrected.
- The goal is to decide *which* slices matter most.

The central contribution is a **budget-constrained slice selection strategy** that optimizes downstream segmentation accuracy.

## What This Project IS

- A decision-theoretic formulation of expert-in-the-loop segmentation
- A slice-level optimization problem under a hard budget
- A reproducible, simulation-based evaluation of interaction strategies
- A research prototype suitable for MICCAI / IEEE TMI–style evaluation

## What This Project IS NOT

- Not an interactive UI or annotation tool
- Not an active learning or retraining framework
- Not a human factors or usability study
- Not a new segmentation architecture
- Not a clinical deployment system

## High-Level Phases

1. Problem formulation and scope definition
2. Dataset loading and axial slicing (BraTS)
3. Frozen segmentation backbone inference
4. Predictive uncertainty estimation
5. Correction impact estimation
6. Impact-weighted slice selection algorithm
7. Expert correction simulation
8. Baseline comparison
9. Effort–accuracy trade-off analysis
10. Failure analysis and limitations

Each phase must preserve the separation between:

- Prediction
- Decision
- Correction
- Evaluation

## Success Definition

The project is successful if it demonstrates that intelligent slice selection under a fixed expert budget yields consistently higher segmentation quality than uncertainty-only or random strategies.
