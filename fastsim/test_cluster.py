import unittest
from pfobjects import Cluster, SmearedCluster
from detectors.CMS import cms
from ROOT import TVector3
import math
import numpy as np
from ROOT import TFile, TH1F, TH2F
 
class TestCluster(unittest.TestCase):

    def test_pt(self):
        '''Test that pT is correctly set.'''
        cluster = Cluster(10., TVector3(1,0,0), 1, 1)
        self.assertAlmostEqual(cluster.pt, 10.)
        cluster.set_energy(5.)
        self.assertAlmostEqual(cluster.pt, 5.)

    def test_smear(self):
        rootfile = TFile('test_cluster_smear.root', 'recreate')
        h_e = TH1F('h_e','cluster energy', 200, 5, 15.)
        energy = 10.
        cluster = Cluster(energy, TVector3(1,0,0), 1, 1)
        ecal = cms.elements['ecal']
        energies = []
        for i in range(10000):
            smeared = cluster.smear(ecal, accept=True)
            h_e.Fill(smeared.energy)
            energies.append(smeared.energy)
        npe = np.array(energies)
        mean = np.mean(npe)
        rms = np.std(npe)
        eres = ecal.energy_resolution(cluster)
        self.assertAlmostEqual(mean, energy, places=2)
        self.assertAlmostEqual(rms, eres*energy, places=2)
        rootfile.Write()
        rootfile.Close()
        
    def test_acceptance(self):
        rootfile = TFile('test_cluster_acceptance.root', 'recreate')
        h_evseta = TH2F('h_evseta','cluster energy vs eta',
                        100, -5, 5, 100, 0, 15)
        h_ptvseta = TH2F('h_ptvseta','cluster pt vs eta',
                         100, -5, 5, 100, 0, 15)
        nclust = 10000.
        energies = np.random.uniform(0., 10., nclust)
        thetas = np.random.uniform(0, math.pi, nclust)
        costhetas = np.cos(thetas)
        sinthetas = np.sin(thetas)
        clusters = []
        for energy, cos, sin in zip(energies, costhetas, sinthetas):
            clusters.append(Cluster(energy, TVector3(sin,0,cos), 1, 1))
        ecal = cms.elements['ecal']
        smeared_clusters = []
        min_energy = -999.
        for cluster in clusters:
            smeared_cluster = cluster.smear(ecal)
            if smeared_cluster:
                h_evseta.Fill(smeared_cluster.position.Eta(),
                              smeared_cluster.energy)
                h_ptvseta.Fill(smeared_cluster.position.Eta(),
                               smeared_cluster.pt)
                smeared_clusters.append(smeared_cluster)
                if smeared_cluster.energy > min_energy:
                    min_energy = smeared_cluster.energy
        self.assertGreater(len(clusters), len(smeared_clusters))
        self.assertGreater(min_energy, ecal.emin)
        rootfile.Write()
        rootfile.Close()
        
if __name__ == '__main__':
    unittest.main()
