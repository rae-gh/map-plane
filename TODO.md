07/04/2026
[ ] - Bug, the fig01 test works locally but fails in pytest due to the request for negative values in the colouir scale.

03/04/2026
[x] - Add options to umap
[x] - add umap to dataframe for plotting
[x] - enable scrolling though images based on cluster
[ ] - enable overlay of images based on cluster ????? or ..... tau ...... ? Stop procrstinating and write up now with this.

01/01/2026
[x] - Get dssp working
[x] - finish restructure without image classifier

30/03/2026 End of week summary
Done:

    Generated 8,810 peptide bond images across 91 ultra-high resolution structures
    Built Streamlit annotation tool for manual labeling and review
    Established labeling definition — multiple visible rings = True
    ~540 manually labeled (190 True, 348 False)
    Tried image classifier — ResNet18 and UNI — concluded insufficient data and wrong approach for blind classification
    Identified feature-based approach as more scientifically sound

To do:

[ ] - Annotate all 8,810 bonds with features:  
  -  [ ] - B-factor  
  -  [ ] - Secondary structure (DSSP)  
  -  [ ] - Phi/psi/omega, tau angles  
  -  [ ] - Bond lengths inc peptide and C:0
  -  [ ] - Distance from maxima  
  -  [ ] - previous and next aa
  
[ ] - PCA — what drives variance?  
[ ] - UMAP — do ring-positive bonds cluster?  
[ ] - Simple interpretable ML on feature table (random forest / logistic regression) with sklearn
[ ] - Continue manual labeling to grow has_rings ground truth  


