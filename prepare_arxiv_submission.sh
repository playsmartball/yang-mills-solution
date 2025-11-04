#!/bin/bash
# prepare_arxiv_submission.sh
# Prepares clean arXiv submission package

echo "======================================"
echo "arXiv Submission Package Preparation"
echo "======================================"
echo ""

# Create submission directory
SUBMIT_DIR="arxiv_submission"
rm -rf $SUBMIT_DIR
mkdir -p $SUBMIT_DIR

echo "✓ Created submission directory: $SUBMIT_DIR"

# Copy main manuscript
cp manuscript_skeleton.tex $SUBMIT_DIR/manuscript.tex
echo "✓ Copied main manuscript"

# Copy all appendices
cp appendix_technical_lemmas.tex $SUBMIT_DIR/
cp appendix_A2_measure_construction_full.tex $SUBMIT_DIR/
cp appendix_phi_regularization_rigorous.tex $SUBMIT_DIR/
cp appendix_B_reflection_positivity_full_proof.tex $SUBMIT_DIR/
cp appendix_spectral_gap_proof.tex $SUBMIT_DIR/
cp appendix_lattice_implementation.tex $SUBMIT_DIR/
echo "✓ Copied all appendices (6 files)"

# Convert figures to PDF if needed (arXiv prefers PDF)
if [ -f "coupling_evolution.png" ]; then
    echo "⚠ Note: Convert PNG figures to PDF for better arXiv compatibility"
    echo "  Use: convert coupling_evolution.png coupling_evolution.pdf"
fi

# Create README for arXiv admins
cat > $SUBMIT_DIR/00README.txt << 'EOF'
Yang-Mills Mass Gap Solution via φ-Coordinate Regularization

Main file: manuscript.tex

Appendices (automatically included via \input):
- appendix_technical_lemmas.tex
- appendix_A2_measure_construction_full.tex  
- appendix_phi_regularization_rigorous.tex
- appendix_B_reflection_positivity_full_proof.tex
- appendix_spectral_gap_proof.tex
 - appendix_lattice_implementation.tex

Compile: pdflatex manuscript.tex (twice for references)

Code and data: github.com/playsmartball/yang-mills-solution

Contact: jhodge1@mail.stmarytx.edu
EOF

echo "✓ Created 00README.txt for arXiv admins"

# Check for complete LaTeX compilation
cd $SUBMIT_DIR
echo ""
echo "Testing LaTeX compilation..."
pdflatex -interaction=nonstopmode manuscript.tex > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✓ LaTeX compilation successful!"
    pdflatex -interaction=nonstopmode manuscript.tex > /dev/null 2>&1
    echo "✓ Second pass completed (for references)"
    
    # Count pages
    PAGES=$(pdfinfo manuscript.pdf 2>/dev/null | grep Pages | awk '{print $2}')
    if [ ! -z "$PAGES" ]; then
        echo "✓ Generated PDF: $PAGES pages"
    fi
else
    echo "⚠ LaTeX compilation had warnings/errors"
    echo "  Check log file: $SUBMIT_DIR/manuscript.log"
fi

cd ..

# Create tarball for upload
echo ""
echo "Creating submission tarball..."
cd $SUBMIT_DIR
tar -czf ../yang-mills-arxiv.tar.gz *.tex 00README.txt
cd ..
echo "✓ Created: yang-mills-arxiv.tar.gz"

# Summary
echo ""
echo "======================================"
echo "Submission Package Ready!"
echo "======================================"
echo ""
echo "Contents of $SUBMIT_DIR/:"
ls -lh $SUBMIT_DIR/
echo ""
echo "Upload options:"
echo "  1. Individual .tex files from $SUBMIT_DIR/"
echo "  2. Tarball: yang-mills-arxiv.tar.gz"
echo ""
echo "Next steps:"
echo "  1. Review generated PDF: $SUBMIT_DIR/manuscript.pdf"
echo "  2. Check page count (should be 60-80 with appendices)"
echo "  3. Upload to arXiv.org"
echo ""
echo "Categories to select:"
echo "  - Primary: hep-th"
echo "  - Cross-list: math-ph, hep-lat"
echo ""
echo "Good luck! 🚀"
