# Methods: Automated Ring Artefact Classification

## Image Generation

Electron density slice images were generated for all peptide bonds across
the complete set of ultra-high resolution structures retrieved from the
Protein Data Bank (PDB) on 23 March 2026 (query: X-ray structures with
resolution ≤ 0.8 Å; n = 91 structures). For each peptide bond, a 2D slice
through the electron density map was computed in the plane defined by three
atomic coordinates: the central carbonyl carbon (origin), the adjacent
nitrogen (x-axis direction), and a planar atom defining the peptide plane
orientation.

Slices were rendered as heatmaps with the following fixed parameters across
all images to ensure comparability:

- **Width**: 6 Å
- **Sampling**: 400 × 400 grid points (for labeling); images saved at
  reduced resolution for training
- **Interpolation**: B-spline
- **Density clipping**: 1st to 85th percentile, to reveal interatomic
  features otherwise obscured by the dynamic range of atomic peak density

To prevent the classifier from learning structure-specific features rather
than density patterns, each image was assigned a random filename (UUID4)
with no embedded structural information. A separate metadata file records
the mapping between filenames and structural identifiers (PDB code, residue
index, amino acid, resolution).

In total, 8,810 images were generated across 91 structures.

## Manual Labeling

A subset of images was manually classified by the author using an
interactive labeling tool. Images were presented in randomised order to
avoid systematic bias from sequential structure labeling. Each image was
assigned one of three labels:

- **True** — Fourier truncation rings clearly visible in the peptide bond plane
- **False** — No rings visible
- **Uncertain** — Rings ambiguous or partially visible

A conservative labeling threshold was applied: images were labeled True
only when rings were unambiguously present. Borderline cases were labeled
Uncertain and excluded from classifier training.

A total of [N] images were manually labeled ([N_true] True, [N_false]
False, [N_uncertain] Uncertain). All manually labeled images are recorded
as `classified_by = human` and `manually_verified = True` in the metadata
file.

## Classifier Training

A binary image classifier was trained to predict `has_rings` (True/False)
using transfer learning from a ResNet18 architecture pretrained on
ImageNet. All convolutional layers were frozen; only the final fully
connected layer was retrained on the labeled dataset. This approach is
appropriate given the relatively small labeled dataset and leverages the
pretrained model's existing knowledge of low-level visual features
(edges, periodic patterns, contrast gradients) relevant to ring detection.

Uncertain labels were excluded from training. The labeled dataset was
split into training (80%) and validation (20%) sets using stratified
sampling to preserve the True/False class ratio in both splits.

Training hyperparameters:

| Parameter           | Value        |
|---------------------|--------------|
| Architecture        | ResNet18     |
| Pretrained weights  | ImageNet     |
| Image size          | 224 × 224    |
| Batch size          | 16           |
| Learning rate       | 1 × 10⁻⁴    |
| Epochs              | 10           |
| Loss function       | BCE with logits |
| Optimiser           | Adam         |
| Decision threshold  | 0.62         |

The decision threshold was set to 0.62 (rather than the default 0.5) to
reduce false positive predictions of ring presence, reflecting the
conservative approach applied during manual labeling.

Data augmentation during training comprised random horizontal and vertical
flips and minor brightness/contrast jitter. No geometric distortions were
applied, as the orientation of the density plane is physically meaningful.

Model performance was evaluated on the held-out validation set using
accuracy, precision, recall, and F1-score for each class, together with
a confusion matrix.

## Inference and Verification

The trained classifier was applied to all unlabeled images to generate
predicted labels and confidence scores (sigmoid probability). Predictions
were recorded alongside `classified_by = model_vN` in the metadata file,
where N denotes the model version.

Images were ranked by classification confidence (distance from decision
boundary). Low-confidence predictions (probability closest to the decision
threshold) were prioritised for manual verification. High-confidence
predictions were accepted subject to random spot-checking.

The labeling, training, and inference pipeline was iterated until
sufficient coverage was achieved across the full dataset.

All model weights, training metadata, and the complete labeled dataset are
deposited at [Zenodo DOI: TBD].