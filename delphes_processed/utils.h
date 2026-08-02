#ifndef UTILS_H
#define UTILS_H

#include "TLorentzVector.h"
#include "ROOT/RVec.hxx"
#include <vector>
#include <cmath>

namespace FCCAnalyses {

    // Reconstructs two Dark Photons from 4 muons by minimizing the mass difference
    std::vector<float> reconstruct_dark_photons(ROOT::VecOps::RVec<TLorentzVector> vecs, ROOT::VecOps::RVec<float> charges) {
        std::vector<float> masses;
        
        // Safety check: Ensure we have exactly 4 muons
        if (vecs.size() != 4 || charges.size() != 4) return masses;
        
        // Separate into positive and negative muons
        std::vector<TLorentzVector> pos, neg;
        for (size_t i = 0; i < 4; ++i) {
            if (charges[i] > 0) pos.push_back(vecs[i]);
            else neg.push_back(vecs[i]);
        }
        
        // Safety check: We need exactly 2 positive and 2 negative
        if (pos.size() != 2 || neg.size() != 2) return masses;
        
        // Option 1: Pair (Pos1+Neg1) and (Pos2+Neg2)
        float m1_A = (pos[0] + neg[0]).M();
        float m1_B = (pos[1] + neg[1]).M();
        float diff1 = std::abs(m1_A - m1_B);
        
        // Option 2: Pair (Pos1+Neg2) and (Pos2+Neg1)
        float m2_A = (pos[0] + neg[1]).M();
        float m2_B = (pos[1] + neg[0]).M();
        float diff2 = std::abs(m2_A - m2_B);
        
        // Keep the pairing that produces the most similar masses
        if (diff1 < diff2) {
            masses.push_back(m1_A); masses.push_back(m1_B);
        } else {
            masses.push_back(m2_A); masses.push_back(m2_B);
        }
        return masses;
    }

} // end namespace FCCAnalyses

#endif
